import os
import sys
import tty
import termios
import traceback
import string
import requests
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

# TODO: make letters bold
# TODO: add mouse support to be able to use the on-screen keyboard

VERSION = "v0.3.3-beta"
GUESSES = 6

guesses_used = 0
words = [[(" ", "none")] * 5] * 6
letter_colors = {}
for l in string.ascii_uppercase + " ":
    letter_colors[l] = "bright_white"
KEYBOARD_LETTERS = [
    "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM",
]

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
        if clr == "none":
            temp.append(f"[black]▂▂▂[/]")
        else:
            temp.append(f"[{clr}]▂▂▂[/]")
    string += " ".join(temp) + "\n"
    temp = []

    for c, clr in zip(chars, colors):
        if clr == "none":
            temp.append(f"[black]▍{c}🮈[/]")
        else:
            temp.append(f"[#000000 on {clr}]⠀{c}⠀[/]")
                # if not small_box else temp.append(f"[{clr}]🮈[/][#000000 on {clr}]{c}[/][{clr}]▍[/]")
    string += " ".join(temp) + "\n"
    temp = []

    for c, clr in zip(chars, colors):
        if clr == "none":
            temp.append(f"[black]🮂🮂🮂[/]")
        else:
            temp.append(f"[{clr}]🮂🮂🮂[/]")
    string += " ".join(temp)

    print(string, justify="center")

def print_keyboard(letter_colors: dict[str, str]) -> None:
    for row_letters in KEYBOARD_LETTERS:
        colors = [letter_colors[c] for c in row_letters]
        formatted_keys = [f"[{clr}]🮈[/][#000000 on {clr}]{c}[/][{clr}]▍[/]" for c, clr in zip(row_letters, colors)]
        print(" ".join(formatted_keys) + "\n", justify="center")

def print_ui(words: list[list[tuple[str, str]]], letter_colors: dict[str, str]) -> None:
    lines = os.get_terminal_size().lines

    _print("\r\033[1000A\033[2J", end="")
    print_panel(f"[bold][green]Wordle CLI[/] [bright_white]{VERSION}[/][/]")

    _print(f"\r\033[1000A\033[{lines // 2 - 11}B", end="")

    for pair in words:
        word = "".join([x[0] for x in pair])
        colors = [x[1] for x in pair]
        print_colored_chars(word, colors)

    print("\n")

    # for row_letters in KEYBOARD_LETTERS:
    #     colors = [letter_colors[c] for c in row_letters]
    #     print_colored_chars(row_letters, colors, small_box=True)
    print_keyboard(letter_colors)

status = 0
is_error_printed = False

try:
    _print("\033[?1049h\r\033[1000A\033[2J", end="")
    print_panel(f"[bold][green]Wordle CLI[/] [bright_white]{VERSION}[/][/]")

    print("\n[bright_yellow]Fetching today's wordle...[/]")

    now = datetime.now()
    r = requests.get(f"https://www.nytimes.com/svc/wordle/v2/{now.year}-{now.month:02}-{now.day:02}.json")
    r.raise_for_status()
    word = r.json()['solution'].upper()

    print("[bright_green]Successfully fetched![/]\n")

    print_ui(words, letter_colors)

    while True:
        if not is_error_printed:
            temp: list[str] = []
        is_error_printed = False

        while True:
            char = getch().upper()

            if char == "\r":
                break
            elif char == "\177":
                if temp:
                    del temp[-1]
                    words[guesses_used] = [(temp[i], "none") if i < len(temp) else (" ", "none") for i in range(5)]
                    print_ui(words, letter_colors)
            elif char == "\x03":
                raise KeyboardInterrupt
            elif len(temp) >= 5 or char not in string.ascii_letters:
                continue
            else:
                temp += char
                words[guesses_used] = [(temp[i], "none") if i < len(temp) else (" ", "none") for i in range(5)]
                print_ui(words, letter_colors)

        user_inp = [x[0] for x in words[guesses_used]]

        if any([x == ' ' for x in user_inp]):
            print("Isn't 5 letters long!")
            is_error_printed = True
            continue

        for i, c in enumerate(user_inp):
            if c == word[i]:
                words[guesses_used][i] = (c, "green")
                letter_colors[c] = "green"

            elif c in word:
                words[guesses_used][i] = (c, "yellow")
                if letter_colors[c] not in ["green"]:
                    letter_colors[c] = "yellow"

            else:
                words[guesses_used][i] = (c, "black")
                if letter_colors[c] not in ["green", "yellow"]:
                    letter_colors[c] = "black"

        print_ui(words, letter_colors)

        if all([x[1] == "green" for x in words[guesses_used]]):
            print("[bright_green]You guessed today's wordle! Congrats![/]")
            break

        guesses_used += 1

        if guesses_used == GUESSES:
            print(f"[bright_red]You failed to guess today's wordle :c[/]\nToday's wordle is: [bold]{word}[/]")
            break

except Exception:
    status = 1
    traceback.print_exc()

finally:
    print("\n[bright_yellow]Press any key to exit.[/]")
    getch()
    _print("\033[?1049l", end="")
    sys.exit(status)
