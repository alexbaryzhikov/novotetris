import  pygame
from    config import *
import  config as G
import  numpy as np

'''
=============================
Glyph
=============================
'''
class Glyph:

    '''
    =============================
    __init__
    =============================
    '''
    def __init__(self, type, angle):
        self.type           = type
        self.angle          = angle
        self.cells          = [
            np.array(GLYPHS[type][0]),
            np.array(GLYPHS[type][1]),
            np.array(GLYPHS[type][2]),
            np.array(GLYPHS[type][3])]
        self.rect           = pygame.Rect(0, 0, 0, 0)
        self.rect.width     = self.cells[angle].shape[1]*G.cell_w
        self.rect.height    = self.cells[angle].shape[0]*G.cell_w
        self.pos_in_well    = None

    '''
    =============================
    rotate
    =============================
    '''
    def rotate(self, direction='cw'):
        ## update angle
        if direction == 'cw':
            if self.angle < 3:  self.angle += 1
            else:               self.angle = 0
        if direction == 'ccw':
            if self.angle > 0:  self.angle -= 1
            else:               self.angle = 3
        ## update rect size
        self.rect.width     = self.cells[self.angle].shape[1]*G.cell_w
        self.rect.height    = self.cells[self.angle].shape[0]*G.cell_w

    '''
    =============================
    save_pos
    =============================
    '''
    def save_pos(self):
        x = (self.rect.left-G.well.rect.left)//G.cell_w
        y = (self.rect.top-G.well.rect.top)//G.cell_w
        self.pos_in_well = (x, y)
