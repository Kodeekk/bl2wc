import json
import tkinter as tk
from tkinter import ttk
import pyperclip

class MinecraftBlockSelector:
    def __init__(self, root, blocks_data):
        self.root = root
        self.root.title("Minecraft Block Selector")
        self.checked_ids = []
        self.text_sign = "Selected Blocks: "
        self.all_blocks = json.loads(blocks_data)
        self.filtered_blocks = self.all_blocks.copy()

        self.create_widgets()
        self.create_checkboxes()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_var.trace("w", self.filter_blocks)

        self.checkboxes_frame = ttk.Frame(main_frame)
        self.checkboxes_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.checkboxes_frame, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(
            self.checkboxes_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.text_sign_label = ttk.Label(
            main_frame,
            text=self.text_sign,
            wraplength=400
        )
        self.text_sign_label.pack(fill=tk.X, pady=(10, 5))

        set_text_frame = ttk.Frame(main_frame)
        set_text_frame.pack(fill=tk.X, pady=(5, 0))

        self.text_entry = ttk.Entry(set_text_frame)
        self.text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        set_text_button = ttk.Button(
            set_text_frame,
            text="Copy Blocks",
            command=self.set_text_sign
        )
        set_text_button.pack(side=tk.RIGHT)

    def create_checkboxes(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        for block in self.filtered_blocks:
            var = tk.IntVar(value=1 if block['id'] in self.checked_ids else 0)
            cb = ttk.Checkbutton(
                self.scrollable_frame,
                text=f"{block['item']} ({block['id']})",
                variable=var,
                command=lambda b=block['id'], v=var: self.toggle_block(b, v)
            )
            cb.pack(anchor=tk.W, padx=5, pady=2)

    def filter_blocks(self, *args):
        search_term = self.search_var.get().lower()
        if not search_term:
            self.filtered_blocks = self.all_blocks.copy()
        else:
            self.filtered_blocks = [
                block for block in self.all_blocks
                if search_term in block['item'].lower() or search_term in block['id'].lower()
            ]
        self.create_checkboxes()

    def toggle_block(self, block_id, var):
        if var.get() == 1:
            if block_id not in self.checked_ids:
                self.checked_ids.append("minecraft:" + block_id)
        else:
            if block_id in self.checked_ids:
                self.checked_ids.remove("minecraft:" + block_id)
        self.update_text_sign()

    def update_text_sign(self):
        percentage = 100/len(self.checked_ids)
        command = ""
        if command == "":
            command += f"{percentage:.1f}%"
        self.text_sign_label.config(
            text=f"{',{}'.join(self.checked_ids) if self.checked_ids else 'None'}".removeprefix(",")
        )

    def set_text_sign(self):
        # new_text = self.text_entry.get()
        percentage = 100/len(self.checked_ids)
        base = self.text_entry.get() + " "
        command = ""
        for index, block_id in enumerate(self.checked_ids):
            if command == "":
                command += f"{round(percentage)}%"
            command += block_id
            if index != len(self.checked_ids) - 1:
                command += f",{round(percentage)}%"

        out = base + command
        pyperclip.copy(out)
        # if new_text:
        #     self.text_sign = new_text
        #     self.text_sign_label.config(text=self.text_sign)
        #     self.text_entry.delete(0, tk.END)

if __name__ == "__main__":
    with open("./blocks.json", "r") as f:
        blocks_json = f.read()

    root = tk.Tk()
    app = MinecraftBlockSelector(root, blocks_json)
    root.geometry("600x500")
    root.mainloop()
