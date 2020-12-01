#!/usr/bin/python3

'''
Copyright 2020 Tomas Töws
hello@tomastoews.de
'''

import os, sys, time
import pygame
import pygame.locals

pygame.init()

FIELD_SIZE = 50

size = width, height = FIELD_SIZE*17, FIELD_SIZE*14
fps = 60
pygame.mouse.set_visible(False)

pygame.display.init()
screen = pygame.display.set_mode(size)

WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
border_thickness = 2

CROSS_COLOR = WHITE

all_fields = []
fields = []
map_fields = []
fields_in_elements_panel = []
visible_fields_min_index = 0
visible_fields_max_index = 0

font_1 = "./resources/fonts/Kenney_Mini_Square.ttf"

dragging_field = None
is_dragging = False
field_original_pos = None
field_dragging_id = None
highlighted_field = None

inventary_panel_x = FIELD_SIZE+border_thickness
inventary_panel_y = FIELD_SIZE*3+border_thickness
map_panel_x = FIELD_SIZE*6+border_thickness
map_panel_y = FIELD_SIZE*3+border_thickness

map_start_x = FIELD_SIZE*6+border_thickness
map_end_x = width-FIELD_SIZE-border_thickness
map_start_y = FIELD_SIZE*3+border_thickness
map_end_y = height-FIELD_SIZE-border_thickness

panel_start_x = inventary_panel_x
panel_end_x = inventary_panel_x+(FIELD_SIZE*5)+border_thickness
panel_start_y = inventary_panel_y
panel_end_y = height-(FIELD_SIZE+border_thickness)

textures_path = "./resources/textures/road2"

if border_thickness % 2 != 0:
    raise Exception("border_thickness must be an even number")

class Field(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(self)
        self.x = x
        self.y = y
        self.width = FIELD_SIZE
        self.height = FIELD_SIZE

    def set_image(self, image):
        self.image_path = image
        self.image = pygame.image.load(os.path.join(textures_path, image)).convert()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

def load_fields():
    global all_fields, fields, visible_fields_min_index, visible_fields_max_index
    texture_files = os.listdir(textures_path)
    texture_files.sort()
    row_count = 0
    column_count = 0

    for texture_file in texture_files:
        field = Field(x=0,y=0)
        field.set_image(texture_file)
        all_fields.append(field)
        column_count = column_count + 1
        if column_count == 4:
            column_count = 0
            row_count = row_count + 1

    visible_fields_min_index = 0
    visible_fields_max_index = len(all_fields) if len(all_fields) < 40 else 40
    fields = all_fields[visible_fields_min_index:visible_fields_max_index]

def is_field_within_map(x, y):
    center_point_x = x+(FIELD_SIZE/2)
    center_point_y = y+(FIELD_SIZE/2)

    if center_point_x > map_start_x \
            and center_point_x < map_end_x \
            and center_point_y > map_start_y \
            and center_point_y < map_end_y:
        return True
    else:
        return False

def is_field_within_elements_panel(x, y):
    center_point_x = x+(FIELD_SIZE/2)
    center_point_y = y+(FIELD_SIZE/2)

    if center_point_x > panel_start_x \
            and center_point_x < panel_end_x \
            and center_point_y > panel_start_y \
            and center_point_y < panel_end_y:
        return True
    else:
        return False

def get_nearest_field(x, y):
    # Get nearest map field to coordinates within map
    for map_x in range(10):
        for map_y in range(10):
            map_field_x_start = map_panel_x+(map_x*FIELD_SIZE)
            map_field_x_end = map_panel_x+(map_x*FIELD_SIZE)+FIELD_SIZE
            map_field_y_start = map_panel_y+(map_y*FIELD_SIZE)
            map_field_y_end = map_panel_y+(map_y*FIELD_SIZE)+FIELD_SIZE
            if x+(FIELD_SIZE/2) >= map_field_x_start \
                    and x+(FIELD_SIZE/2) <= map_field_x_end \
                    and y+(FIELD_SIZE/2) >= map_field_y_start \
                    and y+(FIELD_SIZE/2) <= map_field_y_end:
                highlighted_field = (map_field_x_start, map_field_y_start)
                return (map_field_x_start, map_field_y_start)
                break

def set_dragging_field_position(x, y):
    global is_dragging, dragging_field, field_original_pos
    # Check if a field from the elements panel or the map is being moved
    if is_field_within_elements_panel(field_original_pos[0], field_original_pos[1]):
        dragging_field.rect.x = x
        dragging_field.rect.y = y
    else:
        map_fields[field_dragging_id].rect.x = x
        map_fields[field_dragging_id].rect.y = y

def get_dragging_field_position():
    global dragging_field
    # Check if a field from the elements panel or the map is being moved
    if is_field_within_elements_panel(field_original_pos[0], field_original_pos[1]):
        return dragging_field.rect.x, dragging_field.rect.y
    else:
        return map_fields[field_dragging_id].rect.x, map_fields[field_dragging_id].rect.y

def is_map_field_occupied(x, y):
    global map_fields, field_original_pos
    if is_field_within_map(x, y):
        occupied_fields = list(filter(lambda field: field.rect.x == x and field.rect.y == y, map_fields))
        if len(occupied_fields) is not 0:
            # Check if the occupied field is the origin
            if occupied_fields[0].rect.x == field_original_pos[0] and occupied_fields[0].rect.y == field_original_pos[1]:
                return False
            else:
                return True
        else:
            return False
    else:
        return False

def draw():
    global dragging_field, highlighted_field, visible_fields_min_index, visible_fields_max_index, border_thickness

    toolbar_panel = pygame.Rect(FIELD_SIZE, FIELD_SIZE, width-(FIELD_SIZE*2)+(border_thickness*1.5), FIELD_SIZE)
    elements_panel = pygame.Rect(FIELD_SIZE, FIELD_SIZE*3, FIELD_SIZE*4+(border_thickness*1.5), height-FIELD_SIZE*4+(border_thickness*1.5))
    map_panel = pygame.Rect(FIELD_SIZE*6, FIELD_SIZE*3, FIELD_SIZE*10+(border_thickness*1.5), height-FIELD_SIZE*4+(border_thickness*1.5))

    print(f"width: {map_panel.width} | height: {map_panel.height}")

    pygame.draw.rect(screen, WHITE, toolbar_panel, border_thickness)
    pygame.draw.rect(screen, WHITE, elements_panel, border_thickness)
    pygame.draw.rect(screen, WHITE, map_panel, border_thickness)

    # Draw text
    font_file = pygame.font.match_font("Arial")
    font = pygame.font.Font(font_1, 20)
    text = font.render("Scroll Tiles: UP DOWN", 1, WHITE, None)
    text_rect = text.get_rect()
    text_rect.x = FIELD_SIZE+(FIELD_SIZE/2)
    text_rect.y = FIELD_SIZE+(FIELD_SIZE/2)-(text_rect.height/2)
    screen.blit(text, text_rect)

    # Draw element fields
    row_count = 0
    column_count = 0
    for field in fields:
        field.rect.x = inventary_panel_x+(column_count*FIELD_SIZE)
        field.rect.y = inventary_panel_y+(row_count*FIELD_SIZE)
        screen.blit(field.image, field.rect)
        column_count = column_count + 1
        if column_count == 4:
            column_count = 0
            row_count = row_count + 1

    # Draw map fields
    for map_field in map_fields:
        screen.blit(map_field.image, map_field.rect)

    # Draw hightlighted field
    if is_dragging and highlighted_field:
        x, y = get_dragging_field_position()
        if is_field_within_map(x, y):
            h_f = pygame.Rect(highlighted_field[0], highlighted_field[1], FIELD_SIZE, FIELD_SIZE)
            color = RED if is_map_field_occupied(highlighted_field[0], highlighted_field[1]) else GREEN
            pygame.draw.rect(screen, color, h_f, 3)

    # Draw inventary panel grid lines from left to right
    for i in range(1, 10):
        start_line = (inventary_panel_x-(border_thickness/2), inventary_panel_y+FIELD_SIZE*i)
        end_line = (inventary_panel_x+(FIELD_SIZE*4), inventary_panel_y+FIELD_SIZE*i)
        pygame.draw.line(screen, WHITE, start_line, end_line, 2)

    # Draw inventary pabel grid lines from top to bottom
    for i in range(1, 4):
        start_line = (inventary_panel_x+(FIELD_SIZE*i), inventary_panel_y-(border_thickness/2))
        end_line = (inventary_panel_x+(FIELD_SIZE*i), inventary_panel_y+(FIELD_SIZE*10)-(border_thickness/2))
        pygame.draw.line(screen, WHITE, start_line, end_line, 2)

    # Draw dragging field
    if dragging_field:
        screen.blit(dragging_field.image, dragging_field.rect)

    # Draw cursor
    x, y = pygame.mouse.get_pos()
    if is_dragging:
        # Draw dragging graphic
        lines = [
            ((x-(FIELD_SIZE/2), y-(FIELD_SIZE/2)), (x-(FIELD_SIZE/4), y-(FIELD_SIZE/2))),
            ((x+(FIELD_SIZE/4), y-(FIELD_SIZE/2)), (x+(FIELD_SIZE/2), y-(FIELD_SIZE/2))),
            ((x-(FIELD_SIZE/2), y+(FIELD_SIZE/2)), (x-(FIELD_SIZE/4), y+(FIELD_SIZE/2))),
            ((x+(FIELD_SIZE/4), y+(FIELD_SIZE/2)), (x+(FIELD_SIZE/2), y+(FIELD_SIZE/2))),

            ((x-(FIELD_SIZE/2), y-(FIELD_SIZE/2)), (x-(FIELD_SIZE/2), y-(FIELD_SIZE/4))),
            ((x-(FIELD_SIZE/2), y+(FIELD_SIZE/4)), (x-(FIELD_SIZE/2), y+(FIELD_SIZE/2))),
            ((x+(FIELD_SIZE/2), y-(FIELD_SIZE/2)), (x+(FIELD_SIZE/2), y-(FIELD_SIZE/4))),
            ((x+(FIELD_SIZE/2), y+(FIELD_SIZE/4)), (x+(FIELD_SIZE/2), y+(FIELD_SIZE/2))),
        ]
        for line in lines:
            pygame.draw.line(screen, WHITE, line[0], line[1], border_thickness)
    else:
        # Draw Cross
        pygame.draw.line(screen, CROSS_COLOR, (x-15,y), (x+15,y), border_thickness)
        pygame.draw.line(screen, CROSS_COLOR, (x,y-15), (x,y+15), border_thickness)


def events():
    global is_dragging, dragging_field, field_dragging_id, all_fields, fields, map_fields, highlighted_field, field_original_pos, visible_fields_min_index, visible_fields_max_index

    for event in pygame.event.get():
        #print(pygame.event.event_name(event.type))
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if len(all_fields) > 40:
                    if len(all_fields) > visible_fields_max_index + 40:
                        visible_fields_min_index = visible_fields_max_index
                        visible_fields_max_index = visible_fields_max_index + 40
                        fields = all_fields[visible_fields_min_index:visible_fields_max_index]
                    else:
                        visible_fields_min_index = len(all_fields)-40
                        visible_fields_max_index = len(all_fields)
                        fields = all_fields[visible_fields_min_index:visible_fields_max_index]

            if event.key == pygame.K_UP:
                if len(all_fields) > 40:
                    if visible_fields_min_index - 40 > 0:
                        visible_fields_min_index = visible_fields_min_index - 40
                        visible_fields_max_index = visible_fields_min_index + 40
                        fields = all_fields[visible_fields_min_index:visible_fields_max_index]
                    else:
                        visible_fields_min_index = 0
                        visible_fields_max_index = 40
                        fields = all_fields[visible_fields_min_index:visible_fields_max_index]

        if event.type == pygame.MOUSEMOTION:
            if is_dragging:
                mouse_pos = pygame.mouse.get_pos()
                x = mouse_pos[0]-(FIELD_SIZE/2)
                y = mouse_pos[1]-(FIELD_SIZE/2)

                # Place field in center of cursor cross
                set_dragging_field_position(x, y)

                if is_field_within_map(x, y):
                    highlighted_field = get_nearest_field(x, y)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get field that is clicked by the cursor
            if not is_dragging:
                mouse_pos = pygame.mouse.get_pos()

                # Elements panel fields
                for i in range(len(fields)):
                    if fields[i].rect.collidepoint(mouse_pos):
                        x = fields[i].rect.x
                        y = fields[i].rect.y
                        # Copy the field from elements panel to dragging_field
                        dragging_field = Field(x, y)
                        dragging_field.set_image(fields[i].image_path)
                        field_dragging_id = i
                        field_original_pos = (x, y)
                        highlighted_field = (x, y)
                        pygame.mouse.set_pos(x+(FIELD_SIZE/2), y+(FIELD_SIZE/2))
                        is_dragging = True

                # Map fields
                for i in range(len(map_fields)):
                    if map_fields[i].rect.collidepoint(mouse_pos):
                        x = map_fields[i].rect.x
                        y = map_fields[i].rect.y
                        field_dragging_id = i
                        highlighted_field = (x, y)
                        field_original_pos = (x, y)
                        pygame.mouse.set_pos(x+(FIELD_SIZE/2), y+(FIELD_SIZE/2))
                        dragging_field = None
                        is_dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            if is_dragging:
                # Drop field

                x, y = get_dragging_field_position()
                new_coords = get_nearest_field(x, y)

                # Check if the origin position is within the map and if there is already a field in the drop position
                if is_field_within_map(x, y) and not is_map_field_occupied(new_coords[0], new_coords[1]):
                    set_dragging_field_position(x=new_coords[0], y=new_coords[1])

                    # If the fields is from elements panel, add it to map fields and remove dragging field
                    if is_field_within_elements_panel(field_original_pos[0], field_original_pos[1]):
                        map_fields.append(dragging_field)
                # Check if the original position is within the elements panel
                else:
                    if is_field_within_map(field_original_pos[0], field_original_pos[1]):
                        set_dragging_field_position(x=field_original_pos[0], y=field_original_pos[1])

                field_dragging_id = None
                field_original_pos = None
                dragging_field = None
                is_dragging = False

load_fields()

while True:
    screen.fill((0,0,0))
    events()
    draw()
    pygame.display.update()
