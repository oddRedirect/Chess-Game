import pygame, sys, ChessEngine, random, time
from pygame.locals import *

backcolour = (255, 255, 255)
boardcolour = (0, 0, 0)
white = (252, 230, 201)
black = (156, 102, 31)
lightblue = (102, 255, 255)
blue = (0, 0, 128)
green = (0, 255, 0)

marginsize = 30
screenwidth = 1024
screenheight = 640
pi = 3.14159

if screenwidth >= screenheight:
    xcorner = (screenwidth - screenheight) / 2 + marginsize
    ycorner = marginsize
    boardsize = screenheight - 2*marginsize
else:
    xcorner = marginsize
    ycorner = (screenheight - screenwidth) / 2 + marginsize
    boardsize = screenwidth - 2*marginsize

squaresize = boardsize / 8
buttonx = screenwidth / 2 - marginsize
buttony = screenheight - 3*(marginsize / 4)

pygame.init()
screen = pygame.display.set_mode((screenwidth, screenheight))
MessageFont = pygame.font.SysFont("comic sans", 18) 


# Draws the board to the screen
def drawBoard():
    x = xcorner
    y = ycorner
    size = boardsize
    k = squaresize
    pygame.draw.rect(screen, boardcolour, (x, y, size, size), 3)
    i = k
    while i <= size - k:
        pygame.draw.lines(screen, boardcolour, False, [(x+i, y), (x+i, y+size)], 3)
        i += k
    i = k
    while i <= size - k:
        pygame.draw.lines(screen, boardcolour, False, [(x, y+i), (x+size, y+i)], 3)
        i += k


# Draws the pieces to the screen
def drawPieces():
    k = squaresize
    for p in ChessEngine.allpieces:
        for sqr in p.piecelist:
            x = xcorner + (sqr % 8)*k
            y = ycorner + (7 - sqr / 8)*k
            pieceImage = pygame.image.load(p.picture)
            pieceImage = pygame.transform.smoothscale(pieceImage, (k-4, k-4))
            screen.blit(pieceImage, (x+2, y+2)) #Gives the illusion of white space
    pygame.display.update()


# Draws the reset button
def drawButton():
    x = buttonx
    y = buttony
    ButtonFont = pygame.font.SysFont("comic sans", 15)
    pygame.draw.rect(screen, boardcolour, (x, y, 75, 12), 2)
    message = ButtonFont.render("New Game pls", 1, blue)
    screen.blit(message, (x+2, y+2))


# Highlights the last move made by the computer
def drawHighlight(sqr):
    f = sqr % 8
    r = 7 - sqr / 8
    x = xcorner + f * squaresize
    y = ycorner + r * squaresize
    pygame.draw.rect(screen, green, (x, y, squaresize, squaresize), 2)
    pygame.display.update()
    

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
    for s in ChessEngine.PieceMovement(sqr):
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
    drawBoard()
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
    ChessEngine.resetgame()
    drawStuff()


# Makes a move for the computer
def DoCompTurn(turn):
    if ChessEngine.isEndgame():
        start, end = ChessEngine.BasicMates(turn)
    elif mainState.movenumber <= 5:
        start, end = ChessEngine.OpeningMoves(turn, mainState.movenumber, mainState.randmove)
    else:
        start, end = ChessEngine.FindBest(turn)
    ChessEngine.MovePiece(start, end)
    ChessEngine.updateCastlingRights()
    #time.sleep(1)
    drawStuff()
    drawHighlight(end)
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
            if event.type == pygame.MOUSEBUTTONUP:
                mousex, mousey = event.pos
                msqr = squareClicked(mousex, mousey)
                if msqr != -1:

                    # Moves a piece if one was selected
                    if temp != -1:
                        for s in ChessEngine.PieceMovement(temp):
                            if msqr == s:
                                ChessEngine.MovePiece(temp, msqr)
                                ChessEngine.updateCastlingRights()
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
                            folder = ChessEngine.whitepieces
                        elif turn == 'black':
                            folder = ChessEngine.blackpieces
                        for piece in folder:
                            for i in piece.piecelist:
                                if msqr == i:
                                    drawMoves(msqr)
                                    temp = msqr
                                    break

                                             
def main():
    # Variables and such
    pygame.display.set_caption('Good Luck Loser!')
    ChessEngine.updateCastlingRights()
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
        # Checks for mate
        if mainState.turn != 'end':
            k = ChessEngine.isMated(mainState.turn)
        if k:
            if k == 'checkmate':
                message = MessageFont.render("CHECKMATE!", 1, blue)
            elif k == 'stalemate':
                message = MessageFont.render("STALEMATE!", 1, blue)
            screen.blit(message, (screenwidth / 2 - marginsize, marginsize /2))
            pygame.display.update()
            mainState.turn = 'end'
        # Checks for draw
        if ChessEngine.isDraw():
            message = MessageFont.render("INSUFFICIENT MATERIAL", 1, blue)
            screen.blit(message, (screenwidth / 2 - 2*marginsize, marginsize / 2))
            pygame.display.update()
            mainState.turn = 'end'

        elif mainState.turn == 'white':
            DoPlayerTurn(mainState.turn)

        elif mainState.turn == 'black':
            DoCompTurn(mainState.turn)
main()
