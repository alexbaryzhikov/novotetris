'''
NovoTetris v0.015

Tetris is a tile-matching puzzle video game, originally designed and programmed by Russian game
designer Alexey Pajitnov. 

"Tetriminos" are game pieces shaped like tetrominoes, geometric shapes composed of four square
blocks each. A random sequence of Tetriminos fall down the playing field (a rectangular vertical
shaft, called the "well" or "matrix"). The objective of the game is to manipulate these Tetriminos,
by moving each one sideways (if the player feels the need) and rotating it by 90 degree units,
with the aim of creating a horizontal line of ten units without gaps. When such a line is created,
it disappears, and any block above the deleted line will fall. When a certain number of lines are
cleared, the game enters a new level. As the game progresses, each level causes the Tetriminos to
fall faster, and the game ends when the stack of Tetriminos reaches the top of the playing field
and no new Tetriminos are able to enter.
'''

import  pygame
from    pygame.locals import *
import  time
import  random
from    config import *
import  config as G
from    fps import FPS
from    well import Well
from    nextglyph import NextGlyph
from    thisglyph import ThisGlyph
from    utilities import get_bg
from    stats import Stats
from    message import Message
from    highscores import HighScores

'''
=============================
load
=============================
'''
def load():
    random.seed()
    pygame.init()
    pygame.display.set_caption('NovoTetris')
    icon = pygame.image.load('t-icon.png')
    pygame.display.set_icon(icon)
    G.fs_resolution = pygame.display.list_modes()[0]
    G.mode_change   = True
    G.mode          = RESIZABLE
    G.screen_w      = SCREEN_W
    G.screen_h      = SCREEN_H

    reset_game_state()
    vid_restart()
    reset_game_objects()
    redraw_game_screen()

'''
=============================
reset_game_state
=============================
'''
def reset_game_state():
    G.level         = 0
    G.lines         = 0
    G.score         = 0
    G.state         = 'playing' # playing, paused, finished
    G.level_speed   = SPEED_LEVELS[G.level]
    G.speed         = G.level_speed
    G.tick          = 0
    G.tick_rewind   = 0
    G.tick_edge     = False

'''
=============================
reset_game_objects
=============================
'''
def reset_game_objects():
    G.well.reset()
    G.message.reset()
    if G.this_glyph.glyph is None:
        G.this_glyph.update(0)
        G.next_glyph.update(0)
    else:
        ## generate next glyph
        G.next_glyph.used = True
        G.next_glyph.update(0)
        ## hand new glyph to this_glyph
        G.this_glyph.glyph = None
        G.this_glyph.update(0)
        ## generate next glyph
        G.next_glyph.update(0)

'''
=============================
vid_restart
=============================
'''
def vid_restart():
    ## set display mode
    if G.mode == FULLSCREEN:
        G.screen = pygame.display.set_mode(G.fs_resolution, G.mode)
    else:
        if G.screen_w < G.screen_h*1.2: G.screen_w = int(G.screen_h*1.2) # aspect guardian
        G.screen = pygame.display.set_mode([G.screen_w, G.screen_h], G.mode)

    ## get cell width and screen background
    G.cell_w        = G.screen.get_rect().height//(WELL_H+1)
    bg_width        = G.screen.get_rect().width//G.cell_w + 1
    bg_height       = G.screen.get_rect().height//G.cell_w + 1
    G.background    = get_bg(bg_width, bg_height, BG_COLOR1, BG_COLOR2)

    if 'well' not in G.__dict__:
        ## create game objects
        G.dirty_rects   = []
        G.fps           = FPS()
        G.well          = Well()
        G.stats         = Stats()
        G.message       = Message()
        G.highscores    = HighScores()
        G.this_glyph    = ThisGlyph()
        G.next_glyph    = NextGlyph()
    else:
        ## reinit game objects
        G.dirty_rects   = []
        G.fps           = FPS()
        G.well.reinit()
        G.stats.reinit()
        G.message.reinit()
        G.highscores.reinit()
        G.this_glyph.reinit()
        G.next_glyph.reinit()

'''
=============================
redraw_game_screen
=============================
'''
def redraw_game_screen():
    well_frame = (G.well.rect.left-1, G.well.rect.top-1, G.well.rect.width+2, G.well.rect.height+2)
    pygame.draw.rect(G.background, WELL_COLOR3, well_frame, 1)
    G.screen.blit(G.background, (0, 0))
    G.highscores.draw(G.screen)
    G.well.redraw(G.screen)
    G.this_glyph.draw(G.screen)
    G.next_glyph.draw(G.screen)
    G.stats.draw(G.screen)
    G.message.draw(G.screen)
    pygame.display.flip()

'''
=============================
events
=============================
'''
def events(events_queue):
    for event in events_queue:

        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            G.highscores.save()
            return True

        if event.type == VIDEORESIZE and G.mode == RESIZABLE:
            if G.mode_change:
                G.mode_change = False
            else:
                G.screen_w = event.w
                G.screen_h = event.h
                if G.this_glyph.glyph: G.this_glyph.glyph.save_pos()
                vid_restart()
                redraw_game_screen()

        if event.type == KEYDOWN:
            ## do not allow actions while paused or finished
            if G.state not in ('paused', 'finished'):
                if   event.__dict__['scancode'] == 75:          # arrow left
                    G.this_glyph.move_left = True
                    G.this_glyph.move_left_now = True
                elif event.__dict__['scancode'] == 77:          # arrow right
                    G.this_glyph.move_right = True
                    G.this_glyph.move_right_now = True
                elif event.__dict__['scancode'] == 72:          # arrow up
                    G.this_glyph.rotate = True
                elif event.__dict__['scancode'] == 80:          # arrow down
                    G.speed = 0.04
                elif event.__dict__['scancode'] == 57:          # space
                    G.this_glyph.drop = True

            if event.__dict__['scancode'] == 28:                # enter
                if   G.state == 'paused':
                    ## unpause
                    G.message.reset()
                    redraw_game_screen()
                    G.state = 'playing'
                elif G.state == 'playing':
                    ## pause
                    G.message.set_text('paused', 'press enter')
                    G.state = 'paused'
                elif G.state == 'finished':
                    ## start new game
                    reset_game_state()
                    reset_game_objects()
                    redraw_game_screen()

            elif event.__dict__['scancode'] == 33:              # 'f'
                ## change screen mode
                if G.mode == RESIZABLE:
                    G.mode = FULLSCREEN
                else:
                    G.mode = RESIZABLE
                if G.this_glyph.glyph: G.this_glyph.glyph.save_pos()
                G.mode_change = True
                vid_restart()
                redraw_game_screen()

        if event.type == KEYUP:
            if   event.__dict__['scancode'] == 75:              # arrow left
                G.this_glyph.move_left = False
            elif event.__dict__['scancode'] == 77:              # arrow right
                G.this_glyph.move_right = False
            elif event.__dict__['scancode'] == 80:              # arrow down
                G.speed = G.level_speed

'''
=============================
update
=============================
'''
def update(dt):
    ## fps and message
    if DRAW_FPS: G.fps.update(dt)
    G.message.update(dt)

    if G.state in ('paused', 'finished'): return
    
    ## tick timing
    G.tick          += dt
    G.tick          -= G.tick_rewind
    G.tick_rewind   = 0
    
    if G.tick > G.speed:
        G.tick = 0
        G.tick_edge = True

    ## update game elements
    G.this_glyph.update(dt)
    G.next_glyph.update(dt)
    G.well.update(dt)
    G.stats.update(dt)

    G.tick_edge = False

'''
=============================
draw
=============================
'''
def draw(screen):
    if DRAW_FPS: G.fps.draw(screen)
    if G.this_glyph.dirty:  G.this_glyph.draw(screen)
    if G.next_glyph.dirty:  G.next_glyph.draw(screen)
    if G.well.dirty:        G.well.draw(screen)
    if G.stats.dirty:       G.stats.draw(screen)
    if G.message.dirty:     G.message.draw(screen)

    pygame.display.update(G.dirty_rects)

'''
=============================
main
=============================
'''
def main():
    load()
    # init clock
    t, t_last = 0.0, 0.0
    time.clock()

    while True: # main loop
        if events(pygame.event.get()): return               # events
        t_loop = time.clock()-t                             # clean loop time
        if t_loop < 1/MAX_FPS: time.sleep(1/MAX_FPS-t_loop) # fps guardian
        t_last = t; t = time.clock()                        # dt
        update(t-t_last)                                    # updates
        draw(G.screen)                                      # draws

    pygame.quit()

if __name__ == '__main__': main()
