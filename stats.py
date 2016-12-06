import  pygame
import  config as G

'''
=============================
Stats
=============================
'''
class Stats:

    '''
    =============================
    __init__
    =============================
    '''
    def __init__(self):
        self.lines      = 0
        self.color      = G.TEXT_COLOR1
        self.dirty      = False
        self.reinit()

    '''
    =============================
    reinit
    =============================
    '''
    def reinit(self):
        self.font_size  = G.cell_w
        self.font       = pygame.font.Font('square-deal.ttf', self.font_size)
        self.rect       = pygame.Rect(G.well.rect.right + G.cell_w, G.cell_w*6, 
                                      G.cell_w*6, self.font_size*5)
        self.background = G.background.subsurface(self.rect)
        G.dirty_rects.append(self.rect)
    
    '''
    =============================
    update
    =============================
    '''
    def update(self, dt):
        if self.lines != G.lines:
            self.lines = G.lines
            self.dirty = True

    '''
    =============================
    draw
    =============================
    '''
    def draw(self, screen):
        surface = self.background.copy()
        ## labels
        text1   = self.font.render('level', 0, self.color)
        text2   = self.font.render('lines', 0, self.color)
        text3   = self.font.render('score', 0, self.color)
        surface.blit(text1, (0, 0))
        surface.blit(text2, (0, self.font_size*2))
        surface.blit(text3, (0, self.font_size*4))
        ## values
        text1   = self.font.render(str(G.level), 0, self.color)
        text2   = self.font.render(str(G.lines), 0, self.color)
        text3   = self.font.render(str(G.score), 0, self.color)
        surface.blit(text1, (G.cell_w*3, 0))
        surface.blit(text2, (G.cell_w*3, self.font_size*2))
        surface.blit(text3, (G.cell_w*3, self.font_size*4))
        screen.blit(surface, self.rect)
