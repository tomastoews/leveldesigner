
def enum(**enums):
    return type('Enum', (), enums)

modes = enum(
    normal_mode="normal_mode",
    field_drag_mode="field_drag_mode",
    field_delete_mode="field_delete_mode",
    ground_fields_edit_mode="ground_fields_edit_mode",
    object_fields_edit_mode="object_fields_edit_mode"
)

cursor_modes = enum(
    normal_mode="normal_mode",
    cross_mode="cross_mode",
    dragging_mode="dragging_mode",
    deleting_mode="deleting_mode"
)

field_types = enum(
    ground="ground",
    object="object"
)