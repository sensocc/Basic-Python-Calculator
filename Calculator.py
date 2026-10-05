import tkinter as tk
from tkinter import ttk

num_one = ''
num_two = ''
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
    num_one = ''
    num_two = ''
    result = 0
    update_display()

def num_1_update(digit1):
    global num_one
    if not num_one:
        num_one = str(digit1)
    elif num_one and digit1:
        num_one += str(digit1)
    update_display()

def num_2_update(digit2):
    global num_two
    if not num_two:
        num_two = str(digit2)
    elif num_two and digit2:
        num_two += str(digit2)
    update_display()

def op_button_click(op):
    global num_one
    global num_two
    global result
    if op == '√':
        result = float(num_one) ** (1 / float(num_two))
    elif op == '+':
        result = float(num_one) + float(num_two)
    elif op == '-':
        result = float(num_one) - float(num_two)
    elif op == '/':
        result = float(num_one) / float(num_two)
    elif op == '*':
        result = float(num_one) * float(num_two)
    elif op == '^':
        result = float(num_one) ** float(num_two)
    update_display()

root = tk.Tk()

def open_about_window():
    about_window = tk.Toplevel(root)
    about_window.title("About This App")
    about_window.configure(bg='black')
    label = tk.Label(about_window, text="VER 2.0! Made by Sasha!", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2')
    label.pack()

def show_result():
    global result
    result_window = tk.Toplevel(root)
    result_window.title("The Calculation Result!")
    result_window.configure(bg='black')
    result_text = tk.Label(result_window, text="Your result is: " + str(result), padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2')
    result_text.pack()

root.title("My Fancy-Shmancy Calculator V2")
root.configure(bg='black')

button_1_1 = tk.Button(root, text="1", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_1_update(1))
button_1_2 = tk.Button(root, text="1", padx= 20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_2_update(1))
button_2_1 = tk.Button(root, text="2", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_1_update(2))
button_2_2 = tk.Button(root, text="2", padx= 20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_2_update(2))
button_3_1 = tk.Button(root, text="3", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_1_update(3))
button_3_2 = tk.Button(root, text="3", padx= 20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_2_update(3))
button_4_1 = tk.Button(root, text="4", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_1_update(4))
button_4_2 = tk.Button(root, text="4", padx= 20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_2_update(4))
button_5_1 = tk.Button(root, text="5", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_1_update(5))
button_5_2 = tk.Button(root, text="5", padx= 20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_2_update(5))
button_6_1 = tk.Button(root, text="6", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_1_update(6))
button_6_2 = tk.Button(root, text="6", padx= 20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_2_update(6))
button_7_1 = tk.Button(root, text="7", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_1_update(7))
button_7_2 = tk.Button(root, text="7", padx= 20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_2_update(7))
button_8_1 = tk.Button(root, text="8", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_1_update(8))
button_8_2 = tk.Button(root, text="8", padx= 20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_2_update(8))
button_9_1 = tk.Button(root, text="9", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_1_update(9))
button_9_2 = tk.Button(root, text="9", padx= 20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_2_update(9))
button_0_1 = tk.Button(root, text="0", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_1_update(0))
button_0_2 = tk.Button(root, text="0", padx= 20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:num_2_update(0))
button_add = tk.Button(root, text="+", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:op_button_click('+'))
button_substract = tk.Button(root, text="-", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:op_button_click('-'))
button_divide = tk.Button(root, text="/", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:op_button_click('/'))
button_multiply = tk.Button(root, text="*", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:op_button_click('*'))
button_power = tk.Button(root, text="^", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:op_button_click('^'))
button_root = tk.Button(root, text="√", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=lambda:op_button_click('√'))
about_button = tk.Button(root, text="About", padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=open_about_window)
equals_button = tk.Button(root, text='=', padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2', command=show_result)
reset_button = tk.Button(root, text = 'Reset', padx=20, font=('Arial', 18), bg='black', fg='SpringGreen2', pady=20, command=num_reset)

display = tk.Label(root, text="Your current first number is: " + str(num_one) + "| Your current second number is: " + str(num_two) + "| Your current shot result is: " + str(result), padx=20, pady=20, font=('Arial', 18), bg='black', fg='SpringGreen2')

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