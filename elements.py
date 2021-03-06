import os
from io import BytesIO
import pygame
import state
from enums import modes, field_types
from constants import buttons_path, textures_path, border_thickness, BUTTON_SIZE, FIELD_SIZE
from functions import switch_field_delete_mode, save_level, open_level

class Panel(pygame.Rect):
    def __init__(self, x, y, width, height, fields_count_x, fields_count_y):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fields_count_x = fields_count_x
        self.fields_count_y = fields_count_y
        self.content_start_x = x+border_thickness
        self.content_end_x = x+(FIELD_SIZE*self.fields_count_x)+border_thickness
        self.content_start_y = y+border_thickness
        self.content_end_y = self.content_start_y+(FIELD_SIZE*self.fields_count_y)+border_thickness

    def is_point_within_panel(self, x, y):
        if x > self.content_start_x \
                and x < self.content_end_x \
                and y > self.content_start_y \
                and y < self.content_end_y:
            return True
        else:
            return False

    def is_field_within_panel(self, x, y):
        center_point_x = x+(FIELD_SIZE/2)
        center_point_y = y+(FIELD_SIZE/2)
        if center_point_x > self.content_start_x \
                and center_point_x < self.content_end_x \
                and center_point_y > self.content_start_y \
                and center_point_y < self.content_end_y:
            return True
        else:
            return False

class ScrollablePanel(Panel):
    def __init__(self, x, y, width, height, fields_count_x, fields_count_y, field_type):
        super().__init__(x, y, width, height, fields_count_x, fields_count_y)
        self.visible_fields_min_index = 0
        self.visible_fields_max_index = 0
        self.field_type = field_type

    def scroll_up(self):
        global state
        max_field_count = self.fields_count_x * self.fields_count_y
        fields = state.all_ground_fields if self.field_type == "ground" else state.all_object_fields
        if len(fields) > max_field_count:
            if self.visible_fields_min_index - max_field_count > 0:
                self.visible_fields_min_index = self.visible_fields_min_index - (max_field_count+1)
                self.visible_fields_max_index = self.visible_fields_min_index + max_field_count
            else:
                self.visible_fields_min_index = 0
                self.visible_fields_max_index = max_field_count
            if self.field_type == "ground":
                state.ground_fields = state.all_ground_fields[self.visible_fields_min_index:self.visible_fields_max_index]
            elif self.field_type == "object":
                state.object_fields = state.all_object_fields[self.visible_fields_min_index:self.visible_fields_max_index]

    def scroll_down(self):
        global state
        max_field_count = self.fields_count_x * self.fields_count_y
        fields = state.all_ground_fields if self.field_type == "ground" else state.all_object_fields
        if len(fields) > max_field_count:
            if len(fields) > self.visible_fields_max_index + max_field_count:
                self.visible_fields_min_index = self.visible_fields_max_index
                self.visible_fields_max_index = self.visible_fields_max_index + max_field_count
            else:
                if not self.visible_fields_max_index == len(fields):
                    self.visible_fields_min_index = self.visible_fields_max_index + 1
                    self.visible_fields_max_index = len(fields)
            if self.field_type == "ground":
                state.ground_fields = state.all_ground_fields[self.visible_fields_min_index:self.visible_fields_max_index]
            elif self.field_type == "object":
                state.object_fields = state.all_object_fields[self.visible_fields_min_index:self.visible_fields_max_index]

class Button(pygame.Rect):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def set_image(self, image_data):
        self.image_data = image_data
        self.image = pygame.image.load(BytesIO(self.image_data)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def set_click_method(self, click_method):
        self.click_method = click_method

    def click_event(self):
        if self.click_method:
            self.click_method()

class DeleteButton(Button):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def click_event(self):
        switch_field_delete_mode()

class SaveButton(Button):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def click_event(self):
        global save_level
        save_level()

class OpenButton(Button):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def click_event(self):
        global save_level
        open_level()

class Field(pygame.Rect):
    def __init__(self, x, y, width, height, field_type):
        super().__init__(x, y, width, height)
        # self.x = x
        # self.y = y
        self.width = FIELD_SIZE
        self.height = FIELD_SIZE
        self.field_type = field_type
        if self.field_type == field_types.object:
            self.object_type = "Collidable"

    def set_object_type(self, object_type):
        if self.field_type == field_types.object:
            self.object_type = object_type
            print(f"Updated object type: {self.object_type}")

    def set_location(self, x, y):
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

    def set_image(self, image_data):
        self.image_data = image_data
        self.image = pygame.image.load(BytesIO(self.image_data)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Window(pygame.Rect):
    