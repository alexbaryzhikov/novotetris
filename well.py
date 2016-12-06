import  pygame
from    pygame.locals import *
from    config import *
import  config as G
import  numpy as np
from    cell import Cell
import  time
from    utilities import get_bg

'''
=============================
Well
=============================
'''
class Well:

    '''
    =============================
    __init__
    =============================
    '''
    def __init__(self):
        self.reinit()
        ## cell arrays
        self.cells          = np.zeros((WELL_H+2, WELL_W), dtype = 'int8')
        self.cells_old      = self.cells.copy()
        self.full_rows      = []
        ## flags
        self.dirty          = False
        self.clear_rows     = False
        self.clear_rows_vis = False

    '''
    =============================
    reinit
    =============================
    '''
    def reinit(self):
        self.cell           = Cell()
        self.background     = get_bg(WELL_W, WELL_H, WELL_COLOR1, WELL_COLOR2)
        self.surface        = self.background.copy()
        self.rect           = self.surface.get_rect()
        _left               = (G.screen.get_rect().width - self.rect.width)//2
        _left               -= _left % G.cell_w
        self.rect.topleft   = (_left, 0)
        self.dirty_rect     = self.rect.copy()
        self.dirty_cells    = [-1, -1, -1, -1] # left, top, right, bottom
        G.dirty_rects.append(self.dirty_rect)

    '''
    =============================
    reset
    =============================
    '''
    def reset(self):
        self.cells.fill(0)
        self.cells_old = self.cells.copy()
        self.full_rows      = []
        self.clear_rows     = False
        self.clear_rows_vis = False

    '''
    =============================
    update
    =============================
    '''
    def update(self, dt):
        if self.clear_rows:
            ## remove full rows
            self.clear_rows     = False
            self.clear_rows_vis = True
            self.full_rows = []
            for i in range(WELL_H+2):
                if self.cells[i].all():
                    self.full_rows.append(i)
                    self.cells[1:i+1] = self.cells[0:i]
                    self.cells[0] = 0
            ## increase score, level and speed
            G.lines += len(self.full_rows)
            G.score += SCORE_POINTS[len(self.full_rows)-1]
            if G.level < 10 and G.score >= LEVEL_SCORES[G.level+1]:
                G.level         += 1
                G.level_speed   = SPEED_LEVELS[G.level]
                G.speed         = G.level_speed
        else:
            ## detect full rows
            for i in range(WELL_H+2):
                if self.cells[i].all(): self.clear_rows = True; break

        ## search dirty cells
        top, left, bottom, right = None, None, None, None
        dirty = False
        
        cells = np.nditer((self.cells[2:], self.cells_old[2:]), flags=['multi_index'])
        for cell, cell_old in cells:
            if cell == cell_old: continue
            if not dirty: top, left = bottom, right = cells.multi_index
            if   cells.multi_index[0] < top    : top       = cells.multi_index[0]
            elif cells.multi_index[0] > bottom : bottom    = cells.multi_index[0]
            if   cells.multi_index[1] < left   : left      = cells.multi_index[1]
            elif cells.multi_index[1] > right  : right     = cells.multi_index[1]
            dirty = True

        ## update attributes
        if dirty:
            self.dirty              = True
            self.cells_old          = self.cells.copy()
            self.dirty_cells        = (left, top, right, bottom)
            self.dirty_rect.topleft = (self.rect.left + left*G.cell_w, self.rect.top + top*G.cell_w)
            self.dirty_rect.size    = ((right-left+1)*G.cell_w, (bottom-top+1)*G.cell_w)
        else:
            self.dirty_cells        = [-1, -1, -1, -1]
            self.dirty_rect.topleft = (0, 0)
            self.dirty_rect.size    = (0, 0)

    '''
    =============================
    draw
    =============================
    '''
    def draw(self, screen):
        ## play row clean animation
        if self.clear_rows_vis: self.remove_rows_visual()

        ## blit patch of clean background on the surface
        patch_rect          = self.dirty_rect.copy()
        patch_rect.left     -= self.rect.left
        patch_rect.top      -= self.rect.top
        patch               = self.background.subsurface(patch_rect)
        self.surface.blit(patch, patch_rect)
        
        ## draw new cells on the surface
        cells = np.nditer(self.cells[2:], flags=['multi_index'])
        for cell in cells:
            ## check if cell is in the dirty frame
            if  cell \
            and (self.dirty_cells[0] <= cells.multi_index[1] <= self.dirty_cells[2]) \
            and (self.dirty_cells[1] <= cells.multi_index[0] <= self.dirty_cells[3]):
                x = cells.multi_index[1]*G.cell_w + 1
                y = cells.multi_index[0]*G.cell_w + 1
                self.surface.blit(self.cell.surface, (x, y))

        ## get mutated patch of the surface and blit to the screen
        patch_rect          = self.dirty_rect.copy()
        patch_rect.left     -= self.rect.left
        patch_rect.top      -= self.rect.top
        patch               = self.surface.subsurface(patch_rect)
        screen.blit(patch, self.dirty_rect)

        ## clear the dirty attribute
        self.dirty = False

    '''
    =============================
    redraw
    =============================
    '''
    def redraw(self, screen):
        ## clean background
        self.surface.blit(self.background, (0, 0))
        
        ## draw cells
        cells = np.nditer(self.cells[2:], flags=['multi_index'])
        for cell in cells:
            if cell:
                x = cells.multi_index[1]*G.cell_w + 1
                y = cells.multi_index[0]*G.cell_w + 1
                self.surface.blit(self.cell.surface, (x, y))

        ## blit to the screen
        screen.blit(self.surface, self.rect)

    '''
    =============================
    remove_rows_visual
    =============================
    '''
    def remove_rows_visual(self):
        self.clear_rows_vis = False
        rows    = [row-2 for row in self.full_rows if row > 1]
        idx     = WELL_W//2 - 1
        rect    = pygame.Rect(self.rect.left, rows[0]*G.cell_w,
                              self.rect.width, (rows[-1]-rows[0]+1)*G.cell_w)
        t_beg   = time.clock()

        ## go from middle to sides
        while idx >= 0:
            glows = []
            
            for row in rows:
                ## left tile
                tile_rect = pygame.Rect(idx*G.cell_w, row*G.cell_w, G.cell_w, G.cell_w)
                tile      = self.background.subsurface(tile_rect)
                tile_rect.left += self.rect.left
                tile_rect.top  += self.rect.top
                G.screen.blit(tile, tile_rect)
                ## glow
                if (not idx%2) and len(rows) > 3:
                    glow_rect           = pygame.Rect(tile_rect.topleft, (0, G.cell_w))
                    glow_rect.width     = (self.rect.center[0] - tile_rect.left)*2
                    glow                = pygame.Surface(glow_rect.size).convert()
                    glow.fill(GLOW_COLOR)
                    glows.append([glow, glow_rect])
                ## right tile
                tile_rect = pygame.Rect((WELL_W-idx-1)*G.cell_w, row*G.cell_w, G.cell_w, G.cell_w)
                tile      = self.background.subsurface(tile_rect)
                tile_rect.left += self.rect.left
                tile_rect.top  += self.rect.top
                G.screen.blit(tile, tile_rect)

            ## flash if tetris
            if glows: 
                tmp_screen = G.screen.subsurface(rect).copy()
                for glow in glows:
                    G.screen.blit(glow[0], glow[1], special_flags = BLEND_ADD)
            else:
                tmp_screen = None
            ## update and delay
            pygame.display.update(rect)
            idx -= 1
            if len(rows) > 3:   time.sleep(1.2/ROW_CLR_SPEED)
            else:               time.sleep(1/ROW_CLR_SPEED)
            ## heal screen after flash
            if tmp_screen: G.screen.blit(tmp_screen, rect)

        ## rewind tick timer to compensate for animation
        t_end           = time.clock()
        G.tick_rewind   = t_end - t_beg