import  pygame
from    config import *
import  config as G
import  numpy as np
from    cell import Cell
from    glyph import Glyph
import  random

'''
=============================
NextGlyph
=============================
'''
class NextGlyph:

    '''
    =============================
    __init__
    =============================
    '''
    def __init__(self):
        self.spawn_pos  = (G.well.rect.right + G.cell_w, G.cell_w)
        self.last_glyph = None
        self.duplicates = 0
        self.get_glyph()
        self.reinit()
        self.dirty      = False
        self.used       = False

    '''
    =============================
    reinit
    =============================
    '''
    def reinit(self):
        self.spawn_pos  = (G.well.rect.right + G.cell_w, G.cell_w)
        self.rect       = pygame.Rect(0, 0, 0, 0)
        self.rect_old   = pygame.Rect(0, 0, 0, 0)
        G.dirty_rects.append(self.rect)
        G.dirty_rects.append(self.rect_old)
        if self.glyph:
            self.glyph.rect.topleft = self.spawn_pos
            self.glyph.rect.width   = self.glyph.cells[self.glyph.angle].shape[1]*G.cell_w
            self.glyph.rect.height  = self.glyph.cells[self.glyph.angle].shape[0]*G.cell_w
            self.cell               = Cell(self.glyph.color)
        else:
            self.cell       = None

    '''
    =============================
    update
    =============================
    '''
    def update(self, dt):
        ## save old rect in case we'll need to erase the old glyph
        self.rect_old.topleft   = self.glyph.rect.topleft
        self.rect_old.size      = self.glyph.rect.size

        ## generate new glyph if required
        if self.used: self.get_glyph()

        ## update rects
        if self.dirty:
            self.rect.topleft   = self.glyph.rect.topleft
            self.rect.size      = self.glyph.rect.size
        else:
            self.rect.size      = (0, 0)
            self.rect_old.size  = (0, 0)

    '''
    =============================
    draw
    =============================
    '''
    def draw(self, screen):
        ## erase old glyph
        if self.rect_old.size != (0, 0):
            patch = G.background.subsurface(self.rect_old)
            screen.blit(patch, self.rect_old)

        ## draw current glyph
        cells = np.nditer(self.glyph.cells[self.glyph.angle], flags = ['multi_index'])
        for cell in cells:
            if cell:
                x = self.glyph.rect.left + cells.multi_index[1]*G.cell_w + 1
                y = self.glyph.rect.top  + cells.multi_index[0]*G.cell_w + 1
                screen.blit(self.cell.surface, (x, y))

        ## clear the dirty attribute
        self.dirty = False

    '''
    =============================
    get_glyph
    =============================
    '''
    def get_glyph(self):
        ## do not spawn too many duplicates
        type = random.choice(list(GLYPHS.keys()))
        if self.duplicates < MAX_DUPLICATES:
            if type == self.last_glyph:
                self.duplicates += 1
            else:
                self.duplicates = 0
        else:
            while type == self.last_glyph: type = random.choice(list(GLYPHS.keys()))
            self.duplicates = 0

        self.last_glyph         = type
        angle                   = random.choice([0, 1, 2, 3])
        self.glyph              = Glyph(type, angle)
        self.glyph.rect.topleft = self.spawn_pos
        self.cell               = Cell(self.glyph.color)
        self.used               = False
        self.dirty              = True
