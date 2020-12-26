#!/usr/bin/python3

'''
Copyright 2020 Tomas Töws
hello@tomastoews.de
'''

import os, sys, io, time
import pygame
import pygame.locals

from enums import modes, cursor_modes
from constants import size, width, height, fps, colors, border_thickness, FIELD_SIZE, BUTTON_SIZE, textures_path, font_1
from elements import Panel, ScrollablePanel, Button, DeleteButton, SaveButton, OpenButton, EditButton, Field
from resource_service import resource_service
from cursor import cursor
import state

pygame.init()

toolbar_panel = None

dragging_field = None
field_original_pos = None
field_dragging_type = None
field_dragging_id = None
highlighted_field = None

ground_fields_panel = None
object_fields_panel = None

def set_mode(new_mode):
    global state
    state.mode = new_mode

def load_fields():
    global state, ground_fields_panel, object_fields_panel

    for field_type in ["ground", "object"]:

        # Load fileds
        texture_files = os.listdir(f"{textures_path}/{field_type}s")
        texture_files.sort()
        row_count = 0
        column_count = 0

        for texture_file in texture_files:
            field = Field(x=0,y=0, width=FIELD_SIZE, height=FIELD_SIZE, field_type=field_type)
            field.set_image(resource_service.load_field_texture(field_type=field_type, texture_name=texture_file))
            test_field = Field(x=0,y=0, width=FIELD_SIZE, height=FIELD_SIZE, field_type=field_type)
            image_data = resource_service.load_field_texture(field_type=field_type, texture_name=texture_file)
            test_field.set_image(image_data)
            test_field_2 = Field(x=0,y=0, width=FIELD_SIZE, height=FIELD_SIZE, field_type=field_type)
            test_field_2.set_image(test_field.image_data)
            if field_type == "ground":
                state.all_ground_fields.append(field)
            elif field_type == "object":
                state.all_object_fields.append(field)
            column_count = column_count + 1
            if column_count == 4:
                column_count = 0
                row_count = row_count + 1

            if field_type == "ground":
                max_fields_count = ground_fields_panel.fields_count_x * ground_fields_panel.fields_count_y
                ground_fields_panel.visible_fields_max_index = len(state.all_ground_fields) if len(state.all_ground_fields) < max_fields_count else max_fields_count
                state.ground_fields = state.all_ground_fields[ground_fields_panel.visible_fields_min_index:ground_fields_panel.visible_fields_max_index]
            elif field_type == "object":
                max_fields_count = object_fields_panel.fields_count_x * object_fields_panel.fields_count_y
                object_fields_panel.visible_fields_max_index = len(state.all_object_fields) if len(state.all_object_fields) < max_fields_count else max_fields_count
                state.object_fields = state.all_object_fields[object_fields_panel.visible_fields_min_index:object_fields_panel.visible_fields_max_index]

def init():
    global state, modes, cursor_modes, cursor, Cursor, toolbar_panel, ground_fields_panel, object_fields_panel, map_panel, modes, mode

    state.mode = modes.normal_mode
    cursor.set_mode(cursor_modes.cross_mode)

    # Init pygame and create screen
    pygame.display.init()
    state.screen = pygame.display.set_mode(size)

    # Create UI elements
    toolbar_panel = Panel(
        x=FIELD_SIZE,
        y=FIELD_SIZE,
        width=width-(FIELD_SIZE*2),
        height=FIELD_SIZE,
        fields_count_x=15,
        fields_count_y=1
    )

    ground_fields_panel = ScrollablePanel(
        x=FIELD_SIZE,
        y=FIELD_SIZE*4,
        width=FIELD_SIZE*4+(border_thickness*1.5),
        height=FIELD_SIZE*4+(border_thickness*1.5), # x + fields count + border_thickness
        fields_count_x=4,
        fields_count_y=4,
        field_type="ground"
    )

    object_fields_panel = ScrollablePanel(
        x=FIELD_SIZE,
        y=FIELD_SIZE*9,
        width=FIELD_SIZE*4+(border_thickness*1.5),
        height=FIELD_SIZE*4+(border_thickness*1.5), # x + fields count + border_thickness
        fields_count_x=4,
        fields_count_y=4,
        field_type="object"
    )

    map_panel = Panel(
        x=FIELD_SIZE*6,
        y=FIELD_SIZE*3,
        width=FIELD_SIZE*10+(border_thickness*1.5),
        height=FIELD_SIZE*10+(border_thickness*1.5),
        fields_count_x=10,
        fields_count_y=10
    )

    button_delete = DeleteButton(
        x=toolbar_panel.x + toolbar_panel.width - (BUTTON_SIZE*1.2),
        y=toolbar_panel.y + (toolbar_panel.height/2) - (BUTTON_SIZE/2),
        width=BUTTON_SIZE,
        height=BUTTON_SIZE
    )
    button_delete.set_image(resource_service.load_button_texture("delete.png"))
    state.buttons.append(button_delete)

    button_save = SaveButton(
        x=toolbar_panel.x + toolbar_panel.width - (BUTTON_SIZE*2.2),
        y=toolbar_panel.y + (toolbar_panel.height/2) - (BUTTON_SIZE/2),
        width=BUTTON_SIZE,
        height=BUTTON_SIZE
    )
    button_save.set_image(resource_service.load_button_texture("save.png"))
    state.buttons.append(button_save)

    button_open = OpenButton(
        x=toolbar_panel.x + toolbar_panel.width - (BUTTON_SIZE*3.2),
        y=toolbar_panel.y + (toolbar_panel.height/2) - (BUTTON_SIZE/2),
        width=BUTTON_SIZE,
        height=BUTTON_SIZE
    )
    button_open.set_image(resource_service.load_button_texture("open.png"))
    state.buttons.append(button_open)

    button_edit = EditButton(
        x=toolbar_panel.x + toolbar_panel.width - (BUTTON_SIZE*4.2),
        y=toolbar_panel.y + (toolbar_panel.height/2) - (BUTTON_SIZE/2),
        width=BUTTON_SIZE,
        height=BUTTON_SIZE
    )
    button_edit.set_image(resource_service.load_button_texture("edit.png"))
    state.buttons.append(button_edit)

    button_ground_fields_panel_scroll_up = Button(
        x=ground_fields_panel.x + (FIELD_SIZE/2) - (BUTTON_SIZE/2),
        y=ground_fields_panel.y - (FIELD_SIZE/2) - (BUTTON_SIZE/2),
        width=BUTTON_SIZE,
        height=BUTTON_SIZE
    )
    button_ground_fields_panel_scroll_up.set_image(resource_service.load_button_texture("up.png"))
    button_ground_fields_panel_scroll_up.set_click_method(ground_fields_panel.scroll_up)
    state.buttons.append(button_ground_fields_panel_scroll_up)

    button_ground_fields_panel_scroll_down = Button(
        x=ground_fields_panel.x + FIELD_SIZE + (FIELD_SIZE/2) - (BUTTON_SIZE/2),
        y=ground_fields_panel.y - (FIELD_SIZE/2) - (BUTTON_SIZE/2),
        width=BUTTON_SIZE,
        height=BUTTON_SIZE
    )
    button_ground_fields_panel_scroll_down.set_image(resource_service.load_button_texture("down.png"))
    button_ground_fields_panel_scroll_down.set_click_method(ground_fields_panel.scroll_down)
    state.buttons.append(button_ground_fields_panel_scroll_down)

    button_object_fields_panel_scroll_up = Button(
        x=object_fields_panel.x + (FIELD_SIZE/2) - (BUTTON_SIZE/2),
        y=object_fields_panel.y - (FIELD_SIZE/2) - (BUTTON_SIZE/2),
        width=BUTTON_SIZE,
        height=BUTTON_SIZE
    )
    button_object_fields_panel_scroll_up.set_image(resource_service.load_button_texture("up.png"))
    button_object_fields_panel_scroll_up.set_click_method(object_fields_panel.scroll_up)
    state.buttons.append(button_object_fields_panel_scroll_up)

    button_object_fields_panel_scroll_down = Button(
        x=object_fields_panel.x + FIELD_SIZE + (FIELD_SIZE/2) - (BUTTON_SIZE/2),
        y=object_fields_panel.y - (FIELD_SIZE/2) - (BUTTON_SIZE/2),
        width=BUTTON_SIZE,
        height=BUTTON_SIZE
    )
    button_object_fields_panel_scroll_down.set_image(resource_service.load_button_texture("down.png"))
    button_object_fields_panel_scroll_down.set_click_method(object_fields_panel.scroll_down)
    state.buttons.append(button_object_fields_panel_scroll_down)

def get_nearest_field(x, y):
    # Get nearest map field to coordinates within map
    for map_x in range(map_panel.fields_count_x):
        for map_y in range(map_panel.fields_count_y):
            map_field_x_start = map_panel.content_start_x+(map_x*FIELD_SIZE)
            map_field_x_end = map_panel.content_start_x+(map_x*FIELD_SIZE)+FIELD_SIZE
            map_field_y_start = map_panel.content_start_y+(map_y*FIELD_SIZE)
            map_field_y_end = map_panel.content_start_y+(map_y*FIELD_SIZE)+FIELD_SIZE
            if x+(FIELD_SIZE/2) >= map_field_x_start \
                    and x+(FIELD_SIZE/2) <= map_field_x_end \
                    and y+(FIELD_SIZE/2) >= map_field_y_start \
                    and y+(FIELD_SIZE/2) <= map_field_y_end:
                highlighted_field = (map_field_x_start, map_field_y_start)
                return (map_field_x_start, map_field_y_start)
                break

def set_dragging_field_position(x, y):
    global state, modes, dragging_field, field_original_pos
    # Check if a field from the elements panel or the map is being moved
    if ground_fields_panel.is_field_within_panel(field_original_pos[0], field_original_pos[1]) or object_fields_panel.is_field_within_panel(field_original_pos[0], field_original_pos[1]):
        dragging_field.rect.x = x
        dragging_field.rect.y = y
    else:
        state.map_fields[field_dragging_type][field_dragging_id].rect.x = x
        state.map_fields[field_dragging_type][field_dragging_id].rect.y = y

def get_dragging_field_position():
    global dragging_field, ground_fields_panel, object_fields_panel
    # Check if a field from the elements panel or the map is being moved
    if ground_fields_panel.is_field_within_panel(field_original_pos[0], field_original_pos[1]) or object_fields_panel.is_field_within_panel(field_original_pos[0], field_original_pos[1]):
        return dragging_field.rect.x, dragging_field.rect.y
    else:
        return state.map_fields[field_dragging_type][field_dragging_id].rect.x, state.map_fields[field_dragging_type][field_dragging_id].rect.y

def is_map_field_occupied(x, y):
    global state, field_original_pos
    if map_panel.is_field_within_panel(x, y):
        # Get field type of the field that is being dragged
        field_type = None
        if not map_panel.is_field_within_panel(field_original_pos[0], field_original_pos[1]):
            field_type = dragging_field.field_type
        else:
            field_type = state.map_fields[field_dragging_type][field_dragging_id].field_type
        # Get map field that is at the current position
        all_fields = []
        all_fields.extend(state.map_fields['object'])
        all_fields.extend(state.map_fields['ground'])
        occupied_fields = list(filter(
            lambda field: field.rect.x == x and field.rect.y == y and field.field_type == field_type,
            all_fields
        ))
        if len(occupied_fields) != 0:
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
    global state, modes, cursor, toolbar_panel, ground_fields_panel, object_fields_panel, map_panel, dragging_field, highlighted_field, border_thickness

    # Draw UI elements
    pygame.draw.rect(state.screen, colors.get("white"), toolbar_panel, border_thickness)
    pygame.draw.rect(state.screen, colors.get("white"), ground_fields_panel, border_thickness)
    pygame.draw.rect(state.screen, colors.get("white"), object_fields_panel, border_thickness)
    pygame.draw.rect(state.screen, colors.get("white"), map_panel, border_thickness)

    # Draw buttons
    for button in state.buttons:
        state.screen.blit(button.image, button.rect)

    mode_text = state.mode.replace("_", " ")

    # Draw text
    font_file = pygame.font.match_font("Arial")
    font = pygame.font.Font(font_1, 20)
    text = font.render(mode_text, 1, colors.get("white"), None)
    text_rect = text.get_rect()
    text_rect.x = FIELD_SIZE+(FIELD_SIZE/2)
    text_rect.y = FIELD_SIZE+(FIELD_SIZE/2)-(text_rect.height/2)
    state.screen.blit(text, text_rect)

    # Draw ground fields
    row_count = 0
    column_count = 0
    for field in state.ground_fields:
        field.rect.x = ground_fields_panel.content_start_x+(column_count*FIELD_SIZE)
        field.rect.y = ground_fields_panel.content_start_y+(row_count*FIELD_SIZE)
        state.screen.blit(field.image, field.rect)
        column_count = column_count + 1
        if column_count == 4:
            column_count = 0
            row_count = row_count + 1

    # Draw object fields
    row_count = 0
    column_count = 0
    for field in state.object_fields:
        field.rect.x = object_fields_panel.content_start_x+(column_count*FIELD_SIZE)
        field.rect.y = object_fields_panel.content_start_y+(row_count*FIELD_SIZE)
        state.screen.blit(field.image, field.rect)
        column_count = column_count + 1
        if column_count == 4:
            column_count = 0
            row_count = row_count + 1

    # Draw map fields
    for map_field in state.map_fields["ground"]:
        state.screen.blit(map_field.image, map_field.rect)
    for map_field in state.map_fields["object"]:
        state.screen.blit(map_field.image, map_field.rect)

    # Draw hightlighted field
    if state.mode == modes.field_drag_mode and highlighted_field:
        x, y = get_dragging_field_position()
        if map_panel.is_field_within_panel(x, y):
            h_f = pygame.Rect(highlighted_field[0], highlighted_field[1], FIELD_SIZE, FIELD_SIZE)
            color = colors.get("red") if is_map_field_occupied(highlighted_field[0], highlighted_field[1]) else colors.get("green")
            pygame.draw.rect(state.screen, color, h_f, 3)

    # Draw ground fields panel grid lines from left to right
    for i in range(1, ground_fields_panel.fields_count_y):
        start_line = (ground_fields_panel.content_start_x-(border_thickness/2), ground_fields_panel.content_start_y+FIELD_SIZE*i)
        end_line = (ground_fields_panel.content_start_x+(FIELD_SIZE*4), ground_fields_panel.content_start_y+FIELD_SIZE*i)
        pygame.draw.line(state.screen, colors.get("white"), start_line, end_line, 2)

    # Draw ground fields pabel grid lines from top to bottom
    for i in range(1, ground_fields_panel.fields_count_x):
        start_line = (ground_fields_panel.x+(FIELD_SIZE*i), ground_fields_panel.content_start_y-(border_thickness/2))
        end_line = (ground_fields_panel.x+(FIELD_SIZE*i), ground_fields_panel.content_start_y+(FIELD_SIZE*object_fields_panel.fields_count_y)-(border_thickness/2))
        pygame.draw.line(state.screen, colors.get("white"), start_line, end_line, 2)

    # Draw object fields panel grid lines from left to right
    for i in range(1, object_fields_panel.fields_count_y):
        start_line = (object_fields_panel.content_start_x-(border_thickness/2), object_fields_panel.content_start_y+FIELD_SIZE*i)
        end_line = (object_fields_panel.content_start_x+(FIELD_SIZE*4), object_fields_panel.content_start_y+FIELD_SIZE*i)
        pygame.draw.line(state.screen, colors.get("white"), start_line, end_line, 2)

    # Draw object fields pabel grid lines from top to bottom
    for i in range(1, object_fields_panel.fields_count_x):
        start_line = (object_fields_panel.x+(FIELD_SIZE*i), object_fields_panel.content_start_y-(border_thickness/2))
        end_line = (object_fields_panel.x+(FIELD_SIZE*i), object_fields_panel.content_start_y+(FIELD_SIZE*object_fields_panel.fields_count_y)-(border_thickness/2))
        pygame.draw.line(state.screen, colors.get("white"), start_line, end_line, 2)

    # Draw dragging field
    if dragging_field:
        state.screen.blit(dragging_field.image, dragging_field.rect)

    # Draw cursor
    cursor.draw()

def events():
    global state, modes, cursor_modes, dragging_field, field_dragging_id, field_dragging_type, highlighted_field, field_original_pos, ground_fields_panel, object_fields_panel, map_panel

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                mouse_pos = pygame.mouse.get_pos()
                if ground_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                    ground_fields_panel.scroll_down()
                elif object_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                    object_fields_panel.scroll_down()

            if event.key == pygame.K_UP:
                mouse_pos = pygame.mouse.get_pos()
                if ground_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                    ground_fields_panel.scroll_up()
                elif object_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                    object_fields_panel.scroll_up()

        if event.type == pygame.MOUSEMOTION:
            if state.mode == modes.field_drag_mode:
                mouse_pos = pygame.mouse.get_pos()
                x = mouse_pos[0]-(FIELD_SIZE/2)
                y = mouse_pos[1]-(FIELD_SIZE/2)

                # Place field in center of cursor cross
                set_dragging_field_position(x=x, y=y)

                if map_panel.is_field_within_panel(x, y):
                    highlighted_field = get_nearest_field(x, y)

            # Check if the cursor is outside or within any panel
            mouse_pos = pygame.mouse.get_pos()
            if state.mode == modes.field_drag_mode:
                cursor.set_mode(cursor_modes.dragging_mode)
            else:
                if map_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                    if state.mode == modes.field_delete_mode:
                        cursor.set_mode(cursor_modes.deleting_mode)
                    else:
                        cursor.set_mode(cursor_modes.cross_mode)
                elif ground_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]) or object_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                    if state.mode == modes.field_drag_mode:
                        cursor.set_mode(cursor_modes.dragging_mode)
                    else:
                        cursor.set_mode(cursor_modes.cross_mode)
                else:
                    cursor.set_mode(cursor_modes.normal_mode)

        if event.type == pygame.MOUSEBUTTONDOWN:

            # Get field that is clicked by the cursor
            if state.mode == modes.normal_mode:
                mouse_pos = pygame.mouse.get_pos()

                if event.button == pygame.BUTTON_WHEELUP:
                    if ground_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                        ground_fields_panel.scroll_up()
                    elif object_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                        object_fields_panel.scroll_up()

                elif event.button == pygame.BUTTON_WHEELDOWN:
                    if ground_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                        ground_fields_panel.scroll_down()
                    elif object_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                        object_fields_panel.scroll_down()

                elif event.button == pygame.BUTTON_LEFT:

                    # Ground & object fields
                    # Determine the panel and drag the field
                    fields = []
                    if ground_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                        fields = state.ground_fields
                    elif object_fields_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                        fields = state.object_fields

                    for i in range(len(fields)):
                        if fields[i].rect.collidepoint(mouse_pos):
                            x = fields[i].rect.x
                            y = fields[i].rect.y
                            # Copy the field from the fields array to dragging_field
                            dragging_field = Field(x=x, y=y, width=FIELD_SIZE, height=FIELD_SIZE, field_type=fields[i].field_type)
                            dragging_field.set_image(fields[i].image_data)
                            field_dragging_id = i
                            field_dragging_type = fields[i].field_type
                            field_original_pos = (x, y)
                            highlighted_field = (x, y)
                            pygame.mouse.set_pos(x+(FIELD_SIZE/2), y+(FIELD_SIZE/2))
                            state.mode = modes.field_drag_mode
                            cursor.set_mode(cursor_modes.dragging_mode)
                            break

                    # Map fields

                    dragging_field_set = False
                    for field_type in ["object", "ground"]:
                        if not dragging_field_set:
                            for i in range(len(state.map_fields[field_type])):
                                if state.map_fields[field_type][i].rect.collidepoint(mouse_pos):
                                    dragging_field_set = True
                                    print("Drag Field: " + field_type)
                                    x = state.map_fields[field_type][i].rect.x
                                    y = state.map_fields[field_type][i].rect.y
                                    field_dragging_id = i
                                    field_dragging_type = state.map_fields[field_type][i].field_type
                                    highlighted_field = (x, y)
                                    field_original_pos = (x, y)
                                    pygame.mouse.set_pos(x+(FIELD_SIZE/2), y+(FIELD_SIZE/2))
                                    dragging_field = None
                                    state.mode = modes.field_drag_mode
                                    cursor.set_mode(cursor_modes.dragging_mode)
                                    break

            elif state.mode == modes.field_delete_mode:
                if event.button == pygame.BUTTON_LEFT:
                    mouse_pos = pygame.mouse.get_pos()
                    # If in deleting mode, delete the field that is colliding with the cursor
                    if  map_panel.is_point_within_panel(mouse_pos[0], mouse_pos[1]):
                        field_removed = False
                        # First check all object fields. If an object field was found, remove it and stop to prevent deleting the underlaying ground field
                        for field_type in ["object", "ground"]:
                            if not field_removed:
                                for i in range(len(state.map_fields[field_type])):
                                    if state.map_fields[field_type][i].rect.collidepoint(mouse_pos):
                                        state.map_fields[field_type].pop(i)
                                        field_removed = True
                                        break

            # Buttons
            if not state.mode == modes.field_drag_mode:
                mouse_pos = pygame.mouse.get_pos()
                for button in state.buttons:
                    if button.rect.collidepoint(mouse_pos):
                        button.click_event()


        if event.type == pygame.MOUSEBUTTONUP and event.button != pygame.BUTTON_WHEELDOWN and event.button != pygame.BUTTON_WHEELUP:
            if state.mode == modes.field_drag_mode:
                # Drop field

                x, y = get_dragging_field_position()
                new_coords = get_nearest_field(x, y)

                # Check if the origin position is within the map and if there is already a field in the drop position
                if map_panel.is_field_within_panel(x, y) and not is_map_field_occupied(new_coords[0], new_coords[1]):
                    set_dragging_field_position(x=new_coords[0], y=new_coords[1])
                    # If the fields is from elements panel, add it to map fields and remove dragging field
                    if not map_panel.is_field_within_panel(field_original_pos[0], field_original_pos[1]):
                        state.map_fields[field_dragging_type].append(dragging_field)
                # Check if the original position is within the elements panel
                else:
                    if map_panel.is_field_within_panel(field_original_pos[0], field_original_pos[1]):
                        set_dragging_field_position(x=field_original_pos[0], y=field_original_pos[1])

                field_dragging_id = None
                field_dragging_type = None
                field_original_pos = None
                dragging_field = None
                state.mode = modes.normal_mode
                cursor.set_mode(cursor_modes.cross_mode)

init()
load_fields()

while True:
    state.screen.fill((0,0,0))
    events()
    draw()
    pygame.display.update()
    # print(state.mode)
    # print(cursor.mode)
