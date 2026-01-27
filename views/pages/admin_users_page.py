
import tkinter as tk
from tkinter import ttk, messagebox
from ..styles import Colors, Fonts

class AdminUsersPage:
    """Admin User Management Page"""
    
    def __init__(self, parent, auth_controller):
        self.frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        self.auth = auth_controller
        self.selected_user = None
        self.create_widgets()
        
    def create_widgets(self):
        """Create page content"""
        # Title section
        title_section = tk.Frame(self.frame, bg=Colors.BACKGROUND)
        title_section.pack(fill=tk.X, pady=(0, 15), padx=15)
        
        users_title = tk.Label(
            title_section,
            text="User Management",
            font=("Arial", 18, "bold"),
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT
        )
        users_title.pack(side=tk.LEFT)
        
        # Action buttons
        buttons_frame = tk.Frame(title_section, bg=Colors.BACKGROUND)
        buttons_frame.pack(side=tk.RIGHT)
        
        self.create_button(buttons_frame, "+ Add User", Colors.SUCCESS, self.show_add_user_dialog)
        self.create_button(buttons_frame, "✏️ Edit", Colors.INFO, self.show_edit_user_dialog)
        self.create_button(buttons_frame, "🗑️ Delete", Colors.DANGER, self.delete_selected_user)
        self.create_button(buttons_frame, "🔄 Refresh", Colors.SECONDARY, self.load_users)
        
        # Table frame
        table_frame = tk.Frame(self.frame, bg=Colors.CARD_BG)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Create treeview
        columns = ("ID", "Username", "Email", "Role", "Status", "Created")
        self.users_tree = ttk.Treeview(table_frame, columns=columns, height=15, show="headings")
        
        column_widths = {
            "ID": 50, "Username": 120, "Email": 200, 
            "Role": 80, "Status": 80, "Created": 150
        }
        
        for col, width in column_widths.items():
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=width)
            
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscroll=scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        self.users_tree.bind("<<TreeviewSelect>>", self.on_user_select)
        
        # Initial load
        self.load_users()
        
    def create_button(self, parent, text, color, command):
        btn = tk.Button(parent, text=text, font=("Arial", 10, "bold"), bg=color, fg="white",
                       relief=tk.FLAT, bd=0, cursor="hand2", command=command, padx=15, pady=8)
        btn.pack(side=tk.LEFT, padx=5)
        return btn

    def load_users(self):
        # Clear existing
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        users = self.auth.get_all_users()
        if users:
            for user in users:
                user_id = user.get("user_id", "")[:8]
                username = user.get("username", "")
                email = user.get("email", "")
                role = user.get("role", "").upper()
                status = "✓ Active" if user.get("is_active", True) else "✗ Inactive"
                created = user.get("created_at", "")[:10]
                
                self.users_tree.insert("", tk.END, iid=user.get("user_id"),
                                     values=(user_id, username, email, role, status, created),
                                     tags=("admin",) if role == "ADMIN" else ("operator",))
                                     
        self.users_tree.tag_configure("admin", foreground=Colors.DANGER)
        self.users_tree.tag_configure("operator", foreground=Colors.INFO)

    def on_user_select(self, event):
        selection = self.users_tree.selection()
        if selection:
            self.selected_user = selection[0]

    def center_dialog(self, dialog, width, height):
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")

    def show_add_user_dialog(self):
        dialog = tk.Toplevel(self.frame)
        dialog.title("Add New User")
        dialog.configure(bg=Colors.BACKGROUND)
        self.center_dialog(dialog, 400, 400)
        dialog.grab_set()
        
        container = tk.Frame(dialog, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Add New User", font=("Arial", 16, "bold"), bg="white").pack(pady=(0,20))
        
        # Fields
        entries = {}
        for field in ["Username", "Email", "Password"]:
            tk.Label(container, text=field+":", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
            entry = tk.Entry(container, bg="#f5f5f5", relief=tk.SOLID, bd=1)
            entry.pack(fill=tk.X, pady=(0, 15))
            if field == "Password": entry.config(show="*")
            entries[field.lower()] = entry
            
        # Role
        tk.Label(container, text="Role:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        role_var = tk.StringVar(value="operator")
        role_frame = tk.Frame(container, bg="white")
        role_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Radiobutton(role_frame, text="Operator", variable=role_var, value="operator", bg="white").pack(side=tk.LEFT)
        tk.Radiobutton(role_frame, text="Admin", variable=role_var, value="admin", bg="white").pack(side=tk.LEFT, padx=20)
        
        def save():
            u = entries['username'].get().strip()
            e = entries['email'].get().strip()
            p = entries['password'].get()
            r = role_var.get()
            
            if self.auth.add_user(u, e, p, r):
                messagebox.showinfo("Success", "User created")
                dialog.destroy()
                self.load_users()
        
        tk.Button(container, text="Save", bg=Colors.SUCCESS, fg="white", command=save, padx=20, pady=5).pack(side=tk.LEFT, pady=10)
        tk.Button(container, text="Cancel", command=dialog.destroy, padx=20, pady=5).pack(side=tk.LEFT, padx=10, pady=10)

    def show_edit_user_dialog(self):
        if not self.selected_user:
            messagebox.showwarning("Warning", "Select a user")
            return
            
        # Fetch current data logic... (simplified for brevity, would access db or tree values)
        # Using tree values
        item = self.users_tree.item(self.selected_user)
        vals = item['values']
        
        dialog = tk.Toplevel(self.frame)
        dialog.title("Edit User")
        dialog.configure(bg=Colors.BACKGROUND)
        self.center_dialog(dialog, 400, 300)
        dialog.grab_set()
        
        container = tk.Frame(dialog, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Edit User", font=("Arial", 16, "bold"), bg="white").pack(pady=(0,20))
        
        # Username Readonly
        tk.Label(container, text="Username:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        tk.Label(container, text=vals[1], bg="#f5f5f5", relief=tk.SOLID, bd=1).pack(fill=tk.X, pady=(0, 15))
        
        # Email
        tk.Label(container, text="Email:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        email_entry = tk.Entry(container, bg="#f5f5f5", relief=tk.SOLID, bd=1)
        email_entry.insert(0, vals[2])
        email_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Role
        tk.Label(container, text="Role:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        role_var = tk.StringVar(value=vals[3].lower())
        role_frame = tk.Frame(container, bg="white")
        role_frame.pack(fill=tk.X)
        tk.Radiobutton(role_frame, text="Operator", variable=role_var, value="operator", bg="white").pack(side=tk.LEFT)
        tk.Radiobutton(role_frame, text="Admin", variable=role_var, value="admin", bg="white").pack(side=tk.LEFT, padx=20)
        
        def save():
            if self.auth.edit_user(self.selected_user, email_entry.get().strip(), role_var.get()):
                messagebox.showinfo("Success", "User updated")
                dialog.destroy()
                self.load_users()

        tk.Button(container, text="Save", bg=Colors.SUCCESS, fg="white", command=save, padx=20, pady=5).pack(side=tk.LEFT, pady=10)
        tk.Button(container, text="Cancel", command=dialog.destroy, padx=20, pady=5).pack(side=tk.LEFT, padx=10, pady=10)

    def delete_selected_user(self):
        if not self.selected_user: return
        if messagebox.askyesno("Confirm", "Delete this user?"):
            if self.auth.delete_user(self.selected_user):
                messagebox.showinfo("Success", "User deleted")
                self.load_users()

    def get_widget(self):
        return self.frame
