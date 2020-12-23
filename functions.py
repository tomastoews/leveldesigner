import state
from enums import modes

def switch_field_delete_mode():
    global state, modes
    print(state.mode)
    state.mode = modes.field_delete_mode if state.mode == modes.normal_mode else modes.normal_mode
