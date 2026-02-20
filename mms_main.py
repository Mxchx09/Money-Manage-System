import customtkinter as ctk
from functools import partial
import csv
import logging
import os

FILE = "balances.csv"


# --- Configuration ---
logging.basicConfig(
    filename="balances.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# name -> (balance, deps, wds)
balances: dict[str, tuple[float, float, float]] = {}

def read_balances():
    if not os.path.exists(FILE):
        logger.warning(f'No file "{FILE}" found')
        return

    try:
        with open("balances.csv", "r", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            
            user_c = 0
            users = []
            
            for line in reader:
                
                if len(line) < 4: continue
                usr = line[0]
                balance = float(line[1]) if line[1] else 0.0
                deps = float(line[2]) if line[2] else 0.0
                wds = float(line[3]) if line[3] else 0.0
                balances[usr] = (balance, deps, wds)
                
                users.append(usr)
                user_c += 1
            logger.info(f'Succesfully read file "{FILE}" :\n{user_c} Users: {users}')
                
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")

def change_usr_balance(usr, parent_win):
    """Creates a window to add to 'Schuldet mir' or 'Schulde ich'."""
    change_win = ctk.CTkToplevel(parent_win)
    change_win.geometry("300x350")
    change_win.title(f"Update: {usr}")
    change_win.grab_set()

    ctk.CTkLabel(change_win, text=f"Update for {usr}", font=("Arial", 16, "bold")).pack(pady=10)
    
    amount_entry = ctk.CTkEntry(change_win, placeholder_text="Betrag (z.B. 10.50)")
    amount_entry.pack(pady=10)

    def apply_change(is_debt_to_me: bool):
        try:
            val = float(amount_entry.get().replace(",", "."))
            # Current values: (total_balance, schuldet_mir, schulde_ich)
            current = balances[usr]
            
            if is_debt_to_me:
                # Update "Schuldet mir" (Index 1)
                new_data = (current[0] + val, current[1] + val, current[2])
                logger.info(f'Changed {usr}s Depts from {current[0]}€ to {new_data[0]}€ ({val})€')
            else:
                # Update "Schulde ich" (Index 2)
                new_data = (current[0] - val, current[1], current[2] + val)
                logger.info(f'Changed {usr}s WDS from {abs(current[0])}€ to {abs(new_data[2])}€ ({val})€')
            
            balances[usr] = new_data
            save_balances() # Save immediately to be safe
            change_win.destroy()
            parent_win.destroy() # Close selection window too
        except ValueError:
            amount_entry.configure(border_color="red")

    ctk.CTkButton(change_win, text="Schuldet mir (+)", 
                  fg_color="green", hover_color="#006400",
                  command=lambda: apply_change(True)).pack(pady=5)
    
    ctk.CTkButton(change_win, text="Schulde ich (-)", 
                  fg_color="red", hover_color="#8B0000",
                  command=lambda: apply_change(False)).pack(pady=5)

def update_balance_window():
    if not balances:
        return

    new_win = ctk.CTkToplevel(root)
    new_win.geometry("300x400")
    new_win.title("Person auswählen")
    new_win.grab_set()

    ctk.CTkLabel(new_win, text="Wer hat Geld bewegt?").pack(pady=10)
    
    # Scrollable frame if you have many people
    scroll_frame = ctk.CTkScrollableFrame(new_win, width=250, height=300)
    scroll_frame.pack(pady=10, padx=10)

    for person in balances.keys():
        ctk.CTkButton(scroll_frame, text=person, 
                      command=partial(change_usr_balance, person, new_win)).pack(pady=5, fill="x")

def save_balances():
    with open("balances.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "balance", "deps", "wds"])
        for name, values in balances.items():
            writer.writerow([name, *values])
            
        logger.info(f'Succesfully saved commited changes to "{FILE}"')

def set_usr_win():
    def set_usr():
        name = name_input.get().strip()
        if not name: return

        if name in balances:
            del balances[name]
        else:
            balances[name] = (0.0, 0.0, 0.0)
        
        save_balances()
        new_win.destroy()

    new_win = ctk.CTkToplevel(root)
    new_win.geometry("300x200")
    new_win.grab_set()

    ctk.CTkLabel(new_win, text="Name hinzufügen/löschen:").pack(pady=10)
    name_input = ctk.CTkEntry(new_win)
    name_input.pack(pady=10)
    
    ctk.CTkButton(new_win, text="Bestätigen", command=set_usr).pack(pady=10)

def show_table():
    new_win = ctk.CTkToplevel(root)
    new_win.geometry("550x400")
    new_win.title("Aktuelle Liste")
    new_win.grab_set()

    headers = ["Name", "Saldo (Gesamt)", "Schuldet mir", "Schulde ich"]
    for col, text in enumerate(headers):
        ctk.CTkLabel(new_win, text=text, font=("Arial", 12, "bold")).grid(row=0, column=col, padx=15, pady=10)

    for row, (name, values) in enumerate(balances.items(), start=1):
        ctk.CTkLabel(new_win, text=name).grid(row=row, column=0, padx=10, pady=5)
        # Saldo formatting: Red if negative, Green if positive
        color = "green" if values[0] >= 0 else "red"
        ctk.CTkLabel(new_win, text=f"{values[0]:.2f}€", text_color=color).grid(row=row, column=1, padx=10, pady=5)
        ctk.CTkLabel(new_win, text=f"{values[1]:.2f}€").grid(row=row, column=2, padx=10, pady=5)
        ctk.CTkLabel(new_win, text=f"{values[2]:.2f}€").grid(row=row, column=3, padx=10, pady=5)

def on_close():
    save_balances()
    root.destroy()

# --- Main App ---
root = ctk.CTk()
root.geometry("400x350")
root.title("Finanz-Tracker")

ctk.CTkLabel(root, text="Schulden-Verwaltung", font=("Arial", 20, "bold")).pack(pady=20)

ctk.CTkButton(root, text="Personen verwalten", command=set_usr_win).pack(pady=10)
ctk.CTkButton(root, text="Tabelle anzeigen", command=show_table).pack(pady=10)
ctk.CTkButton(root, text="Betrag ändern", command=update_balance_window).pack(pady=10)

read_balances()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()