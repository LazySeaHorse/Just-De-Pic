"""Main window and application controller for Just De Pic."""

import tkinter as tk
from tkinter import ttk
from gui.folder_view import FolderView
from gui.single_image_view import SingleImageView


class JustDePicApp:
    """Main application class."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Just De Pic - Image Metadata Tool")
        self.root.geometry("1200x800")
        
        # Configure grid weight
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create folder view tab
        self.folder_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.folder_frame, text="Folder Mode")
        self.folder_view = FolderView(self.folder_frame)
        
        # Create single image view tab
        self.single_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.single_frame, text="Single Image Mode")
        self.single_view = SingleImageView(self.single_frame)
        
        # Set up menu bar
        self._create_menu()
        
    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Folder", command=self.folder_view.open_folder)
        file_menu.add_command(label="Open Image", command=self.single_view.open_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle View Mode", command=self.folder_view.toggle_view_mode)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _show_about(self):
        """Show about dialog."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Just De Pic")
        about_window.geometry("400x200")
        about_window.transient(self.root)
        
        tk.Label(about_window, text="Just De Pic", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(about_window, text="Image Metadata Removal and Editing Tool").pack()
        tk.Label(about_window, text="Version 1.0").pack()
        tk.Label(about_window, text="\nRemove metadata, resize, and crop images\nwith ease!").pack(pady=10)
        tk.Button(about_window, text="OK", command=about_window.destroy).pack(pady=10)
    
    def run(self):
        """Start the application."""
        self.root.mainloop()