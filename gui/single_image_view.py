"""Single image view for detailed metadata inspection and editing."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from core.image_processor import ImageProcessor
from core.metadata_handler import MetadataHandler
from utils.helpers import get_file_size_str, is_image_file
from pathlib import Path


class SingleImageView:
    """Manages the single image view interface."""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_image_path = None
        self.current_image = None
        self.photo = None
        self.metadata = {}
        
        self.processor = ImageProcessor()
        self.metadata_handler = MetadataHandler()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the single image view UI."""
        # Configure grid
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=0)
        
        # Toolbar
        toolbar = ttk.Frame(self.parent)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Button(toolbar, text="Open Image", command=self.open_image).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save Changes", command=self.save_changes).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove All Metadata", command=self.remove_all_metadata).pack(side=tk.LEFT, padx=2)
        
        # Image display area
        self.image_frame = ttk.LabelFrame(self.parent, text="Image Preview")
        self.image_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Canvas for image with scrollbars
        self.canvas = tk.Canvas(self.image_frame, bg="gray")
        v_scrollbar = ttk.Scrollbar(self.image_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(self.image_frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)
        
        # Image info label
        self.info_label = ttk.Label(self.image_frame, text="No image loaded")
        self.info_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Metadata panel
        metadata_panel = ttk.LabelFrame(self.parent, text="Metadata", width=400)
        metadata_panel.grid(row=1, column=1, sticky="ns", padx=5, pady=5)
        metadata_panel.grid_propagate(False)
        
        # Metadata display with scrollbar
        metadata_container = ttk.Frame(metadata_panel)
        metadata_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for metadata
        self.metadata_tree = ttk.Treeview(metadata_container, columns=("value",), show="tree headings")
        self.metadata_tree.heading("#0", text="Field")
        self.metadata_tree.heading("value", text="Value")
        self.metadata_tree.column("#0", width=150)
        self.metadata_tree.column("value", width=200)
        
        metadata_scrollbar = ttk.Scrollbar(metadata_container, orient="vertical", 
                                         command=self.metadata_tree.yview)
        self.metadata_tree.configure(yscrollcommand=metadata_scrollbar.set)
        
        self.metadata_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        metadata_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to edit
        self.metadata_tree.bind("<Double-1>", self._on_metadata_double_click)
        
        # Operations panel
        ops_frame = ttk.LabelFrame(metadata_panel, text="Operations")
        ops_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Resize controls
        ttk.Label(ops_frame, text="Resize (max dimensions):").pack(anchor="w", pady=(5, 0))
        resize_frame = ttk.Frame(ops_frame)
        resize_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(resize_frame, text="Width:").pack(side=tk.LEFT)
        self.resize_width_var = tk.StringVar(value="1920")
        ttk.Entry(resize_frame, textvariable=self.resize_width_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(resize_frame, text="Height:").pack(side=tk.LEFT, padx=(10, 0))
        self.resize_height_var = tk.StringVar(value="1080")
        ttk.Entry(resize_frame, textvariable=self.resize_height_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(ops_frame, text="Resize Image", command=self.resize_image).pack(fill=tk.X, pady=2)
        
        # Crop controls
        ttk.Separator(ops_frame).pack(fill=tk.X, pady=10)
        ttk.Label(ops_frame, text="Crop (exact dimensions):").pack(anchor="w")
        crop_frame = ttk.Frame(ops_frame)
        crop_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(crop_frame, text="Width:").pack(side=tk.LEFT)
        self.crop_width_var = tk.StringVar(value="800")
        ttk.Entry(crop_frame, textvariable=self.crop_width_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(crop_frame, text="Height:").pack(side=tk.LEFT, padx=(10, 0))
        self.crop_height_var = tk.StringVar(value="600")
        ttk.Entry(crop_frame, textvariable=self.crop_height_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(ops_frame, text="Crop Center", command=self.crop_image).pack(fill=tk.X, pady=2)
        
    def open_image(self):
        """Open an image file."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path and is_image_file(file_path):
            self.current_image_path = Path(file_path)
            self._load_image()
            self._load_metadata()
            
    def _load_image(self):
        """Load and display the current image."""
        if not self.current_image_path:
            return
            
        try:
            # Load image
            self.current_image = Image.open(self.current_image_path)
            
            # Create display copy (max 800px for display)
            display_image = self.current_image.copy()
            display_image.thumbnail((800, 800))
            
            self.photo = ImageTk.PhotoImage(display_image)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Update info
            size_str = get_file_size_str(self.current_image_path)
            info_text = (f"File: {self.current_image_path.name} | "
                        f"Size: {size_str} | "
                        f"Dimensions: {self.current_image.width}x{self.current_image.height}")
            self.info_label.config(text=info_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            
    def _load_metadata(self):
        """Load and display metadata."""
        if not self.current_image_path:
            return
            
        # Clear existing metadata
        self.metadata_tree.delete(*self.metadata_tree.get_children())
        
        try:
            # Get metadata
            self.metadata = self.metadata_handler.get_all_metadata(str(self.current_image_path))
            
            # Display metadata in tree
            for category, fields in self.metadata.items():
                if fields:
                    # Add category as parent
                    category_item = self.metadata_tree.insert("", "end", text=category, values=("",))
                    
                    # Add fields as children
                    for field, value in fields.items():
                        # Truncate long values for display
                        display_value = str(value)
                        if len(display_value) > 50:
                            display_value = display_value[:47] + "..."
                        
                        self.metadata_tree.insert(category_item, "end", 
                                                text=field, 
                                                values=(display_value,),
                                                tags=(category, field, str(value)))
                    
                    # Expand category
                    self.metadata_tree.item(category_item, open=True)
                    
        except Exception as e:
            print(f"Error loading metadata: {e}")
            
    def _on_metadata_double_click(self, event):
        """Handle double-click on metadata item for editing."""
        selection = self.metadata_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        tags = self.metadata_tree.item(item, "tags")
        
        if len(tags) >= 3:  # It's a field, not a category
            category, field, current_value = tags[0], tags[1], tags[2]
            
            # Create edit dialog
            dialog = tk.Toplevel(self.parent)
            dialog.title(f"Edit {field}")
            dialog.geometry("400x150")
            dialog.transient(self.parent)
            
            ttk.Label(dialog, text=f"Field: {field}").pack(pady=5)
            ttk.Label(dialog, text="Value:").pack()
            
            value_var = tk.StringVar(value=current_value)
            entry = ttk.Entry(dialog, textvariable=value_var, width=50)
            entry.pack(pady=5, padx=10, fill=tk.X)
            
            def save_value():
                new_value = value_var.get()
                # Update metadata
                if category in self.metadata and field in self.metadata[category]:
                    self.metadata[category][field] = new_value
                    # Update display
                    self.metadata_tree.item(item, values=(new_value,))
                dialog.destroy()
                
            button_frame = ttk.Frame(dialog)
            button_frame.pack(pady=10)
            ttk.Button(button_frame, text="Save", command=save_value).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
            
            entry.focus()
            entry.bind("<Return>", lambda e: save_value())
            
    def save_changes(self):
        """Save metadata changes to the image file."""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please open an image first.")
            return
            
        try:
            self.metadata_handler.update_metadata(str(self.current_image_path), self.metadata)
            messagebox.showinfo("Success", "Metadata saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save metadata: {str(e)}")
            
    def remove_all_metadata(self):
        """Remove all metadata from the current image."""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please open an image first.")
            return
            
        if messagebox.askyesno("Confirm", "Remove all metadata from this image?"):
            try:
                self.metadata_handler.remove_all_metadata(str(self.current_image_path))
                messagebox.showinfo("Success", "All metadata removed.")
                self._load_metadata()  # Reload to show empty metadata
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove metadata: {str(e)}")
                
    def resize_image(self):
        """Resize the current image."""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please open an image first.")
            return
            
        try:
            max_width = int(self.resize_width_var.get())
            max_height = int(self.resize_height_var.get())
            
            self.processor.resize_image(str(self.current_image_path), max_width, max_height)
            messagebox.showinfo("Success", "Image resized successfully.")
            self._load_image()  # Reload to show new size
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid dimensions.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to resize image: {str(e)}")
            
    def crop_image(self):
        """Crop the current image."""
        if not self.current_image_path:
            messagebox.showwarning("No Image", "Please open an image first.")
            return
            
        try:
            width = int(self.crop_width_var.get())
            height = int(self.crop_height_var.get())
            
            self.processor.crop_center(str(self.current_image_path), width, height)
            messagebox.showinfo("Success", "Image cropped successfully.")
            self._load_image()  # Reload to show cropped image
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid dimensions.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to crop image: {str(e)}")