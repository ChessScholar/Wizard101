import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
import re

class ItemTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Item Tracker")

        # Modern color scheme
        self.bg_color = "#2E3440"
        self.fg_color = "#D8DEE9"
        self.accent_color = "#5E81AC"
        self.entry_bg_color = "#3B4252"
        self.entry_fg_color = "#ECEFF4"
        self.grid_border_color = "#4C566A"

        self.root.configure(bg=self.bg_color)

        # Initialize item list
        self.items = []

        # Create and place widgets
        self.create_widgets()

    def create_widgets(self):
        # Frame for item input
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(padx=10, pady=10)

        tk.Label(input_frame, text="Item Name:", fg=self.fg_color, bg=self.bg_color).grid(row=0, column=0, sticky="w")
        self.item_name_entry = tk.Entry(input_frame, bg=self.entry_bg_color, fg=self.entry_fg_color, relief='flat')
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Quantity Needed:", fg=self.fg_color, bg=self.bg_color).grid(row=1, column=0, sticky="w")
        self.quantity_needed_entry = tk.Entry(input_frame, bg=self.entry_bg_color, fg=self.entry_fg_color, relief='flat')
        self.quantity_needed_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Quantity on Hand:", fg=self.fg_color, bg=self.bg_color).grid(row=2, column=0, sticky="w")
        self.quantity_on_hand_entry = tk.Entry(input_frame, bg=self.entry_bg_color, fg=self.entry_fg_color, relief='flat')
        self.quantity_on_hand_entry.grid(row=2, column=1, padx=5, pady=5)

        self.add_button = tk.Button(input_frame, text="Add Item", command=self.add_item, bg=self.accent_color, fg=self.fg_color, relief='flat')
        self.add_button.grid(row=3, column=0, columnspan=2, pady=5)

        # Frame for displaying items in grid format
        self.items_frame = tk.Frame(self.root, bg=self.bg_color, bd=1, relief="solid")
        self.items_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Add headers for the grid
        headers = ["Image", "Name", "Have", "Need"]
        for i, header in enumerate(headers):
            header_label = tk.Label(self.items_frame, text=header, font=('Arial', 12, 'bold'), fg=self.fg_color, bg=self.bg_color, padx=5, pady=5)
            header_label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
            header_label.config(borderwidth=1, relief="ridge")

        self.items_frame.grid_columnconfigure(0, weight=1, uniform="col")
        self.items_frame.grid_columnconfigure(1, weight=2, uniform="col")
        self.items_frame.grid_columnconfigure(2, weight=1, uniform="col")
        self.items_frame.grid_columnconfigure(3, weight=1, uniform="col")

        # Buttons for item operations
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=5)

        self.delete_button = tk.Button(button_frame, text="Delete Item", command=self.delete_item, bg=self.accent_color, fg=self.fg_color, relief='flat')
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear All", command=self.clear_items, bg=self.accent_color, fg=self.fg_color, relief='flat')
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Menu bar
        menubar = tk.Menu(self.root, bg=self.bg_color, fg=self.fg_color, relief='flat')
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0, bg=self.entry_bg_color, fg=self.entry_fg_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_items)
        file_menu.add_command(label="Load", command=self.load_items)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Frame for file search
        search_frame = tk.Frame(self.root, bg=self.bg_color)
        search_frame.pack(padx=10, pady=10)

        tk.Label(search_frame, text="Search:", fg=self.fg_color, bg=self.bg_color).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, bg=self.entry_bg_color, fg=self.entry_fg_color, relief='flat')
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_file_list)

        self.search_content_var = tk.BooleanVar()
        search_content_check = tk.Checkbutton(search_frame, text="Search Contents", variable=self.search_content_var, fg=self.fg_color, bg=self.bg_color, command=self.update_file_list)
        search_content_check.pack(side=tk.LEFT, padx=5)

        # Add Items button
        self.add_items_button = tk.Button(search_frame, text="Add Items", command=self.add_items_from_file, bg=self.accent_color, fg=self.fg_color, relief='flat')
        self.add_items_button.pack(side=tk.LEFT, padx=5)

        # Listbox to display files
        self.file_listbox = tk.Listbox(self.root, bg=self.entry_bg_color, fg=self.entry_fg_color, relief='flat')
        self.file_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Bind selection event
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        self.populate_file_list()

    def populate_file_list(self):
        # Clear existing items in the listbox
        self.file_listbox.delete(0, tk.END)

        # Scan the exported_data folder and its subfolders for .txt files
        self.file_list = []
        folder_path = "exported_data"
        if os.path.exists(folder_path):
            for root, dirs, files in os.walk(folder_path):
                for filename in files:
                    if filename.endswith(".txt"):
                        file_path = os.path.join(root, filename)
                        self.file_list.append(file_path)
                        print(f"Adding file to list: {file_path}")  # Debug print
                        self.file_listbox.insert(tk.END, os.path.relpath(file_path, folder_path))

    def update_file_list(self, event=None):
        search_term = self.search_entry.get().lower()

        # Clear existing items in the listbox
        self.file_listbox.delete(0, tk.END)

        # Search based on filename or content
        for file_path in self.file_list:
            file_name = os.path.basename(file_path).lower()

            # Check if we're searching content as well
            if self.search_content_var.get():
                try:
                    with open(file_path, 'r') as file:
                        content = file.read().lower()
                        if search_term in file_name or search_term in content:
                            self.file_listbox.insert(tk.END, os.path.relpath(file_path, "exported_data"))
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
            else:
                if search_term in file_name:
                    self.file_listbox.insert(tk.END, os.path.relpath(file_path, "exported_data"))

    def on_file_select(self, event):
        selected_index = self.file_listbox.curselection()
        if not selected_index:
            return
        
        # Get the relative path from the listbox
        relative_path = self.file_listbox.get(selected_index[0])
        folder_path = "exported_data"
        file_path = os.path.join(folder_path, relative_path)
        
        # Debug print to check which file is being read
        print(f"Selected file path: {file_path}")

        # Clear previous content display
        if hasattr(self, 'content_display'):
            self.content_display.destroy()

        self.content_display = tk.Text(self.root, bg=self.entry_bg_color, fg=self.entry_fg_color, wrap='word')
        self.content_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                
                # Define regex patterns for detecting numerical values and web addresses
                url_pattern = re.compile(r'https?://\S+')
                number_pattern = re.compile(r'\d+')
                
                filtered_lines = [
                    line for line in lines 
                    if number_pattern.search(line) and not url_pattern.search(line)
                ]

                # Insert filtered lines into the content_display Text widget
                for line in filtered_lines:
                    self.content_display.insert(tk.END, line)
                
                if not filtered_lines:
                    self.content_display.insert(tk.END, "No relevant content found.")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")

    def add_image(self, index):
        item = self.items[index]
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png")])
        if not image_path:
            messagebox.showerror("Input Error", "Please select an image.")
            return

        item["image_path"] = image_path
        self.update_items_display()

    def add_item(self):
        name = self.item_name_entry.get().strip()
        try:
            needed = int(self.quantity_needed_entry.get().strip())
            on_hand = int(self.quantity_on_hand_entry.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers for quantities.")
            return

        if not name:
            messagebox.showerror("Input Error", "Item name cannot be empty.")
            return

        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png")])
        if not image_path:
            messagebox.showerror("Input Error", "Please select an image.")
            return

        item = {
            "name": name,
            "needed": needed,
            "on_hand": on_hand,
            "image_path": image_path
        }
        self.items.append(item)
        self.update_items_display()

        self.item_name_entry.delete(0, tk.END)
        self.quantity_needed_entry.delete(0, tk.END)
        self.quantity_on_hand_entry.delete(0, tk.END)

    def add_items_from_file(self):
        selected_index = self.file_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a file to add items from.")
            return

        # Get the relative path from the listbox
        relative_path = self.file_listbox.get(selected_index[0])
        folder_path = "exported_data"
        file_path = os.path.join(folder_path, relative_path)

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                
                for line in lines:
                    # Process each line to extract item data
                    parts = line.strip().split(":")
                    if len(parts) == 2:
                        item_name, quantity = parts
                        item_name = item_name.strip()
                        try:
                            quantity = int(quantity.strip())
                            # Check if item already exists
                            existing_item = next((item for item in self.items if item["name"] == item_name), None)
                            if existing_item:
                                existing_item["needed"] += quantity
                            else:
                                # Add new item
                                item = {
                                    "name": item_name,
                                    "needed": quantity,
                                    "on_hand": 0,
                                    "image_path": ""  # Default to empty image path
                                }
                                self.items.append(item)
                        except ValueError:
                            continue  # Skip lines that don't have valid quantity

                self.update_items_display()
                messagebox.showinfo("Success", "Items added successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")
                    
    def update_items_display(self):
        # Clear existing display
        for widget in self.items_frame.winfo_children():
            if widget.grid_info()['row'] != '0':
                widget.destroy()

        # Add headers for new columns if not already added
        headers = ["Image", "Name", "Have", "Need", "Actions"]
        for i, header in enumerate(headers):
            header_label = tk.Label(self.items_frame, text=header, font=('Arial', 12, 'bold'), fg=self.fg_color, bg=self.bg_color, padx=5, pady=5)
            header_label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
            header_label.config(borderwidth=1, relief="ridge")

        # Configure columns
        self.items_frame.grid_columnconfigure(0, weight=1, uniform="col")
        self.items_frame.grid_columnconfigure(1, weight=2, uniform="col")
        self.items_frame.grid_columnconfigure(2, weight=1, uniform="col")
        self.items_frame.grid_columnconfigure(3, weight=1, uniform="col")
        self.items_frame.grid_columnconfigure(4, weight=1, uniform="col")

        # Display items
        for i, item in enumerate(self.items):
            # Display image
            if os.path.exists(item["image_path"]):
                img = Image.open(item["image_path"]).resize((50, 50))
                img = ImageTk.PhotoImage(img)
                img_label = tk.Label(self.items_frame, image=img, bg=self.bg_color)
                img_label.image = img
                img_label.grid(row=i+1, column=0, padx=1, pady=1, sticky="nsew")
            else:
                no_image_label = tk.Label(self.items_frame, text="No Image", bg=self.bg_color, fg=self.fg_color)
                no_image_label.grid(row=i+1, column=0, padx=1, pady=1, sticky="nsew")
                add_image_button = tk.Button(self.items_frame, text="Add Image", command=lambda idx=i: self.add_image(idx), bg=self.accent_color, fg=self.fg_color)
                add_image_button.grid(row=i+1, column=4, padx=1, pady=1, sticky="nsew")

            # Display item name
            tk.Label(self.items_frame, text=item["name"], bg=self.bg_color, fg=self.fg_color).grid(row=i+1, column=1, padx=1, pady=1, sticky="nsew")

            # Display quantity on hand with entry and buttons
            on_hand_frame = tk.Frame(self.items_frame, bg=self.bg_color)
            on_hand_frame.grid(row=i+1, column=2, padx=1, pady=1, sticky="nsew")
            tk.Button(on_hand_frame, text="-", command=lambda idx=i: self.update_quantity(idx, 'on_hand', -1), bg=self.accent_color, fg=self.fg_color, width=2).pack(side=tk.LEFT)
            self.on_hand_entry = tk.Entry(on_hand_frame, bg=self.entry_bg_color, fg=self.entry_fg_color, width=5, justify='center')
            self.on_hand_entry.insert(0, str(item["on_hand"]))
            self.on_hand_entry.pack(side=tk.LEFT)
            self.on_hand_entry.bind("<FocusOut>", lambda event, idx=i: self.update_quantity_from_entry(idx, 'on_hand'))
            tk.Button(on_hand_frame, text="+", command=lambda idx=i: self.update_quantity(idx, 'on_hand', 1), bg=self.accent_color, fg=self.fg_color, width=2).pack(side=tk.LEFT)

            # Display quantity needed with entry and buttons
            needed_frame = tk.Frame(self.items_frame, bg=self.bg_color)
            needed_frame.grid(row=i+1, column=3, padx=1, pady=1, sticky="nsew")
            tk.Button(needed_frame, text="-", command=lambda idx=i: self.update_quantity(idx, 'needed', -1), bg=self.accent_color, fg=self.fg_color, width=2).pack(side=tk.LEFT)
            self.needed_entry = tk.Entry(needed_frame, bg=self.entry_bg_color, fg=self.entry_fg_color, width=5, justify='center')
            self.needed_entry.insert(0, str(item["needed"]))
            self.needed_entry.pack(side=tk.LEFT)
            self.needed_entry.bind("<FocusOut>", lambda event, idx=i: self.update_quantity_from_entry(idx, 'needed'))
            tk.Button(needed_frame, text="+", command=lambda idx=i: self.update_quantity(idx, 'needed', 1), bg=self.accent_color, fg=self.fg_color, width=2).pack(side=tk.LEFT)

    def update_quantity(self, index, field, amount):
        # Update quantity logic
        item = self.items[index]
        if field == 'on_hand':
            item['on_hand'] = max(0, item['on_hand'] + amount)  # Ensure non-negative value
        elif field == 'needed':
            item['needed'] = max(0, item['needed'] + amount)  # Ensure non-negative value
        self.update_items_display()

    def delete_item(self):
        item = self.items[index]
        try:
            if field == 'on_hand':
                item['on_hand'] = max(0, int(self.on_hand_entry.get()))  # Ensure non-negative value
            elif field == 'needed':
                item['needed'] = max(0, int(self.needed_entry.get()))  # Ensure non-negative value
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid integer.")
            return
        self.update_items_display()

    def clear_items(self):
        self.items = []
        self.update_items_display()

    def save_items(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not save_path:
            return

        try:
            with open(save_path, 'w') as file:
                json.dump(self.items, file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    def load_items(self):
        load_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not load_path:
            return

        try:
            with open(load_path, 'r') as file:
                self.items = json.load(file)
                self.update_items_display()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ItemTrackerApp(root)
    root.mainloop()
