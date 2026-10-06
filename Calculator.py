"""A small Tkinter calculator - version 11.

Version 11 is the interface overhaul asked for in issue #9:

* five colour themes, in a Theme menu and on a Theme button: Terminal (the old
  black and green), Light, Dark, Solarized Light and Solarized Dark
* every window follows the theme, including the About, result and history
  windows that happen to be open at the time
* a bigger number, roomier buttons that light up under the pointer, and a font
  chosen from the ones this machine actually has rather than assuming Arial,
  which is not installed everywhere

Versions 1 to 10 built the calculator itself: one keypad, guarded arithmetic
that says what went wrong, a decimal point and a sign, eˣ / ln / log / percent,
the trigonometry with its DEG/RAD switch, the constants π and e, the keyboard,
and a history of what has been worked out.

Run it with:

    python3 Calculator.py
"""
import math
import sys
from collections import namedtuple
from types import SimpleNamespace

try:
    import tkinter as tk
    import tkinter.font as tkfont
except (ImportError, OSError) as error:  # tkinter, or the Tk libraries it needs, is missing
    tk = None
    tkfont = None
    TKINTER_ERROR = error

# Every theme is a set of colours for the parts of a window. "Terminal" is the
# look the calculator had before version 11; the two Solarized pairs are that
# well known palette, which is built to sit easy on the eyes.
THEMES = {
    "Terminal": {
        "window": "black",
        "display": "black",
        "text": "SpringGreen2",
        "status": "SpringGreen2",
        "button": "black",
        "button_text": "SpringGreen2",
        "button_active": "#123a1c",
    },
    "Light": {
        "window": "#f2f3f5",
        "display": "#ffffff",
        "text": "#1b1f24",
        "status": "#5b6470",
        "button": "#e4e7eb",
        "button_text": "#1b1f24",
        "button_active": "#cbd2da",
    },
    "Dark": {
        "window": "#22242a",
        "display": "#191b20",
        "text": "#9ee6b4",
        "status": "#8b93a1",
        "button": "#2c2f36",
        "button_text": "#d7dae0",
        "button_active": "#3d424c",
    },
    "Solarized Light": {
        "window": "#fdf6e3",
        "display": "#eee8d5",
        "text": "#268bd2",
        "status": "#657b83",
        "button": "#eee8d5",
        "button_text": "#586e75",
        "button_active": "#93a1a1",
    },
    "Solarized Dark": {
        "window": "#002b36",
        "display": "#073642",
        "text": "#2aa198",
        "status": "#93a1a1",
        "button": "#073642",
        "button_text": "#93a1a1",
        "button_active": "#586e75",
    },
}

THEME_NAMES = tuple(THEMES)

# Families that exist on one machine or another. The first of these that this
# machine has is used, and Tk's own default font is the last resort - it is
# always there.
FONT_CANDIDATES = ("DejaVu Sans", "Liberation Sans", "Noto Sans", "Segoe UI",
                   "Helvetica Neue", "Arial")

# The characters on the keypad that a font might not have.
ODD_CHARACTERS = "√⌫±÷π°eˣ"

LABEL_SIZE = 18     # the buttons
NUMBER_SIZE = 30    # the number being typed
SMALL_SIZE = 12     # the small line above it, and the little windows

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

# the two famous numbers, and the label each button shows
CONSTANTS = {"π": math.pi, "e": math.e}

# How many finished calculations the history keeps; the oldest drop off.
HISTORY_LIMIT = 20

# One finished calculation: what it says on the status line, and the answer.
HistoryEntry = namedtuple("HistoryEntry", "text value")

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
    ("tg", 8, 0, 1), ("ctg", 8, 1, 1), ("π", 8, 2, 1), ("e", 8, 3, 1),
    ("⌫", 9, 0, 1), ("DEG", 9, 1, 1), ("History", 9, 2, 1), ("Theme", 9, 3, 1),
    ("Reset", 10, 0, 1), ("=", 10, 1, 2), ("About", 10, 3, 1),
)

# The whole calculator state lives here, so no function needs a `global` line.
state = SimpleNamespace(
    root=None,
    display_label=None,
    status_label=None,
    theme="Terminal",    # which of THEMES is on
    themed=[],           # every widget painted from the theme, so a change can repaint it
    font_family=None,    # the three fonts, chosen when the window is built
    font=None,
    small_font=None,
    number_font=None,
    theme_var=None,      # the tick in the Theme menu
    theme_button=None,   # the button that steps to the next theme
    angle_button=None,   # the DEG/RAD switch, so its label can change
    result_window=None,
    result_label=None,
    first=None,          # the number to the left of the operator
    operator=None,       # the operator waiting to be used, if any
    entry="",            # the digits being typed right now
    status="",           # the small line above the big number
    error=None,          # a message to show instead of the status line
    angle_mode="deg",    # what sin, cos, tg and ctg measure angles in
    keys=None,           # what each keyboard key does, filled in when the window is built
    history=[],          # finished calculations, newest first
    history_window=None, # the window that shows them
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

def theme_colour(part):
    """The colour the chosen theme uses for one part of a window."""
    return THEMES[state.theme][part]


def paint(widget, parts):
    """Give one widget the theme's colours for the parts of it that matter."""
    widget.configure(**{option: theme_colour(part) for option, part in parts.items()})


def colour_widget(widget, **parts):
    """Colour a widget from the theme and remember how, for the next theme change.

    Every themed widget goes on one list, which is what makes switching theme
    able to repaint the lot - including windows that are already open.
    """
    state.themed.append((widget, parts))
    paint(widget, parts)
    return widget


def apply_theme():
    """Repaint everything on screen, and forget the windows that have closed."""
    still_open = []
    for widget, parts in state.themed:
        if not widget.winfo_exists():
            continue
        paint(widget, parts)
        still_open.append((widget, parts))
    state.themed = still_open


def can_draw(family, size=LABEL_SIZE):
    """Whether a font family has the odd characters the keypad needs."""
    font = tkfont.Font(family=family, size=size)
    return all(font.measure(character) for character in set(ODD_CHARACTERS))


def choose_font_family():
    """Pick a font this machine has, rather than one it is only hoped to have.

    Arial, for instance, is not installed everywhere - it is not on this machine -
    and Tk quietly substitutes something else when a family is missing. So the
    family is chosen from what is here and then checked against the characters on
    the keypad, falling back to Tk's own default font if nothing else will do.
    """
    families = set(tkfont.families())
    default_family = tkfont.nametofont("TkDefaultFont").actual("family")
    present = [family for family in FONT_CANDIDATES if family in families]
    for family in present + [default_family]:
        if can_draw(family):
            return family
    return present[0] if present else default_family


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
    button = colour_widget(
        tk.Button(state.root, text=text, font=state.font, command=command, padx=8, pady=8),
        background="button",
        foreground="button_text",
        activebackground="button_active",
        activeforeground="button_text",
    )
    button.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=4, pady=4)
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


def remember(text, value):
    """Keep a finished calculation for the history, newest first."""
    state.history.insert(0, HistoryEntry(text, value))
    del state.history[HISTORY_LIMIT:]


def finish_calculation():
    """Work out  first <operator> entry.  Returns True when it worked."""
    expression = f"{format_number(state.first)} {state.operator} {state.entry}"
    try:
        value = calculate(state.first, state.operator, to_number(state.entry))
        text = format_number(value)
    except ValueError as error:
        refuse(str(error))
        return False

    state.first = value
    state.operator = None
    state.entry = ""
    state.status = f"{expression} = {text}"
    remember(state.status, value)
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


def finish_with(value, written):
    """Finish the waiting calculation, with `value` as its last number.

    `written` is how that last number reads on the status line: a function's
    label such as `ln(3)`, or a constant's name such as `π`. Returns True when
    the calculation worked.
    """
    left = format_number(state.first)
    operator = state.operator
    try:
        combined = calculate(state.first, operator, value)
    except ValueError as error:
        refuse(str(error))
        return False

    state.first = combined
    state.operator = None
    state.entry = ""
    state.status = f"{left} {operator} {written} = {format_number(combined)}"
    remember(state.status, combined)
    return True


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
        remember(state.status, answer)
        update_display()
        return

    # Something like  2 + 3  is waiting: finish it with the answer as its last number.
    finish_with(answer, written)
    update_display()


def press_backspace():
    """Take the last character off the number being typed.

    With nothing being typed it just tidies the message line away, so the key
    does something sensible rather than nothing at all.
    """
    state.error = None

    if state.entry:
        state.entry = state.entry[:-1]
        if state.entry == "-":
            state.entry = ""          # a lone minus sign is not a number
        update_display()
        return

    state.status = ""
    update_display()


def press_constant(name):
    """Put π or e on show.

    A constant behaves like an answer rather than a typed number: it takes the
    place of whatever is on show, it finishes a calculation that is waiting, and
    typing a digit afterwards starts a fresh number.
    """
    state.error = None
    value = CONSTANTS[name]

    if state.operator is None or state.first is None:
        state.first = value
        state.entry = ""
        state.status = name          # the digits are already in the display
        update_display()
        return

    finish_with(value, name)
    update_display()


def switch_theme(name):
    """Put one of the themes on, from the menu or from the button."""
    if name not in THEMES:
        return
    state.theme = name
    state.theme_var.set(name)
    apply_theme()
    state.error = None
    state.status = "Theme: " + name
    update_display()


def press_theme():
    """Step to the next theme in the list."""
    names = list(THEME_NAMES)
    switch_theme(names[(names.index(state.theme) + 1) % len(names)])


def press_history():
    """Show the history in its own window, or bring that window up to date.

    The list is rebuilt every time rather than kept in step, so there is nothing
    to go stale when a calculation is added or the list is cleared.
    """
    window = state.history_window
    if window is not None and window.winfo_exists():
        for child in window.winfo_children():
            child.destroy()
    else:
        window = colour_widget(tk.Toplevel(state.root), background="window")
        window.title("The Calculation History!")
        state.history_window = window

    if not state.history:
        colour_widget(
            tk.Label(window, text="Nothing has been worked out yet.", padx=24, pady=20,
                     font=state.font),
            background="window",
            foreground="status",
        ).pack()
    for number, entry in enumerate(state.history, start=1):
        colour_widget(
            tk.Button(window, text=f"{number}. {entry.text}", padx=20, pady=10,
                      font=state.small_font, anchor="w",
                      command=lambda entry=entry: reuse_answer(entry)),
            background="button",
            foreground="button_text",
            activebackground="button_active",
            activeforeground="button_text",
        ).pack(fill="x", padx=12, pady=3)
    colour_widget(
        tk.Button(window, text="Clear", padx=20, pady=10, font=state.small_font,
                  command=clear_history),
        background="button",
        foreground="button_text",
        activebackground="button_active",
        activeforeground="button_text",
    ).pack(pady=(10, 20))
    window.lift()


def reuse_answer(entry):
    """Put an old answer back on show, ready to carry on from."""
    state.error = None
    state.first = entry.value
    state.operator = None
    state.entry = ""
    state.status = entry.text
    update_display()


def clear_history():
    """Forget everything that has been worked out."""
    state.history.clear()
    press_history()


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

    if finish_calculation():
        show_result_window(format_number(state.first))
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

    window = colour_widget(tk.Toplevel(state.root), background="window")
    window.title("The Calculation Result!")
    state.result_label = colour_widget(
        tk.Label(window, text="Your result is: " + answer, padx=24, pady=20, font=state.font),
        background="window",
        foreground="text",
    )
    state.result_label.pack()
    state.result_window = window


def open_about_window():
    window = colour_widget(tk.Toplevel(state.root), background="window")
    window.title("About This App")
    colour_widget(
        tk.Label(window, text="VER 11.0! Made by Sasha!", padx=24, pady=20, font=state.font),
        background="window",
        foreground="text",
    ).pack()
    colour_widget(
        tk.Label(window, text="Version 11: five colour themes, from issue #9.",
                 padx=24, font=state.small_font),
        background="window",
        foreground="status",
    ).pack(pady=(0, 20))


def build_key_map():
    """Which keyboard key does what.

    Every entry calls the handler the matching button calls, so there is no
    second copy of the logic to keep in step. Both the name Tk gives a key and
    the character it types are in here, because Tk calls the `*` key
    `asterisk`; the numeric keypad is in as well. Anything missing from the map
    is ignored, so an unrelated key never does anything surprising.
    """
    keys = {}

    def add(action, *names):
        for name in names:
            keys[name] = action

    for digit in "0123456789":
        add(lambda digit=digit: press_digit(digit), digit, "KP_" + digit)
    for operator in "+-*/^":
        add(lambda operator=operator: press_operator(operator), operator)
    add(lambda: press_operator("+"), "KP_Add")
    add(lambda: press_operator("-"), "KP_Subtract")
    add(lambda: press_operator("*"), "KP_Multiply")
    add(lambda: press_operator("/"), "KP_Divide")
    add(press_decimal_point, ".", "period", "KP_Decimal")
    add(lambda: press_function("percent"), "%", "percent")
    add(press_equals, "=", "equal", "Return", "KP_Enter")
    add(press_reset, "Escape")
    add(press_backspace, "BackSpace")
    return keys


def on_key(event):
    """Do what the matching button does for a key, and nothing for any other key.

    Returning "break" stops Tk from handing the same key on to a button that
    happens to have the keyboard focus, which would otherwise do everything
    twice.
    """
    action = state.keys.get(event.keysym) or state.keys.get(event.char)
    if action is None:
        return None
    action()
    return "break"


# --- starting up -------------------------------------------------------------

def build_window():
    """Create the calculator window and remember its widgets on state."""
    root = tk.Tk()
    root.title("My Fancy-Shmancy Calculator V11")

    # A font this machine really has, in three sizes, and a fresh register of
    # everything that is painted from the theme.
    state.font_family = choose_font_family()
    state.font = (state.font_family, LABEL_SIZE)
    state.small_font = (state.font_family, SMALL_SIZE)
    state.number_font = (state.font_family, NUMBER_SIZE)
    state.themed = []
    state.root = root
    colour_widget(root, background="window")

    # The themes in a menu, with About and Quit next to them.
    state.theme_var = tk.StringVar(value=state.theme)
    menubar = tk.Menu(root)
    theme_menu = tk.Menu(menubar, tearoff=False)
    for name in THEME_NAMES:
        theme_menu.add_radiobutton(label=name, variable=state.theme_var, value=name,
                                   command=lambda name=name: switch_theme(name))
    help_menu = tk.Menu(menubar, tearoff=False)
    help_menu.add_command(label="About", command=open_about_window)
    help_menu.add_command(label="Quit", command=root.destroy)
    menubar.add_cascade(label="Theme", menu=theme_menu)
    menubar.add_cascade(label="Help", menu=help_menu)
    for menu in (menubar, theme_menu, help_menu):
        colour_widget(menu, background="window", foreground="text")
    root.configure(menu=menubar)

    state.status_label = colour_widget(
        tk.Label(root, text="", font=state.small_font, anchor="e", padx=24),
        background="window",
        foreground="status",
    )
    state.status_label.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(10, 0))

    state.display_label = colour_widget(
        tk.Label(root, text="0", font=state.number_font, anchor="e", padx=24, pady=16),
        background="display",
        foreground="text",
    )
    state.display_label.grid(row=1, column=0, columnspan=4, sticky="ew", padx=12, pady=(4, 10))

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
        elif label in CONSTANTS:
            command = lambda name=label: press_constant(name)
        elif label == "⌫":
            command = press_backspace
        elif label == "History":
            command = press_history
        elif label == "DEG":
            command = press_angle_mode
        elif label == "Reset":
            command = press_reset
        elif label == "About":
            command = open_about_window
        elif label == "Theme":
            command = press_theme
        else:
            command = lambda digit=label: press_digit(digit)
        button = add_button(label, command, row, column, columnspan)
        if label == "DEG":
            state.angle_button = button       # its label follows the switch
        if label == "Theme":
            state.theme_button = button

    for column in range(4):
        root.columnconfigure(column, weight=1)
    state.keys = build_key_map()
    root.bind("<Key>", on_key)

    for row in range(2, 11):
        root.rowconfigure(row, weight=1)
    root.minsize(430, 700)
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
