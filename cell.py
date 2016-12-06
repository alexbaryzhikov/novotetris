import  pygame
import  config as G

'''
=============================
Cell
=============================
'''
class Cell:

    '''
    =============================
    __init__
    =============================
    '''
    def __init__(self, color=G.CELL_COLOR1):
        self.color      = color
        self.surface    = self.get_surface()
        self.rect       = self.surface.get_rect()

    '''
    =============================
    get_surface
    =============================
    '''
    def get_surface(self):
        s = pygame.Surface((G.cell_w-2, G.cell_w-2)).convert()
        s.fill(self.color)
        return s
