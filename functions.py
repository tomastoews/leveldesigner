import os, io, json, base64
from tkinter import Tk, filedialog, messagebox, simpledialog
import state
from enums import modes
from constants import FIELD_SIZE
import elements

tk_root = Tk()
# tk_root.overridecolors.redirect(1)
tk_root.withdraw()

def switch_field_delete_mode():
    global state, modes
    print(state.mode)
    state.mode = modes.field_delete_mode if state.mode == modes.normal_mode else modes.normal_mode

def save_level():
    global state, modes
    state.mode = modes.normal_mode
    if len(state.map_fields["ground"]) == 0 and len(state.map_fields["object"]) == 0:
        messagebox.showwarning("", "There are no fields on the map.")
        return None

    # Ask for level name
    level_name = ""
    while level_name == "":
        level_name = simpledialog.askstring(
            title="Level name",
            prompt="Please enter a name for this level",
            initialvalue=state.loaded_level.get("name")
        ) # ok_event=

    file_path = filedialog.asksaveasfilename(initialfile=state.loaded_level.get("file_location"))

    level = dict({
        "name": level_name,
        "fields": {
            "ground": [],
            "object": []
        }
    })

    for field_type in ["ground", "object"]:
        for field in state.map_fields[field_type]:

            # Binary -> base64
            image_data_base64 = base64.b64encode(field.image_data)
            # base64 -> String
            image_data_string = base64.b64encode(image_data_base64).decode('utf-8')

            new_field = dict({
                "x": field.rect.x,
                "y": field.rect.y,
                "image_data": image_data_string
            })
            level["fields"][field_type].append(new_field)

    json_data = json.dumps(level)
    save_file = open(file_path, "w")
    save_file.write(json_data)
    save_file.close()

def open_level():
    global state, modes

    file_path = filedialog.askopenfilename()

    if file_path:
        level_file = open(file_path, "r")
        level_data = dict(json.loads(level_file.read()))

        # Set level data
        state.is_level_loaded = True
        state.loaded_level["name"] = level_data.get("name")
        state.loaded_level["file_location"] = file_path

        # Clear map fields
        state.map_fields["ground"].clear()
        state.map_fields["object"].clear()

        # Load map fields
        for field_type in level_data.get("fields"):
            for field_data in level_data["fields"][field_type]:
                field = elements.Field(x=field_data["x"], y=field_data["y"], width=FIELD_SIZE, height=FIELD_SIZE, field_type=field_type)

                # String -> base64
                image_data_base64 = base64.b64decode(field_data["image_data"])
                # base64 -> Binary
                image_data_binary = base64.b64decode(image_data_base64)
                field.set_image(image_data_binary)

                state.map_fields[field_type].append(field)
