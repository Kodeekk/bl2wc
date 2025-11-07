import json
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

class MinecraftBlockSelector(Gtk.Window):
    def __init__(self, blocks_data):
        Gtk.Window.__init__(self, title="Minecraft Block Selector")
        self.set_default_size(600, 500)
        self.checked_ids = []
        self.text_sign = "Selected Blocks: "
        self.all_blocks = json.loads(blocks_data)
        self.filtered_blocks = self.all_blocks.copy()
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.set_margin_top(10)
        self.main_box.set_margin_bottom(10)
        self.main_box.set_margin_start(10)
        self.main_box.set_margin_end(10)
        self.add(self.main_box)
        self.create_search_bar()
        self.create_blocks_list()
        self.create_bottom_controls()

    def create_search_bar(self):
        search_box = Gtk.Box(spacing=5)
        self.main_box.pack_start(search_box, False, False, 0)

        search_label = Gtk.Label(label="Search:")
        search_box.pack_start(search_label, False, False, 0)

        self.search_entry = Gtk.Entry()
        self.search_entry.connect("changed", self.on_search_changed)
        search_box.pack_start(self.search_entry, True, True, 0)

    def create_blocks_list(self):
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.main_box.pack_start(scrolled_window, True, True, 0)
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled_window.add(self.list_box)

        self.update_blocks_list()

    def create_bottom_controls(self):
        self.selection_label = Gtk.Label(label=self.text_sign)
        self.selection_label.set_line_wrap(True)
        self.selection_label.set_xalign(0)
        self.main_box.pack_start(self.selection_label, False, False, 0)

        copy_box = Gtk.Box(spacing=5)
        self.main_box.pack_start(copy_box, False, False, 0)

        self.text_entry = Gtk.Entry()
        copy_box.pack_start(self.text_entry, True, True, 0)

        copy_button = Gtk.Button(label="Copy Blocks")
        copy_button.connect("clicked", self.on_copy_clicked)
        copy_box.pack_start(copy_button, False, False, 0)

    def update_blocks_list(self):
        for child in self.list_box.get_children():
            self.list_box.remove(child)

        for block in self.filtered_blocks:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(spacing=5)
            row.add(box)

            checkbox = Gtk.CheckButton()
            checkbox.set_active(block['id'] in self.checked_ids)
            checkbox.connect("toggled", self.on_checkbox_toggled, block['id'])
            box.pack_start(checkbox, False, False, 0)

            label = Gtk.Label(label=f"{block['item']} ({block['id']})")
            label.set_xalign(0)
            box.pack_start(label, True, True, 0)

            self.list_box.add(row)

        self.list_box.show_all()

    def on_search_changed(self, entry):
        search_term = entry.get_text().lower()
        if not search_term:
            self.filtered_blocks = self.all_blocks.copy()
        else:
            self.filtered_blocks = [
                block for block in self.all_blocks
                if search_term in block['item'].lower() or search_term in block['id'].lower()
            ]
        self.update_blocks_list()

    def on_checkbox_toggled(self, checkbox, block_id):
        full_id = "minecraft:" + block_id
        if checkbox.get_active():
            if full_id not in self.checked_ids:
                self.checked_ids.append(full_id)
        else:
            if full_id in self.checked_ids:
                self.checked_ids.remove(full_id)
        self.update_selection_label()

    def update_selection_label(self):
        if not self.checked_ids:
            self.selection_label.set_text("None")
            return

        percentage = 100/len(self.checked_ids)
        command = f"{percentage:.1f}%"
        self.selection_label.set_text(f"{','.join(self.checked_ids)}")

    def on_copy_clicked(self, button):
        if not self.checked_ids:
            return

        percentage = 100/len(self.checked_ids)
        base = self.text_entry.get_text() + " "
        command = f"{round(percentage)}%"

        for index, block_id in enumerate(self.checked_ids):
            command += block_id
            if index != len(self.checked_ids) - 1:
                command += f",{round(percentage)}%"

        out = base + command
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(out, -1)
        clipboard.store()
if __name__ == "__main__":
    with open("./blocks.json", "r") as f:
        blocks_json = f.read()

    win = MinecraftBlockSelector(blocks_json)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
