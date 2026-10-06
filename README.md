# Basic Python Calculator — version 6

[![Tests](https://github.com/sensocc/Basic-Python-Calculator/actions/workflows/tests.yml/badge.svg)](https://github.com/sensocc/Basic-Python-Calculator/actions/workflows/tests.yml)

A small desktop calculator written in Python with [Tkinter](https://docs.python.org/3/library/tkinter.html).
Type the first number, pick an operator, type the second number, press `=` — the answer appears in the main
window and in a small popup. The numbers can be decimals, and the `±` button makes them negative. There are
also one-number buttons: `eˣ`, `ln`, `log` and `%`. Made by Sasha.

**This is version 6**, the newest one, tagged `v6.0`: the `log` and `%` buttons that
[issue #4][issue] asked for, on top of the tests and the workflow that keep the calculator working.

[issue]: https://github.com/sensocc/Basic-Python-Calculator/issues/4

## The six versions

This repository keeps every version of the calculator as a version of **one file** — `Calculator.py`, each
with its own `README.md` — instead of several files sitting side by side:

| Tag | What it is | How to get it |
|-----|------------|---------------|
| `v1.0` | The original. Two digit pads, one per number, 26 near-identical click handlers, whole-number state, Tk's default look. | `git checkout v1.0`, or the [Releases](https://github.com/sensocc/Basic-Python-Calculator/releases) page |
| `v2.0` | The tidy-up. Numbers kept as text, a handler per *kind* of button, black/`SpringGreen2` styling. | `git checkout v2.0` |
| `v3.0` | One keypad instead of two, guarded maths with messages instead of tracebacks, and a clear hint when the Tk libraries are missing. | `git checkout v3.0` |
| `v4.0` | Adds `eˣ` and `ln`, the two one-number buttons from issue #1. | `git checkout v4.0` |
| `v5.0` | Type decimals and negatives: a `.` and a `±` beside the digits. | `git checkout v5.0` |
| `v6.0` | **This version.** Adds `log` (base 10) and `%` (divide by 100). | `git checkout v6.0` |

Every tag is also a GitHub Release, so any version can be downloaded as a zip without using git.

## Requirements

* Python 3 (developed against Python 3.14, tested on 3.9 as well)
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
  │ 0  │ .  │ ±  │ +  │
  ├────┼────┼────┼────┤
  │ √  │ ^  │ ln │ eˣ │
  ├────┴────┼────┴────┤
  │   log   │    %    │
  ├────┬────┴────┬────┤
  │Reset│   =    │About│
  └─────┴────────┴─────┘
```

1. Press the digits of the first number. Decimals and negatives are typed the same way: `.` starts `0.` and
   `±` flips the sign, so `12` `.` `5` `±` is `-12.5`.
2. Press an operator — the small line above shows what is waiting, e.g. `12 +`.
3. Press the digits of the second number.
4. Press `=` to see the answer. `Reset` starts a new calculation, `About` says hello.

Pressing a second operator finishes the first calculation, so `2 + 3 + 4 =` gives `9` (the small line names
the step it just did: `5 + 4 = 9`).
After `=`, typing a digit (or `.`) starts a fresh number, while pressing an operator keeps using the answer.

The one-number buttons `eˣ`, `ln`, `log` and `%` are used the other way round: type the number, then press
the button (`√` is not one of them — it takes the order of the root as its second number: `8 √ 3 =` is `2`).
Pressing one while an answer is already on show works on that answer, and pressing one while a calculation is
waiting finishes it — `2 + 3 ln` is `2 + ln(3)`.

`±` is the exception to "number first": it acts on whatever is on show, so `3 - 5 =` then `±` shows `2`.

### Operators, functions and typing

| Button | Meaning | Example |
|--------|---------|---------|
| `+` | addition | `12.5 + 0.5 =` → `13` |
| `-` | subtraction | `12 - 5 =` → `7` |
| `*` | multiplication | `12 * 5 =` → `60` |
| `/` | division | `12 / 5 =` → `2.4` |
| `^` | power | `2 ^ 10 =` → `1024` |
| `√` | the second number is the **order of the root**, kept from version 1 | `8 √ 3 =` → `2`, `9 √ 2 =` → `3` |
| `eˣ` | natural exponent: e (about 2.71828) to the power of the number | `2 eˣ` → `7.38905609893` |
| `ln` | natural logarithm: the power you raise e to, to get the number | `10 ln` → `2.30258509299` |
| `log` | common logarithm, base 10 | `100 log` → `2`, `0.1 log` → `-1` |
| `%` | percent: the number divided by 100 | `50 %` → `0.5`, `200 %` → `2` |
| `.` | decimal point — one per number | `1 . 5` → `1.5`, `.` on its own → `0.` |
| `±` | flips the sign of the number on show | `5 ±` → `-5`, `3 - 5 = ±` → `2` |

`eˣ` and `ln` undo each other, so `5 eˣ ln` gives `5` back.

### Messages instead of crashes

Bad input gets a sentence in the status line rather than a red traceback in the terminal:

| You pressed | It says |
|-------------|---------|
| `5 / 0 =` | You cannot divide by zero. |
| `3 - 5 =` then `√ 2 =` | I cannot take a root of a negative number. |
| `8 √ 0 =` | A root cannot have the order zero. |
| `9 ^ 9 =`, then `^ 9 =` twice | That power is too big to work out. |
| `0 ln`, `0 log`, or `4 ±` then `ln` | I can only take the logarithm of a number above zero. |
| `999 eˣ` | That exponent is too big to work out. |
| `=` before entering an operator | Type it like this:  12 + 5 = |
| an operator, a function or `±` before entering a number | Type a number first. |

`calculate()` and `apply_function()` also refuse a negative base with a fractional exponent and anything that
comes out infinite or too large for a float; those are hard to reach by clicking, so they are covered by
tests rather than by a button sequence.

## What changed in version 6

* **`log` — the common logarithm.** `100 log` gives `2` and `0.1 log` gives `-1`. It refuses zero and
  negative numbers with exactly the sentence `ln` uses, because it is the same rule: that rule now lives in
  one `logarithm()` helper instead of being written out twice.
* **`%` — percent.** `50 %` gives `0.5`, `200 %` gives `2`, in other words the number divided by 100. It has
  nothing to refuse at all, which is pinned down by a test.
* **They have their own row.** `log` and `%` sit above `Reset`, spanning two columns each, so the keypad is
  seven rows of buttons and the window is one row taller than version 5.
* **In the code:** `apply_function()` gained the two cases, `write_function()` now names every function
  explicitly (`log(100)`, `50%`) and complains if it meets one it does not know, and `press_function()` works
  out the label only once the answer is known — so a function that is refused never gets a label.
* **In the tests:** 10 new ones — the maths for both, the two buttons, `log` of a decimal and of a negative
  number, percent of an answer, a logarithm finishing a waiting calculation, and the issue's own example
  (`100 log + 1 =` → `3`).

### Earlier versions

* **Version 5** — a decimal point and a `±` sign, so numbers no longer have to be whole and positive, plus
  `format_number()` learning that `-0.0` is `0`.
* **Version 4** — `eˣ` and `ln`, so the calculator could do more than arithmetic, plus the `FUNCTIONS` table
  and `apply_function()` they are built on.
* **Version 3** — one keypad instead of two pads, a handler per *kind* of button instead of per button, no
  `global` lines, guarded maths with readable messages, tidier numbers (`.12g`), one reused result popup, and
  a helpful message when the Tk libraries are missing.
* **Version 2** — numbers kept as text, three handlers instead of 26, and the black/`SpringGreen2` look.
* **Version 1** — the original: two digit pads, whole numbers, Tk's default look, no error handling.

## Tests

Two test files, both plain [`unittest`](https://docs.python.org/3/library/unittest.html) — no packages to
install:

| File | What it checks | Needs |
|------|----------------|-------|
| `test_calculator.py` | the maths, every operator, the one-number functions, typing decimals and signs, all the error messages, chaining, the reused result popup, the About window, and the helpful message when Tk is missing. The keypad is driven through a stand-in for `tkinter`, so no window is needed. | nothing but Python |
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

* `%` is simply the number divided by 100. It does not mean "this much of the number before", so
  `200 + 10 % =` gives `200.1`, not `220`.
* One decimal point per number, and no scientific notation to type — `1e-5` cannot be entered.
* `±` flips the whole number; there is no way to negate just part of an expression.
* `±` needs a number on show: pressing it while an operator is waiting for its second number says
  `Type a number first.`
* The result popup belongs to `=`; the one-number buttons answer in the big display and the status line.
* Numbers are shown rounded to 12 significant digits, so very long results are shortened; very large or very
  small ones come out in scientific notation, e.g. `1e+20`.
* No history and no keyboard shortcuts yet — those are the next ideas, in
  [#8](https://github.com/sensocc/Basic-Python-Calculator/issues/8) and
  [#7](https://github.com/sensocc/Basic-Python-Calculator/issues/7), along with
  [#5](https://github.com/sensocc/Basic-Python-Calculator/issues/5) trig with a degrees/radians switch,
  [#6](https://github.com/sensocc/Basic-Python-Calculator/issues/6) π and e, and
  [#9](https://github.com/sensocc/Basic-Python-Calculator/issues/9) the interface overhaul.
