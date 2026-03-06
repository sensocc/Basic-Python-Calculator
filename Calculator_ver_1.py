import tkinter as tk
from tkinter import ttk

num_one = 0
num_two = 0
result = 0

def update_display ():
    global num_one
    global num_two
    global result
    global display
    new_text = f'Your current first number: {num_one} | Your current second number: {num_two} | Your short result: {result}'
    display.config(text= new_text)

def num_reset ():
    global num_one
    global num_two
    global result
    num_one = 0
    num_two = 0
    result = 0
    update_display()

def on_num1button1_click():
    global num_one
    if not num_one:
        num_one += 1
    elif num_one:
        num_one = str(num_one)
        num_one += "1"
        num_one = int(num_one)
    update_display()

def on_num2button1_click():
    global num_two
    if not num_two:
        num_two += 1
    elif num_two:
        num_two = str(num_two)
        num_two += "1"
        num_two = int(num_two)
    update_display()

def on_num1button2_click():
    global num_one
    if not num_one:
        num_one += 2
    elif num_one:
        num_one = str(num_one)
        num_one += "2"
        num_one = int(num_one)
    update_display()

def on_num2button2_click():
    global num_two
    if not num_two:
        num_two += 2
    elif num_two:
        num_two = str(num_two)
        num_two += "2"
        num_two = int(num_two)
    update_display()

def on_num1button3_click():
    global num_one
    if not num_one:
        num_one += 3
    elif num_one:
        num_one = str(num_one)
        num_one += "3"
        num_one = int(num_one)
    update_display()

def on_num2button3_click():
    global num_two
    if not num_two:
        num_two += 3
    elif num_two:
        num_two = str(num_two)
        num_two += "3"
        num_two = int(num_two)
    update_display()

def on_num1button4_click():
    global num_one
    if not num_one:
        num_one += 4
    elif num_one:
        num_one = str(num_one)
        num_one += "4"
        num_one = int(num_one)
    update_display()

def on_num2button4_click():
    global num_two
    if not num_two:
        num_two += 4
    elif num_two:
        num_two = str(num_two)
        num_two += "4"
        num_two = int(num_two)
    update_display()

def on_num1button5_click():
    global num_one
    if not num_one:
        num_one += 5
    elif num_one:
        num_one = str(num_one)
        num_one += "5"
        num_one = int(num_one)
    update_display()

def on_num2button5_click():
    global num_two
    if not num_two:
        num_two += 5
    elif num_two:
        num_two = str(num_two)
        num_two += "5"
        num_two = int(num_two)
    update_display()

def on_num1button6_click():
    global num_one
    if not num_one:
        num_one += 6
    elif num_one:
        num_one = str(num_one)
        num_one += "6"
        num_one = int(num_one)
    update_display()

def on_num2button6_click():
    global num_two
    if not num_two:
        num_two += 6
    elif num_two:
        num_two = str(num_two)
        num_two += "6"
        num_two = int(num_two)
    update_display()

def on_num1button7_click():
    global num_one
    if not num_one:
        num_one += 7
    elif num_one:
        num_one = str(num_one)
        num_one += "7"
        num_one = int(num_one)
    update_display()

def on_num2button7_click():
    global num_two
    if not num_two:
        num_two += 7
    elif num_two:
        num_two = str(num_two)
        num_two += "7"
        num_two = int(num_two)
    update_display()

def on_num1button8_click():
    global num_one
    if not num_one:
        num_one += 8
    elif num_one:
        num_one = str(num_one)
        num_one += "8"
        num_one = int(num_one)
    update_display()

def on_num2button8_click():
    global num_two
    if not num_two:
        num_two += 8
    elif num_two:
        num_two = str(num_two)
        num_two += "8"
        num_two = int(num_two)
    update_display()

def on_num1button9_click():
    global num_one
    if not num_one:
        num_one += 9
    elif num_one:
        num_one = str(num_one)
        num_one += "9"
        num_one = int(num_one)
    update_display()

def on_num2button9_click():
    global num_two
    if not num_two:
        num_two += 9
    elif num_two:
        num_two = str(num_two)
        num_two += "9"
        num_two = int(num_two)
    update_display()

def on_num1button0_click():
    global num_one
    num_one = str(num_one)
    num_one += "0"
    num_one = int(num_one)
    update_display()

def on_num2button0_click():
    global num_two
    num_two = str(num_two)
    num_two += "0"
    num_two = int(num_two)
    update_display()

def on_addbutton_click():
    global num_one
    global num_two
    global result
    result = num_one + num_two
    update_display()

def on_substractbutton_click():
    global num_one
    global num_two
    global result
    result = num_one - num_two
    update_display()

def on_dividebutton_click():
    global num_one
    global num_two
    global result
    result = num_one / num_two
    update_display()

def on_multiplybutton_click():
    global num_one
    global num_two
    global result
    result = num_one * num_two
    update_display()

def on_powerbutton_click():
    global num_one
    global num_two
    global result
    result = num_one ** num_two
    update_display()

def on_rootbutton_click():
    global num_one
    global num_two
    global result
    result = num_one ** (1 / num_two)
    update_display()

root = tk.Tk()

def open_about_window():
    about_window = tk.Toplevel(root)
    about_window.title("About This App")
    label = tk.Label(about_window, text="My first GUI app! Made by Sasha!", padx=20, pady=20)
    label.pack()

def show_result():
    global result
    result_window = tk.Toplevel(root)
    result_window.title("The Calculation Result!")
    result_text = tk.Label(result_window, text="Your result is: " + str(result), padx=20, pady=20)
    result_text.pack()

root.title("My Fancy-Shmancy Calculator")

button_1_1 = tk.Button(root, text="1", padx=20, pady=20, command=on_num1button1_click)
button_1_2 = tk.Button(root, text="1", padx= 20, pady=20, command=on_num2button1_click)
button_2_1 = tk.Button(root, text="2", padx=20, pady=20, command=on_num1button2_click)
button_2_2 = tk.Button(root, text="2", padx= 20, pady=20, command=on_num2button2_click)
button_3_1 = tk.Button(root, text="3", padx=20, pady=20, command=on_num1button3_click)
button_3_2 = tk.Button(root, text="3", padx= 20, pady=20, command=on_num2button3_click)
button_4_1 = tk.Button(root, text="4", padx=20, pady=20, command=on_num1button4_click)
button_4_2 = tk.Button(root, text="4", padx= 20, pady=20, command=on_num2button4_click)
button_5_1 = tk.Button(root, text="5", padx=20, pady=20, command=on_num1button5_click)
button_5_2 = tk.Button(root, text="5", padx= 20, pady=20, command=on_num2button5_click)
button_6_1 = tk.Button(root, text="6", padx=20, pady=20, command=on_num1button6_click)
button_6_2 = tk.Button(root, text="6", padx= 20, pady=20, command=on_num2button6_click)
button_7_1 = tk.Button(root, text="7", padx=20, pady=20, command=on_num1button7_click)
button_7_2 = tk.Button(root, text="7", padx= 20, pady=20, command=on_num2button7_click)
button_8_1 = tk.Button(root, text="8", padx=20, pady=20, command=on_num1button8_click)
button_8_2 = tk.Button(root, text="8", padx= 20, pady=20, command=on_num2button8_click)
button_9_1 = tk.Button(root, text="9", padx=20, pady=20, command=on_num1button9_click)
button_9_2 = tk.Button(root, text="9", padx= 20, pady=20, command=on_num2button9_click)
button_0_1 = tk.Button(root, text="0", padx=20, pady=20, command=on_num1button0_click)
button_0_2 = tk.Button(root, text="0", padx= 20, pady=20, command=on_num2button0_click)
button_add = tk.Button(root, text="+", padx=20, pady=20, command=on_addbutton_click)
button_substract = tk.Button(root, text="-", padx=20, pady=20, command=on_substractbutton_click)
button_divide = tk.Button(root, text="/", padx=20, pady=20, command=on_dividebutton_click)
button_multiply = tk.Button(root, text="*", padx=20, pady=20, command=on_multiplybutton_click)
button_power = tk.Button(root, text="^", padx=20, pady=20, command=on_powerbutton_click)
button_root = tk.Button(root, text="√", padx=20, pady=20, command=on_rootbutton_click)
about_button = tk.Button(root, text="About", padx=20, pady=20, command=open_about_window)
equals_button = tk.Button(root, text='=', padx=20, pady=20, command=show_result)
reset_button = tk.Button(root, text = 'Reset', padx=20, pady=20, command=num_reset)

display = tk.Label(root, text="Your current first number is: " + str(num_one) + "| Your current second number is: " + str(num_two) + "| Your current shot result is: " + str(result), padx=20, pady=20)

display.grid(row=0, column=0, columnspan=4, sticky="ew", padx=10, pady=10)

about_button.grid(row=10, column=10)
button_1_1.grid(row=1, column=0)
button_1_2.grid(row=1, column= 10)
button_2_1.grid(row=1, column=1)
button_2_2.grid(row=1, column= 11)
button_3_1.grid(row=1, column=2)
button_3_2.grid(row=1, column= 12)
button_4_1.grid(row=2, column=0)
button_4_2.grid(row=2, column= 10)
button_5_1.grid(row=2, column=1)
button_5_2.grid(row=2, column= 11)
button_6_1.grid(row=2, column=2)
button_6_2.grid(row=2, column= 12)
button_7_1.grid(row=3, column=0)
button_7_2.grid(row=3, column= 10)
button_8_1.grid(row=3, column=1)
button_8_2.grid(row=3, column= 11)
button_9_1.grid(row=3, column=2)
button_9_2.grid(row=3, column= 12)
button_0_1.grid(row=4, column=1)
button_0_2.grid(row=4, column= 11)
button_add.grid(row=10, column=0)
button_substract.grid(row=10, column=1)
button_divide.grid(row=10, column=2)
button_multiply.grid(row=11, column=0)
button_power.grid(row=11, column=1)
button_root.grid(row=11, column=2)
equals_button.grid(row=12, column=1)
reset_button.grid(row=10, column=9)

root.mainloop()