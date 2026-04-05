import os
import sys
import tty
import termios
import traceback
import re
import requests
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

VERSION = "v0.1.0-alpha"
guesses = 6

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

status = 0

try:
    _print("\033[?1049h\r\033[1000A", end="")
    print_panel(f"[bold][green]Wordle CLI[/] [bright_white]{VERSION}[/][/]")

    print("\n[bright_yellow]Fetching today's wordle...[/]")

    now = datetime.now()
    r = requests.get(f"https://www.nytimes.com/svc/wordle/v2/{now.year}-{now.month:02}-{now.day:02}.json")
    r.raise_for_status()
    word = r.json()['solution'].upper()

    print("[bright_green]Successfully fetched![/]\n")

    while True:
        user_inp = input(f"({guesses})> ").upper()

        if len(user_inp) != 5:
            print("Isn't 5 letters long!")
            continue

        if not bool(re.fullmatch("[A-Z]+", user_inp)):
            print("Must contain only letters!")
            continue

        colors = []
        for i, c in enumerate(user_inp):
            if c == word[i]:
                colors.append("green")
            elif c in word:
                colors.append("yellow")
            else:
                colors.append("black")

        print_colored_chars(user_inp, colors)

        if all([x == "green" for x in colors]):
            print("[bright_green]You guessed today's wordle! Congrats![/]")
            break

        guesses -= 1

        if guesses == 0:
            print(f"[bright_red]You failed to guess today's wordle :c[/]\nToday's wordle is: [bold]{word}[/]")
            break

except Exception:
    status = 1
    traceback.print_exc()

finally:
    input("\nPress Enter to exit.\n")
    _print("\033[?1049l", end="")
    sys.exit(status)
