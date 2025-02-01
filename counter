import pyfiglet as pf
import time as t
from urwid import Text, Filler, MainLoop, ExitMainLoop

palette = [
    ("red", '', '', '', '#d00', ''),
    ("blue", '', '', '', '#0ad', ''),
    ("white", '', '', '', '#fff', ''),
]

font = 'big'

def Exit(key):
    global num, bg
    if (key in ['q', 'Q', 'esc']):
        raise ExitMainLoop()
    elif (key in '+'):
        num += 1
        ascii_rt = pf.figlet_format(f"{num}", font=font)
        if (num >= 0):
            txt.set_text(('blue', f"{ascii_rt}"))
        else:
            txt.set_text(('red', f"{ascii_rt}"))
    elif (key in '-'):
        num -= 1
        ascii_rt = pf.figlet_format(f"{num}", font=font)
        if (num >= 0):
            txt.set_text(('blue', f"{ascii_rt}"))
        else:
            txt.set_text(('red', f"{ascii_rt}"))

num = 0
ascii_rt = pf.figlet_format(f"{num}", font=font)
txt = Text(('white',  f"{ascii_rt}"), 'center')
fill = Filler(txt)

loop = MainLoop(fill, palette, unhandled_input=Exit)
loop.screen.set_terminal_properties(256)
loop.run()
