"""A small Tkinter calculator - version 3.

Cleaned up from version 2:

* one keypad instead of two duplicated digit pads
* one handler per kind of button instead of a function per button
* readable messages instead of Python tracebacks when the maths goes wrong
* a clear hint instead of an ImportError when the Tk libraries are missing

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

# label, grid row, grid column, columnspan
KEYPAD = (
    ("7", 2, 0, 1), ("8", 2, 1, 1), ("9", 2, 2, 1), ("/", 2, 3, 1),
    ("4", 3, 0, 1), ("5", 3, 1, 1), ("6", 3, 2, 1), ("*", 3, 3, 1),
    ("1", 4, 0, 1), ("2", 4, 1, 1), ("3", 4, 2, 1), ("-", 4, 3, 1),
    ("0", 5, 0, 1), ("√", 5, 1, 1), ("^", 5, 2, 1), ("+", 5, 3, 1),
    ("Reset", 6, 0, 1), ("=", 6, 1, 2), ("About", 6, 3, 1),
)

# The whole calculator state lives here, so no function needs a `global` line.
state = SimpleNamespace(
    root=None,
    display_label=None,
    status_label=None,
    result_window=None,
    result_label=None,
    first=None,          # the number to the left of the operator
    operator=None,       # the operator waiting to be used, if any
    entry="",            # the digits being typed right now
    status="",           # the small line above the big number
    error=None,          # a message to show instead of the status line
)


# --- the maths --------------------------------------------------------------

def format_number(value):
    """Show a number without a pile of floating point noise."""
    try:
        return f"{float(value):.12g}"
    except (TypeError, ValueError, OverflowError):
        raise ValueError("That number is too big to show.") from None


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


# --- what the buttons do -----------------------------------------------------

def press_digit(digit):
    """Add a digit to the number being typed."""
    state.error = None
    if state.operator is None and not state.entry:
        # Nothing is half finished, so this is a brand new calculation.
        state.first = None
        state.status = ""
    state.entry += str(digit)
    update_display()


def finish_calculation():
    """Work out  first <operator> entry.  Returns True when it worked."""
    try:
        value = calculate(state.first, state.operator, to_number(state.entry))
        text = format_number(value)
    except ValueError as error:
        state.first = None
        state.operator = None
        state.entry = ""
        state.status = ""
        state.error = str(error)
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
        text="VER 3.0! Made by Sasha!",
        padx=20,
        pady=20,
        font=FONT,
        bg=BACKGROUND,
        fg=FOREGROUND,
    ).pack()
    tk.Label(
        window,
        text="Cleaned up and modernised from version 2.",
        padx=20,
        font=SMALL_FONT,
        bg=BACKGROUND,
        fg=FOREGROUND,
    ).pack(pady=(0, 20))


# --- starting up -------------------------------------------------------------

def build_window():
    """Create the calculator window and remember its widgets on state."""
    root = tk.Tk()
    root.title("My Fancy-Shmancy Calculator V3")
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
        elif label == "=":
            command = press_equals
        elif label == "Reset":
            command = press_reset
        elif label == "About":
            command = open_about_window
        else:
            command = lambda digit=label: press_digit(digit)
        add_button(label, command, row, column, columnspan)

    for column in range(4):
        root.columnconfigure(column, weight=1)
    for row in range(2, 7):
        root.rowconfigure(row, weight=1)
    root.minsize(360, 430)
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
