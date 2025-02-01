import sys
import time
import pyfiglet
import urwid
import urwid.escape as esc
import requests

# Constants for cursor control
SHOW_CURSOR = "\x1b[?25h"
HIDE_CURSOR = "\x1b[?25l"


class LeftLabelLineBox(urwid.WidgetWrap):
    """
    A custom widget similar to urwid.LineBox().
    It draws a box around the given widget and
    optionally places a label on the left edge of the top border.
    """
    def __init__(
        self,
        original_widget: urwid.Widget,
        label: str = "",
        tlcorner: str = "┌",
        tline: str = "─",
        trcorner: str = "┐",
        lline: str = "│",
        rline: str = "│",
        blcorner: str = "└",
        bline: str = "─",
        brcorner: str = "┘",
    ):
        self.original_widget = original_widget
        self.label = label
        self.tlcorner = tlcorner
        self.tline = tline
        self.trcorner = trcorner
        self.lline = lline
        self.rline = rline
        self.blcorner = blcorner
        self.bline = bline
        self.brcorner = brcorner
        super().__init__(self._construct())

    def _construct(self) -> urwid.Widget:
        top_left = urwid.Text(self.tlcorner + self.label)
        top_line = urwid.SolidFill(self.tline)
        top_right = urwid.Text(self.trcorner)

        top_row = urwid.Columns(
            [
                ("pack", top_left),
                ("weight", 1, top_line),
                ("pack", top_right),
            ],
            box_columns=[1],
            dividechars=0,
            focus_column=None
        )

        middle_row = urwid.LineBox(
            self.original_widget,
            title="",
            tlcorner=self.lline, tline="",
            trcorner=self.rline,
            lline=self.lline, rline=self.rline,
            blcorner=self.lline, bline="",
            brcorner=self.rline
        )

        bottom_left = urwid.Text(self.blcorner)
        bottom_line = urwid.SolidFill(self.bline)
        bottom_right = urwid.Text(self.brcorner)

        bottom_row = urwid.Columns(
            [
                ("pack", bottom_left),
                ("weight", 1, bottom_line),
                ("pack", bottom_right),
            ],
            box_columns=[1],
            dividechars=0,
            focus_column=None
        )

        return urwid.Pile([
            ("pack", top_row),
            middle_row,
            ("pack", bottom_row),
        ])


class CursorAwareEdit(urwid.Edit):
    """
    Edit widget that explicitly shows the cursor when focused
    and triggers search on ENTER.
    """
    def __init__(self, controller, caption="", edit_text="", allow_tab=False):
        super().__init__(caption=caption, edit_text=edit_text, allow_tab=allow_tab)
        self.controller = controller

    def render(self, size, focus=False):
        if focus:
            esc.SHOW_CURSOR = SHOW_CURSOR
        return super().render(size, focus)

    def keypress(self, size, key):
        # If user presses ENTER, perform the search
        if key == 'enter':
            self.controller.perform_search(self.edit_text)
            return
        return super().keypress(size, key)


class MenuButton(urwid.Button):
    """
    Custom button class that supports plain string or (attr, string) caption.
    This avoids type errors by storing and rendering styled text fragments.
    """
    def __init__(self, caption, on_press=None, user_data=None):
        super().__init__("", on_press=on_press, user_data=user_data)

        self._prefix_unfocused = "   "
        self._prefix_focused = "-> "

        # Decide how to store style and text
        if isinstance(caption, tuple) and len(caption) == 2:
            self._style, self._text = caption
        else:
            self._style, self._text = "menu-normal", str(caption)

        label_text = [
            (self._style, self._prefix_unfocused),
            (self._style, self._text)
        ]
        self._label = urwid.SelectableIcon(label_text, cursor_position=-1)
        self._w = urwid.AttrMap(
            urwid.Padding(self._label, align="left", width=("relative", 100)),
            "menu-normal",
            "menu-focus"
        )

    def render(self, size, focus=False):
        # Hide the cursor in the results box, but highlight with arrow if focused
        if focus:
            esc.SHOW_CURSOR = HIDE_CURSOR
            label_text = [
                (self._style, self._prefix_focused),
                (self._style, self._text)
            ]
        else:
            label_text = [
                (self._style, self._prefix_unfocused),
                (self._style, self._text)
            ]
        self._label.set_text(label_text)
        self._label.cursor_position = -1
        return super().render(size, focus)

    def get_caption(self):
        return self._text


class NonTabSearchPile(urwid.Pile):
    """
    Custom Pile that manages cursor visibility based on which widget is focused.
    Index 0 is the search input, so we show the cursor there. Otherwise, we hide it.
    """
    def render(self, size, focus=False):
        if self.focus_position == 0:
            esc.SHOW_CURSOR = SHOW_CURSOR
        else:
            esc.SHOW_CURSOR = HIDE_CURSOR
        return super().render(size, focus)

    def keypress(self, size, key):
        if key == "tab":
            return key
        return super().keypress(size, key)


class MouseAwarePile(urwid.Pile):
    """
    Mouse-aware top-level Pile that decides which widget gets focus
    based on where the user clicks.
    By default, Urwid doesn't always focus the search Edit widget if you
    click on it. This class handles that scenario to allow typing in the box.
    """
    def mouse_event(self, size, event, button, col, row, focus):
        if button == 1 and event == "mouse press":
            # We'll figure out if the user clicked the top (search box) or the bottom (menu box)
            box0_size = self.contents[0][0].rows(size, focus=True)
            # The first item is "search_box", the second is the big menu box
            if row < box0_size:
                self.focus_position = 0  # Focus on the search box
            else:
                self.focus_position = 1  # Focus on the menu box
        return super().mouse_event(size, event, button, col, row, focus)


class FocusReportingListBox(urwid.ListBox):
    """
    A custom ListBox that retains default key and mouse behaviors for the menu.
    """
    def __init__(self, body, controller):
        super().__init__(body)
        self.controller = controller

    def keypress(self, size, key):
        return super().keypress(size, key)

    def mouse_event(self, size, event, button, col, row, focus):
        return super().mouse_event(size, event, button, col, row, focus)


class MenuController:
    """
    Controller that handles searching after ENTER instead of on each keystroke.
    Displays status messages in a separate message area in 'g42' color,
    centers them, rather than using the menu items as placeholders.
    """
    def __init__(self):
        self.menu_list = None
        self.message_widget = urwid.Text(("g42", "Results appear here."), align="center")
        self.footer = urwid.Text(
            ("instructions", " q/esc: Quit  ↑/↓: Navigate  n: Focus Search "),
            align="center"
        )
        self.menu_content = None
        self.menu_pile = None
        self.loop = None

    def menu_handler(self, button, choice):
        pass

    def exit_program(self, button=None):
        raise urwid.ExitMainLoop()

    def perform_search(self, query):
        """
        Called when the user presses ENTER in the search box.
        Displays 'Fetching...' in the message area,
        fetches anime data from Jikan v4,
        then updates the result list or shows an appropriate message.
        """
        query = query.strip()
        if not query:
            self.message_widget.set_text(("g42", "Results appear here."))
            self.menu_list.clear()
            return

        self.message_widget.set_text(("g42", "Fetching..."))
        self.menu_list.clear()
        if self.loop:
            self.loop.draw_screen()

        url = f"https://api.jikan.moe/v4/anime?q={query}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json().get("data", [])
        except Exception as e:
            self.message_widget.set_text(("g42", f"Error: {e}"))
            return

        if not data:
            self.message_widget.set_text(("g42", "No results found."))
            return

        self.message_widget.set_text("")
        for anime in data:
            title = anime.get("title", "Unknown Title")
            button = MenuButton(title)
            urwid.connect_signal(button, "click", self.menu_handler, user_args=[button])
            self.menu_list.append(button)

    def create_menu(self):
        search_edit = CursorAwareEdit(controller=self, caption=" ⌕ ", allow_tab=False)
        search_edit_widget = urwid.Padding(search_edit, align="left", width=("relative", 100))

        search_box = LeftLabelLineBox(
            search_edit_widget,
            label="",
            tlcorner="┌", tline="─", trcorner="┐",
            lline="│", rline="│",
            blcorner="└", bline="─", brcorner="┘"
        )

        self.menu_list = urwid.SimpleFocusListWalker([])
        listbox_widget = FocusReportingListBox(self.menu_list, self)
        scrollbar = urwid.ScrollBar(listbox_widget)
        scrollframe = urwid.AttrMap(scrollbar, "scrollbar")

        self.message_widget.set_text(("g42", "Results appear here."))
        message_map = urwid.AttrMap(self.message_widget, "menu-normal")

        main_list_area = urwid.Columns([
            ("weight", 1, listbox_widget),
            ("fixed", 1, scrollframe),
        ], dividechars=0)

        body_pile = urwid.Pile([
            ("pack", message_map),
            main_list_area
        ])

        self.menu_content = NonTabSearchPile([body_pile])

        menu_box = urwid.LineBox(
            self.menu_content,
            title="",
            title_attr="title-col",
            tlcorner="┌", tline="─", lline="│",
            trcorner="┐", blcorner="└", rline="│",
            bline="─", brcorner="┘"
        )

        # Put them in a MouseAwarePile so we can set focus by clicking
        self.menu_pile = MouseAwarePile([
            ("pack", search_box),
            menu_box
        ])

        return urwid.Padding(self.menu_pile, left=1, right=1)

    def focus_search_box(self):
        if self.menu_pile is not None:
            self.menu_pile.focus_position = 0

    def handle_key(self, key):
        if key in ("q", "Q", "esc"):
            self.exit_program()
        elif key in ("n", "N"):
            self.focus_search_box()

    def show_splash_screen(self, loop, user_data):
        self.loop = loop
        ascii_art = pyfiglet.figlet_format("AnimePaheDL", font="slant")
        splash_text = urwid.Text(ascii_art, align="center")
        splash = urwid.AttrMap(splash_text, "splash-col")
        filler = urwid.Filler(splash, valign="middle")
        loop.widget = filler
        loop.set_alarm_in(2, self.show_menu)

    def show_menu(self, loop, user_data):
        menu = self.create_menu()
        main = urwid.Pile([
            menu,
            ("pack", self.footer)
        ])

        main = urwid.Padding(main, left=1, right=1)

        top = urwid.Overlay(
            main,
            urwid.SolidFill(" "),
            align="center",
            width=("relative", 50),
            valign="middle",
            height=("relative", 50)
        )
        loop.widget = top


def main():
    controller = MenuController()
    palette = [
        ("title-col", "dark red", ""),
        ("center", "default", ""),
        ("bold", "bold", ""),
        ("splash-col", "light cyan", ""),
        ("menu-normal", "default", ""),
        ("menu-focus", "dark magenta", ""),
        ("instructions", "", "", "", "g66", ""),
        ("scrollbar", "light gray", "black"),
        ("g42", "", "", "", "g42", ""),  # Gray text color
    ]

    # With handle_mouse=True, the user can click on the search box to focus it
    loop = urwid.MainLoop(
        urwid.SolidFill(" "),
        palette=palette,
        unhandled_input=controller.handle_key,
        handle_mouse=True
    )
    controller.loop = loop
    loop.set_alarm_in(0, controller.show_splash_screen)
    loop.screen.set_terminal_properties(colors=256)
    loop.run()


if __name__ == "__main__":
    main()
