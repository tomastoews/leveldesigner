import os
from io import BytesIO
from constants import textures_path, buttons_path

class ResourceService:

    # Return the binary image data and when loading the image use BytesIO() to create a usable file-like object from that binary data

    def load_button_texture(self, button_name):
        # file = open(os.path.join(buttons_path, button_name), "rb") # buffering=0)
        # return file
        path = os.path.join(buttons_path, button_name)
        file = open(path, "rb")
        return file.read()

    def load_field_texture(self, field_type, texture_name):
        path = os.path.join(f"{textures_path}/{field_type}s", texture_name)
        file = open(path, "rb")
        return file.read()

resource_service = ResourceService()
