import pygame
import sys
import ChessEngine
import PieceMovement as pm
from PieceMovement import WHITE, BLACK
import random
import time

backcolour = (255, 255, 255)
boardcolour = (0, 0, 0)
lightblue = (102, 255, 255)
blue = (0, 0, 128)
green = (0, 255, 0)
brown = (153, 76, 0)
purple = (138, 6, 255)

marginsize = 30
screenwidth = 1024 # 640 for a smaller screen
screenheight = 640 # 480 for a smaller screen

if screenwidth >= screenheight:
    dx, dy = (screenwidth - screenheight)/2, 0
else:
    dx, dy = 0, (screenheight - screenwidth)/2
xcorner, ycorner = dx + marginsize, dy + marginsize
boardsize = min(screenheight, screenwidth) - 2 * marginsize

squaresize = boardsize / 8
buttonx = screenwidth / 2 - marginsize
buttony = screenheight - 3*(marginsize / 4)
undox = buttonx + 100

pygame.init()
screen = pygame.display.set_mode((screenwidth, screenheight))
MessageFont = pygame.font.SysFont("comic sans", 18)
ButtonFont = pygame.font.SysFont("comic sans", 15)


# helper to obtain file and rank
def fileAndRank(sqr):
    return sqr%8, 7 - sqr/8


def checkType(event):
    # Check for quit
    if event.type == pygame.QUIT:
        pygame.quit(); sys.exit();
    # Reset the game if 'new game' selected
    if event.type == pygame.MOUSEBUTTONUP:
        mousex, mousey = event.pos
        if buttonx < mousex < buttonx + 75 and buttony < mousey < buttony + 12:
            resetState()
            return True
        elif undox < mousex < undox + 75 and buttony < mousey < buttony + 12:
            UndoStuff()
            return True


# Draws a message above the board
def displayMessage(message, xcoord):
    message = MessageFont.render(message, 1, blue)
    screen.blit(message, (xcoord, marginsize /2))
    pygame.display.update()
    mainState.turn = 'end'


# Draws the board to the screen
def drawBoard():
    x, y = xcorner, ycorner
    size = boardsize
    k = squaresize
    pygame.draw.rect(screen, boardcolour, (x, y, size, size), 3)
    for sqr in range(64):
        sx = x + (sqr % 8)*k + 2 # Add 2 to centre the board
        sy = y + (7 - sqr / 8)*k + 2
        a, b = sqr/8, sqr%2
        if a%2 == b:
            pygame.draw.rect(screen, brown, (sx, sy, k, k))
        else:
            pygame.draw.rect(screen, lightblue, (sx, sy, k, k))        


# Draws the pieces to the screen
def drawPieces():
    k = squaresize
    for p in pm.allpieces:
        pieceImage = pygame.image.load(p.picture)
        pieceImage = pygame.transform.smoothscale(pieceImage, (k, k))
        for sqr in p.piecelist:
            x = xcorner + (sqr % 8)*k
            y = ycorner + (7 - sqr / 8)*k 
            screen.blit(pieceImage, (x, y))
    pygame.display.update()


# Draws the buttons below the board
def buttonHelper(xcoord, text):
    x, y = xcoord, buttony
    pygame.draw.rect(screen, boardcolour, (x, y, 75, 12), 2)
    message = ButtonFont.render(text, 1, blue)
    screen.blit(message, (x+2, y+2))

def drawButtons():
    buttonHelper(buttonx, "NEW GAME")
    buttonHelper(undox, "UNDO")
    

# Highlights the specified square
def drawHighlight(sqr):
    f, r = fileAndRank(sqr)
    x = xcorner + f * squaresize + 2
    y = ycorner + r * squaresize + 2
    pygame.draw.rect(screen, purple, (x, y, squaresize, squaresize))
    

# Returns square clicked (as a number) or False if mouse was off board
def squareClicked(mousex, mousey):
    x = mousex - xcorner
    y = mousey - ycorner
    size = boardsize
    k = squaresize
    if x>0 and x<size and y>0 and y<size:
        fil = x // k
        rank = y // k
        sqr = 8*(7-rank) + fil
        return sqr
    return -1


# Draws a circle for each valid move of the piece on sqr
def drawMoves(sqr):
    for s in pm.PieceMovement(sqr):
        f, r = fileAndRank(s)
        size = boardsize
        k = squaresize
        x = (xcorner + k*f + k/2) // 1
        y = (ycorner + k*r + k/2) // 1
        rad = k//4
        pygame.draw.circle(screen, green, (x, y), rad, 0)
        pygame.display.update()


# Redraws the board and pieces
def drawStuff(sqr=-1):
    screen.fill(backcolour)
    drawButtons()
    drawBoard()
    if sqr != -1:
        drawHighlight(sqr)
    drawPieces()


# A class used for resetting the game
class GameState:
    movenumber = 0
    turn = WHITE
    randmove = random.random()

mainState = GameState()

def resetState():
    mainState.randmove = random.random()
    mainState.movenumber = 0
    mainState.turn = WHITE
    pm.resetgame()
    drawStuff()


# Undoes a move !!
def UndoStuff():
    if mainState.turn != 'end':
        pm.UndoMove()
        pm.UndoMove()
        drawStuff()
    if mainState.movenumber == 1:
        mainState.turn = WHITE
    if mainState.movenumber != 0:
        mainState.movenumber -= 1


# Switches turn and increases move number
def switchTurn(turn):
    if turn == WHITE:
        mainState.turn = BLACK
        mainState.movenumber += 1
    elif turn == BLACK:
        mainState.turn = WHITE


# Makes a move for the computer
def DoCompTurn(turn):
    if mainState.movenumber <= 5:
        start, end = ChessEngine.OpeningMoves(turn, mainState.movenumber, mainState.randmove)
    else:
        k = ChessEngine.FindBest(turn)
        start, end = k.movestart, k.moveend
    pm.MovePiece(start, end)
    drawStuff(end)
    switchTurn(turn)


# Moves a piece selected by the player
def DoPlayerTurn(turn):
    temp = -1
    while (True):
        for event in pygame.event.get():
            if checkType(event):
                return
            if event.type == pygame.MOUSEBUTTONUP:
                mousex, mousey = event.pos
                msqr = squareClicked(mousex, mousey)
                if msqr != -1:

                    # Moves a piece if one was selected
                    if temp != -1:
                        for s in pm.PieceMovement(temp):
                            if msqr == s:
                                pm.MovePiece(temp, msqr)
                                drawStuff()
                                switchTurn(turn)
                                return
                        drawStuff()
                        temp = -1

                    # Displays valid moves
                    else:
                        if turn == WHITE:
                            folder = pm.whitepieces
                        elif turn == BLACK:
                            folder = pm.blackpieces
                        for piece in folder:
                            if id(piece) == pm.boardlist[msqr]:
                                drawMoves(msqr)
                                temp = msqr
                                break

                                             
def main():
    # Variables and such
    pygame.display.set_caption('Can you beat Shallow Blue in chess?')
    pm.updateCastlingRights()
    drawStuff()

    # Main game loop:
    while (True):
        for event in pygame.event.get():
            checkType(event)
        # Checks for mate
        if mainState.turn != 'end':
            mate_status = pm.isMated(mainState.turn)
        if mate_status:
            displayMessage(mate_status + "!", screenwidth / 2 - marginsize)
        # Checks for draw
        draw_status = pm.isDraw() 
        if draw_status:
            displayMessage(draw_status, screenwidth / 2 - 2*marginsize)

        elif mainState.turn == WHITE:
            DoPlayerTurn(mainState.turn)

        elif mainState.turn == BLACK:
            DoCompTurn(mainState.turn)
main()
