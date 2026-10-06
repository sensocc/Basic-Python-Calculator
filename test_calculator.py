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
import types
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


# Every widget ever made, of whatever kind, so a window can be asked for its
# children the way Tk would be asked.
EVERY_WIDGET = []


class FakeWidget:
    instances = []

    def __init__(self, master=None, **options):
        self.master = master
        self.options = dict(options)
        self.command = options.get("command")
        self.grid_options = {}
        self.pack_options = {}
        self.destroyed = False
        self.instances.append(self)
        EVERY_WIDGET.append(self)

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
        return not self.destroyed

    def winfo_children(self):
        # destroyed children are gone, exactly as they would be in Tk
        return [widget for widget in EVERY_WIDGET
                if widget.master is self and not widget.destroyed]

    def destroy(self):
        self.destroyed = True

    def lift(self):
        pass


class FakeTk(FakeWidget):
    def __init__(self, *args, **options):
        super().__init__(None, **options)
        self.title_text = None
        self.bindings = {}

    def title(self, text):
        self.title_text = text

    def bind(self, sequence, handler):
        """Remember it, so a test can prove the window wired the keyboard up."""
        self.bindings[sequence] = handler

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
        EVERY_WIDGET.clear()
        Calculator.state.result_window = None
        Calculator.state.result_label = None
        Calculator.state.history_window = None
        self.root = Calculator.build_window()
        self.buttons = {widget.cget("text"): widget for widget in FakeButton.instances}
        # A new window is not a new calculator: the state has to be cleaned out too,
        # or one test carries a half-finished calculation into the next one.
        self.press("Reset")
        # The switch is a setting, so Reset deliberately leaves it alone - here it has
        # to be put back by hand, or one test's degrees leak into the next test. The
        # history outlives Reset as well: it is a record, and Clear is what empties it.
        Calculator.state.angle_mode = "deg"
        Calculator.state.history.clear()

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
    def test_there_are_thirty_four_buttons(self):
        self.assertEqual(len(Calculator.KEYPAD), 34)
        self.assertEqual(len(self.buttons), 34)

    def test_every_keypad_entry_has_a_button(self):
        for entry in Calculator.KEYPAD:
            self.assertIn(entry[0], self.buttons)

    def test_no_label_is_used_for_two_buttons(self):
        labels = [widget.cget("text") for widget in FakeButton.instances]
        self.assertEqual(len(labels), len(set(labels)))

    def test_the_buttons_are_in_the_conventional_places(self):
        for label, row, column in (("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("/", 2, 3),
                                   ("1", 4, 0),
                                   ("0", 5, 0), (".", 5, 1), ("±", 5, 2), ("+", 5, 3),
                                   ("√", 6, 0), ("ln", 6, 2), ("eˣ", 6, 3),
                                   ("log", 7, 0), ("sin", 7, 2), ("cos", 7, 3),
                                   ("tg", 8, 0), ("ctg", 8, 1), ("π", 8, 2), ("e", 8, 3),
                                   ("⌫", 9, 0), ("DEG", 9, 1), ("History", 9, 2),
                                   ("Reset", 10, 0), ("=", 10, 1), ("About", 10, 3)):
            options = self.buttons[label].grid_options
            self.assertEqual((options["row"], options["column"]), (row, column),
                             "button " + label)

    def test_the_buttons_use_four_columns_below_the_display(self):
        columns = sorted({widget.grid_options["column"] for widget in FakeButton.instances})
        rows = sorted({widget.grid_options["row"] for widget in FakeButton.instances})
        self.assertEqual(columns, [0, 1, 2, 3])
        self.assertEqual(rows, [2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_the_bottom_row_holds_the_whole_window_controls(self):
        for label, column in (("Reset", 0), ("=", 1), ("About", 3)):
            with self.subTest(button=label):
                options = self.buttons[label].grid_options
                self.assertEqual((options["row"], options["column"]), (10, column))

    def test_equals_is_a_wide_button_again(self):
        self.assertEqual(self.buttons["="].grid_options["columnspan"], 2)

    def test_the_status_line_sits_above_the_number(self):
        status = Calculator.state.status_label.grid_options
        display = Calculator.state.display_label.grid_options
        self.assertEqual(status["columnspan"], 4)
        self.assertEqual(display["columnspan"], 4)
        self.assertLess(status["row"], display["row"])

    def test_the_window_has_a_title(self):
        self.assertEqual(self.root.title_text, "My Fancy-Shmancy Calculator V10")


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
            (-0.0, "0"),
            (0.0, "0"),
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

    def test_the_common_logarithm(self):
        for value, expected in ((1, 0.0), (100, 2.0), (1000, 3.0), (0.1, -1.0), (2, math.log10(2))):
            with self.subTest(value=value):
                self.assertAlmostEqual(Calculator.apply_function("log10", value), expected)

    def test_percent(self):
        for value, expected in ((50, 0.5), (200, 2.0), (3, 0.03), (0, 0.0), (-25, -0.25)):
            with self.subTest(value=value):
                self.assertAlmostEqual(Calculator.apply_function("percent", value), expected)

    def test_the_trigonometry_in_degrees(self):
        for function, value, expected in (("sin", 30, 0.5), ("sin", 90, 1.0), ("sin", 0, 0.0),
                                          ("cos", 60, 0.5), ("cos", 0, 1.0),
                                          ("tg", 45, 1.0), ("tg", 0, 0.0),
                                          ("ctg", 45, 1.0), ("ctg", 45.0, 1.0)):
            with self.subTest(function=function, value=value):
                self.assertAlmostEqual(Calculator.apply_function(function, value), expected)

    def test_the_trigonometry_in_radians(self):
        for function, value, expected in (("sin", 0.5, math.sin(0.5)), ("cos", 0, 1.0),
                                          ("tg", 1, math.tan(1)),
                                          ("ctg", 1, math.cos(1) / math.sin(1))):
            with self.subTest(function=function, value=value):
                self.assertAlmostEqual(
                    Calculator.apply_function(function, value, "rad"), expected)

    def test_the_two_units_disagree(self):
        self.assertAlmostEqual(Calculator.apply_function("sin", 30, "deg"), 0.5)
        self.assertAlmostEqual(Calculator.apply_function("sin", 30, "rad"), math.sin(30))

    def test_answers_that_should_be_zero_are_shown_as_zero(self):
        # Python gives 6.1e-17 for cos 90° and -1.2e-16 for tan 180°
        for function, value in (("cos", 90), ("sin", 180), ("tg", 180), ("ctg", 90)):
            with self.subTest(function=function, value=value):
                self.assertEqual(Calculator.apply_function(function, value, "deg"), 0.0)

    def test_impossible_trigonometry_is_refused(self):
        for function, value, complaint in (("tg", 90, "tangent"),
                                           ("tg", 270, "tangent"),
                                           ("ctg", 0, "cotangent"),
                                           ("ctg", 180, "cotangent")):
            with self.subTest(function=function, value=value):
                with self.assertRaises(ValueError) as caught:
                    Calculator.apply_function(function, value, "deg")
                self.assertIn("cannot take the " + complaint, str(caught.exception))

    def test_the_exponent_and_the_logarithm_undo_each_other(self):
        for value in (0.5, 2, 99):
            with self.subTest(value=value):
                self.assertAlmostEqual(
                    Calculator.apply_function("ln", Calculator.apply_function("exp", value)), value)

    def test_impossible_functions_are_refused(self):
        for function, value, complaint in (
            ("ln", 0, "logarithm of a number above zero"),
            ("ln", -1, "logarithm of a number above zero"),
            ("log10", 0, "logarithm of a number above zero"),
            ("log10", -1, "logarithm of a number above zero"),
            ("exp", 1000, "exponent is too big"),
            ("exp", float("nan"), "not a number I can show"),
            ("sqrt", 1, "I do not know the function"),
        ):
            with self.subTest(function=function, value=value):
                with self.assertRaises(ValueError) as caught:
                    Calculator.apply_function(function, value)
                self.assertIn(complaint, str(caught.exception))

    def test_how_a_function_reads_on_the_status_line(self):
        self.assertEqual(Calculator.write_function("exp", "2"), "e^2")
        self.assertEqual(Calculator.write_function("ln", "2"), "ln(2)")
        self.assertEqual(Calculator.write_function("log10", "100"), "log(100)")
        self.assertEqual(Calculator.write_function("percent", "50"), "50%")
        self.assertEqual(Calculator.write_function("sin", "30"), "sin(30°)")
        self.assertEqual(Calculator.write_function("sin", "0.5", "rad"), "sin(0.5 rad)")

    def test_a_number_too_big_to_show_is_refused(self):
        with self.assertRaises(ValueError):
            Calculator.format_number(10 ** 400)

    def test_typed_digits_become_a_number(self):
        for typed, expected in (("12", 12.0), ("12.", 12.0), ("0.5", 0.5),
                                ("-5", -5.0), ("-0.5", -0.5), ("-0", -0.0)):
            with self.subTest(typed=typed):
                self.assertEqual(Calculator.to_number(typed), expected)
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
        self.assertEqual(labels, ["VER 10.0! Made by Sasha!",
                                 "Version 10: the calculation history, from issue #8."])


class TestTypingDecimalsAndSigns(KeypadTestCase):
    """The two buttons from issue #3."""

    def test_a_decimal_number(self):
        self.press("1", ".", "5")
        self.assertEqual(self.display(), "1.5")

    def test_a_decimal_point_on_its_own_starts_with_zero(self):
        self.press(".")
        self.assertEqual(self.display(), "0.")
        self.press("5")
        self.assertEqual(self.display(), "0.5")

    def test_a_second_decimal_point_is_ignored(self):
        self.press("1", ".", "2", ".", "3")
        self.assertEqual(self.display(), "1.23")

    def test_half_typed_decimals_still_add_up(self):
        self.press("1", "2", ".", "+", "5", "=")
        self.assertEqual(self.display(), "17")
        # the status line names the number it used, so a careless 12. reads as 12
        self.assertEqual(self.status(), "12 + 5 = 17")

    def test_a_decimal_point_after_an_answer_starts_a_new_number(self):
        self.press("1", "+", "1", "=")
        self.assertEqual(self.display(), "2")
        self.press(".")
        self.assertEqual(self.display(), "0.")

    def test_a_decimal_point_while_an_operator_waits(self):
        self.press("2", "+", ".", "5", "=")
        self.assertEqual(self.display(), "2.5")

    def test_the_sign_button(self):
        self.press("5", "±")
        self.assertEqual(self.display(), "-5")
        self.press("±")
        self.assertEqual(self.display(), "5")

    def test_typing_carries_on_after_the_sign_button(self):
        self.press("5", "±", "2")
        self.assertEqual(self.display(), "-52")

    def test_the_sign_button_works_on_an_answer(self):
        self.press("3", "-", "5", "=")
        self.assertEqual(self.display(), "-2")
        self.press("±")
        self.assertEqual(self.display(), "2")
        self.assertEqual(self.status(), "-(-2) = 2")

    def test_a_flipped_answer_carries_on(self):
        self.press("3", "-", "5", "=", "±", "+", "7", "=")
        self.assertEqual(self.display(), "9")

    def test_minus_zero_is_just_zero(self):
        self.press("0", "±")
        self.assertEqual(self.display(), "0")

    def test_a_decimal_point_and_a_sign_typed_together(self):
        self.press("0", ".", "5", "±")
        self.assertEqual(self.display(), "-0.5")

    def test_the_issue_3_example(self):
        self.press("1", "2", ".", "5", "±", "+", "0", ".", "5", "=")
        self.assertEqual(self.display(), "-12")
        self.assertEqual(self.status(), "-12.5 + 0.5 = -12")

    def test_the_sign_button_before_a_number(self):
        self.press("±")
        self.assertEqual(self.status(), "Type a number first.")

    def test_the_sign_button_after_an_operator_with_no_number(self):
        self.press("2", "+", "±")
        self.assertEqual(self.status(), "Type a number first.")


class TestTheHistory(KeypadTestCase):
    """The history window, from issue #8."""

    def texts(self):
        return [entry.text for entry in Calculator.state.history]

    def children_texts(self):
        return [widget.cget("text") for widget in Calculator.state.history_window.winfo_children()]

    def test_a_result_is_remembered(self):
        self.press("1", "2", "+", "5", "=")
        self.assertEqual(self.texts(), ["12 + 5 = 17"])
        self.assertEqual(Calculator.state.history[0].value, 17.0)

    def test_a_one_number_function_is_remembered(self):
        self.press("1", "0", "0", "log")
        self.assertEqual(self.texts(), ["log(100) = 2"])

    def test_a_function_finishing_a_calculation_is_remembered(self):
        self.press("2", "+", "3", "ln")
        self.assertEqual(self.texts(), ["2 + ln(3) = 3.09861228867"])

    def test_a_step_finished_by_a_second_operator_is_remembered(self):
        self.press("2", "+", "3", "+")
        self.assertEqual(self.texts()[:1], ["2 + 3 = 5"])

    def test_the_newest_calculation_comes_first(self):
        self.press("1", "0", "+", "5", "=")
        self.press("2", "+", "2", "=")
        self.press("6", "*", "7", "=")
        self.assertEqual(self.texts(), ["6 * 7 = 42", "2 + 2 = 4", "10 + 5 = 15"])

    def test_a_refused_calculation_is_not_remembered(self):
        self.press("5", "/", "0", "=")
        self.press("0", "ln")
        self.assertEqual(self.texts(), [])

    def test_putting_a_constant_on_show_is_not_a_calculation(self):
        self.press("π")
        self.assertEqual(self.texts(), [])

    def test_the_list_is_capped(self):
        for number in range(1, Calculator.HISTORY_LIMIT + 6):
            for digit in str(number):
                self.press(digit)
            self.press("+", "1", "=")
        self.assertEqual(len(Calculator.state.history), Calculator.HISTORY_LIMIT)
        self.assertEqual(self.texts()[0], "25 + 1 = 26")
        self.assertEqual(self.texts()[-1], "6 + 1 = 7")

    def test_reset_does_not_empty_the_history(self):
        self.press("1", "+", "1", "=")
        self.fresh()
        self.assertEqual(self.texts(), ["1 + 1 = 2"])

    def test_the_window_opens_and_lists_what_has_been_worked_out(self):
        self.press("1", "+", "1", "=")
        self.press("History")
        self.assertEqual(Calculator.state.history_window.title_text, "The Calculation History!")
        self.assertEqual(self.children_texts(), ["1. 1 + 1 = 2", "Clear"])

    def test_an_empty_history_says_so(self):
        self.press("History")
        self.assertEqual(self.children_texts(),
                         ["Nothing has been worked out yet.", "Clear"])

    def test_picking_an_entry_brings_its_answer_back(self):
        self.press("1", "0", "+", "5", "=")
        self.fresh()
        self.press("History")
        entry = [widget for widget in Calculator.state.history_window.winfo_children()
                 if widget.cget("text") == "1. 10 + 5 = 15"][0]
        entry.command()
        self.assertEqual(self.display(), "15")
        self.press("*", "2", "=")
        self.assertEqual(self.display(), "30")

    def test_the_window_is_reused_rather_than_stacked(self):
        self.press("History")
        first = Calculator.state.history_window
        self.press("Reset", "1", "+", "1", "=", "History")
        self.assertIs(Calculator.state.history_window, first)
        self.assertEqual(self.children_texts(), ["1. 1 + 1 = 2", "Clear"])

    def test_clear_empties_the_list_and_the_window(self):
        self.press("1", "+", "1", "=", "History")
        clear = [widget for widget in Calculator.state.history_window.winfo_children()
                 if widget.cget("text") == "Clear"][0]
        clear.command()
        self.assertEqual(Calculator.state.history, [])
        self.assertEqual(self.children_texts(),
                         ["Nothing has been worked out yet.", "Clear"])


class TestTheBackspaceButton(KeypadTestCase):
    """⌫, the Small half of issue #7."""

    def test_it_takes_the_last_character_off(self):
        self.press("1", "2", "3", "⌫")
        self.assertEqual(self.display(), "12")

    def test_it_can_empty_the_number_being_typed(self):
        self.press("7", "⌫")
        self.assertEqual(self.display(), "0")
        self.assertEqual(Calculator.state.entry, "")

    def test_it_takes_a_decimal_point_off(self):
        self.press("1", ".", "⌫")
        self.assertEqual(self.display(), "1")

    def test_it_never_leaves_a_lone_minus_sign(self):
        self.press("5", "±", "⌫")
        self.assertEqual(Calculator.state.entry, "")
        self.press("+")                      # and the operator does not blow up
        self.assertEqual(self.status(), "Type a number first.")

    def test_it_leaves_a_waiting_calculation_alone(self):
        self.press("2", "+", "1", "⌫")
        self.assertEqual(self.display(), "2")
        self.assertEqual(self.status(), "2 +")

    def test_with_nothing_typed_it_clears_the_message(self):
        self.press("1", "+", "1", "=")
        self.assertEqual(self.status(), "1 + 1 = 2")
        self.press("⌫")
        self.assertEqual(self.status(), "")
        self.assertEqual(self.display(), "2")        # the answer is left alone

    def test_it_clears_a_refusal(self):
        self.press("5", "/", "0", "=")
        self.assertEqual(self.status(), "You cannot divide by zero.")
        self.press("⌫")
        self.assertEqual(self.status(), "")


class TestTheKeyboard(KeypadTestCase):
    """The Middle half of issue #7: the keys do what the buttons do."""

    def press_key(self, keysym, char=""):
        """A key press as Tk would deliver it."""
        return Calculator.on_key(types.SimpleNamespace(keysym=keysym, char=char))

    def test_the_map_holds_the_keys_the_issue_asks_for(self):
        keys = Calculator.state.keys
        for name in list("0123456789") + list("+-*/^") + [".", "%", "=", "Return",
                                                         "Escape", "BackSpace"]:
            with self.subTest(key=name):
                self.assertIn(name, keys)
        for name in ("KP_7", "KP_Decimal", "KP_Add", "KP_Enter"):
            with self.subTest(key=name):
                self.assertIn(name, keys)

    def test_typing_numbers_and_operators(self):
        for key in "1", "2", "+", "5":
            self.press_key(key, key)
        self.assertEqual(self.display(), "5")
        self.assertEqual(self.status(), "12 +")
        self.press_key("Return")
        self.assertEqual(self.display(), "17")

    def test_enter_and_equals_are_the_same_key(self):
        self.press_key("1", "1")
        self.press_key("+", "+")
        self.press_key("2", "2")
        self.press_key("=", "=")
        self.assertEqual(self.display(), "3")
        self.press_key("Escape")
        self.assertEqual(self.display(), "0")

    def test_the_star_key_is_named_asterisk_by_tk(self):
        self.press_key("2", "2")
        self.press_key("asterisk", "*")           # Tk's name for the * key
        self.press_key("3", "3")
        self.press_key("equal", "=")
        self.assertEqual(self.display(), "6")

    def test_the_keyboard_can_type_a_decimal_point_and_a_percent(self):
        self.press_key("period", ".")
        self.press_key("5", "5")
        self.assertEqual(self.display(), "0.5")
        self.press_key("percent", "%")
        self.assertEqual(self.display(), "0.005")

    def test_the_numeric_keypad_works(self):
        self.press_key("KP_7")
        self.press_key("KP_Add")
        self.press_key("KP_3")
        self.press_key("KP_Enter")
        self.assertEqual(self.display(), "10")

    def test_backspace_is_the_backspace_button(self):
        self.press_key("1", "1")
        self.press_key("2", "2")
        self.press_key("BackSpace")
        self.assertEqual(self.display(), "1")

    def test_a_key_that_is_not_wired_up_does_nothing(self):
        self.press_key("4", "4")
        for keysym, char in (("F5", ""), ("z", "z"), ("space", " "), ("Up", "")):
            with self.subTest(keysym=keysym):
                self.assertIsNone(self.press_key(keysym, char))
                self.assertEqual(self.display(), "4")

    def test_the_window_binds_the_keyboard(self):
        self.assertIn("<Key>", self.root.bindings)
        event = types.SimpleNamespace(keysym="7", char="7")
        self.assertEqual(self.root.bindings["<Key>"](event), "break")
        self.assertEqual(self.display(), "7")

    def test_a_handled_key_stops_tk_from_handling_it_twice(self):
        # returning "break" keeps a focused button from acting on the same key
        self.assertEqual(self.press_key("5", "5"), "break")
        self.assertIsNone(self.press_key("z", "z"))


class TestTheConstantButtons(KeypadTestCase):
    """π and e, from issue #6."""

    def test_pi(self):
        self.press("π")
        self.assertEqual(self.display(), "3.14159265359")
        self.assertEqual(self.status(), "π")

    def test_e(self):
        self.press("e")
        self.assertEqual(self.display(), "2.71828182846")
        self.assertEqual(self.status(), "e")

    def test_the_issue_6_example(self):
        self.press("π", "*", "2", "=")
        self.assertEqual(self.display(), "6.28318530718")

    def test_a_constant_in_a_calculation(self):
        self.press("e", "+", "1", "=")
        self.assertEqual(self.display(), "3.71828182846")

    def test_a_digit_after_a_constant_starts_a_new_number(self):
        self.press("π", "7")
        self.assertEqual(self.display(), "7")
        self.assertEqual(self.status(), "")

    def test_a_decimal_point_after_a_constant_starts_a_new_number(self):
        self.press("π", ".")
        self.assertEqual(self.display(), "0.")

    def test_a_constant_finishes_a_waiting_calculation(self):
        self.press("2", "+", "π")
        self.assertEqual(self.display(), "5.14159265359")
        self.assertEqual(self.status(), "2 + π = 5.14159265359")

    def test_a_constant_takes_the_place_of_a_half_typed_number(self):
        self.press("1", "2", "+", "5", "π")
        self.assertEqual(self.display(), "15.1415926536")
        self.assertEqual(self.status(), "12 + π = 15.1415926536")

    def test_the_sign_button_flips_a_constant(self):
        self.press("π", "±")
        self.assertEqual(self.display(), "-3.14159265359")

    def test_a_constant_can_be_fed_to_a_function(self):
        self.press("e", "ln")
        self.assertEqual(self.display(), "1")
        self.assertEqual(self.status(), "ln(2.71828182846) = 1")

    def test_the_operators_can_carry_on_from_a_constant(self):
        self.press("e", "+", "e", "=")
        self.assertEqual(self.display(), "5.43656365692")


class TestTheAngleButtons(KeypadTestCase):
    """sin, cos, tg, ctg and the DEG/RAD switch, from issue #5."""

    def test_sine_in_degrees(self):
        self.press("3", "0", "sin")
        self.assertEqual(self.display(), "0.5")
        self.assertEqual(self.status(), "sin(30°) = 0.5")

    def test_the_other_three_in_degrees(self):
        for label, keys, expected in (("cos", ("6", "0"), "0.5"),
                                      ("tg", ("4", "5"), "1"),
                                      ("ctg", ("4", "5"), "1")):
            with self.subTest(button=label):
                self.fresh()
                self.press(*keys, label)
                self.assertEqual(self.display(), expected)

    def test_a_right_angle_cosine_is_zero(self):
        self.press("9", "0", "cos")
        self.assertEqual(self.display(), "0")

    def test_the_switch_changes_the_answer(self):
        self.press("3", "0", "sin")
        self.assertEqual(self.display(), "0.5")
        self.press("DEG")                       # the same button flips back and forth
        self.assertEqual(self.display(), "0.5")
        self.assertEqual(self.status(), "Angles in radians")
        self.press("3", "0", "sin")
        self.assertEqual(self.display(), "-0.988031624093")
        self.assertEqual(self.status(), "sin(30 rad) = -0.988031624093")

    def test_the_switch_renames_itself(self):
        self.assertEqual(self.buttons["DEG"].cget("text"), "DEG")
        self.press("DEG")
        self.assertEqual(self.buttons["DEG"].cget("text"), "RAD")
        self.assertEqual(self.status(), "Angles in radians")
        self.press("DEG")
        self.assertEqual(self.buttons["DEG"].cget("text"), "DEG")
        self.assertEqual(self.status(), "Angles in degrees")

    def test_the_switch_keeps_the_number_being_typed(self):
        self.press("3", "0", "DEG")
        self.assertEqual(self.display(), "30")
        self.press("sin")
        self.assertEqual(self.display(), "-0.988031624093")

    def test_reset_leaves_the_switch_alone(self):
        self.press("DEG")
        self.fresh()
        self.assertEqual(self.buttons["DEG"].cget("text"), "RAD")
        self.press("3", "0", "sin")
        self.assertEqual(self.display(), "-0.988031624093")

    def test_the_angle_buttons_still_finish_a_calculation(self):
        self.press("2", "+", "3", "0", "sin")
        self.assertEqual(self.display(), "2.5")
        self.assertEqual(self.status(), "2 + sin(30°) = 2.5")

    def test_the_issue_5_example(self):
        self.press("3", "0", "sin")
        self.assertEqual(self.display(), "0.5")
        self.press("DEG")
        self.press("3", "0", "sin")
        self.assertEqual(self.display(), "-0.988031624093")


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

    def test_the_common_logarithm_button(self):
        self.press("1", "0", "0", "log")
        self.assertEqual(self.display(), "2")
        self.assertEqual(self.status(), "log(100) = 2")

    def test_the_percent_button(self):
        self.press("5", "0", "%")
        self.assertEqual(self.display(), "0.5")
        self.assertEqual(self.status(), "50% = 0.5")

    def test_percent_of_an_answer(self):
        self.press("1", "+", "1", "=")
        self.assertEqual(self.display(), "2")
        self.press("%")
        self.assertEqual(self.display(), "0.02")

    def test_a_logarithm_finishes_a_waiting_calculation(self):
        self.press("2", "+", "1", "0", "0", "log")
        self.assertEqual(self.display(), "4")
        self.assertEqual(self.status(), "2 + log(100) = 4")

    def test_percent_carries_on_into_a_calculation(self):
        self.press("5", "0", "%", "+", "1", "=")
        self.assertEqual(self.display(), "1.5")

    def test_the_issue_4_example(self):
        self.press("1", "0", "0", "log", "+", "1", "=")
        self.assertEqual(self.display(), "3")

    def test_a_decimal_logarithm(self):
        self.press("0", ".", "1", "log")
        self.assertEqual(self.display(), "-1")

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
        self.assertEqual(self.complain("0", "log"),
                         "I can only take the logarithm of a number above zero.")

    def test_the_common_logarithm_of_a_negative_number(self):
        self.assertEqual(self.complain("3", "-", "5", "=", "log"),
                         "I can only take the logarithm of a number above zero.")

    def test_the_logarithm_of_a_negative_number(self):
        self.assertEqual(self.complain("3", "-", "5", "=", "ln"),
                         "I can only take the logarithm of a number above zero.")

    def test_an_exponent_that_is_too_big(self):
        self.assertEqual(self.complain("9", "9", "9", "eˣ"),
                         "That exponent is too big to work out.")

    def test_a_negative_number_cannot_be_given_a_logarithm(self):
        self.assertEqual(self.complain("4", "±", "ln"),
                         "I can only take the logarithm of a number above zero.")

    def test_a_negative_number_can_be_given_an_exponent(self):
        self.press("1", "±", "eˣ")
        self.assertEqual(self.display(), "0.367879441171")

    def test_the_tangent_of_a_right_angle(self):
        self.assertEqual(self.complain("9", "0", "tg"),
                         "I cannot take the tangent of that angle.")

    def test_the_cotangent_of_zero(self):
        self.assertEqual(self.complain("0", "ctg"),
                         "I cannot take the cotangent of that angle.")

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
