# Basic Python Calculator — version 2

The same calculator as version 1, tidied up and dressed in black and green. Made by Sasha.

**This is version 2.** Versions 1 and 3 are in this repository's
[Releases](https://github.com/sensocc/Basic-Python-Calculator/releases) as the tags `v1.0` and `v3.0`.

## Requirements

* Python 3
* Tkinter **and** the Tcl/Tk libraries it loads. Python often ships `tkinter` without them, and then the
  program stops with `ImportError: libtk8.6.so: cannot open shared object file`.

| System | Command |
|--------|---------|
| Omarchy / Arch | `omarchy pkg add tk` (or `sudo pacman -S tk`) |
| Debian / Ubuntu | `sudo apt install python3-tk` |
| Fedora | `sudo dnf install python3-tkinter` |
| macOS / Windows | Reinstall Python from [python.org](https://www.python.org/downloads/) — Tk is included |

## Running it

```bash
python3 Calculator.py
```

## How to use it

```
        the display line, e.g.   Your current first number: 12 | Your current second number: 5 | Your short result: 17
  ┌─────────────┐   ┌─────────────┐
  │ 1  2  3     │   │ 1  2  3     │
  │ 4  5  6     │   │ 4  5  6     │
  │ 7  8  9     │   │ 7  8  9     │
  │    0        │   │    0        │
  └─────────────┘   └─────────────┘
     left pad           right pad
  ┌────┬────┬────┬────┬────┬────┐
  │ +  │ -  │ /  │ *  │ ^  │ √  │   and  About   Reset   =
  └────┴────┴────┴────┴────┴────┘
```

1. The **left pad** types the first number, the **right pad** types the second one. There are only the
   digits 0-9, so there is no decimal point and no minus sign.
2. An **operator** button calculates immediately and puts the answer in the "short result" part of the
   display line.
3. `=` opens a small window with the result, `About` opens a credits window, `Reset` sets both numbers and
   the result back to 0.

### Operators

| Button | Meaning | Example |
|--------|---------|---------|
| `+` | addition | `12` `+` `5` → 17.0 |
| `-` | subtraction | `12` `-` `5` → 7.0 |
| `*` | multiplication | `12` `*` `5` → 60.0 |
| `/` | division | `12` `/` `5` → 2.4 |
| `^` | power | `2` `^` `10` → 1024.0 |
| `√` | the second number is the **order of the root** | `8` `√` `3` → 2, `9` `√` `2` → 3 |

### Quirks worth knowing

* Still two pads and still no decimal point button.
* The numbers are text now, so a leading `0` is kept: pressing `0` then `1` shows `01` and calculates
  with `1`.
* Because every calculation goes through `float()`, whole answers are printed with a `.0`: `12 + 5` shows
  `17.0`.
* Results are printed exactly as Python prints them, so `10 / 3` shows `3.3333333333333335`.
* Wrong input is a traceback in the terminal, not a message in the window:
  * pressing an operator or `=` before typing a number raises `ValueError: could not convert string to float: ''`
  * dividing by zero raises `ZeroDivisionError`, and so does a `√` with a second number of `0`
  * a large power such as `999 ^ 999` raises `OverflowError: (34, 'Numerical result out of range')`

  The window keeps working after the traceback, but it is not a nice way to be told you cannot divide by
  zero. Version 3 fixed all of this.

### What changed from version 1

* The numbers are kept as **text** (`num_one = ''`) instead of whole numbers, so a digit is just appended
  to the string.
* One function per **kind** of button instead of one per button: `num_1_update(digit)`,
  `num_2_update(digit)` and `op_button_click(operator)`, wired to the buttons with `lambda`. That turned 26
  handlers into 3 and made room for the next batch of buttons.
* All the maths moved into `op_button_click`, where both numbers are turned into `float`s first — that is
  where the `.0` on whole answers comes from.
* The look: a black window with `SpringGreen2` text in Arial 18 (`bg='black'`, `fg='SpringGreen2'`) for the
  main window, the About window and the result window. About now says `VER 2.0! Made by Sasha!`.
