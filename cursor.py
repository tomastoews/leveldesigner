import pygame
from enums import modes, cursor_modes
from constants import colors, border_thickness, FIELD_SIZE, BUTTON_SIZE
import state

class Cursor:

    def __init__(self):
        self.color = colors.get("white")
        self.mode = cursor_modes.normal_mode

    def set_mode(self, mode):
        global cursor_modes
        self.mode = mode
        if not self.mode == cursor_modes.normal_mode:
            pygame.mouse.set_visible(False) 

    def draw(self):
        global state, modes, cursor_modes
        x, y = pygame.mouse.get_pos()

        if self.mode == cursor_modes.normal_mode:
            # Show system cursor
            pygame.mouse.set_visible(True)

        elif self.mode == cursor_modes.cross_mode:
            # Draw cross graphic
            pygame.draw.line(state.screen, self.color, (x-15,y), (x+15,y), border_thickness)
            pygame.draw.line(state.screen, self.color, (x,y-15), (x,y+15), border_thickness)

        elif self.mode == cursor_modes.dragging_mode:
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
                pygame.draw.line(state.screen, colors.get("white"), line[0], line[1], border_thickness)

        elif self.mode == cursor_modes.deleting_mode:
            # Draw a red X
            lines = [
                ((x-15, y-15), (x+15, y+15)),
                ((x+15, y-15), (x-15, y+15))
            ]
            for line in lines:
                pygame.draw.line(state.screen, colors.get("red"), line[0], line[1], border_thickness)

cursor = Cursor()
