import customtkinter as ctk
from functools import partial
import csv
import logging
import os

logging.basicConfig(
    filename="balances.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

root = ctk.CTk()
root.geometry("400x300")
root.title("Balances")

# name -> (balance, deps, wds)
balances: dict[str, tuple[float, float, float]] = {}


def read_balances():
    if not os.path.exists("balances.csv"):
        logging.warning("No file 'balances.csv' found")
        return

    with open("balances.csv", "r", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # header überspringen

        for line in reader:
            usr = line[0]
            balance = float(line[1]) if line[1] else 0.0
            deps = float(line[2]) if line[2] else 0.0
            wds = float(line[3]) if line[3] else 0.0

            balances[usr] = (balance, deps, wds)
            
def update_balance_window():

    new_win = ctk.CTkToplevel(root)
    new_win.geometry("300x400")
    new_win.title("Change Balance")

    new_win.transient(root)
    new_win.grab_set()
    new_win.focus_force()
    
    def change_usr_balance(usr):
        change_balance_win = ctk.CTkToplevel(new_win)
        change_balance_win.geometry("300x300")
        change_balance_win.title(f"Change Balance for {usr}")
        

    label = ctk.CTkLabel(new_win, text="Person:")
    label.pack(pady=10)
    
    for i, person in enumerate(balances.keys()):
        usr_button = ctk.CTkButton(new_win, text=person, command=partial(change_usr_balance, person))
        usr_button.pack(pady=5)
    



def save_balances():
    with open("balances.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "balance", "deps", "wds"])

        for name, (balance, deps, wds) in balances.items():
            writer.writerow([name, balance, deps, wds])


def set_usr_win():
    def set_usr():
        name = name_input.get().strip()

        if not name:
            return

        if name in balances:
            del balances[name]
            new_win.destroy()

        else:
            balances[name] = (0.0, 0.0, 0.0)
            new_win.destroy()

    new_win = ctk.CTkToplevel(root)
    new_win.geometry("300x200")
    new_win.title("Set Person")

    new_win.transient(root)
    new_win.grab_set()
    new_win.focus_force()

    label = ctk.CTkLabel(new_win, text="Add / Remove Person")
    name_input = ctk.CTkEntry(new_win, placeholder_text="Name")
    submit_btn = ctk.CTkButton(new_win, text="Submit", command=set_usr)

    label.pack(pady=20)
    name_input.pack(pady=10)
    submit_btn.pack(pady=20)

    name_input.focus()


def show_table():
    new_win = ctk.CTkToplevel(root)
    new_win.geometry("500x300")
    new_win.title("Balances")

    new_win.transient(root)
    new_win.grab_set()
    new_win.focus_force()

    headers = ["Name", "Saldo", "Schuldet mir", "Schulde ich"]

    for col, text in enumerate(headers):
        lbl = ctk.CTkLabel(new_win, text=text, font=("Arial", 14, "bold"))
        lbl.grid(row=0, column=col, padx=10, pady=5)

    for row, (name, values) in enumerate(balances.items(), start=1):
        ctk.CTkLabel(new_win, text=name).grid(
            row=row, column=0, padx=10, pady=5
        )

        for col, value in enumerate(values, start=1):
            ctk.CTkLabel(new_win, text=f"{value:.2f}").grid(
                row=row, column=col, padx=10, pady=5
            )


def on_close():
    save_balances()
    root.destroy()


# Buttons
add_usr_btn = ctk.CTkButton(root, text="Add / Remove Person", command=set_usr_win)
add_usr_btn.pack(pady=20)

show_table_btn = ctk.CTkButton(root, text="Show Table", command=show_table)
show_table_btn.pack(pady=10)

change_balance_btn = ctk.CTkButton(root, text="Change Balance", command=update_balance_window) # if balances.keys() else None
change_balance_btn.pack(pady=20)

# Init
read_balances()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
