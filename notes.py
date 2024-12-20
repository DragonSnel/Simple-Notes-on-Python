import os
from tkinter import Tk, Text, Button, filedialog, Label, messagebox, ttk, simpledialog
from datetime import datetime

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes")

        # Configure styling
        self.root.configure(bg="#2E2E2E")
        style = ttk.Style()
        style.configure("TNotebook", background="#2E2E2E", padding=10)
        style.configure("TNotebook.Tab", background="#FFD700", padding=(10, 5), relief="raised")
        style.map("TNotebook.Tab", background=[("selected", "#FFD700")])

        # Paths for saving files
        self.save_path = ""
        self.hidden_notes_path = os.path.join(os.getcwd(), "Hidden")
        os.makedirs(self.hidden_notes_path, exist_ok=True)

        # Create tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=1, fill="both")

        self.create_editor_tab()
        self.create_saved_notes_tab()
        self.create_recent_notes_tab()
        self.create_hidden_notes_tab()

    def create_editor_tab(self):
        self.editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_frame, text="Editor")

        self.text_area = Text(
            self.editor_frame, wrap="word", font=("Arial", 14), 
            bg="#2E2E2E", fg="#FFFFFF", insertbackground="#FFFFFF"
        )
        self.text_area.pack(expand=1, fill="both", padx=5, pady=5)

        Button(
            self.editor_frame, text="Save Note", command=self.save_note, 
            bg="#FFD700", fg="#000", relief="raised", bd=5
        ).pack(pady=5)

        Button(
            self.editor_frame, text="Save Hidden Note", command=self.save_hidden_note, 
            bg="#FFD700", fg="#000", relief="raised", bd=5
        ).pack(pady=5)

        Button(
            self.editor_frame, text="Select Folder", command=self.choose_folder, 
            bg="#FFD700", fg="#000", relief="raised", bd=5
        ).pack(pady=5)

        self.folder_label = Label(
            self.editor_frame, text="Save Folder: Not Selected", wraplength=400, 
            bg="#2E2E2E", fg="#FFFFFF"
        )
        self.folder_label.pack(pady=5)

    def create_saved_notes_tab(self):
        self.saved_notes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.saved_notes_frame, text="Saved Notes")

        self.saved_notes_list = ttk.Treeview(
            self.saved_notes_frame, columns=("name", "time"), show="headings"
        )
        self.saved_notes_list.heading("name", text="File Name")
        self.saved_notes_list.heading("time", text="Save Time")
        self.saved_notes_list.pack(expand=1, fill="both", padx=5, pady=5)

        self.load_saved_notes()

    def create_recent_notes_tab(self):
        self.recent_notes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.recent_notes_frame, text="Recent Notes")

        self.recent_notes_list = ttk.Treeview(
            self.recent_notes_frame, columns=("name", "time"), show="headings"
        )
        self.recent_notes_list.heading("name", text="File Name")
        self.recent_notes_list.heading("time", text="Save Time")
        self.recent_notes_list.pack(expand=1, fill="both", padx=5, pady=5)

        self.recent_notes = []

    def create_hidden_notes_tab(self):
        self.hidden_notes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hidden_notes_frame, text="Hidden Notes")

        self.hidden_notes_list = ttk.Treeview(
            self.hidden_notes_frame, columns=("name", "time"), show="headings"
        )
        self.hidden_notes_list.heading("name", text="File Name")
        self.hidden_notes_list.heading("time", text="Save Time")
        self.hidden_notes_list.pack(expand=1, fill="both", padx=5, pady=5)

        self.load_hidden_notes()

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_path = folder
            self.folder_label.config(text=f"Save Folder: {self.save_path}")
            self.load_saved_notes()

    def save_note(self):
        file_name = filedialog.asksaveasfilename(
            initialdir=self.save_path if self.save_path else os.getcwd(),
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )

        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(self.text_area.get(1.0, "end-1c"))
                save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.add_to_saved_notes(os.path.basename(file_name), save_time)
                self.text_area.delete(1.0, "end")
                messagebox.showinfo("Success", f"File saved: {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def save_hidden_note(self):
        password = simpledialog.askstring("Password", "Enter password for the hidden note:", show='*')
        if not password:
            messagebox.showwarning("Canceled", "Hidden note saving canceled.")
            return

        file_name = os.path.join(self.hidden_notes_path, f"hidden_{datetime.now().strftime('%Y%m%d%H%M%S')}.hidden")

        try:
            encrypted_content = self.encrypt_text(self.text_area.get(1.0, "end-1c"), password)
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(encrypted_content)
            save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.add_to_hidden_notes(os.path.basename(file_name), save_time)
            self.text_area.delete(1.0, "end")
            messagebox.showinfo("Success", f"Hidden note saved: {file_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save hidden note: {e}")

    def encrypt_text(self, text, password):
        return "".join(chr(ord(c) ^ ord(password[i % len(password)])) for i, c in enumerate(text))

    def add_to_saved_notes(self, file_name, save_time):
        self.saved_notes_list.insert("", "end", values=(file_name, save_time))
        self.add_to_recent_notes(file_name, save_time)

    def add_to_hidden_notes(self, file_name, save_time):
        self.hidden_notes_list.insert("", "end", values=(file_name, save_time))

    def add_to_recent_notes(self, file_name, save_time):
        self.recent_notes.insert(0, (file_name, save_time))
        if len(self.recent_notes) > 10:
            self.recent_notes.pop()
        self.update_recent_notes()

    def update_recent_notes(self):
        for row in self.recent_notes_list.get_children():
            self.recent_notes_list.delete(row)
        for note in self.recent_notes:
            self.recent_notes_list.insert("", "end", values=note)

    def load_saved_notes(self):
        if not self.save_path:
            return
        for row in self.saved_notes_list.get_children():
            self.saved_notes_list.delete(row)
        try:
            for file_name in os.listdir(self.save_path):
                if file_name.endswith(".txt"):
                    file_path = os.path.join(self.save_path, file_name)
                    save_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                    self.saved_notes_list.insert("", "end", values=(file_name, save_time))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notes: {e}")

    def load_hidden_notes(self):
        for row in self.hidden_notes_list.get_children():
            self.hidden_notes_list.delete(row)
        try:
            for file_name in os.listdir(self.hidden_notes_path):
                if file_name.endswith(".hidden"):
                    file_path = os.path.join(self.hidden_notes_path, file_name)
                    save_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                    self.hidden_notes_list.insert("", "end", values=(file_name, save_time))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load hidden notes: {e}")

if __name__ == "__main__":
    root = Tk()
    app = NotesApp(root)
    root.mainloop()
