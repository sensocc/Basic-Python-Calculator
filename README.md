# Basic Python Calculator — version 4

[![Tests](https://github.com/sensocc/Basic-Python-Calculator/actions/workflows/tests.yml/badge.svg)](https://github.com/sensocc/Basic-Python-Calculator/actions/workflows/tests.yml)

A small desktop calculator written in Python with [Tkinter](https://docs.python.org/3/library/tkinter.html).
Type the first number, pick an operator, type the second number, press `=` — the answer appears in the main
window and in a small popup. There are also two one-number buttons: `eˣ` (natural exponent) and `ln`
(natural logarithm). Made by Sasha.

**This is version 4**, the newest one: the `main` branch is this code, tagged `v4.0`, plus the tests and the
workflow that keep it working. The two new buttons are what [issue #1][issue] asked for.

[issue]: https://github.com/sensocc/Basic-Python-Calculator/issues/1

## The four versions

This repository keeps every version of the calculator as a version of **one file** — `Calculator.py`, each
with its own `README.md` — instead of several files sitting side by side:

| Tag | What it is | How to get it |
|-----|------------|---------------|
| `v1.0` | The original. Two digit pads, one per number, 26 near-identical click handlers, whole-number state, Tk's default look. | `git checkout v1.0`, or the [Releases](https://github.com/sensocc/Basic-Python-Calculator/releases) page |
| `v2.0` | The tidy-up. Numbers kept as text, a handler per *kind* of button, black/`SpringGreen2` styling. | `git checkout v2.0` |
| `v3.0` | One keypad instead of two, guarded maths with messages instead of tracebacks, and a clear hint when the Tk libraries are missing. | `git checkout v3.0` |
| `v4.0` | **This version.** Adds the `eˣ` and `ln` buttons from issue #1, with tests for both. | `git checkout v4.0` |

Every tag is also a GitHub Release, so any version can be downloaded as a zip without using git.

## Requirements

* Python 3 (developed against Python 3.14)
* Tkinter **and** the Tcl/Tk libraries it loads. Python often ships `tkinter` without them, and then the
  program stops with `ImportError: libtk8.6.so: cannot open shared object file`.

Install Tk first:

| System | Command |
|--------|---------|
| Omarchy / Arch | `omarchy pkg add tk` (or `sudo pacman -S tk`) |
| Debian / Ubuntu | `sudo apt install python3-tk` |
| Fedora | `sudo dnf install python3-tkinter` |
| macOS / Windows | Reinstall Python from [python.org](https://www.python.org/downloads/) — Tk is included |

Check it worked:

```bash
python3 -c "import tkinter; print('Tk', tkinter.TkVersion)"
```

## Running it

```bash
python3 Calculator.py
```

If Tk is missing you get a short explanation and the install command instead of a traceback:

```
$ python3 Calculator.py
This calculator needs Python's tkinter toolkit, and Tk is not installed.
...
  Omarchy / Arch    omarchy pkg add tk
```

## How to use it

```
                      12 +
                     ______
                          5     <- the big number is what you are typing
  ┌────┬────┬────┬────┐
  │ 7  │ 8  │ 9  │ /  │
  ├────┼────┼────┼────┤
  │ 4  │ 5  │ 6  │ *  │
  ├────┼────┼────┼────┤
  │ 1  │ 2  │ 3  │ -  │
  ├────┼────┼────┼────┤
  │ 0  │ √  │ ^  │ +  │
  ├────┴────┼────┴────┤
  │   eˣ    │   ln    │   <- the two buttons from issue #1
  ├────┬────┴────┬────┤
  │Reset│   =    │About│
  └─────┴────────┴─────┘
```

1. Press the digits of the first number.
2. Press an operator — the small line above shows what is waiting, e.g. `12 +`.
3. Press the digits of the second number.
4. Press `=` to see the answer. `Reset` starts a new calculation, `About` says hello.

Pressing a second operator finishes the first calculation, so `2 + 3 + 4 =` gives `9` (the small line names
the step it just did: `5 + 4 = 9`).
After `=`, typing a digit starts a fresh number, while pressing an operator keeps using the answer.

`eˣ` and `ln` take **one** number, so they are used the other way round: type the number, then press the
button. Pressing one while an answer is already on show works on that answer, and pressing one while a
calculation is waiting finishes it — `2 + 3 ln` is `2 + ln(3)`.

### Operators and functions

| Button | Meaning | Example |
|--------|---------|---------|
| `+` | addition | `12 + 5 =` → `17` |
| `-` | subtraction | `12 - 5 =` → `7` |
| `*` | multiplication | `12 * 5 =` → `60` |
| `/` | division | `12 / 5 =` → `2.4` |
| `^` | power | `2 ^ 10 =` → `1024` |
| `√` | the second number is the **order of the root**, kept from version 1 | `8 √ 3 =` → `2`, `9 √ 2 =` → `3` |
| `eˣ` | natural exponent: e (about 2.71828) to the power of the number | `2` `eˣ` → `7.38905609893` |
| `ln` | natural logarithm: the power you raise e to, to get the number | `10` `ln` → `2.30258509299` |

`eˣ` and `ln` undo each other, so `5 eˣ ln` gives `5` back.

### Messages instead of crashes

Bad input gets a sentence in the status line rather than a red traceback in the terminal:

| You pressed | It says |
|-------------|---------|
| `5 / 0 =` | You cannot divide by zero. |
| `3 - 5 =` then `√ 2 =` | I cannot take a root of a negative number. |
| `8 √ 0 =` | A root cannot have the order zero. |
| `9 ^ 9 =`, then `^ 9 =` twice | That power is too big to work out. |
| `0 ln`, or `3 - 5 =` then `ln` | I can only take the logarithm of a number above zero. |
| `999 eˣ` | That exponent is too big to work out. |
| `=` before entering an operator | Type it like this:  12 + 5 = |
| an operator or function before entering a number | Type a number first. |

`calculate()` and `apply_function()` also refuse a negative base with a fractional exponent and anything that
comes out infinite or too large for a float; those are hard to reach by clicking, so they are covered by
tests rather than by a button sequence.

## What changed in version 4

* **The two buttons from issue #1.** `eˣ` (natural exponent) and `ln` (natural logarithm) sit next to each
  other on their own row, above `Reset`.
* **They take one number.** Type the number, press the button, and the answer is there: `2` `eˣ` shows
  `7.38905609893`, `10` `ln` shows `2.30258509299`. Pressing one while an answer is on show works on that
  answer, so `9 √ 2 =` then `ln` gives `1.09861228867`.
* **They fit the flow.** If a calculation is waiting, the function is worked out first and the calculation is
  finished with it: `2 + 3 ln` shows `2 + ln(3) = 3.09861228867`. Typing a digit afterwards starts a new
  number, exactly as after `=`.
* **Guarded like everything else.** `ln` of zero or of a negative number, and an exponent too big for Python
  to work out, get a sentence in the status line instead of a traceback.
* **In the code:** one new table (`FUNCTIONS`), one new maths function (`apply_function()`), one new button
  handler (`press_function()`), and a small `refuse()` helper that the old calculation path and the new
  function path share. `calculate()` itself is untouched.
* **In the tests:** both functions are covered end to end, and `setUp` now resets the *calculator* as well as
  the window — before this, one test could carry a half-finished calculation into the next one.

## What changed in version 3

* **One keypad.** Version 2 had two identical sets of digit buttons (one for each operand). Now there is a
  single conventional grid and the program tracks which number you are typing.
* **A handler per kind of button, not per button.** Version 1 had 26 hand-written click handlers; version 2
  merged the digits into `num_1_update` / `num_2_update`; version 3 uses `press_digit(digit)` and
  `press_operator(operator)`, driven by the `KEYPAD` table in `build_window()`.
* **No `global` lines.** The state lives in one `SimpleNamespace` called `state`, and the handlers reach the
  labels through it.
* **Guarded maths.** `calculate()` raises `ValueError` with a readable message for division by zero, an
  impossible root, a negative base with a fractional exponent, infinity and overflow.
* **Tidier numbers.** Results are formatted with `.12g`, so `1 / 3` shows as `0.333333333333` and
  `0.1 + 0.2` shows as `0.3` instead of `0.30000000000000004`.
* **One result popup.** Pressing `=` reuses the popup window instead of piling up a new one every time.
* **Helpful startup.** A missing Tk install is explained instead of raising `ImportError`, and the module
  can be imported without Tk, which keeps the maths testable.

## Tests

Two test files, both plain [`unittest`](https://docs.python.org/3/library/unittest.html) — no packages to
install:

| File | What it checks | Needs |
|------|----------------|-------|
| `test_calculator.py` | the maths, every operator, both one-number functions, all the error messages, chaining, the reused result popup, the About window, and the helpful message when Tk is missing. The keypad is driven through a stand-in for `tkinter`, so no window is needed. | nothing but Python |
| `test_gui_smoke.py` | the same buttons on a **real** Tk window — real widgets, real clicks, no errors inside Tk — and then starts `Calculator.py` to see that its window stays open. | tkinter, the Tcl/Tk libraries and a display; it skips itself when one of those is missing |

Run them:

```bash
python3 -m unittest discover -v
```

Every push and pull request runs them in
[GitHub Actions](https://github.com/sensocc/Basic-Python-Calculator/actions/workflows/tests.yml):

* **Tests — Python 3.9 / 3.13**: the whole suite on two Python versions with no display, so the window tests
  skip themselves.
* **Tests — with a real window**: the same suite under `xvfb-run`, which hands Tk a real display, so
  `test_gui_smoke.py` runs for real.

## Known limits

* No decimal point button (the original had none either) and no way to type a negative number directly —
  but `3 - 5` gives `-2` and you can carry on calculating from it.
* `eˣ` and `ln` are used as *number, then button*. There is no `ln` `10` `=` order, and no `e` or `ln`
  buttons for the second number of a calculation.
* The result popup belongs to `=`; `eˣ` and `ln` answer in the big display and the status line.
* Numbers are shown rounded to 12 significant digits, so very long results are shortened.
* Very large or very small results are printed in scientific notation, e.g. `1e+20`.
* No history, no keyboard shortcuts — only the buttons.
