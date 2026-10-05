"""Tests for Calculator.py: the maths, and every button on the keypad.

Run them with:

    python3 -m unittest discover -v

The keypad is driven through a stand-in for `tkinter`, so nothing here needs a
window, a display or the Tcl/Tk libraries - these tests run wherever Python runs.
test_gui_smoke.py presses the same buttons on a real window.

Calculator.py is built to make this possible: it imports tkinter inside a
try/except and keeps working with `tk = None` when Tk is missing, so the module
can be imported and driven without Tk.
"""

import importlib.util
import math
import subprocess
import sys
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CALCULATOR_PY = HERE / "Calculator.py"


# --- a stand-in for tkinter ---------------------------------------------------
# Just enough of Tk for Calculator.py to build its window: the widgets remember
# the options they were given, and a button remembers its `command`, so a test
# can "press" it.

class TclError(Exception):
    """Stands in for tkinter.TclError."""


class FakeWidget:
    instances = []

    def __init__(self, master=None, **options):
        self.master = master
        self.options = dict(options)
        self.command = options.get("command")
        self.grid_options = {}
        self.pack_options = {}
        self.instances.append(self)

    def config(self, **options):
        self.options.update(options)

    configure = config

    def cget(self, option):
        return self.options.get(option)

    def grid(self, **options):
        self.grid_options = dict(options)

    def pack(self, **options):
        self.pack_options = dict(options)

    def winfo_exists(self):
        return True

    def lift(self):
        pass


class FakeTk(FakeWidget):
    def __init__(self, *args, **options):
        super().__init__(None, **options)
        self.title_text = None

    def title(self, text):
        self.title_text = text

    def columnconfigure(self, *args, **options):
        pass

    def rowconfigure(self, *args, **options):
        pass

    def minsize(self, *args, **options):
        pass

    def mainloop(self):
        raise AssertionError("a test must not start the real event loop")


class FakeToplevel(FakeWidget):
    def __init__(self, master=None, **options):
        super().__init__(master, **options)
        self.title_text = None

    def title(self, text):
        self.title_text = text


class FakeLabel(FakeWidget):
    pass


class FakeButton(FakeWidget):
    pass


WIDGETS = (FakeTk, FakeToplevel, FakeLabel, FakeButton)
for widget in WIDGETS:
    widget.instances = []


def load_calculator():
    """Import Calculator.py with the stand-in in place of tkinter."""
    already_imported = sys.modules.pop("tkinter", None)
    stand_in = types.ModuleType("tkinter")
    stand_in.Tk = FakeTk
    stand_in.Toplevel = FakeToplevel
    stand_in.Label = FakeLabel
    stand_in.Button = FakeButton
    stand_in.TclError = TclError
    sys.modules["tkinter"] = stand_in
    try:
        # A name of its own, so this file never shares a module with
        # test_gui_smoke.py, which loads Calculator.py with the real tkinter.
        spec = importlib.util.spec_from_file_location("calculator_with_fake_tk", CALCULATOR_PY)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        if already_imported is None:
            sys.modules.pop("tkinter", None)
        else:
            sys.modules["tkinter"] = already_imported
    return module


Calculator = load_calculator()


class KeypadTestCase(unittest.TestCase):
    """Builds the window and collects the buttons for every test."""

    def setUp(self):
        for widget in WIDGETS:
            widget.instances.clear()
        Calculator.state.result_window = None
        Calculator.state.result_label = None
        self.root = Calculator.build_window()
        self.buttons = {widget.cget("text"): widget for widget in FakeButton.instances}
        # A new window is not a new calculator: the state has to be cleaned out too,
        # or one test carries a half-finished calculation into the next one.
        self.press("Reset")

    def press(self, *labels):
        for label in labels:
            button = self.buttons.get(label)
            self.assertIsNotNone(button, "there is no button labelled " + repr(label))
            button.command()

    def display(self):
        return Calculator.state.display_label.cget("text")

    def status(self):
        return Calculator.state.status_label.cget("text")

    def fresh(self):
        self.press("Reset")


class TestLayout(KeypadTestCase):
    def test_there_are_twenty_one_buttons(self):
        self.assertEqual(len(Calculator.KEYPAD), 21)
        self.assertEqual(len(self.buttons), 21)

    def test_every_keypad_entry_has_a_button(self):
        for entry in Calculator.KEYPAD:
            self.assertIn(entry[0], self.buttons)

    def test_no_label_is_used_for_two_buttons(self):
        labels = [widget.cget("text") for widget in FakeButton.instances]
        self.assertEqual(len(labels), len(set(labels)))

    def test_the_buttons_are_in_the_conventional_places(self):
        for label, row, column in (("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("/", 2, 3),
                                   ("1", 4, 0), ("0", 5, 0), ("+", 5, 3),
                                   ("eˣ", 6, 0), ("ln", 6, 2),
                                   ("Reset", 7, 0), ("=", 7, 1), ("About", 7, 3)):
            options = self.buttons[label].grid_options
            self.assertEqual((options["row"], options["column"]), (row, column),
                             "button " + label)

    def test_the_buttons_use_four_columns_below_the_display(self):
        columns = sorted({widget.grid_options["column"] for widget in FakeButton.instances})
        rows = sorted({widget.grid_options["row"] for widget in FakeButton.instances})
        self.assertEqual(columns, [0, 1, 2, 3])
        self.assertEqual(rows, [2, 3, 4, 5, 6, 7])

    def test_equals_spans_two_columns(self):
        self.assertEqual(self.buttons["="].grid_options["columnspan"], 2)

    def test_the_status_line_sits_above_the_number(self):
        status = Calculator.state.status_label.grid_options
        display = Calculator.state.display_label.grid_options
        self.assertEqual(status["columnspan"], 4)
        self.assertEqual(display["columnspan"], 4)
        self.assertLess(status["row"], display["row"])

    def test_the_window_has_a_title(self):
        self.assertEqual(self.root.title_text, "My Fancy-Shmancy Calculator V4")


class TestTheMaths(unittest.TestCase):
    def test_each_operator(self):
        for left, operator, right, expected in (
            (12, "+", 5, 17),
            (12, "-", 5, 7),
            (12, "*", 5, 60),
            (12, "/", 5, 2.4),
            (2, "^", 10, 1024),
            (9, "√", 2, 3),
            (8, "√", 3, 2),
        ):
            with self.subTest(operator=operator, left=left, right=right):
                self.assertAlmostEqual(Calculator.calculate(left, operator, right), expected)

    def test_impossible_maths_is_refused(self):
        for left, operator, right, complaint in (
            (5, "/", 0, "divide by zero"),
            (8, "√", 0, "order zero"),
            (-8, "√", 2, "negative"),
            (-8, "^", 0.5, "not a real number"),
            (0, "^", -1, "0 to a negative power"),
            (1e308, "*", 1e308, "not a number I can show"),
            (10 ** 300, "^", 9, "too big to show"),   # an int too large for a float
            (1, "!", 2, "I do not know the operator"),
        ):
            with self.subTest(operator=operator, left=left, right=right):
                with self.assertRaises(ValueError) as caught:
                    Calculator.calculate(left, operator, right)
                self.assertIn(complaint, str(caught.exception))

    def test_numbers_are_shown_without_float_noise(self):
        for value, expected in (
            (6.0, "6"),
            (387420489.0, "387420489"),
            (0.1 + 0.2, "0.3"),
            (1 / 3, "0.333333333333"),
            (2.4, "2.4"),
            (-2.0, "-2"),
        ):
            with self.subTest(value=value):
                self.assertEqual(Calculator.format_number(value), expected)

    def test_the_natural_exponent(self):
        for value, expected in ((0, 1.0), (1, math.e), (2, math.e ** 2), (-1, 1 / math.e)):
            with self.subTest(value=value):
                self.assertAlmostEqual(Calculator.apply_function("exp", value), expected)

    def test_the_natural_logarithm(self):
        for value, expected in ((1, 0.0), (math.e, 1.0), (10, math.log(10)), (0.5, -math.log(2))):
            with self.subTest(value=value):
                self.assertAlmostEqual(Calculator.apply_function("ln", value), expected)

    def test_the_exponent_and_the_logarithm_undo_each_other(self):
        for value in (0.5, 2, 99):
            with self.subTest(value=value):
                self.assertAlmostEqual(
                    Calculator.apply_function("ln", Calculator.apply_function("exp", value)), value)

    def test_impossible_functions_are_refused(self):
        for function, value, complaint in (
            ("ln", 0, "logarithm of a number above zero"),
            ("ln", -1, "logarithm of a number above zero"),
            ("exp", 1000, "exponent is too big"),
            ("exp", float("nan"), "not a number I can show"),
            ("sin", 1, "I do not know the function"),
        ):
            with self.subTest(function=function, value=value):
                with self.assertRaises(ValueError) as caught:
                    Calculator.apply_function(function, value)
                self.assertIn(complaint, str(caught.exception))

    def test_how_a_function_reads_on_the_status_line(self):
        self.assertEqual(Calculator.write_function("exp", "2"), "e^2")
        self.assertEqual(Calculator.write_function("ln", "2"), "ln(2)")

    def test_a_number_too_big_to_show_is_refused(self):
        with self.assertRaises(ValueError):
            Calculator.format_number(10 ** 400)

    def test_typed_digits_become_a_number(self):
        self.assertEqual(Calculator.to_number("12"), 12.0)
        with self.assertRaises(ValueError):
            Calculator.to_number("")


class TestButtons(KeypadTestCase):
    def test_addition(self):
        self.press("1", "2", "+", "5", "=")
        self.assertEqual(self.display(), "17")
        self.assertEqual(self.status(), "12 + 5 = 17")

    def test_each_operator_once(self):
        for operator, left, right, expected in (
            ("-", "12", "5", 7),
            ("*", "12", "5", 60),
            ("/", "12", "5", 2.4),
            ("^", "2", "10", 1024),
            ("√", "9", "2", 3),
        ):
            with self.subTest(operator=operator):
                self.fresh()
                self.press(*(list(left) + [operator] + list(right) + ["="]))
                self.assertAlmostEqual(float(self.display()), expected)

    def test_division_keeps_a_hidden_decimal(self):
        self.press("1", "/", "3", "=")
        self.assertEqual(self.display(), "0.333333333333")

    def test_the_popup_shows_the_answer(self):
        self.press("1", "2", "+", "5", "=")
        self.assertEqual(Calculator.state.result_label.cget("text"), "Your result is: 17")

    def test_a_second_operator_finishes_the_first_calculation(self):
        self.press("2", "+", "3", "+", "4", "=")
        self.assertEqual(self.display(), "9")
        self.assertEqual(self.status(), "5 + 4 = 9")

    def test_an_operator_carries_the_answer_on(self):
        self.press("2", "+", "3", "+", "4", "=", "+", "7", "=")
        self.assertEqual(self.display(), "16")

    def test_a_digit_after_equals_starts_a_new_number(self):
        self.press("1", "2", "+", "5", "=", "7", "+", "6", "=")
        self.assertEqual(self.display(), "13")
        self.assertEqual(self.status(), "7 + 6 = 13")

    def test_reset_clears_everything(self):
        self.press("1", "2", "+")
        self.fresh()
        self.assertEqual(self.display(), "0")
        self.assertEqual(self.status(), "")
        self.assertIsNone(Calculator.state.first)
        self.assertIsNone(Calculator.state.operator)

    def test_the_result_popup_is_reused(self):
        self.press("1", "+", "1", "=")
        first_popup = Calculator.state.result_window
        self.press("Reset", "2", "+", "2", "=")
        self.assertIs(Calculator.state.result_window, first_popup)
        self.assertEqual(Calculator.state.result_label.cget("text"), "Your result is: 4")

    def test_about_opens_a_window(self):
        self.press("About")
        about = FakeToplevel.instances[-1]
        self.assertEqual(about.title_text, "About This App")
        labels = [widget.cget("text") for widget in FakeLabel.instances
                  if widget.master is about]
        self.assertEqual(labels, ["VER 4.0! Made by Sasha!",
                                 "Version 4: eˣ and ln, from issue #1."])


class TestTheFunctionButtons(KeypadTestCase):
    def test_the_natural_exponent_button(self):
        self.press("1", "eˣ")
        self.assertEqual(self.display(), "2.71828182846")
        self.assertEqual(self.status(), "e^1 = 2.71828182846")

    def test_the_natural_logarithm_button(self):
        self.press("1", "0", "ln")
        self.assertEqual(self.display(), "2.30258509299")
        self.assertEqual(self.status(), "ln(10) = 2.30258509299")

    def test_a_function_works_on_the_answer_on_show(self):
        self.press("9", "√", "2", "=")                  # 9 √ 2 = 3
        self.assertEqual(self.display(), "3")
        self.press("ln")
        self.assertEqual(self.status(), "ln(3) = 1.09861228867")

    def test_a_function_finishes_a_waiting_calculation(self):
        self.press("2", "+", "3", "ln")
        self.assertEqual(self.display(), "3.09861228867")
        self.assertEqual(self.status(), "2 + ln(3) = 3.09861228867")

    def test_the_answer_carries_on(self):
        self.press("2", "eˣ", "+", "1", "=")
        self.assertEqual(self.display(), "8.38905609893")

    def test_a_digit_after_a_function_starts_a_new_number(self):
        self.press("2", "eˣ", "7", "+", "1", "=")
        self.assertEqual(self.display(), "8")

    def test_the_two_functions_undo_each_other(self):
        self.press("5", "eˣ")
        self.assertNotEqual(self.display(), "5")
        self.press("ln")
        self.assertEqual(self.display(), "5")

    def test_a_function_before_a_number(self):
        self.press("eˣ")
        self.assertEqual(self.status(), "Type a number first.")

    def test_a_function_after_an_operator_with_no_number(self):
        self.press("2", "+", "ln")
        self.assertEqual(self.status(), "Type a number first.")


class TestBadInput(KeypadTestCase):
    """Wrong input must say something instead of raising."""

    def complain(self, *labels):
        self.fresh()
        try:
            self.press(*labels)
        except Exception as error:                      # noqa: BLE001 - the point of the test
            self.fail("pressing " + " ".join(labels) + " raised "
                      + type(error).__name__ + ": " + str(error))
        return self.status()

    def test_dividing_by_zero(self):
        self.assertEqual(self.complain("5", "/", "0", "="), "You cannot divide by zero.")

    def test_a_root_of_a_negative_number(self):
        self.assertEqual(self.complain("3", "-", "5", "=", "√", "2", "="),
                         "I cannot take a root of a negative number.")

    def test_a_root_of_order_zero(self):
        self.assertEqual(self.complain("8", "√", "0", "="), "A root cannot have the order zero.")

    def test_a_power_that_is_too_big(self):
        self.assertEqual(self.complain("9", "^", "9", "=", "^", "9", "=", "^", "9", "="),
                         "That power is too big to work out.")

    def test_equals_before_anything_is_typed(self):
        self.assertEqual(self.complain("="), "Type it like this:  12 + 5 =")

    def test_equals_without_an_operator(self):
        self.assertEqual(self.complain("5", "="), "Type it like this:  12 + 5 =")

    def test_an_operator_before_a_number(self):
        self.assertEqual(self.complain("+"), "Type a number first.")

    def test_the_logarithm_of_zero(self):
        self.assertEqual(self.complain("0", "ln"),
                         "I can only take the logarithm of a number above zero.")

    def test_the_logarithm_of_a_negative_number(self):
        self.assertEqual(self.complain("3", "-", "5", "=", "ln"),
                         "I can only take the logarithm of a number above zero.")

    def test_an_exponent_that_is_too_big(self):
        self.assertEqual(self.complain("9", "9", "9", "eˣ"),
                         "That exponent is too big to work out.")

    def test_a_refused_function_clears_the_calculation(self):
        self.press("0", "ln")
        self.assertIsNone(Calculator.state.first)
        self.assertEqual(Calculator.state.entry, "")

    def test_a_complaint_clears_the_half_finished_calculation(self):
        self.complain("5", "/", "0", "=")
        self.assertIsNone(Calculator.state.first)
        self.assertIsNone(Calculator.state.operator)
        self.assertEqual(Calculator.state.entry, "")

    def test_the_calculator_carries_on_after_a_complaint(self):
        self.press("5", "/", "0", "=", "4", "+", "2", "=")
        self.assertEqual(self.display(), "6")
        self.assertEqual(self.status(), "4 + 2 = 6")


class TestMissingTk(unittest.TestCase):
    def test_it_explains_how_to_install_tk(self):
        # `sys.modules['tkinter'] = None` makes `import tkinter` fail, which is
        # what happens on a machine without the Tcl/Tk libraries.
        program = (
            "import importlib.util, sys\n"
            "sys.modules['tkinter'] = None\n"
            "spec = importlib.util.spec_from_file_location('calculator_without_tk', "
            + repr(str(CALCULATOR_PY)) + ")\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
            "raise SystemExit(module.main())\n"
        )
        result = subprocess.run([sys.executable, "-c", program],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("Tk is not installed", result.stderr)
        self.assertIn("omarchy pkg add tk", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
