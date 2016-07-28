import pygame
import sys
import ChessEngine
import PieceMovement
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
    for p in PieceMovement.allpieces:
        pieceImage = pygame.image.load(p.picture)
        pieceImage = pygame.transform.smoothscale(pieceImage, (k, k))
        for sqr in p.piecelist:
            x = xcorner + (sqr % 8)*k
            y = ycorner + (7 - sqr / 8)*k 
            screen.blit(pieceImage, (x, y))
    pygame.display.update()


# Draws the reset button
def drawButton():
    x, y = buttonx, buttony
    pygame.draw.rect(screen, boardcolour, (x, y, 75, 12), 2)
    message = ButtonFont.render("NEW GAME", 1, blue)
    screen.blit(message, (x+2, y+2))


# Draws the undo button
def drawUndo():
    x, y = undox, buttony
    pygame.draw.rect(screen, boardcolour, (x, y, 75, 12), 2)
    message = ButtonFont.render("UNDO", 1, blue)
    screen.blit(message, (x+2, y+2))


# Highlights the specified square
def drawHighlight(sqr):
    f = sqr % 8
    r = 7 - sqr / 8
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
    for s in PieceMovement.PieceMovement(sqr):
        f = s % 8
        r = 7 - s//8
        size = boardsize
        k = squaresize
        x = (xcorner + k*f + k/2) // 1
        y = (ycorner + k*r + k/2) // 1
        rad = k//4
        pygame.draw.circle(screen, green, (x, y), rad, 0)
        pygame.display.update()


# Redraws the board and pieces
def drawStuff():
    screen.fill(backcolour)
    drawButton()
    drawUndo()
    drawBoard()
    drawPieces()

def drawStuffWithHighlight(sqr):
    screen.fill(backcolour)
    drawButton()
    drawUndo()
    drawBoard()
    drawHighlight(sqr)
    drawPieces()


# A class used for resetting the game
class GameState:
    movenumber = 0
    turn = 'white'
    randmove = random.random()

mainState = GameState()

def resetState():
    mainState.randmove = random.random()
    mainState.movenumber = 0
    mainState.turn = 'white'
    PieceMovement.resetgame()
    drawStuff()


# Undoes a move !!
def UndoStuff():
    if mainState.turn != 'end':
        PieceMovement.UndoMove()
        PieceMovement.UndoMove()
        drawStuff()


# Makes a move for the computer
def DoCompTurn(turn):
    if ChessEngine.isEndgame():
        start, end = ChessEngine.BasicMates(turn)
    elif mainState.movenumber <= 5:
        start, end = ChessEngine.OpeningMoves(turn, mainState.movenumber, mainState.randmove)
    else:
        k = ChessEngine.FindBest(turn, 2)
        start, end = k.movestart, k.moveend
    PieceMovement.MovePiece(start, end)
    drawStuffWithHighlight(end)
    if turn == 'white':
        mainState.turn = 'black'
        mainState.movenumber += 1
    elif turn == 'black':
        mainState.turn = 'white'


# Moves a piece selected by the player
def DoPlayerTurn(turn):
    temp = -1
    while (True):
        for event in pygame.event.get():
            # Check for quit
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit();
            # Reset the game if 'new game' selected
            if event.type == pygame.MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if buttonx < mousex < buttonx + 75 and buttony < mousey < buttony + 12:
                    resetState()
                    return
                elif undox < mousex < undox + 75 and buttony < mousey < buttony + 12:
                    UndoStuff()
                    return
            if event.type == pygame.MOUSEBUTTONUP:
                mousex, mousey = event.pos
                msqr = squareClicked(mousex, mousey)
                if msqr != -1:

                    # Moves a piece if one was selected
                    if temp != -1:
                        for s in PieceMovement.PieceMovement(temp):
                            if msqr == s:
                                PieceMovement.MovePiece(temp, msqr)
                                drawStuff()
                                if turn == 'white':
                                    mainState.turn = 'black'
                                    mainState.movenumber += 1
                                elif turn == 'black':
                                    mainState.turn = 'white'
                                return
                        drawStuff()
                        temp = -1

                    # Displays valid moves
                    else:
                        if turn == 'white':
                            folder = PieceMovement.whitepieces
                        elif turn == 'black':
                            folder = PieceMovement.blackpieces
                        for piece in folder:
                            if id(piece) == PieceMovement.boardlist[msqr]:
                                drawMoves(msqr)
                                temp = msqr
                                break

                                             
def main():
    # Variables and such
    pygame.display.set_caption('Can you beat Shallow Blue in chess?')
    PieceMovement.updateCastlingRights()
    drawStuff()

    # Main game loop:
    while (True):
        for event in pygame.event.get():
            # Check for quit
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit();
            # Reset the game if 'new game' selected
            if event.type == pygame.MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if buttonx < mousex < buttonx + 75 and buttony < mousey < buttony + 12:
                    resetState()
                elif undox < mousex < undox + 75 and buttony < mousey < buttony + 12:
                    UndoStuff()
        # Checks for mate
        if mainState.turn != 'end':
            mate_status = PieceMovement.isMated(mainState.turn)
        if mate_status:
            message = MessageFont.render(mate_status + "!", 1, blue)
            screen.blit(message, (screenwidth / 2 - marginsize, marginsize /2))
            pygame.display.update()
            mainState.turn = 'end'
        # Checks for draw
        draw_status = PieceMovement.isDraw() 
        if draw_status:
            message = MessageFont.render(draw_status, 1, blue)
            screen.blit(message, (screenwidth / 2 - 2*marginsize, marginsize / 2))
            pygame.display.update()
            mainState.turn = 'end'

        elif mainState.turn == 'white':
            DoPlayerTurn(mainState.turn)

        elif mainState.turn == 'black':
            DoCompTurn(mainState.turn)
main()
