# Basic Python Calculator — version 1

The first version of my Tkinter calculator: two number pads, one operator at a time. Made by Sasha.

**This is version 1.** Versions 2 and 3 are in this repository's
[Releases](https://github.com/sensocc/Basic-Python-Calculator/releases) as the tags `v2.0` and `v3.0`.

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
| `+` | addition | `12` `+` `5` → 17 |
| `-` | subtraction | `12` `-` `5` → 7 |
| `*` | multiplication | `12` `*` `5` → 60 |
| `/` | division | `12` `/` `5` → 2.4 |
| `^` | power | `2` `^` `10` → 1024 |
| `√` | the second number is the **order of the root** | `8` `√` `3` → 2, `9` `√` `2` → 3 |

### Quirks worth knowing

* The two numbers are **whole numbers**. A leading `0` disappears, because `0` then `1` is read as `1`.
* `/` is the one operator that can give a decimal, because Python's `/` does.
* Both numbers start at `0`, so pressing `+` before typing anything just gives `0`.
* Still, dividing by the untouched `0` crashes: the terminal prints a `ZeroDivisionError` traceback and no
  result appears. `√` with a second number of `0` does the same, because a 0th root divides by zero.
* The window uses Tk's default look — no colours, no font settings. Version 2 fixed that.

### How it is built

* 26 click handlers, one per button: `on_num1button1_click`, `on_num2button1_click`, … `on_multiplybutton_click`.
* `num_one`, `num_two` and `result` are global whole numbers. A digit is appended by turning the number into
  text and back again: `num_one = int(str(num_one) + "3")`.
* One `display` label is rewritten by `update_display()` after every click.
