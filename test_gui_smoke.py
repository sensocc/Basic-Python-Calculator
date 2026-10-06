"""The real-window tests: Calculator.py on an actual Tk window.

Run them with:

    python3 -m unittest -v test_gui_smoke

These need Python's tkinter, the Tcl/Tk libraries and a display. When any of the
three is missing they skip themselves, so `python3 -m unittest discover` is safe
to run anywhere.

One test maps its window for a moment: Tk only delivers key events to a window
that is mapped and focused, so a withdrawn one silently receives nothing. On GitHub Actions they run under `xvfb-run`, which provides a
display; on your own machine without a desktop session the same works:

    xvfb-run -a python3 -m unittest -v test_gui_smoke

test_calculator.py checks the work the same way without a window at all.
"""

import importlib.util
import subprocess
import sys
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CALCULATOR_PY = HERE / "Calculator.py"

try:
    import tkinter
except (ImportError, OSError) as error:      # no tkinter, or no Tcl/Tk libraries
    tkinter = None
    TKINTER_ERROR = error


def load_calculator():
    """Import Calculator.py again, so it binds to the real tkinter.

    A name of its own, so this file never shares a module with test_calculator.py,
    which loads Calculator.py with a stand-in for tkinter.
    """
    spec = importlib.util.spec_from_file_location("calculator_on_a_real_window", CALCULATOR_PY)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(tkinter, "tkinter is not available on this machine")
class TestRealWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            probe = tkinter.Tk()
        except tkinter.TclError as error:
            raise unittest.SkipTest("there is no display to open a window on: " + str(error))
        probe.destroy()

    def test_the_buttons_work_on_a_real_window(self):
        """Real Tk widgets, real clicks. This is what catches a bad widget option."""
        real_tk, real_toplevel, real_button = tkinter.Tk, tkinter.Toplevel, tkinter.Button
        callback_errors = []

        class HiddenTk(real_tk):
            """Withdrawn, so the test cannot flash a window on your screen."""

            def __init__(self, *args, **options):
                super().__init__(*args, **options)
                self.withdraw()
                self.report_callback_exception = lambda *info: callback_errors.append(
                    info[0].__name__ + ": " + str(info[1])
                )

        class HiddenToplevel(real_toplevel):
            def __init__(self, *args, **options):
                super().__init__(*args, **options)
                self.withdraw()

        tkinter.Tk, tkinter.Toplevel = HiddenTk, HiddenToplevel
        try:
            calculator = load_calculator()
            root = calculator.build_window()
            root.update_idletasks()
            buttons = {widget.cget("text"): widget
                       for widget in root.winfo_children()
                       if isinstance(widget, real_button)}
            self.assertEqual(len(buttons), 35, "the keypad is not complete")

            def press(*labels):
                for label in labels:
                    buttons[label].invoke()

            press("1", "2", "+", "5", "=")
            self.assertEqual(calculator.state.display_label.cget("text"), "17")
            self.assertEqual(calculator.state.status_label.cget("text"), "12 + 5 = 17")

            press("Reset", "1", "/", "3", "=")
            self.assertEqual(calculator.state.display_label.cget("text"), "0.333333333333")

            press("Reset", "5", "/", "0", "=")
            self.assertEqual(calculator.state.status_label.cget("text"),
                             "You cannot divide by zero.")

            press("4", "+", "2", "=")
            self.assertEqual(calculator.state.display_label.cget("text"), "6")

            press("Reset", "1", "0", "ln")            # the two buttons from issue #1
            self.assertEqual(calculator.state.display_label.cget("text"), "2.30258509299")
            press("Reset", "1", "eˣ")
            self.assertEqual(calculator.state.display_label.cget("text"), "2.71828182846")

            press("Reset", "1", ".", "5", "±")         # the two buttons from issue #3
            self.assertEqual(calculator.state.display_label.cget("text"), "-1.5")

            press("Reset", "1", "0", "0", "log")       # and the two from issue #4
            self.assertEqual(calculator.state.display_label.cget("text"), "2")
            press("Reset", "5", "0", "%")
            self.assertEqual(calculator.state.display_label.cget("text"), "0.5")

            press("Reset", "3", "0", "sin")            # and issue #5's trigonometry
            self.assertEqual(calculator.state.display_label.cget("text"), "0.5")
            press("DEG")                               # the switch is a real button
            press("Reset", "3", "0", "sin")
            self.assertEqual(calculator.state.display_label.cget("text"), "-0.988031624093")
            self.assertEqual(calculator.state.angle_button.cget("text"), "RAD")

            press("DEG")                               # back to degrees for the rest
            press("Reset", "π")                        # the two constants from issue #6
            self.assertEqual(calculator.state.display_label.cget("text"), "3.14159265359")
            press("Reset", "2", "+", "e")
            self.assertEqual(calculator.state.display_label.cget("text"), "4.71828182846")

            press("Reset", "1", "2", "3", "⌫")        # the backspace from issue #7
            self.assertEqual(calculator.state.display_label.cget("text"), "12")

            press("Reset", "1", "0", "+", "5", "=")    # the history from issue #8
            press("History")
            history = calculator.state.history_window
            self.assertEqual(history.title(), "The Calculation History!")
            listed = [widget.cget("text") for widget in history.winfo_children()
                      if isinstance(widget, real_button)]
            self.assertEqual(listed[0], "1. 10 + 5 = 15")   # newest first
            self.assertEqual(listed[-1], "Clear")           # everything else filed above it

            listed_widgets = [widget for widget in history.winfo_children()
                              if isinstance(widget, real_button)]
            listed_widgets[0].invoke()                 # pick the answer back up
            self.assertEqual(calculator.state.display_label.cget("text"), "15")
            history.destroy()

            press("About")            # opens a real Toplevel with real Labels
            press("=")
            self.assertEqual(callback_errors, [], "a button raised inside Tk")

            root.destroy()
        finally:
            tkinter.Tk, tkinter.Toplevel = real_tk, real_toplevel

    def test_the_themes_work_on_a_real_window(self):
        """Real colours on real widgets, including a window that is already open."""
        real_tk, real_toplevel, real_button = tkinter.Tk, tkinter.Toplevel, tkinter.Button
        callback_errors = []

        class HiddenTk(real_tk):
            def __init__(self, *args, **options):
                super().__init__(*args, **options)
                self.withdraw()
                self.report_callback_exception = lambda *info: callback_errors.append(
                    info[0].__name__ + ": " + str(info[1]))

        class HiddenToplevel(real_toplevel):
            def __init__(self, *args, **options):
                super().__init__(*args, **options)
                self.withdraw()

        tkinter.Tk, tkinter.Toplevel = HiddenTk, HiddenToplevel
        try:
            calculator = load_calculator()
            root = calculator.build_window()
            root.update_idletasks()
            buttons = {widget.cget("text"): widget
                       for widget in root.winfo_children()
                       if isinstance(widget, real_button)}
            self.assertEqual(len(buttons), 35)

            # the font is one this machine really has, and it can draw the keypad
            family = calculator.state.font_family
            self.assertIn(family, set(tkinter.font.families()))
            self.assertTrue(calculator.can_draw(family), "the chosen font lacks a keypad glyph")

            self.assertEqual(root.cget("background"), "black")
            self.assertEqual(buttons["7"].cget("background"), "black")

            buttons["About"].invoke()                      # a window left open
            about = [widget for widget in root.winfo_children()
                     if isinstance(widget, real_toplevel)][-1]
            about_label = about.winfo_children()[0]

            buttons["Theme"].invoke()                      # Terminal -> Light
            root.update_idletasks()
            self.assertEqual(calculator.state.theme, "Light")
            self.assertEqual(root.cget("background"), "#f2f3f5")
            self.assertEqual(buttons["7"].cget("background"), "#e4e7eb")
            self.assertEqual(buttons["7"].cget("activebackground"), "#cbd2da")
            self.assertEqual(calculator.state.display_label.cget("background"), "#ffffff")
            self.assertEqual(about_label.cget("background"), "#f2f3f5",
                             "the window that was already open did not follow the theme")

            self.assertTrue(root.cget("menu"), "there is no menu bar")
            self.assertEqual(callback_errors, [])
            root.destroy()
        finally:
            tkinter.Tk, tkinter.Toplevel = real_tk, real_toplevel

    def test_the_keyboard_works_on_a_real_window(self):
        """Real key events, which is the part of issue #7 that fails silently.

        Tk hands key events to the focused window, and a withdrawn window cannot
        be focused: generating them there does nothing at all, with no error. So
        this test shows the window for the moment it takes to type, which is the
        only way to prove the binding really works.
        """
        calculator = load_calculator()
        root = calculator.build_window()
        try:
            root.deiconify()
            root.update()
            root.focus_force()
            root.update()

            def type_key(keysym):
                root.event_generate("<KeyPress>", keysym=keysym)
                root.update()

            for keysym in ("1", "2", "plus", "5"):     # 12 + 5, typed
                type_key(keysym)
            type_key("Return")
            self.assertEqual(calculator.state.display_label.cget("text"), "17")
            self.assertEqual(calculator.state.status_label.cget("text"), "12 + 5 = 17")

            type_key("Escape")
            self.assertEqual(calculator.state.display_label.cget("text"), "0")

            type_key("asterisk")                       # Tk's name for the * key
            self.assertEqual(calculator.state.status_label.cget("text"), "Type a number first.")

            for keysym in ("7", "8", "BackSpace"):     # the ⌫ key
                type_key(keysym)
            self.assertEqual(calculator.state.display_label.cget("text"), "7")

            type_key("F5")                             # not wired up: does nothing
            self.assertEqual(calculator.state.display_label.cget("text"), "7")
        finally:
            root.destroy()

    def test_the_app_starts_and_keeps_its_window_open(self):
        """Run Calculator.py the way a person would, and see that it stays up."""
        process = subprocess.Popen([sys.executable, str(CALCULATOR_PY)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 3
            while time.monotonic() < deadline and process.poll() is None:
                time.sleep(0.25)
            stayed_open = process.poll() is None
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                # communicate() also closes the pipes, so no ResourceWarning
                output = (process.communicate(timeout=10)[1] or "").strip()
            except subprocess.TimeoutExpired:
                process.kill()
                output = (process.communicate()[1] or "").strip()

        if stayed_open:
            return                                      # the window is up and the event loop running
        self.assertNotIn("Traceback", output)
        if "Tk is not installed" in output or "could not open a window" in output:
            self.skipTest("no window could be opened here: " + (output or "no output").splitlines()[0])
        self.fail("the calculator exited on its own: " + repr(output))


if __name__ == "__main__":
    unittest.main(verbosity=2)
