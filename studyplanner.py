import csv
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

FILENAME = "study_plans.csv"

HEADERS = ["Session Name", "Subject", "Start Date", "End Date", "Duration (hrs)",
           "Priority", "Study Method", "Resources", "Goals", "Created On"]


# ---------- CSV Helpers ----------
def read_sessions():
    try:
        with open(FILENAME, "r") as file:
            return list(csv.reader(file))
    except FileNotFoundError:
        return []


def write_sessions(sessions):
    with open(FILENAME, "w", newline="") as file:
        csv.writer(file).writerows(sessions)


def append_session(session):
    with open(FILENAME, "a", newline="") as file:
        csv.writer(file).writerow(session)


# ---------- GUI Functions ----------
def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    for i, session in enumerate(read_sessions()):
        tree.insert("", "end", iid=i, values=session)


def clear_inputs():
    for entry in entry_fields.values():
        entry.delete(0, tk.END)


def add_study_session():
    session = []
    for field in HEADERS[:-1]:
        value = entry_fields[field].get().strip()
        if not value:
            messagebox.showwarning("Warning", f"⚠️ {field} cannot be empty!")
            return
        session.append(value)
    session.append(datetime.today().strftime("%Y-%m-%d"))
    append_session(session)
    messagebox.showinfo("Success", "✅ Study session added successfully!")
    clear_inputs()
    refresh_table()


def delete_study_session():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "❗ Select a session to delete.")
        return
    index = int(selected[0])
    sessions = read_sessions()
    del sessions[index]
    write_sessions(sessions)
    messagebox.showinfo("Deleted", "🗑️ Study session deleted successfully!")
    clear_inputs()
    refresh_table()


def update_study_session():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "❗ Select a session to update.")
        return
    index = int(selected[0])
    sessions = read_sessions()

    updated_session = []
    for field in HEADERS[:-1]:
        value = entry_fields[field].get().strip()
        if not value:
            messagebox.showwarning("Warning", f"⚠️ {field} cannot be empty!")
            return
        updated_session.append(value)
    updated_session.append(datetime.today().strftime("%Y-%m-%d"))

    sessions[index] = updated_session
    write_sessions(sessions)
    messagebox.showinfo("Updated", "🔄 Study session updated successfully!")
    clear_inputs()
    refresh_table()


def search_study_session():
    term = search_entry.get().strip().lower()
    if not term:
        refresh_table()
        return
    results = []
    for i, session in enumerate(read_sessions()):
        if term in ", ".join(session).lower():
            results.append((i, session))
    for row in tree.get_children():
        tree.delete(row)
    for i, session in results:
        tree.insert("", "end", iid=i, values=session)


def on_row_select(event):
    selected = tree.selection()
    if not selected:
        return
    index = int(selected[0])
    sessions = read_sessions()
    if index < len(sessions):
        for i, field in enumerate(HEADERS[:-1]):
            entry_fields[field].delete(0, tk.END)
            entry_fields[field].insert(0, sessions[index][i])


# ---------- Sorting ----------
sort_orders = {col: False for col in HEADERS}  # Track ASC/DESC

def sort_column(col):
    sessions = read_sessions()
    col_index = HEADERS.index(col)
    reverse = sort_orders[col]
    try:
        # Try numeric sort
        sessions.sort(key=lambda x: float(x[col_index]), reverse=reverse)
    except ValueError:
        # Fallback to string sort
        sessions.sort(key=lambda x: x[col_index], reverse=reverse)
    sort_orders[col] = not reverse
    for row in tree.get_children():
        tree.delete(row)
    for i, session in enumerate(sessions):
        tree.insert("", "end", iid=i, values=session)


# ---------- GUI Setup ----------
root = tk.Tk()
root.title("📚 Study Planner")
root.geometry("1300x650")
root.configure(bg="#f8f9fa")

# Input Frame
input_frame = tk.LabelFrame(root, text="📌 Session Details", padx=10, pady=10, bg="#f8f9fa")
input_frame.pack(fill="x", padx=10, pady=5)

entry_fields = {}
for i, field in enumerate(HEADERS[:-1]):
    lbl = tk.Label(input_frame, text=field + ":", bg="#f8f9fa")
    lbl.grid(row=i // 3, column=(i % 3) * 2, sticky="e", padx=5, pady=5)
    ent = tk.Entry(input_frame, width=25)
    ent.grid(row=i // 3, column=(i % 3) * 2 + 1, padx=5, pady=5)
    entry_fields[field] = ent

# Buttons
button_frame = tk.Frame(root, bg="#f8f9fa")
button_frame.pack(pady=10)

btn_add = tk.Button(button_frame, text="➕ Add", command=add_study_session, width=15, bg="#28a745", fg="white")
btn_add.grid(row=0, column=0, padx=5)

btn_update = tk.Button(button_frame, text="🔄 Update", command=update_study_session, width=15, bg="#007bff", fg="white")
btn_update.grid(row=0, column=1, padx=5)

btn_delete = tk.Button(button_frame, text="🗑️ Delete", command=delete_study_session, width=15, bg="#dc3545", fg="white")
btn_delete.grid(row=0, column=2, padx=5)

btn_refresh = tk.Button(button_frame, text="🔃 Refresh", command=refresh_table, width=15, bg="#6c757d", fg="white")
btn_refresh.grid(row=0, column=3, padx=5)

# Search Box
search_frame = tk.Frame(root, bg="#f8f9fa")
search_frame.pack(pady=5)

tk.Label(search_frame, text="🔍 Search:", bg="#f8f9fa").pack(side="left", padx=5)
search_entry = tk.Entry(search_frame, width=40)
search_entry.pack(side="left", padx=5)
btn_search = tk.Button(search_frame, text="Go", command=search_study_session, width=10, bg="#17a2b8", fg="white")
btn_search.pack(side="left", padx=5)

# Treeview Table
tree = ttk.Treeview(root, columns=HEADERS, show="headings")
for col in HEADERS:
    tree.heading(col, text=col, command=lambda c=col: sort_column(c))  # Sortable
    tree.column(col, width=120, anchor="center")
tree.pack(fill="both", expand=True, padx=10, pady=10)

tree.bind("<<TreeviewSelect>>", on_row_select)

# Scrollbar
scrollbar = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

refresh_table()
root.mainloop()
