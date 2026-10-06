"""The real-window tests: Calculator.py on an actual Tk window.

Run them with:

    python3 -m unittest -v test_gui_smoke

These need Python's tkinter, the Tcl/Tk libraries and a display. When any of the
three is missing they skip themselves, so `python3 -m unittest discover` is safe
to run anywhere. On GitHub Actions they run under `xvfb-run`, which provides a
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
            self.assertEqual(len(buttons), 32, "the keypad is not complete")

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

            press("About")            # opens a real Toplevel with real Labels
            press("=")
            self.assertEqual(callback_errors, [], "a button raised inside Tk")

            root.destroy()
        finally:
            tkinter.Tk, tkinter.Toplevel = real_tk, real_toplevel

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
