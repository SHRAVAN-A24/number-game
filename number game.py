
import pygame
import random
import os
from pygame.locals import *

print("loading game...")

pygame.init()




# screen setup
screen = pygame.display.set_mode((600, 700))
pygame.display.set_caption("Memory Match - My Version")
clock = pygame.time.Clock()

# colors i picked
darkblue = (0, 0, 128)
whitecol = (255, 255, 255)
blackcol = (0, 0, 0)
greencard = (40, 140, 40)
ltgreencard = (90, 190, 90)
goldcol = (255, 215, 0)
silvercol = (180, 180, 180)

CARDW = 100
GRIDW = 4
GAP = 20

# fonts 
numfont = pygame.font.Font(None, 72)
qfont = pygame.font.Font(None, 42)
textfont = pygame.font.Font(None, 32)

class Card:
    def __init__(self, value, xstart, ystart):
        self.value = value
        self.rect = Rect(xstart, ystart, CARDW, CARDW)
        self.faceup = False
        self.matched = False
        self.flipprog = 0.0
        self.flipback = False  # NEW FOR FLIP BACK
    
    def drawit(self, surf):
        # flip effect rect
        r = self.rect.copy()
        if self.flipback:
            # SHRINK BACKWARDS when mismatch
            r.width *= max(0.1, 1.0 - self.flipprog)
        else:
            r.width *= min(1.0, self.flipprog)
        r.center = self.rect.center
        
        # borders
        pygame.draw.rect(surf, silvercol, r, 4)
        pygame.draw.rect(surf, blackcol, r, 2)
        
        # card face
        if self.faceup or self.matched:
            pygame.draw.rect(surf, goldcol if self.matched else whitecol, r)
            txt = numfont.render(str(self.value), True, blackcol)
        else:
            color = ltgreencard if self.flipprog > 0.4 else greencard
            pygame.draw.rect(surf, color, r)
            txt = qfont.render("?", True, blackcol)
        
        # center text
        tr = txt.get_rect(center=r.center)
        surf.blit(txt, tr)
    
    def updateflip(self, dt):
        if self.flipback:
            # FLIP BACK ANIMATION
            if self.flipprog > 0:
                self.flipprog -= dt * 5
                if self.flipprog <= 0:
                    self.flipback = False
                    self.faceup = False
                    self.flipprog = 0
        elif self.flipprog < 1.0:
            self.flipprog += dt * 5

def newgame():
    cardslist = []
    vals = list(range(8)) * 2
    random.shuffle(vals)
    
    x = GAP
    y = GAP + 40
    for i, val in enumerate(vals):
        cardslist.append(Card(val, x, y))
        x += CARDW + GAP
        if (i + 1) % 4 == 0:
            x = GAP
            y += CARDW + GAP
    return cardslist

def savehigh(score):
    try:
        with open("score.txt", "w") as f:
            f.write(str(score))
    except:
        pass

def loadhigh():
    try:
        if os.path.exists("score.txt"):
            with open("score.txt") as f:
                return int(f.read().strip())
    except:
        pass
    return 0

def drawtext(msg, fnt, col, x, y):
    txtsurf = fnt.render(msg, True, col)
    recttxt = txtsurf.get_rect(center=(x, y))
    screen.blit(txtsurf, recttxt)

print("Game ready! Watch the cards then match em!")

keepgoing = True

while keepgoing:
    cards = newgame()
    gamestate = "showall"  # showall, playtime, waitmatch, hidecards
    picked1 = picked2 = None
    matchesmade = tries = 0
    gamestart = pygame.time.get_ticks()
    besthigh = loadhigh()
    
    while keepgoing and matchesmade < 8:
        frametime = clock.tick(60) / 1000.0
        nowtime = pygame.time.get_ticks()
        
        # input stuff
        for ev in pygame.event.get():
            if ev.type == QUIT:
                keepgoing = False
            elif ev.type == KEYDOWN:
                if ev.key == K_r:
                    break
                elif ev.key == K_ESCAPE:
                    keepgoing = False
            elif ev.type == MOUSEBUTTONDOWN and gamestate == "playtime":
                mx, my = ev.pos
                for card in cards:
                    if (card.rect.collidepoint(mx, my) and 
                        not card.faceup and not card.matched):
                        if picked1 is None:
                            picked1 = card
                            card.faceup = True
                            card.flipprog = 0.1
                        elif picked2 is None and card != picked1:
                            picked2 = card
                            card.faceup = True
                            card.flipprog = 0.1
                            tries += 1
                            gamestate = "waitmatch"
        
        # game logic states
        if gamestate == "showall":
            for card in cards:
                card.faceup = True
            if nowtime - gamestart > 3000:
                for card in cards:
                    card.faceup = False
                    card.flipprog = 0
                gamestate = "playtime"
        
        elif gamestate == "waitmatch" and nowtime - gamestart > 800:
            if picked1 and picked2:
                if picked1.value == picked2.value:
                    # MATCH - keep showing
                    picked1.matched = picked2.matched = True
                    matchesmade += 1
                else:
                    # NO MATCH - FLIP THEM BACK
                    picked1.faceup = False
                    picked2.faceup = False
                    picked1.flipback = True  # START FLIPBACK
                    picked2.flipback = True
                    gamestate = "hidecards"
            
            picked1 = picked2 = None
            gamestate = "playtime"
        
        elif gamestate == "hidecards" and nowtime - gamestart > 1600:
            gamestate = "playtime"
        
        # animate cards
        for card in cards:
            card.updateflip(frametime)
        
        # draw scene
        screen.fill(darkblue)
        for card in cards:
            card.drawit(screen)
        
        # show info
        if gamestate == "showall":
            drawtext("Watch & Remember!", qfont, whitecol, 300, 30)
        else:
            elapsed = (nowtime - gamestart) / 1000
            m, s = divmod(int(elapsed), 60)
            pct = (matchesmade * 2 * 100) / tries if tries else 0
            
            drawtext(f"{matchesmade}/8", textfont, whitecol, 80, 25)
            drawtext(f"tries: {tries}", textfont, whitecol, 200, 25)
            drawtext(f"{int(pct)}%", textfont, whitecol, 320, 25)
            drawtext(f"{m}:{s:02d}", textfont, whitecol, 500, 25)
            drawtext("R=restart  ESC=quit", textfont, ltgreencard, 300, 670)
            
            if matchesmade == 8:
                finalpct = 100 if tries == 0 else (16 * 100) / tries
                finalscr = int(finalpct * 1000 / (elapsed + 1))
                drawtext("WINNER!", numfont, goldcol, 300, 150)
                drawtext(f"score: {finalscr}", qfont, whitecol, 300, 220)
                drawtext(f"best: {besthigh}", textfont, whitecol, 300, 270)
        
        pygame.display.flip()
    
    # win screen wait
    if matchesmade == 8:
        while keepgoing:
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    keepgoing = False
                elif ev.type == KEYDOWN:
                    if ev.key == K_r:
                        break
                    if ev.key == K_ESCAPE:
                        keepgoing = False
            
            elapsed = (pygame.time.get_ticks() - gamestart) / 1000
            finalpct = 100 if tries == 0 else (16 * 100) / tries
            finalscr = int(finalpct * 1000 / (elapsed + 1))
            
            if finalscr > besthigh:
                besthigh = finalscr
                savehigh(finalscr)
            
            screen.fill(darkblue)
            drawtext("NICE!", numfont, goldcol, 300, 120)
            drawtext(f"{finalscr} points", qfont, whitecol, 300, 190)
            drawtext(f"high: {besthigh}", textfont, whitecol, 300, 240)
            drawtext("R or ESC", textfont, ltgreencard, 300, 650)
            pygame.display.flip()
            clock.tick(60)

pygame.quit()
print("BYE!")
