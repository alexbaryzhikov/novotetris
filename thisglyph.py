import  pygame
from    config import *
import  config as G
import  numpy as np
from    cell import Cell
from    glyph import Glyph

'''
=============================
ThisGlyph
=============================
'''
class ThisGlyph:

    '''
    =============================
    __init__
    =============================
    '''
    def __init__(self):
        self.spawn_pos      = (G.well.rect.left + G.cell_w*(WELL_W//2-1), G.well.rect.top)
        self.glyph          = None
        self.reinit()
        self.dirty          = False
        ## actions
        self.move_left      = False
        self.move_left_now  = False
        self.move_right     = False
        self.move_right_now = False
        self.rotate         = False
        self.drop           = False
        ## movement repeat control
        self._mov_left      = False
        self._mov_right     = False
        self._mov_time      = 0
        self._delay         = True

    '''
    =============================
    reinit
    =============================
    '''
    def reinit(self):
        self.cell           = Cell()
        self.spawn_pos      = (G.well.rect.left + G.cell_w*(WELL_W//2-1), G.well.rect.top)
        self.rect           = pygame.Rect(0, 0, 0, 0)
        self.rect_old       = pygame.Rect(0, 0, 0, 0)
        G.dirty_rects.append(self.rect)
        G.dirty_rects.append(self.rect_old)
        if self.glyph:
            self.glyph.rect.left    = G.well.rect.left + self.glyph.pos_in_well[0]*G.cell_w
            self.glyph.rect.top     = G.well.rect.top  + self.glyph.pos_in_well[1]*G.cell_w
            self.glyph.rect.width   = self.glyph.cells[self.glyph.angle].shape[1]*G.cell_w
            self.glyph.rect.height  = self.glyph.cells[self.glyph.angle].shape[0]*G.cell_w

    '''
    =============================
    update
    =============================
    '''
    def update(self, dt):
        ## generate repeated movement
        self.generate_move(dt)

        # glyph guardian
        if not self.glyph: self.get_glyph()

        ## save old rect in case we'll need to erase the old glyph
        self.match_rect_to_glyph(self.rect_old)

        ## actions
        if self.drop        : self.drop_glyph()
        if self.rotate      : self.rorate_glyph()
        if self._mov_left   : self.move_glyph_left()
        if self._mov_right  : self.move_glyph_right()

        ## on tick edge or drop glyph either moves down or gets placed
        if G.tick_edge or self.drop: self.fall_or_place()

        ## update rects
        if self.dirty:
            self.match_rect_to_glyph(self.rect)
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
            patch_rect          = self.rect_old.copy()
            patch_rect.left     -= G.well.rect.left
            patch_rect.top      -= G.well.rect.top
            patch               = G.well.surface.subsurface(patch_rect)
            screen.blit(patch, self.rect_old)

        if self.glyph.rect.top < 0:
            ## draw part of the glyph
            row = abs(self.glyph.rect.top)//G.cell_w
            cells = np.nditer(self.glyph.cells[self.glyph.angle][row:], flags = ['multi_index'])
            for cell in cells:
                if cell:
                    x = self.glyph.rect.left + cells.multi_index[1]*G.cell_w + 1
                    y = cells.multi_index[0]*G.cell_w + 1
                    screen.blit(self.cell.surface, (x, y))
        else:
            ## draw full glyph
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
        ## create glyph
        type                    = G.next_glyph.glyph.type
        angle                   = G.next_glyph.glyph.angle
        self.glyph              = Glyph(type, angle)
        self.glyph.rect.topleft = self.spawn_pos
        ## offset horizontal 'I'
        if self.glyph.rect.width//G.cell_w == 4: self.glyph.rect.left -= G.cell_w
        ## set flags
        G.next_glyph.used       = True
        self.dirty              = True
        ## check collision on spawn
        if self.collision(0, 0, 0):
            G.state = 'finished'
            G.message.set_text('game over', 'press enter')
            G.highscores.add(G.score)

    '''
    =============================
    fall_or_place
    =============================
    '''
    def fall_or_place(self):
        self.drop   = False
        self.dirty  = True
        if self.collision(0, 1):
            ## place
            left, top, right, bot = self.get_position()
            top += 2; bot += 2
            G.well.cells[top:bot+1,left:right+1] |= self.glyph.cells[self.glyph.angle]
            ## get new glyph
            self.get_glyph()
        else:
            ## fall
            self.glyph.rect.top += G.cell_w

    '''
    =============================
    drop_glyph
    =============================
    '''
    def drop_glyph(self):
        i = 0
        while not self.collision(0, i): i += 1
        self.glyph.rect.top += (i-1)*G.cell_w

    '''
    =============================
    move_glyph_left
    =============================
    '''
    def move_glyph_left(self):
        self._mov_left          = False
        if not self.collision(-1, 0):
            self.glyph.rect.left    -= G.cell_w
            self.dirty              = True

    '''
    =============================
    move_glyph_right
    =============================
    '''
    def move_glyph_right(self):
        self._mov_right         = False
        if not self.collision(1, 0):
            self.glyph.rect.left    += G.cell_w
            self.dirty              = True

    '''
    =============================
    rorate_glyph
    =============================
    '''
    def rorate_glyph(self):
        self.rotate             = False

        if   self.glyph.type == 'O': pass
        
        elif self.glyph.type == 'I':
            if self.glyph.angle in (0, 2) and not self.collision(2, -2, 1):
                self.glyph.rotate()
                self.glyph.rect.left += G.cell_w*2
                self.glyph.rect.top  -= G.cell_w*2
                self.dirty = True
            elif self.glyph.angle in (1, 3) and not self.collision(-2, 2, 1):
                self.glyph.rotate()
                self.glyph.rect.left -= G.cell_w*2
                self.glyph.rect.top  += G.cell_w*2
                self.dirty = True

        elif self.glyph.type in ('J', 'L', 'T'):
            if self.glyph.angle == 0 and not self.collision(0, -1, 1):
                self.glyph.rotate()
                self.glyph.rect.top  -= G.cell_w
                self.dirty = True
            elif self.glyph.angle == 1 and not self.collision(0, 0, 1):
                self.glyph.rotate()
                self.dirty = True
            elif self.glyph.angle == 2 and not self.collision(1, 0, 1):
                self.glyph.rotate()
                self.glyph.rect.left += G.cell_w
                self.dirty = True
            elif self.glyph.angle == 3 and not self.collision(-1, 1, 1):
                self.glyph.rotate()
                self.glyph.rect.left -= G.cell_w
                self.glyph.rect.top  += G.cell_w
                self.dirty = True

        elif self.glyph.type == 'S':
            if self.glyph.angle in (0, 2) and not self.collision(0, -1, 1):
                self.glyph.rotate()
                self.glyph.rect.top  -= G.cell_w
                self.dirty = True
            elif self.glyph.angle in (1, 3) and not self.collision(0, 1, 1):
                self.glyph.rotate()
                self.glyph.rect.top  += G.cell_w
                self.dirty = True

        elif self.glyph.type == 'Z':
            if self.glyph.angle in (0, 2) and not self.collision(1, -1, 1):
                self.glyph.rotate()
                self.glyph.rect.left += G.cell_w
                self.glyph.rect.top  -= G.cell_w
                self.dirty = True
            elif self.glyph.angle in (1, 3) and not self.collision(-1, 1, 1):
                self.glyph.rotate()
                self.glyph.rect.left -= G.cell_w
                self.glyph.rect.top  += G.cell_w
                self.dirty = True

    '''
    =============================
    generate_move
    =============================
    '''
    def generate_move(self, dt):
        if not (self.move_left or self.move_right):
            self._delay     = True
            self._mov_time  = 0
        else:
            if self.move_left_now:
                self.move_left_now  = False
                self._mov_left      = True
            elif self.move_right_now:
                self.move_right_now = False
                self._mov_right     = True
            elif self._delay and self._mov_time > MOVE_DELAY:
                self._delay         = False
                self._mov_time      = 0
                if self.move_left : self._mov_left  = True
                if self.move_right: self._mov_right = True
            elif not self._delay and self._mov_time > MOVE_INTERVAL:
                self._mov_time      = 0
                if self.move_left : self._mov_left  = True
                if self.move_right: self._mov_right = True
            else:
                self._mov_time += dt

    '''
    =============================
    match_rect_to_glyph
    =============================
    '''
    def match_rect_to_glyph(self, rect):
        if self.glyph.rect.top < 0:
            rect.top       = 0
            rect.left      = self.glyph.rect.left
            rect.height    = self.glyph.rect.height + self.glyph.rect.top
            rect.width     = self.glyph.rect.width
        else:
            rect.topleft   = self.glyph.rect.topleft
            rect.size      = self.glyph.rect.size

    '''
    =============================
    get_position
    =============================
    '''
    def get_position(self, a=None):
        if a is None: a = self.glyph.angle
        left    = (self.glyph.rect.left - G.well.rect.left)//G.cell_w
        top     = (self.glyph.rect.top  - G.well.rect.top )//G.cell_w
        right   = left + self.glyph.cells[a].shape[1] - 1 
        bot     = top  + self.glyph.cells[a].shape[0] - 1
        return left, top, right, bot

    '''
    =============================
    collision
    =============================
    '''
    def collision(self, x, y, a=0):
        '''(x, y) is position offset, a is angle offset in [-1, 0, 1]'''
        if   self.glyph.angle+a > 3: a = 0
        elif self.glyph.angle+a < 0: a = 3
        else: a += self.glyph.angle
        left, top, right, bot = self.get_position(a)
        left += x; right += x
        top  += y; bot   += y
        ## check well boundary
        if left < 0 or right > WELL_W-1 or bot > WELL_H-1: return True
        ## check well contents
        top += 2; bot += 2
        return (G.well.cells[top:bot+1,left:right+1] & self.glyph.cells[a]).any()
