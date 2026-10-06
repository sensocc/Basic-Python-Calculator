# Basic Python Calculator — version 11

[![Tests](https://github.com/sensocc/Basic-Python-Calculator/actions/workflows/tests.yml/badge.svg)](https://github.com/sensocc/Basic-Python-Calculator/actions/workflows/tests.yml)

A small desktop calculator written in Python with [Tkinter](https://docs.python.org/3/library/tkinter.html).
Type the first number, pick an operator, type the second number, press `=` — the answer appears in the main
window and in a small popup. The numbers can be decimals, and the `±` button makes them negative. There are
one-number buttons for `eˣ`, `ln`, `log`, `%`, and for the trigonometry `sin`, `cos`, `tg` and `ctg` — those
four with a `DEG` / `RAD` switch — plus the two constants `π` and `e`. Everything can be done from the
keyboard, every finished calculation is kept in a history you can pick answers back out of, and the whole
thing comes in five colour themes. Made by Sasha.

**This is version 11**, the newest one, tagged `v11.0`: the interface overhaul that [issue #9][issue] asked
for. That was the last idea on the list — every issue in this repository is now built.

[issue]: https://github.com/sensocc/Basic-Python-Calculator/issues/9

## The eleven versions

This repository keeps every version of the calculator as a version of **one file** — `Calculator.py`, each
with its own `README.md` — instead of several files sitting side by side:

| Tag | What it is | How to get it |
|-----|------------|---------------|
| `v1.0` | The original. Two digit pads, one per number, 26 near-identical click handlers, whole-number state, Tk's default look. | `git checkout v1.0`, or the [Releases](https://github.com/sensocc/Basic-Python-Calculator/releases) page |
| `v2.0` | The tidy-up. Numbers kept as text, a handler per *kind* of button, black/`SpringGreen2` styling. | `git checkout v2.0` |
| `v3.0` | One keypad instead of two, guarded maths with messages instead of tracebacks, and a clear hint when the Tk libraries are missing. | `git checkout v3.0` |
| `v4.0` | Adds `eˣ` and `ln`, the two one-number buttons from issue #1. | `git checkout v4.0` |
| `v5.0` | Type decimals and negatives: a `.` and a `±` beside the digits. | `git checkout v5.0` |
| `v6.0` | Adds `log` (base 10) and `%` (divide by 100). | `git checkout v6.0` |
| `v7.0` | Adds `sin`, `cos`, `tg` and `ctg`, and the `DEG` / `RAD` switch they obey. | `git checkout v7.0` |
| `v8.0` | Adds the constants `π` and `e`. | `git checkout v8.0` |
| `v9.0` | Adds keyboard input and the `⌫` button. | `git checkout v9.0` |
| `v10.0` | Adds the calculation history and its window. | `git checkout v10.0` |
| `v11.0` | **This version.** Five colour themes, chosen from a menu or a button, and a modernised look. | `git checkout v11.0` |

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
  ┌ Theme ▾ ┬ Help ▾ ┐           <- a menu bar: the themes, About and Quit
  │                 │
  │          12 +   │           <- the small line says what is waiting
  │             __  │
  │              5  │           <- the big number is what you are typing
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
  ├────┼────┼────┼────┤
  │log │ %  │sin │cos │
  ├────┼────┼────┼────┤
  │ tg │ctg │ π  │ e  │
  ├────┼────┼────┼────┤
  │ ⌫  │DEG │Hist│Them│
  ├────┼────┼────┼────┤
  │Reset│   =    │About│
  └─────┴────────┴─────┘
```

The buttons light up while the pointer is over them, and the whole grid grows with the window instead of
leaving a gap in a corner.

1. Press the digits of the first number. Decimals and negatives are typed the same way: `.` starts `0.` and
   `±` flips the sign, so `12` `.` `5` `±` is `-12.5`.
2. Press an operator — the small line above shows what is waiting, e.g. `12 +`.
3. Press the digits of the second number.
4. Press `=` to see the answer. `Reset` starts a new calculation, `About` says hello.

Pressing a second operator finishes the first calculation, so `2 + 3 + 4 =` gives `9` (the small line names
the step it just did: `5 + 4 = 9`).
After `=`, typing a digit (or `.`) starts a fresh number, while pressing an operator keeps using the answer.

The one-number buttons `eˣ`, `ln`, `log`, `%`, `sin`, `cos`, `tg` and `ctg` are used the other way round:
type the number, then press the button (`√` is not one of them — it takes the order of the root as its second
number: `8 √ 3 =` is `2`). Pressing one while an answer is already on show works on that answer, and pressing
one while a calculation is waiting finishes it — `2 + 3 ln` is `2 + ln(3)`.

Two kinds of button are the exceptions to "number first":

* `±` acts on whatever is on show, so `3 - 5 =` then `±` shows `2`.
* `π` and `e` **are** numbers, not operations: they take the place of whatever is on show. `π + 1 =` is
  `4.14159265359`, and a digit typed afterwards starts a fresh number rather than adding to the digits of π.
  If a calculation is waiting, the constant is its last number: `2 + π` shows `2 + π = 5.14159265359` there
  and then.

### Themes

Five themes ship with the calculator:

| Theme | What it looks like |
|-------|--------------------|
| `Terminal` | the original look: black, with SpringGreen2 for everything |
| `Light` | paper white, near-black text, light grey buttons |
| `Dark` | soft charcoal with a muted mint number — dark, but not glaring |
| `Solarized Light` | the [Solarized](https://ethanschoonover.com/solarized/) palette on its light background |
| `Solarized Dark` | the same palette on its dark background |

Change it in either of two ways:

* the **Theme menu** in the menu bar, which lists all five and ticks the one in use, or
* the **Theme button** on the keypad, which steps to the next one each time it is pressed (and wraps round).

Switching repaints **every window**, including the About, result and history windows if they happen to be
open. The theme is a setting, like the `DEG` / `RAD` switch, so `Reset` leaves it alone — and it is not
remembered between runs, so the calculator always starts on `Terminal`.

### The calculation history

`History` opens a window listing every calculation that has been finished, newest first, each one numbered.
Picking one puts its **answer** back on the display, ready to carry on from:

```
10 + 5 =        shows 15
History         lists   1. 10 + 5 = 15
pick it         shows 15 again, with 10 + 5 = 15 on the small line
* 2 =           shows 30
```

What goes in the list:

* anything you finished with `=`,
* the answer a one-number button worked out — `100 log` is filed as `log(100) = 2`,
* a step that finished because you pressed a second operator — `2 + 3 +` files `2 + 3 = 5`,
* a function or constant that finished a waiting calculation — `2 + ln(3) = 3.09861228867`.

What does not: a calculation that was refused (nothing was worked out), and pressing `π` or `e` on its own,
which is not a calculation at all.

`Clear` at the bottom of the window empties the list. The list holds the last **20** calculations, dropping
the oldest, and lives in memory only — closing the window loses it, and it is never written to disk. `Reset`
does not touch it either: the history is a record of what you did, not part of the sum you are working on.

### Typing without the mouse

The keyboard does what the buttons do, so `1` `2` `+` `5` and Enter gives `17` without touching the mouse:

| Key | What it does |
|-----|--------------|
| `0` to `9` (and the numeric keypad) | the digits |
| `.` | decimal point |
| `+` `-` `*` `/` `^` | the operators, the same as the buttons |
| `%` | percent |
| `=` or `Enter` | the answer, exactly as the `=` button |
| `Esc` | `Reset` |
| `Backspace` | the `⌫` button: one character off the number being typed |

A key that is not in that table does nothing at all — no beeps, no surprises. The window has to be the
focused one, and the letter-named buttons (`ln`, `log`, `sin`, `cos`, `tg`, `ctg`, `π`, `e`, `±`, `DEG`,
`History`, `Theme`) are mouse-only for now.

### Angles: the DEG / RAD switch

`sin`, `cos`, `tg` and `ctg` need a unit, so the `DEG` button is really a switch: press it and it renames
itself to `RAD`, press it again and it goes back. It starts in `DEG`, so `30 sin` is `0.5` straight away
rather than `-0.988031624093`.

The unit is part of the answer, so the small line says which one made it — `sin(30°) = 0.5` in degrees,
`sin(30 rad) = -0.988031624093` in radians. `Reset` leaves the switch alone: it is a setting, not part of the
sum you are working on.

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
| `sin` `cos` `tg` `ctg` | sine, cosine, tangent and cotangent of an angle, in the unit the switch is set to | `30 sin` → `0.5`, `45 tg` → `1` |
| `DEG` / `RAD` | the unit the four angle buttons use; it starts on `DEG` and renames itself when pressed | `30 sin` → `0.5`, then press it: `30 sin` → `-0.988031624093` |
| `π` | 3.141592653589793, put straight on show | `π * 2 =` → `6.28318530718` |
| `e` | 2.718281828459045, put straight on show | `e + 1 =` → `3.71828182846` |
| `.` | decimal point — one per number | `1 . 5` → `1.5`, `.` on its own → `0.` |
| `±` | flips the sign of the number on show | `5 ±` → `-5`, `3 - 5 = ±` → `2` |
| `⌫` | takes one character off the number being typed | `1 2 3 ⌫` → `12` |
| `History` | lists the finished calculations in their own window | pick one to put its answer back on show |
| `Theme` | steps to the next colour theme | press it five times to come back where you started |

`eˣ` and `ln` undo each other, so `5 eˣ ln` gives `5` back — and `e ln` is `1`, since the natural logarithm of
`e` is what it was built on.

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
| `90 tg`, or `270 tg` | I cannot take the tangent of that angle. |
| `0 ctg`, or `180 ctg` | I cannot take the cotangent of that angle. |
| `=` before entering an operator | Type it like this:  12 + 5 = |
| an operator, a function or `±` before entering a number | Type a number first. |

`calculate()` and `apply_function()` also refuse a negative base with a fractional exponent and anything that
comes out infinite or too large for a float; those are hard to reach by clicking, so they are covered by
tests rather than by a button sequence.

## What changed in version 11

* **Five colour themes**, in a `THEMES` table: `Terminal` (the old black and green), `Light`, `Dark` and the
  two Solarized palettes. Each theme names a colour for every part of a window — the window, the number area,
  the number, the small line, the button faces, the button text, and the colour a button takes under the
  pointer.
* **Two ways to change it:** a Theme menu in a new menu bar (with ticks, so you can see where you are), and a
  Theme button on the keypad that steps to the next theme and wraps round.
* **Every window follows**, including ones already open. That is what the `themed` register is for: each
  widget is painted from the theme and remembered, so a change is one loop over the register. Closed windows
  are forgotten as it goes.
* **A font this machine really has.** The old code asked for `Arial`, which is not installed everywhere — not
  on this machine — and Tk quietly substitutes something else. Now the family is chosen from everything
  installed, and then *checked against the odd characters on the keypad* (`√ ⌫ ± ÷ π ° eˣ`), falling back to
  Tk's own default font if the first choices cannot draw them. On this machine that lands on
  `Liberation Sans`, which has all seven.
* **A roomier look**: the number is 30pt instead of 18pt, the buttons have padding inside and out, and they
  use Tk's active state to light up under the pointer. The status line got its own quieter colour.
* **In the tests:** 14 new ones for the theming and the font choice, plus a real-window test that switches
  theme and checks the actual colours of the main window, a button, the number area *and a window that was
  already open*.

### Earlier versions

* **Version 10** — the calculation history, its window and picking old answers back up.
* **Version 9** — keyboard input (digits, `.`, the operators, Enter, Escape, Backspace, numeric keypad) and
  the `⌫` button.
* **Version 8** — the constants `π` and `e`, plus the `finish_with()` helper they share with the function
  buttons.
* **Version 7** — `sin`, `cos`, `tg` and `ctg`, with the `DEG` / `RAD` switch, and the two traps that came
  with them (no tangent at 90°, and `cos 90°` showing as `0` rather than `6.1e-17`).
* **Version 6** — `log` (base 10) and `%`, plus the `logarithm()` helper those two buttons share.
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
| `test_calculator.py` | the maths, every operator, the one-number and angle functions, the constants, typing decimals and signs, the key map, the backspace, the history, the themes and the font choice, all the error messages, chaining, the reused result popup, the About window, and the helpful message when Tk is missing. The keypad is driven through a stand-in for `tkinter`, so no window is needed. | nothing but Python |
| `test_gui_smoke.py` | the same buttons on a **real** Tk window: real clicks, real key events, a real history window, real colours when the theme changes, and the font checked against the installed ones — and then starts `Calculator.py` to see that its window stays open. | tkinter, the Tcl/Tk libraries and a display; it skips itself when one of those is missing |

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

* The theme is not remembered between runs: the calculator always starts on `Terminal`. Nothing is written to
  disk, which also means no file to go stale or fail on a read-only folder.
* The five themes are built in; there is no way to add your own without editing the `THEMES` table.
* Where a menu bar appears is up to the system: on macOS it goes to the top of the screen rather than into the
  window, which is the platform's own behaviour.
* The "lighting up" of a button is Tk's active state, so it appears while the pointer is over a button; there
  is no separate animation or rounded corners — plain Tk cannot draw those without extra dependencies.
* The history is kept in memory only: it does not survive closing the calculator, and there is no way to save
  it to a file.
* It holds the last 20 calculations. Older ones drop off silently — there is no "more" to scroll back to.
* Entries cannot be edited or deleted one at a time; `Clear` empties the lot.
* `Reset` does not empty the history, and does not change the theme: both are settings rather than part of the
  sum.
* The keyboard only covers the keys that mean something on a keypad: the letter-named buttons (`ln`, `log`,
  `sin`, `cos`, `tg`, `ctg`, `π`, `e`, `±`, `DEG`, `History`, `Theme`) have no shortcuts.
* Keys are only seen by the focused window, and the window has to be mapped — a minimised or hidden one gets
  nothing.
* `π` and `e` cannot be edited digit by digit: pressing one replaces what is on show, and a digit afterwards
  starts a new number.
* `e` is the constant and `eˣ` is the exponent — neighbours on the keypad, and easy to mix up.
* Angles are degrees or radians; there are no gradians, and no inverse trigonometry (`asin` and friends).
* A trig answer within `1e-12` of zero is shown as `0`, which is why `90 cos` is `0` rather than
  `6.12323399574e-17`. Genuinely tiny answers from the other buttons are still shown in full.
* `%` is simply the number divided by 100: `200 + 10 % =` gives `200.1`, not `220`.
* One decimal point per number, and no scientific notation to type — `1e-5` cannot be entered.
* `±` needs a number on show: pressing it while an operator is waiting for its second number says
  `Type a number first.`
* The result popup belongs to `=`; the one-number buttons answer in the big display and the status line.
* Numbers are shown rounded to 12 significant digits, so very long results are shortened; very large or very
  small ones come out in scientific notation, e.g. `1e+20`.
