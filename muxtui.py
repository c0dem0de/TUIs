import urwid

import urwid.escape as esc

import time

import pyfiglet



# Preserve original escape codes for showing and hiding the cursor

SHOW_CURSOR_ORIGINAL = esc.SHOW_CURSOR

HIDE_CURSOR_ORIGINAL = esc.HIDE_CURSOR



class LeftLabelLineBox(urwid.WidgetWrap):

    """

    A custom widget similar to urwid.LineBox(). It draws a box around the given

    widget but places a label on the left edge of the top border, right after

    the top-left corner. The rest of the border is drawn across the top.

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





class MenuButton(urwid.Button):

    """

    Custom button class for menu items, left-aligned with an arrow when focused,

    and hides the cursor in the menu area.

    """

    def __init__(self, caption, on_press=None, user_data=None):

        super().__init__("", on_press=on_press, user_data=user_data)

        self._caption = caption

        self._prefix_unfocused = "   "

        self._prefix_focused = "-> "

        # Create a label widget with cursor initially hidden

        label_text = self._prefix_unfocused + caption

        self._label = urwid.SelectableIcon(label_text, cursor_position=-1)

        # Wrap it in an AttrMap for possible interactive styling

        self._w = urwid.AttrMap(

            urwid.Padding(self._label, align='left', width=('relative', 100)),

            None, None

        )



    def get_caption(self):

        return self._caption



    def render(self, size, focus=False):

        """

        Update the displayed text based on focus state while keeping cursor hidden

        """

        prefix = self._prefix_focused if focus else self._prefix_unfocused

        self._label.set_text(prefix + self._caption)

        self._label.cursor_position = -1

        return super().render(size, focus)





class NonTabSearchPile(urwid.Pile):

    """

    A custom Pile that forbids normal arrow or tab navigation into the search box

    and toggles the cursor display depending on focus.

    """

    def render(self, size, focus=False):

        # Reset SHOW_CURSOR to the correct ANSI escape sequence, not a Boolean

        if self.focus_position == 0:

            esc.SHOW_CURSOR = SHOW_CURSOR_ORIGINAL

        else:

            esc.SHOW_CURSOR = HIDE_CURSOR_ORIGINAL

        return super().render(size, focus)



    def keypress(self, size, key):

        if self.focus_position != 0:

            if key in ('shift tab', 'page up'):

                return None

        elif self.focus_position == 1 and key == 'up':

            return None

        return super().keypress(size, key)





class MenuController:

    def __init__(self):

        self.menu_items = [

            'Apples', 'Bananas', 'Avocado', 'Grapes', 'Oranges',

            'Pineapple', 'Mango', 'Strawberries', 'Blueberries', 'Peaches',

            'Cherries', 'Watermelon', 'Lemon', 'Lime', 'Kiwi',

            'Papaya', 'Passion Fruit', 'Dragon Fruit', 'Pomegranate', 'Coconut'

        ]

        self.footer = urwid.Text("", align='center')

        self.menu_list = None

        self.menu_content = None

        self.MAX_OPTION_LENGTH = max(len(item) for item in self.menu_items + ['Exit'])



    def menu_handler(self, button, choice):

        # Grab the selected menu item's label for the footer

        selected_text = choice.get_caption()

        self.footer.set_text(('center', f"You chose: {selected_text}"))



    def exit_program(self, button):

        raise urwid.ExitMainLoop()



    def handle_search_input(self, edit, text):

        """

        Rebuilds the entire list based on the search text

        to ensure proper rendering (including arrow indicators).

        """

        # Clear everything from the listwalker

        self.menu_list.clear()



        # Add matching buttons

        for item in self.menu_items:

            if text.strip().lower() in item.lower():

                button = MenuButton(item)

                urwid.connect_signal(button, 'click', self.menu_handler, user_args=[button])

                self.menu_list.append(button)



        # Always include an Exit option at the end

        exit_button = MenuButton('Exit')

        urwid.connect_signal(exit_button, 'click', self.exit_program)

        self.menu_list.append(exit_button)



        # Optionally reset focus to the top item so navigation remains consistent

        if len(self.menu_list) > 0:

            self.menu_list.set_focus(0)



    def create_menu(self):

        # Create the search box (with cursor visible)

        search_edit = urwid.Edit("", allow_tab=False)

        search_edit_widget = urwid.Padding(search_edit, align='left', width=('relative', 100))

        urwid.connect_signal(search_edit, 'change', self.handle_search_input)



        # Decorate search box

        search_box = LeftLabelLineBox(

            search_edit_widget,

            label="Search:",

            tlcorner='┌', tline='─', trcorner='┐',

            lline='│', rline='│',

            blcorner='└', bline='─', brcorner='┘'

        )



        # Create default menu items

        body = []

        for item in self.menu_items:

            button = MenuButton(item)

            urwid.connect_signal(button, 'click', self.menu_handler, user_args=[button])

            body.append(button)



        exit_button = MenuButton('Exit')

        urwid.connect_signal(exit_button, 'click', self.exit_program)

        body.append(exit_button)



        self.menu_list = urwid.SimpleFocusListWalker(body)

        listbox = urwid.ListBox(self.menu_list)

        scrollbar = urwid.AttrMap(urwid.ScrollBar(listbox), None)



        # Compose the NonTabSearchPile

        self.menu_content = NonTabSearchPile([

            ('pack', search_box),

            ('pack', urwid.Divider()),

            scrollbar,

            ('pack', urwid.Divider())

        ])



        menu_box = urwid.LineBox(

            self.menu_content,

            title="Fruits",

            title_attr='title-col',

            tlcorner='┏', tline='━', lline='┃',

            trcorner='┓', blcorner='┗', rline='┃',

            bline='━', brcorner='┛'

        )



        menu = urwid.Padding(menu_box, left=2, right=2)

        return urwid.Filler(menu, height=('relative', 100))



    def focus_search_box(self):

        self.menu_content.focus_position = 0



    def handle_key(self, key):

        if key in ('q', 'Q', 'esc'):

            raise urwid.ExitMainLoop()

        elif key in ('n', 'N'):

            self.focus_search_box()



    def show_splash_screen(self, loop, user_data):

        # Generate ASCII art using pyfiglet

        ascii_art = pyfiglet.figlet_format("Fruit Buy", font="slant")

        # Wrap the ASCII art in an AttrMap to color it red

        splash_text = urwid.Text(ascii_art, align='center')

        splash = urwid.AttrMap(splash_text, 'splash-col')

        filler = urwid.Filler(splash, valign='middle')

        loop.widget = filler

        # Set a timer to transition to the menu after 2 seconds

        loop.set_alarm_in(2, self.show_menu)



    def show_menu(self, loop, user_data):

        menu = self.create_menu()

        main = urwid.Pile([

            menu,

            ('pack', self.footer)

        ])

        main = urwid.Padding(main, left=4, right=4)



        top = urwid.Overlay(

            main,

            urwid.SolidFill(' '),

            align='center',

            width=('relative', 80),

            valign='middle',

            height=('relative', 80)

        )

        loop.widget = top





if __name__ == "__main__":

    controller = MenuController()

    loop = urwid.MainLoop(

        urwid.SolidFill(' '),

        palette=[

            ("title-col", "dark red", ""),

            ('center', 'default', ''),

            ('bold', 'bold', ''),

            # New style below for coloring the splash text

            ('splash-col', 'light cyan', '')

        ],

        unhandled_input=controller.handle_key

    )

    # Start with the splash screen

    loop.set_alarm_in(0, controller.show_splash_screen)

    loop.run()
