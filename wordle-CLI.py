import os
import sys
import tty
import termios
import traceback
from rich.console import Console
from rich.panel import Panel

VERSION = "v0.0.0-alpha"

_print = print
con = Console(highlight=False)
print = con.print

def getch(s: str = "", show_input: bool = False) -> str:
    if s:
        print(s, end="")
    if os.name == "nt":
        ch = msvcrt.getch().decode("utf-8")
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if show_input:
        _print(ch)
    return ch

def print_panel(text, border_style = "bold cyan", expand: bool = True) -> None:
    panel = Panel(
        text,
        border_style=border_style,
        width=os.get_terminal_size().columns if expand else None,
    )
    print(panel, justify="center")

def print_colored_chars(chars: str, colors: list[str]) -> None:
    string = ""
    temp = []

    for c, clr in zip(chars, colors):
        temp.append(f"[{clr}]▄▄▄[/]")
    string += " ".join(temp) + "\n"
    temp = []

    for c, clr in zip(chars, colors):
        temp.append(f"[#000000 on {clr}]⠀{c}⠀[/]")
    string += " ".join(temp) + "\n"
    temp = []

    for c, clr in zip(chars, colors):
        temp.append(f"[{clr}]▀▀▀[/]")
    string += " ".join(temp)

    print(string, justify="center")

try:
    _print("\033[?1047h\033[?25l\r\033[1000A", end="")
    print_panel(f"[bold][green]Wordle CLI[/] [bright_white]{VERSION}[/][/]")
    input()

except Exception:
    _print("\033[?1047l\033[?25h", end="")
    traceback.print_exc()
    exit(1)

else:
    _print("\033[?1047l\033[?25h", end="")
    exit(0)
