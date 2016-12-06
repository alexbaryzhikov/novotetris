import  pygame
import  config as G

'''
=============================
HighScores
=============================
'''
class HighScores:

    '''
    =============================
    __init__
    =============================
    '''
    def __init__(self):
        self.color      = G.TEXT_COLOR3
        self.read()
        self.reinit()

    '''
    =============================
    reinit
    =============================
    '''
    def reinit(self):
        self.font_size  = G.cell_w
        self.font       = pygame.font.Font('square-deal.ttf', self.font_size)
        self.rect       = pygame.Rect(G.well.rect.left - G.cell_w*7, G.cell_w, 
                                      G.cell_w*7, self.font_size*10)
    
    '''
    =============================
    draw
    =============================
    '''
    def draw(self, screen):
        if not self.scores: return

        surface = screen.subsurface(self.rect).copy()
        
        for i in range(len(self.scores)):
            text1 = self.font.render(str(i+1)+'.', 0, self.color)
            text2 = self.font.render(str(self.scores[i]), 0, self.color)
            surface.blit(text1, (G.cell_w//2, self.font_size*i))
            surface.blit(text2, (G.cell_w*2,  self.font_size*i))

        screen.blit(surface, self.rect)

    '''
    =============================
    read
    =============================
    '''
    def read(self):
        self.scores = []
        try:    file = open('highscores.txt')
        except: return
        for line in file:
            score = line.split()[0]
            if score.isdigit(): self.scores.append(int(score))
        file.close()
        self.scores.sort(reverse=True)
        if len(self.scores) > 10: self.scores = self.scores[:10]

    '''
    =============================
    save_scores
    =============================
    '''
    def save(self):
        if not self.scores: return
        try:    file = open('highscores.txt', 'w')
        except: return
        for score in self.scores: file.write(str(score)+'\n')
        file.close()

    '''
    =============================
    add_score
    =============================
    '''
    def add(self, score):
        if not score: return
        self.scores.append(score)
        self.scores.sort(reverse=True)
        if len(self.scores) > 10: self.scores = self.scores[:10]

