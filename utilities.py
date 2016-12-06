import  pygame
import  config as G
import  random

'''
=============================
get_bg
=============================
'''
def get_bg(width, height, color1, color2, col_variance=True):
    s = pygame.Surface((width*G.cell_w, height*G.cell_w)).convert()
    s.fill(color1)
    s.lock()
    for y in range(0, height*G.cell_w, G.cell_w):
        for x in range(0, width*G.cell_w, G.cell_w):
            color = []
            if not col_variance: rnd = random.randint(-1, 1)
            for channel in color2:
                if col_variance: rnd = random.randint(-1, 1)
                color.append(channel+rnd)
            pygame.draw.rect(s, color, [x+1, y+1, G.cell_w-2, G.cell_w-2])
    s.unlock()
    return s
