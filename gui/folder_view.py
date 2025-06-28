"""Folder view for batch image operations."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from PIL import Image, ImageTk
from core.image_processor import ImageProcessor
from core.metadata_handler import MetadataHandler
from utils.helpers import get_file_size_str, is_image_file
import threading


class FolderView:
    """Manages the folder view interface."""

    def __init__(self, parent):
        self.parent = parent
        self.current_folder = None
        self.images = []
        self.selected_images = set()
        self.view_mode = "grid"  # grid or list
        self.thumbnails = {}
        self.thumbnail_frames = []  # Keep track of thumbnail frames
        self.thumbnail_size = 150
        self.grid_padding = 10

        self.processor = ImageProcessor()
        self.metadata_handler = MetadataHandler()

        self._setup_ui()

    def _setup_ui(self):
        """Set up the folder view UI."""
        # Configure grid
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=0)

        # Toolbar
        toolbar = ttk.Frame(self.parent)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        ttk.Button(toolbar, text="Open Folder", command=self.open_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Toggle View", command=self.toggle_view_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clear Selection", command=self.clear_selection).pack(side=tk.LEFT, padx=2)

        # Thumbnail size control
        ttk.Label(toolbar, text="Thumbnail Size:").pack(side=tk.LEFT, padx=(20, 5))
        self.size_var = tk.IntVar(value=150)
        size_spinbox = ttk.Spinbox(toolbar, from_=50, to=300, increment=25,
                                   textvariable=self.size_var, width=8,
                                   command=self._on_thumbnail_size_change)
        size_spinbox.pack(side=tk.LEFT, padx=2)

        # Main content area with scrollbar
        self.content_frame = ttk.Frame(self.parent)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Canvas and scrollbars for grid view
        self.canvas = tk.Canvas(self.content_frame, bg="white")
        self.v_scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.content_frame, orient="horizontal", command=self.canvas.xview)

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure canvas scrolling
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )

        # Bind canvas resize event
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.scrollable_frame.bind('<Configure>', self._on_frame_configure)

        # Treeview for list view
        self.tree = ttk.Treeview(self.content_frame, columns=("size", "dimensions", "metadata"),
                                 show="tree headings", selectmode="extended")
        self.tree.heading("#0", text="Filename")
        self.tree.heading("size", text="Size")
        self.tree.heading("dimensions", text="Dimensions")
        self.tree.heading("metadata", text="Has Metadata")

        self.tree.column("#0", width=300)
        self.tree.column("size", width=100)
        self.tree.column("dimensions", width=150)
        self.tree.column("metadata", width=100)

        self.tree_scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        # Bind tree selection
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Side panel for operations
        side_panel = ttk.LabelFrame(self.parent, text="Operations", padding=10)
        side_panel.grid(row=1, column=1, sticky="ns", padx=5, pady=5)

        # Metadata operations
        ttk.Label(side_panel, text="Metadata Operations", font=("Arial", 10, "bold")).pack(pady=(0, 5))
        ttk.Button(side_panel, text="Remove Metadata from Selected",
                   command=self.remove_metadata_batch).pack(fill=tk.X, pady=2)

        # Resize operations
        ttk.Separator(side_panel, orient="horizontal").pack(fill=tk.X, pady=10)
        ttk.Label(side_panel, text="Resize Operations", font=("Arial", 10, "bold")).pack(pady=(0, 5))

        resize_frame = ttk.Frame(side_panel)
        resize_frame.pack(fill=tk.X, pady=5)

        ttk.Label(resize_frame, text="Max Width:").grid(row=0, column=0, sticky="w")
        self.max_width_var = tk.StringVar(value="1920")
        ttk.Entry(resize_frame, textvariable=self.max_width_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(resize_frame, text="Max Height:").grid(row=1, column=0, sticky="w")
        self.max_height_var = tk.StringVar(value="1080")
        ttk.Entry(resize_frame, textvariable=self.max_height_var, width=10).grid(row=1, column=1, padx=5)

        ttk.Button(side_panel, text="Resize Selected",
                   command=self.resize_batch).pack(fill=tk.X, pady=2)

        # Crop operations
        ttk.Separator(side_panel, orient="horizontal").pack(fill=tk.X, pady=10)
        ttk.Label(side_panel, text="Crop Operations", font=("Arial", 10, "bold")).pack(pady=(0, 5))

        crop_frame = ttk.Frame(side_panel)
        crop_frame.pack(fill=tk.X, pady=5)

        ttk.Label(crop_frame, text="Width:").grid(row=0, column=0, sticky="w")
        self.crop_width_var = tk.StringVar(value="800")
        ttk.Entry(crop_frame, textvariable=self.crop_width_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(crop_frame, text="Height:").grid(row=1, column=0, sticky="w")
        self.crop_height_var = tk.StringVar(value="600")
        ttk.Entry(crop_frame, textvariable=self.crop_height_var, width=10).grid(row=1, column=1, padx=5)

        ttk.Button(side_panel, text="Crop Selected (Center)",
                   command=self.crop_batch).pack(fill=tk.X, pady=2)

        # Status label
        self.status_label = ttk.Label(side_panel, text="No folder selected")
        self.status_label.pack(side=tk.BOTTOM, pady=10)

        # Show grid view by default
        self._show_grid_view()

    def _on_canvas_configure(self, event):
        """Handle canvas resize event."""
        if self.view_mode == "grid" and self.images:
            # Recalculate grid layout when canvas is resized
            self._reorganize_grid()

    def _on_frame_configure(self, event):
        """Handle scrollable frame resize event."""
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_thumbnail_size_change(self):
        """Handle thumbnail size change."""
        self.thumbnail_size = self.size_var.get()
        if self.images and self.view_mode == "grid":
            # Reload with new size
            self._load_images()

    def _show_grid_view(self):
        """Show the grid view."""
        self.tree.grid_forget()
        self.tree_scrollbar.grid_forget()
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

    def _show_list_view(self):
        """Show the list view."""
        self.canvas.grid_forget()
        self.v_scrollbar.grid_forget()
        self.h_scrollbar.grid_forget()
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scrollbar.grid(row=0, column=1, sticky="ns")

    def toggle_view_mode(self):
        """Toggle between grid and list view."""
        if self.view_mode == "grid":
            self.view_mode = "list"
            self._show_list_view()
        else:
            self.view_mode = "grid"
            self._show_grid_view()
            if self.images:
                self._reorganize_grid()

    def open_folder(self):
        """Open a folder and load images."""
        folder_path = filedialog.askdirectory(title="Select Folder")
        if folder_path:
            self.current_folder = Path(folder_path)
            self._load_images()

    def _calculate_columns(self):
        """Calculate number of columns based on canvas width."""
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1:  # Canvas not yet rendered
            canvas_width = 800  # Default width

        # Calculate columns based on thumbnail size and padding
        thumb_total_width = self.thumbnail_size + (self.grid_padding * 2)
        columns = max(1, canvas_width // thumb_total_width)
        return columns

    def _load_images(self):
        """Load images from the current folder."""
        if not self.current_folder:
            return

        self.images = []
        self.selected_images.clear()
        self.thumbnails.clear()
        self.thumbnail_frames = []

        # Clear existing views
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.tree.delete(*self.tree.get_children())

        # Find all image files
        for file_path in self.current_folder.iterdir():
            if file_path.is_file() and is_image_file(str(file_path)):
                self.images.append(file_path)

        self.images.sort()
        self.status_label.config(text=f"Found {len(self.images)} images")

        # Load images in a thread to avoid blocking
        threading.Thread(target=self._load_thumbnails, daemon=True).start()

    def _load_thumbnails(self):
        """Load thumbnails for all images."""
        for i, image_path in enumerate(self.images):
            try:
                # Create thumbnail
                img = Image.open(image_path)
                img.thumbnail((self.thumbnail_size, self.thumbnail_size))
                photo = ImageTk.PhotoImage(img)
                self.thumbnails[str(image_path)] = photo

                # Update UI in main thread
                self.parent.after(0, self._add_image_to_view, image_path, i)

            except Exception as e:
                print(f"Error loading {image_path}: {e}")

    def _add_image_to_view(self, image_path, index):
        """Add an image to both grid and list views."""
        # Create frame for thumbnail
        frame = ttk.Frame(self.scrollable_frame, relief=tk.RAISED, borderwidth=1)

        # Thumbnail
        if str(image_path) in self.thumbnails:
            label = tk.Label(frame, image=self.thumbnails[str(image_path)])
            label.pack(padx=5, pady=5)

        # Filename
        filename_label = tk.Label(frame, text=image_path.name[:25], wraplength=self.thumbnail_size)
        filename_label.pack(pady=(0, 5))

        # Make clickable
        frame.bind("<Button-1>", lambda e, p=image_path: self._on_thumbnail_click(p))
        for child in frame.winfo_children():
            child.bind("<Button-1>", lambda e, p=image_path: self._on_thumbnail_click(p))

        # Store references
        frame.image_path = image_path
        self.thumbnail_frames.append(frame)

        # Add to tree
        try:
            img = Image.open(image_path)
            size_str = get_file_size_str(image_path)
            dimensions = f"{img.width}x{img.height}"
            has_metadata = "Yes" if self.metadata_handler.has_metadata(str(image_path)) else "No"

            self.tree.insert("", "end", text=image_path.name,
                             values=(size_str, dimensions, has_metadata),
                             tags=(str(image_path),))
        except Exception as e:
            print(f"Error adding {image_path} to tree: {e}")

        # Reorganize grid if this is the last image
        if index == len(self.images) - 1:
            self.parent.after(0, self._reorganize_grid)

    def _reorganize_grid(self):
        """Reorganize grid layout based on current canvas width."""
        if not self.thumbnail_frames:
            return

        columns = self._calculate_columns()

        # Rearrange all frames in the grid
        for i, frame in enumerate(self.thumbnail_frames):
            row = i // columns
            col = i % columns
            frame.grid(row=row, column=col, padx=self.grid_padding // 2, pady=self.grid_padding // 2)

        # Update scroll region
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_thumbnail_click(self, image_path):
        """Handle thumbnail click."""
        if image_path in self.selected_images:
            self.selected_images.remove(image_path)
        else:
            self.selected_images.add(image_path)
        self._update_selection_display()

    def _on_tree_select(self, event):
        """Handle tree selection change."""
        self.selected_images.clear()
        for item in self.tree.selection():
            tags = self.tree.item(item, "tags")
            if tags:
                self.selected_images.add(Path(tags[0]))
        self._update_selection_display()

    def _update_selection_display(self):
        """Update the visual display of selected items."""
        # Update grid view
        for frame in self.thumbnail_frames:
            if hasattr(frame, 'image_path'):
                if frame.image_path in self.selected_images:
                    frame.config(relief=tk.SUNKEN, borderwidth=3)
                    # Highlight background
                    frame.config(style='Selected.TFrame')
                else:
                    frame.config(relief=tk.RAISED, borderwidth=1)
                    frame.config(style='TFrame')

        # Update status
        self.status_label.config(text=f"Selected {len(self.selected_images)} of {len(self.images)} images")

    def select_all(self):
        """Select all images."""
        self.selected_images = set(self.images)
        self._update_selection_display()

        # Update tree selection
        self.tree.selection_set(self.tree.get_children())

    def clear_selection(self):
        """Clear selection."""
        self.selected_images.clear()
        self._update_selection_display()

        # Clear tree selection
        self.tree.selection_remove(self.tree.get_children())

    def remove_metadata_batch(self):
        """Remove metadata from selected images."""
        if not self.selected_images:
            messagebox.showwarning("No Selection", "Please select images first.")
            return

        if messagebox.askyesno("Confirm", f"Remove metadata from {len(self.selected_images)} images?"):
            success_count = 0
            for image_path in self.selected_images:
                try:
                    self.metadata_handler.remove_all_metadata(str(image_path))
                    success_count += 1
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")

            messagebox.showinfo("Complete", f"Removed metadata from {success_count} images.")
            self._load_images()  # Reload to update metadata status

    def resize_batch(self):
        """Resize selected images."""
        if not self.selected_images:
            messagebox.showwarning("No Selection", "Please select images first.")
            return

        try:
            max_width = int(self.max_width_var.get())
            max_height = int(self.max_height_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid dimensions.")
            return

        if messagebox.askyesno("Confirm", f"Resize {len(self.selected_images)} images?"):
            success_count = 0
            for image_path in self.selected_images:
                try:
                    self.processor.resize_image(str(image_path), max_width, max_height)
                    success_count += 1
                except Exception as e:
                    print(f"Error resizing {image_path}: {e}")

            messagebox.showinfo("Complete", f"Resized {success_count} images.")
            self._load_images()  # Reload to show new dimensions

    def crop_batch(self):
        """Crop selected images."""
        if not self.selected_images:
            messagebox.showwarning("No Selection", "Please select images first.")
            return

        try:
            width = int(self.crop_width_var.get())
            height = int(self.crop_height_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid dimensions.")
            return

        if messagebox.askyesno("Confirm", f"Crop {len(self.selected_images)} images to {width}x{height}?"):
            success_count = 0
            for image_path in self.selected_images:
                try:
                    self.processor.crop_center(str(image_path), width, height)
                    success_count += 1
                except Exception as e:
                    print(f"Error cropping {image_path}: {e}")

            messagebox.showinfo("Complete", f"Cropped {success_count} images.")
            self._load_images()  # Reload to show new dimensions