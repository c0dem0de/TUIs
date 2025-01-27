import urwid as u

def exit_on_q(key):
    if key in ['q', 'Q']:
        raise u.ExitMainLoop()

palette = [
    ("txt-styles", 'white, bold', 'dark magenta', '', '#fff, underline, bold', '#f60'),
    ("txt-bg", '', '', '', '', "#ff0"),
    ("bg", '', '', '', '', "#f00"),
]


# placeholder = urwid.SolidFill()
# loop = urwid.MainLoop(widget=placeholder, palette=palette, handle_mouse=False, unhandled_input=exit_on_q)
# loop.screen.set_terminal_properties(colors=256)
# loop.widget = urwid.AttrMap(placeholder, "")

# # replaced the widget wrapped by the AttrMap with a pile widget
# loop.widget.original_widget = urwid.Filler(urwid.Pile([]))

# # Get access to the current widget ie pile
# pile = loop.widget.base_widget

# txt = urwid.Text(("banner", " Hello World! "), align="center")
# streak = urwid.AttrMap(txt, "bg2")
# pile.contents.append((streak, pile.options()))
# loop.run()


txt = u.Text(('txt-styles', " Hello World! "), 'center')
fill = u.Filler(txt)
# red_on_gray = u.AttrSpec('#fff', '#f00')
atr = u.AttrMap(fill, 'bg')
loop = u.MainLoop(atr, palette=palette, unhandled_input=exit_on_q)
loop.screen.set_terminal_properties(colors=16, bright_is_bold=True)
loop.run()