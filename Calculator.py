"""A small Tkinter calculator - version 7.

Version 7 adds the trigonometry asked for in issue #5:

* `sin`, `cos`, `tg` and `ctg` - type an angle, press the button
* a `DEG` / `RAD` switch, because an angle means nothing without its unit

Degrees are the default, so `sin 30` is `0.5`. The switch changes its own label,
and the answer says which unit made it: `sin(30°) = 0.5`, `sin(0.5 rad) = 0.479425538604`.

Run it with:

    python3 Calculator.py
"""

import math
import sys
from types import SimpleNamespace

try:
    import tkinter as tk
except (ImportError, OSError) as error:  # tkinter, or the Tk libraries it needs, is missing
    tk = None
    TKINTER_ERROR = error

BACKGROUND = "black"
FOREGROUND = "SpringGreen2"
FONT = ("Arial", 18)
SMALL_FONT = ("Arial", 12)

OPERATORS = ("/", "*", "-", "+", "√", "^")

# the one-number functions that take an angle
ANGLES = ("sin", "cos", "tg", "ctg")

# label -> the one-number function it applies
FUNCTIONS = {
    "eˣ": "exp",
    "ln": "ln",
    "log": "log10",
    "%": "percent",
    "sin": "sin",
    "cos": "cos",
    "tg": "tg",
    "ctg": "ctg",
}

# Anything this close to zero counts as zero: Python's cos 90° is 6.1e-17, and
# its tan 90° is 1.6e16, which is not an answer at all.
SMALL = 1e-12

# label, grid row, grid column, columnspan
KEYPAD = (
    ("7", 2, 0, 1), ("8", 2, 1, 1), ("9", 2, 2, 1), ("/", 2, 3, 1),
    ("4", 3, 0, 1), ("5", 3, 1, 1), ("6", 3, 2, 1), ("*", 3, 3, 1),
    ("1", 4, 0, 1), ("2", 4, 1, 1), ("3", 4, 2, 1), ("-", 4, 3, 1),
    ("0", 5, 0, 1), (".", 5, 1, 1), ("±", 5, 2, 1), ("+", 5, 3, 1),
    ("√", 6, 0, 1), ("^", 6, 1, 1), ("ln", 6, 2, 1), ("eˣ", 6, 3, 1),
    ("log", 7, 0, 1), ("%", 7, 1, 1), ("sin", 7, 2, 1), ("cos", 7, 3, 1),
    ("tg", 8, 0, 1), ("ctg", 8, 1, 1), ("DEG", 8, 2, 2),
    ("Reset", 9, 0, 1), ("=", 9, 1, 2), ("About", 9, 3, 1),
)

# The whole calculator state lives here, so no function needs a `global` line.
state = SimpleNamespace(
    root=None,
    display_label=None,
    status_label=None,
    angle_button=None,   # the DEG/RAD switch, so its label can change
    result_window=None,
    result_label=None,
    first=None,          # the number to the left of the operator
    operator=None,       # the operator waiting to be used, if any
    entry="",            # the digits being typed right now
    status="",           # the small line above the big number
    error=None,          # a message to show instead of the status line
    angle_mode="deg",    # what sin, cos, tg and ctg measure angles in
)


# --- the maths --------------------------------------------------------------

def format_number(value):
    """Show a number without a pile of floating point noise."""
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("That number is too big to show.") from None
    if number == 0:
        return "0"          # -0.0 is just 0, and "-0" looks like a mistake
    return f"{number:.12g}"


def to_number(text):
    """Turn typed digits into a float."""
    try:
        return float(text)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("That is not a number I can use.") from None


def calculate(left, operator, right):
    """Apply an operator to two numbers.

    Raises ValueError with a readable message instead of letting Python blow up.
    """
    if operator == "+":
        result = left + right
    elif operator == "-":
        result = left - right
    elif operator == "*":
        result = left * right
    elif operator == "/":
        if right == 0:
            raise ValueError("You cannot divide by zero.")
        result = left / right
    elif operator == "^":
        if left == 0 and right < 0:
            raise ValueError("You cannot raise 0 to a negative power.")
        try:
            result = left ** right
        except OverflowError:
            raise ValueError("That power is too big to work out.") from None
    elif operator == "√":
        if right == 0:
            raise ValueError("A root cannot have the order zero.")
        if left < 0:
            raise ValueError("I cannot take a root of a negative number.")
        result = left ** (1 / right)
    else:
        raise ValueError(f"I do not know the operator {operator!r}.")

    # (-8) ** 0.5 comes out as a complex number, 1e308 * 1e308 as infinity, and a
    # huge integer cannot even be turned into a float - all of them end up here.
    if isinstance(result, complex):
        raise ValueError("That result is not a real number.")
    try:
        result = float(result)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("That result is too big to show.") from None
    if not math.isfinite(result):
        raise ValueError("That result is not a number I can show.")
    return result


def logarithm(function, value):
    """ln and log₁₀ share the rule that the number has to be above zero."""
    if value <= 0:
        raise ValueError("I can only take the logarithm of a number above zero.")
    if function == "ln":
        return math.log(value)
    return math.log10(value)


def trigonometry(function, value, angle_mode):
    """sin, cos, tg and ctg, with the unit switch and its two traps.

    The traps are that tan 90° is not a number at all - turning 90 into radians
    and asking Python gives 1.6e16 - and that cos 90° comes back as 6.1e-17
    rather than 0, which would make the button look broken.
    """
    angle = math.radians(value) if angle_mode == "deg" else value

    if function == "sin":
        result = math.sin(angle)
    elif function == "cos":
        result = math.cos(angle)
    elif function == "tg":
        if abs(math.cos(angle)) < SMALL:
            raise ValueError("I cannot take the tangent of that angle.")
        result = math.tan(angle)
    else:
        if abs(math.sin(angle)) < SMALL:
            raise ValueError("I cannot take the cotangent of that angle.")
        result = math.cos(angle) / math.sin(angle)

    if abs(result) < SMALL:
        result = 0.0        # what is left of cos 90° is zero for practical purposes
    return result


def apply_function(function, value, angle_mode="deg"):
    """Apply a one-number function. Raises ValueError with a readable message.

    `exp` is the natural exponent, e to the power of the number; `ln` is the
    natural logarithm, the power you raise e to; `log10` is the common
    logarithm, base 10; and `percent` is simply the number divided by 100.

    `sin`, `cos`, `tg` and `ctg` take their number as an angle measured in
    `angle_mode`, which is `deg` unless the switch has been pressed.
    """
    if function == "exp":
        try:
            result = math.exp(value)
        except OverflowError:
            raise ValueError("That exponent is too big to work out.") from None
    elif function in ("ln", "log10"):
        result = logarithm(function, value)
    elif function == "percent":
        result = value / 100
    elif function in ANGLES:
        result = trigonometry(function, value, angle_mode)
    else:
        raise ValueError(f"I do not know the function {function!r}.")

    if not math.isfinite(result):
        raise ValueError("That result is not a number I can show.")
    return result


def write_function(function, text, angle_mode="deg"):
    """How a one-number function reads on the status line."""
    if function == "exp":
        return "e^" + text
    if function == "percent":
        return text + "%"
    if function == "log10":
        return "log(" + text + ")"
    if function in ANGLES:
        # the unit is part of the answer, so say which one made it
        unit = "°" if angle_mode == "deg" else " rad"
        return function + "(" + text + unit + ")"
    if function == "ln":
        return "ln(" + text + ")"
    raise ValueError(f"I do not know how to write the function {function!r}.")


# --- drawing -----------------------------------------------------------------

def update_display():
    """Redraw the small status line and the big number."""
    if state.error:
        state.status_label.config(text=state.error)
    else:
        state.status_label.config(text=state.status)

    if state.entry:
        shown = state.entry
    elif state.first is not None:
        shown = format_number(state.first)
    else:
        shown = "0"
    state.display_label.config(text=shown)


def add_button(text, command, row, column, columnspan):
    button = tk.Button(
        state.root,
        text=text,
        font=FONT,
        bg=BACKGROUND,
        fg=FOREGROUND,
        command=command,
    )
    button.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=3, pady=3)
    return button


# --- what the buttons do -----------------------------------------------------

def begin_a_new_number_if_needed():
    """The rule the digits and the decimal point share.

    Nothing is half finished, so this is a brand new number rather than the one
    that is on show.
    """
    if state.operator is None and not state.entry:
        state.first = None
        state.status = ""


def press_digit(digit):
    """Add a digit to the number being typed."""
    state.error = None
    begin_a_new_number_if_needed()
    state.entry += str(digit)
    update_display()


def press_decimal_point():
    """Start or carry on a decimal number: 0.5, 12., 1.25."""
    state.error = None
    begin_a_new_number_if_needed()
    if not state.entry:
        state.entry = "0."
    elif "." not in state.entry:
        state.entry += "."
    update_display()


def press_sign():
    """Flip the sign of the number on show."""
    state.error = None

    if state.entry:
        if state.entry.startswith("-"):
            state.entry = state.entry[1:]
        else:
            state.entry = "-" + state.entry
        if state.entry.startswith("-") and not state.entry[1:].strip("0."):
            # -0 and -0. are just 0 and 0.
            state.entry = state.entry[1:]
        update_display()
        return

    if state.operator is None and state.first is not None:
        before = format_number(state.first)
        state.first = -state.first
        state.status = f"-({before}) = {format_number(state.first)}"
        update_display()
        return

    state.error = "Type a number first."
    update_display()


def refuse(message):
    """Give up on a half-finished calculation and say why."""
    state.first = None
    state.operator = None
    state.entry = ""
    state.status = ""
    state.error = message


def finish_calculation():
    """Work out  first <operator> entry.  Returns True when it worked."""
    try:
        value = calculate(state.first, state.operator, to_number(state.entry))
        text = format_number(value)
    except ValueError as error:
        refuse(str(error))
        return False

    state.first = value
    state.operator = None
    state.entry = ""
    state.status = text
    return True


def press_operator(operator):
    """Remember an operator, finishing the previous one first if one is waiting."""
    state.error = None
    if state.entry:
        if state.first is None:
            state.first = to_number(state.entry)
        elif state.operator is not None and not finish_calculation():
            update_display()
            return
        state.entry = ""

    if state.first is None:
        state.error = "Type a number first."
        update_display()
        return

    state.operator = operator
    state.status = f"{format_number(state.first)} {operator}"
    update_display()


def press_function(function):
    """Apply a one-number function to the number on show.

    The number being typed is used if there is one, otherwise the answer that is
    already on show. A waiting calculation is finished with the answer, the same
    way pressing an operator finishes it.
    """
    state.error = None

    if state.entry:
        value = to_number(state.entry)
        shown = state.entry
    elif state.operator is None and state.first is not None:
        value = state.first
        shown = format_number(state.first)
    else:
        state.error = "Type a number first."
        update_display()
        return

    try:
        answer = apply_function(function, value, state.angle_mode)
    except ValueError as error:
        refuse(str(error))
        update_display()
        return

    written = write_function(function, shown, state.angle_mode)

    if state.operator is None:
        state.first = answer
        state.entry = ""
        state.status = f"{written} = {format_number(answer)}"
        update_display()
        return

    # Something like  2 + 3  is waiting: finish it with the answer as its last number.
    left = format_number(state.first)
    operator = state.operator
    try:
        combined = calculate(state.first, operator, answer)
    except ValueError as error:
        refuse(str(error))
        update_display()
        return

    state.first = combined
    state.operator = None
    state.entry = ""
    state.status = f"{left} {operator} {written} = {format_number(combined)}"
    update_display()


def press_angle_mode():
    """Switch sin, cos, tg and ctg between degrees and radians.

    The switch is a setting, not part of the sum, so Reset leaves it alone.
    """
    state.error = None
    state.angle_mode = "rad" if state.angle_mode == "deg" else "deg"
    state.angle_button.config(text=state.angle_mode.upper())
    state.status = "Angles in " + ("degrees" if state.angle_mode == "deg" else "radians")
    update_display()


def press_equals():
    """Show the answer, in the window and in its own little popup."""
    state.error = None
    if state.first is None or state.operator is None or not state.entry:
        state.error = "Type it like this:  12 + 5 ="
        update_display()
        return

    expression = f"{format_number(state.first)} {state.operator} {state.entry}"
    if finish_calculation():
        answer = state.status
        state.status = f"{expression} = {answer}"
        show_result_window(answer)
    update_display()


def press_reset():
    """Forget everything and start over."""
    state.first = None
    state.operator = None
    state.entry = ""
    state.status = ""
    state.error = None
    update_display()


def show_result_window(answer):
    """Open the result popup, or refresh it if it is already open."""
    if state.result_window is not None and state.result_window.winfo_exists():
        state.result_label.config(text="Your result is: " + answer)
        state.result_window.lift()
        return

    window = tk.Toplevel(state.root)
    window.title("The Calculation Result!")
    window.configure(bg=BACKGROUND)
    state.result_label = tk.Label(
        window,
        text="Your result is: " + answer,
        padx=20,
        pady=20,
        font=FONT,
        bg=BACKGROUND,
        fg=FOREGROUND,
    )
    state.result_label.pack()
    state.result_window = window


def open_about_window():
    window = tk.Toplevel(state.root)
    window.title("About This App")
    window.configure(bg=BACKGROUND)
    tk.Label(
        window,
        text="VER 7.0! Made by Sasha!",
        padx=20,
        pady=20,
        font=FONT,
        bg=BACKGROUND,
        fg=FOREGROUND,
    ).pack()
    tk.Label(
        window,
        text="Version 7: sin, cos, tg and ctg, with a DEG/RAD switch.",
        padx=20,
        font=SMALL_FONT,
        bg=BACKGROUND,
        fg=FOREGROUND,
    ).pack(pady=(0, 20))


# --- starting up -------------------------------------------------------------

def build_window():
    """Create the calculator window and remember its widgets on state."""
    root = tk.Tk()
    root.title("My Fancy-Shmancy Calculator V7")
    root.configure(bg=BACKGROUND)
    state.root = root

    state.status_label = tk.Label(
        root, text="", font=SMALL_FONT, bg=BACKGROUND, fg=FOREGROUND, anchor="e", padx=20
    )
    state.status_label.grid(row=0, column=0, columnspan=4, sticky="ew")

    state.display_label = tk.Label(
        root, text="0", font=FONT, bg=BACKGROUND, fg=FOREGROUND, anchor="e", padx=20, pady=10
    )
    state.display_label.grid(row=1, column=0, columnspan=4, sticky="ew")

    for label, row, column, columnspan in KEYPAD:
        if label in OPERATORS:
            command = lambda op=label: press_operator(op)
        elif label in FUNCTIONS:
            command = lambda name=FUNCTIONS[label]: press_function(name)
        elif label == "=":
            command = press_equals
        elif label == ".":
            command = press_decimal_point
        elif label == "±":
            command = press_sign
        elif label == "DEG":
            command = press_angle_mode
        elif label == "Reset":
            command = press_reset
        elif label == "About":
            command = open_about_window
        else:
            command = lambda digit=label: press_digit(digit)
        button = add_button(label, command, row, column, columnspan)
        if label == "DEG":
            state.angle_button = button       # its label follows the switch

    for column in range(4):
        root.columnconfigure(column, weight=1)
    for row in range(2, 10):
        root.rowconfigure(row, weight=1)
    root.minsize(360, 610)
    return root


def main():
    """Return an exit code: 0 if the window was opened, 1 if it could not be."""
    if tk is None:
        print(
            "This calculator needs Python's tkinter toolkit, and Tk is not installed.\n"
            f"Python said: {TKINTER_ERROR}\n\n"
            "Install it and try again:\n"
            "  Omarchy / Arch    omarchy pkg add tk\n"
            "  Debian / Ubuntu   sudo apt install python3-tk\n"
            "  Fedora            sudo dnf install python3-tkinter\n"
            "  macOS / Windows   reinstall Python from python.org (Tk is included)",
            file=sys.stderr,
        )
        return 1

    try:
        root = build_window()
    except tk.TclError as error:
        print(f"I could not open a window: {error}", file=sys.stderr)
        return 1

    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
