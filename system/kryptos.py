import tkinter as tk
from tkinter import ttk, messagebox

import sqlite3

def App():
    main = tk.Tk()
    main.title("Kryptos")

    def connect_db():
        '''Establishes connection to the SQLite database.'''
        return sqlite3.connect('data.db')

    def initialize_db():
        '''Creates the database and table "passwords" if it doesn't already exist.
        The table "passwords has 5 columns:

        id       -- Integer, Primary key, Autoincrement
        service  -- String
        password -- String
        username -- String
        email    -- String
        '''
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            password TEXT NOT NULL, 
            username TEXT NOT NULL,
            email TEXT NOT NULL
        )
        ''')

        conn.commit()
        conn.close()

    def create_entry(service, password, username="", email=""):
        '''
        Creates a new entry in the database. 
        If an exact replica exists, it does nothing.
        If a similar entry exists, it asks if you want to continue. 
         - If yes, it creates a new entry. I no, it does nothing.
        It takes exactly 4 arguments.

        service  -- Website / Service the information is for
        password -- password for the account
        username -- optional, username for the service
        email    -- optional, Email for the service
        '''
        if service == "" or password == "":
            return "Service or password not specified!"

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM passwords WHERE service = ? AND username = ? AND password = ? AND email = ?', 
                       (service, username, password, email))
        exact_count = cursor.fetchone()[0]

        if exact_count > 0:
            conn.close()
            return "Already exists"

        cursor.execute('SELECT COUNT(*) FROM passwords WHERE service = ? AND (username = ? OR email = ?)', 
                       (service, username, email))
        similar_count = cursor.fetchone()[0]

        if similar_count > 0:
            continue_box = messagebox.askquestion("Continue?", "Similar entry found. Do you want to continue?")
            if continue_box == "no":
                conn.close()
                return "Added"

        cursor.execute('INSERT INTO passwords (service, username, password, email) VALUES (?, ?, ?, ?)', 
                       (service, username, password, email))
        conn.commit()
        conn.close()

        return "Added"

    def delete_entry(entry_id):
        '''
        Deletes the entry with the specified ID from the database.

        entry_id -- Id of the entry that's being deleted
        '''
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM passwords WHERE id = ?', (entry_id,))
        conn.commit()
        conn.close()

    def on_delete(entry_id, treeview):
        '''
        Deletes an entry after confirmation.
        
        entry_id -- Id of item that should be deleted
        treeview -- Table "passwords" from database displayed in treeview
        '''
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?"):
            delete_entry(entry_id)
            # Remove the entry from the Treeview
            for item in treeview.get_children():
                if treeview.item(item, 'values')[0] == entry_id:
                    treeview.delete(item)
                    break

    def open_creation_window():
        '''
        Creates a new Tkinter window entry_window used for creating a new entry.

        All 4 inputs have:
        _frame -- The frame for the input and all related items
        _label -- A label displaying what's supposed to go into the entry field
        _var -- A StringVar storing the input from the entry field
        _input -- The entry field

        service -- service or website
        username -- optional, username
        email -- optional, linked email address
        password -- password
        '''
        entry_window = tk.Toplevel(main)  # Use Toplevel for non-blocking
        entry_window.title("New account")

        service_frame = tk.Frame(entry_window)
        service_frame.pack(pady=5, expand=True, fill="both")
        service_label = tk.Label(service_frame, text="Service / Website")
        service_label.pack(side="left")
        service_var = tk.StringVar(service_frame)
        service_input = tk.Entry(service_frame, textvariable=service_var)
        service_input.pack(side="right")

        username_frame = tk.Frame(entry_window)
        username_frame.pack(pady=5, expand=True, fill="both")
        username_label = tk.Label(username_frame, text="Username")
        username_label.pack(side="left")
        username_var = tk.StringVar(username_frame)
        username_input = tk.Entry(username_frame, textvariable=username_var)
        username_input.pack(side="right")

        email_frame = tk.Frame(entry_window)
        email_frame.pack(pady=5, expand=True, fill="both")
        email_label = tk.Label(email_frame, text="Email")
        email_label.pack(side="left")
        email_var = tk.StringVar(email_frame)
        email_input = tk.Entry(email_frame, textvariable=email_var)
        email_input.pack(side="right")
        
        password_frame = tk.Frame(entry_window)
        password_frame.pack(pady=5, expand=True, fill="both")
        password_label = tk.Label(password_frame, text="Password")
        password_label.pack(side="left")
        password_var = tk.StringVar(password_frame)
        password_input = tk.Entry(password_frame, textvariable=password_var)
        password_input.pack(side="right")

        def submit_func():
            result = create_entry(service_var.get(), password_var.get(), username_var.get(), email_var.get())
            warning_var.set(result)
            if result == "Added":
                refresh_treeview()  # Refresh the Treeview when a new entry is added
                entry_window.destroy()  # Close the creation window

        submit_button = tk.Button(entry_window, text="Submit", command=submit_func)
        submit_button.pack(pady=10)
        warning_var = tk.StringVar(entry_window)
        warning_label = tk.Label(entry_window, textvariable=warning_var)
        warning_label.pack()

    def populate_treeview(treeview):
        '''
        Fills the treeview with data from the table "passwords" in the database
        '''
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * from passwords')
        entries = cursor.fetchall()
        conn.close()

        for row in entries:
            treeview.insert("", "end", values=row)

    def refresh_treeview():
        '''
        Clears and repopulates the Treeview with current database entries using populate_treeview().
        '''
        for item in treeview.get_children():
            treeview.delete(item)
        populate_treeview(treeview)

    def search_entries():
        '''
        Filters the Treeview based on the search query.
        
        search_var -- StringVar holding query
        '''
        query = search_var.get().lower()
        for item in treeview.get_children():
            treeview.delete(item)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM passwords')
        entries = cursor.fetchall()
        conn.close()

        for row in entries:
            if any(query in str(value).lower() for value in row):
                treeview.insert("", "end", values=row)

    initialize_db()  # Initializes the database when the program starts

    # Tabview
    tabview = ttk.Notebook(main)
    tabview.pack(expand=True, fill="both", anchor="nw")

    ## Tabs
    home_tab = tk.Frame(tabview)
    home_tab.pack(expand=True, fill="both")

    config_tab = tk.Frame(tabview)
    config_tab.pack(expand=True, fill="both")

    ## Add Tabs
    tabview.add(home_tab, text="Home")
    tabview.add(config_tab, text="Config")

    # Home Tab
    add_entry_button = tk.Button(home_tab, text="New Account", command=open_creation_window)
    add_entry_button.pack(pady=10, padx=5)

    search_var = tk.StringVar()
    search_bar_frame = tk.Frame(home_tab)
    search_bar_frame.pack()
    search_entry = tk.Entry(search_bar_frame, textvariable=search_var, width=30)
    search_entry.pack(pady=10, padx=5, side="left")
    search_button = tk.Button(search_bar_frame, text="Search", command=search_entries)
    search_button.pack(pady=5, side="right")

    treeview_columns = ("ID", "Service", "Username", "Password", "Email")
    treeview = ttk.Treeview(home_tab, columns=treeview_columns, show='headings')
    for col in treeview_columns:
        treeview.heading(col, text=col)
        treeview.column(col, anchor="center")
    treeview.pack(expand=True, fill="both")
    populate_treeview(treeview)

    def delete_selected_entry():
        '''
        Deletes the highlighted entry using on_delete().
        '''
        selected_item = treeview.selection()
        if not selected_item:
            messagebox.showwarning("Select Entry", "Please select an entry to delete.")
            return
        
        entry_id = treeview.item(selected_item, 'values')[0]
        on_delete(entry_id, treeview)

    delete_button = tk.Button(home_tab, text="Delete Selected Entry", command=delete_selected_entry)
    delete_button.pack(pady=10)

    treeview_scrollbar = ttk.Scrollbar(home_tab, orient="vertical", command=treeview.yview)
    treeview.configure(yscroll=treeview_scrollbar.set)
    treeview_scrollbar.pack(side="right", fill="y")

    # Config Tab
    

    main.mainloop()

App()