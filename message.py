import  pygame
import  config as G

'''
=============================
Message
=============================
'''
class Message:

    '''
    =============================
    __init__
    =============================
    '''
    def __init__(self):
        self.color      = G.TEXT_COLOR2
        self.text1      = None
        self.text2      = None
        self.dirty      = True
        self.background = None
        self._show      = False
        self._t         = 0
        self.reinit()

    '''
    =============================
    reinit
    =============================
    '''
    def reinit(self):
        self.font_size  = G.cell_w*2
        self.font       = pygame.font.Font('square-deal.ttf', self.font_size)
        self.rect       = pygame.Rect(G.well.rect.left, G.cell_w*6,
                                      G.well.rect.width, self.font_size*3)
        self.background = None
    
    '''
    =============================
    reset
    =============================
    '''
    def reset(self):
        self.text1      = None
        self.text2      = None
        self.background = None
        self._show      = False
        self._t         = 0

    '''
    =============================
    update
    =============================
    '''
    def update(self, dt):
        if self.text1 or self.text2:
            ## blink
            self._t += dt
            if (self._show and self._t > G.MESSAGE_BLINK) \
            or (not self._show and self._t > G.MESSAGE_BLINK/2):
                self._t = 0
                self._show = not self._show
                self.dirty = True
        else:
            self.reset()

    '''
    =============================
    draw
    =============================
    '''
    def draw(self, screen):

        if self.background is None:
            self.background = screen.subsurface(self.rect).copy()

        if not self._show:
            screen.blit(self.background, self.rect)
            pygame.display.update(self.rect)
            self.dirty = False
            return

        if self.text1: 
            t1_w    = self.font.size(self.text1)[0]
            text1_  = self.font.render(self.text1, 0, self.color)
            x       = self.rect.left + int((self.rect.width - t1_w)/2)
            y       = self.rect.top
            screen.blit(text1_, (x, y))

        if self.text2:
            t2_w    = self.font.size(self.text2)[0]
            text2_  = self.font.render(self.text2, 0, self.color)
            x       = self.rect.left + int((self.rect.width - t2_w)/2)
            y       = self.rect.top + self.font_size*2
            screen.blit(text2_, (x, y))

        pygame.display.update(self.rect)
        self.dirty = False


    '''
    =============================
    set_text
    =============================
    '''
    def set_text(self, text1=None, text2=None):
        self.text1 = text1
        self.text2 = text2
        self._show = True
        self.dirty = True
