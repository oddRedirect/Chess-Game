import sys
import copy

class Piece:
    piecelist = []
    colour = ""
    name = ""
    picture = ""
    value = 0

    def loop(self):
        self.piecelist = []
        for num in range(64):
            if boardlist[num] == id(self):
                self.piecelist.append(num)


class boardState:
    prevBoard = None
    prevState = None
    enPassant = None
    # Castling
    ws, wl, bs, bl = True, True, True, True

curState = boardState()


# White pieces:
wk = Piece()
wk.name = "king"
wk.picture = "Pieces/WhiteKing.png"

wq = Piece()
wq.name = "queen"
wq.picture = "Pieces/WhiteQueen.png"

wb = Piece()
wb.name = "bishop"
wb.picture = "Pieces/WhiteBishop.png"

wn = Piece()
wn.name = "knight"
wn.picture = "Pieces/WhiteKnight.png"

wr = Piece()
wr.name = "rook"
wr.picture = "Pieces/WhiteRook.png"

wp = Piece()
wp.name = "pawn"
wp.picture = "Pieces/WhitePawn.png"

whitepieces = [wk, wq, wb, wn, wr, wp]
for y in whitepieces:
    y.colour = 'white'

# Black pieces:
bk = Piece()
bk.name = "king"
bk.picture = "Pieces/BlackKing.png"

bq = Piece()
bq.name = "queen"
bq.picture = "Pieces/BlackQueen.png"

bb = Piece()
bb.name = "bishop"
bb.picture = "Pieces/BlackBishop.png"

bn = Piece()
bn.name = "knight"
bn.picture = "Pieces/BlackKnight.png"

br = Piece()
br.name = "rook"
br.picture = "Pieces/BlackRook.png"

bp = Piece()
bp.name = "pawn"
bp.picture = "Pieces/BlackPawn.png"

blackpieces = [bk, bq, bb, bn, br, bp]
for y in blackpieces:
    y.colour = 'black'

# Misc.
allpieces = whitepieces + blackpieces
boardlist = range(64)


# Clears the board of all pieces
def emptyboard():
    for i in range(64):
        boardlist[i] = 0


# Adds the positions of all pieces on the board to their respective objects
def updatepieces():
    for y in allpieces:
            y.loop()


# Reverts the board to the starting position
def resetboard():
    emptyboard()
    boardlist[4] = id(wk) ## Idea is to use this approach for the entire boardlist, even in MovePiece
    boardlist[3] = id(wq) ## Remove piecelist from Piece class eventually ... orrrr not
    boardlist[2], boardlist[5] = id(wb), id(wb)
    boardlist[1], boardlist[6] = id(wn), id(wn)
    boardlist[0], boardlist[7] = id(wr), id(wr)
    for i in range(8, 16):
        boardlist[i] = id(wp)
    boardlist[60] = id(bk)
    boardlist[59] = id(bq)
    boardlist[61], boardlist[58] = id(bb), id(bb)
    boardlist[62], boardlist[57] = id(bn), id(bn)
    boardlist[63], boardlist[56] = id(br), id(br)
    for i in range(48, 56):
        boardlist[i] = id(bp)
    updatepieces()

resetboard()


# Resets the board and initializes some values
def resetgame():
    global curState
    resetboard()
    curState = boardState()


# Converts sqr to a number for ease of calculation (sqr is a string coord)
def coordtonum(sqr):
    j = ord(sqr[0]) - 97
    return 8 * (int(sqr[1]) - 1) + j


# Converts num back to a coordinate
def numtocoord(num):
    q = num % 8
    n = (num / 8) + 1
    m = chr(q + 97)
    return m + str(n)


# Returns the piece on square num
def pieceatsqr(num):
    if num > 63 or num < 0:
        return None
    s = boardlist[num]
    for y in allpieces:
        if id(y) == s:
            return y
    return None


# Changes the value of the piece on start to end
def ChangeVar(start, end):
    j = pieceatsqr(start)
    boardlist[start] = 0
    boardlist[end] = id(j)


# Checks if a pawn has made it to the eighth/first rank
def pawnPromoted(end):
    s = numtocoord(end)
    pce = pieceatsqr(end)
    if s[1] == '8' and pce == wp:
        return True
    if s[1] == '1' and pce == bp:
        return True
    return False


# Moves the piece on start to end
def MovePiece(start, end):
    j = pieceatsqr(start)
    m = pieceatsqr(end)

    curState.prevState = copy.copy(curState)
    curState.prevBoard = copy.copy(boardlist)
    
    if not j or (m and j.colour == m.colour):
        return 'Invalid move'

    ChangeVar(start, end)

    # Move the rook if the king castled
    if j.name == 'king' and (end - start) == 2:
        ChangeVar(end + 1, start + 1)
    elif j.name == 'king' and (start - end) == 2:
        ChangeVar(end - 2, start - 1)

    # Turn a promoted pawn into a queen
    if pawnPromoted(end):
        if j.colour == 'white':
            boardlist[end] = id(wq)
        if j.colour == 'black':
            boardlist[end] = id(bq)

    curState.enPassant = None
    # Checks if En Passant is valid
    if j.name == 'pawn':
        s, e = start, end
        if abs(s-e) == 16:
            if j.colour == 'black':
                curState.enPassant = e+8
            if j.colour == 'white':
                curState.enPassant = e-8
        if abs(s-e) == 7 or abs(s-e) == 9:
            if not m:
                if j.colour == 'white':
                    boardlist[e-8] = 0
                elif j.colour == 'black':
                    boardlist[e+8] = 0

    updatepieces()
    updateCastlingRights()


# Checks if each side can still castle
def updateCastlingRights():
    if boardlist[4] != id(wk):
        curState.ws, curState.wl = False, False
    if boardlist[60] != id(bk):
        curState.bs, curState.bl = False, False
    if boardlist[0] != id(wr):
        curState.wl = False
    if boardlist[56] != id(br):
        curState.bl = False
    if boardlist[7] != id(wr):
        curState.ws = False
    if boardlist[63] != id(br):
        curState.bs = False


# Undoes the previous move made
def UndoMove():
    global curState
    global boardlist
    if curState.prevState == None:
        return
    
    boardlist = curState.prevBoard
    curState = curState.prevState
        
    updatepieces()

    
#helper
def rookMovement(i, colour):
    p = []
    x = i - 8
    while x >= 0:
        if boardlist[x] != 0:
            m = pieceatsqr(x)
            if m and m.colour != colour:
                p.append(x)
            break
        p.append(x)
        x -= 8
    x = i + 8
    while x < 64:
        if boardlist[x] != 0:
            m = pieceatsqr(x)
            if m and m.colour != colour:
                p.append(x)
            break
        p.append(x)
        x += 8
    x = i
    while x % 8 > 0:
        if boardlist[x-1] != 0:
            m = pieceatsqr(x-1)
            if m and m.colour != colour:
                p.append(x-1)
            break
        p.append(x-1)
        x -= 1
    x = i + 1
    while x % 8 > 0:
        if boardlist[x] != 0:
            m = pieceatsqr(x)
            if m and m.colour != colour:
                p.append(x)
            break
        p.append(x)
        x += 1
    return p

#helper
def bishopMovement(i, colour):
    p =[]
    x = i - 9
    while x % 8 < 7 and x >= 0:
        if boardlist[x] != 0:
            m = pieceatsqr(x)
            if m and m.colour != colour:
                p.append(x)
            break
        p.append(x)
        x -= 9
    x = i + 9
    while x % 8 > 0 and x < 64:
        if boardlist[x] != 0:
            m = pieceatsqr(x)
            if m and m.colour != colour:
                p.append(x)
            break
        p.append(x)
        x += 9
    x = i - 7
    while x % 8 > 0 and x > 0:
        if boardlist[x] != 0:
            m = pieceatsqr(x)
            if m and m.colour != colour:
                p.append(x)
            break
        p.append(x)
        x -= 7
    x = i + 7
    while x % 8 < 7 and x < 64:
        if boardlist[x] != 0:
            m = pieceatsqr(x)
            if m and m.colour != colour:
                p.append(x)
            break
        p.append(x)
        x += 7
    return p

#helper
def kingMovement(i):
    sqr = numtocoord(i)
    m = sqr[0]
    n = sqr[1]
    p = []
    if m != 'a':
        p.append(i - 1)
        if n != '1':
            p.append(i - 9)
        if n != '8':
            p.append(i + 7)
    if m != 'h':
        p.append(i + 1)
        if n != '1':
            p.append(i - 7)
        if n != '8':
            p.append(i + 9)
    if n != '1':
        p.append(i - 8)
    if n != '8':
        p.append(i + 8)
    return p

#helper
def knightMovement(i):
    sqr = numtocoord(i)
    m = sqr[0]
    n = sqr[1]
    p = []
    if m != 'a' and m != 'b':
        if n != '1':
            p.append(i - 10)
        if n != '8':
            p.append(i + 6)
    if n != '1' and n != '2':
        if m != 'a':
            p.append(i - 17)
        if m != 'h':
            p.append(i - 15)
    if n != '7' and n != '8':
        if m != 'a':
            p.append(i + 15)
        if m != 'h':
            p.append(i + 17)
    if m != 'g' and m != 'h':
        if n != '1':
            p.append(i - 6)
        if n != '8':
            p.append(i + 10)
    return p

# Returns a list of squares that are valid moves for the piece on square i
def PieceMovement(i):
    j = pieceatsqr(i)
    sqr = numtocoord(i)
    m = sqr[0]
    n = sqr[1]
    p = []
    
    if not j:
        return 'Invalid start square'

    # King Movement
    elif j.name == 'king':
        p = kingMovement(i)
        # Castling
        if (j.colour == 'white' and curState.ws) or (j.colour == 'black' and curState.bs):
            a = pieceatsqr(i + 1)
            b = pieceatsqr(i + 2)
            if not a and not b:
                # Cannot castle through check
                if isSafe(i+1, j.colour) and isSafe(i+2, j.colour):
                    p.append(i + 2)
        if (j.colour == 'white' and curState.wl) or (j.colour == 'black' and curState.bl):
            a = pieceatsqr(i - 1)
            b = pieceatsqr(i - 2)
            c = pieceatsqr(i - 3)
            if not(a) and not(b) and not(c):
                if isSafe(i-1, j.colour) and isSafe(i-2, j.colour) and isSafe(i-3, j.colour):
                    p.append(i - 2)    

    # Pawn Movement
    elif j.name == 'pawn':
        ep = curState.enPassant
        if j.colour == 'white':
            up1, up2 = i+8, i+16
            xleft, xright = i+7, i+9
            startrank = '2'
        elif j.colour == 'black':
            up1, up2 = i-8, i-16
            xleft, xright = i-9, i-7
            startrank = '7'
        s = pieceatsqr(up1)
        if not(s):
            p.append(up1)
        if m != 'a':
            z = pieceatsqr(xleft)
            if (z and z.colour != j.colour) or ep == xleft:
                p.append(xleft)
        if m != 'h':
            y = pieceatsqr(xright)
            if (y and y.colour != j.colour) or ep == xright:
                p.append(xright)
        if n == startrank:
            t = pieceatsqr(up2)
            if not(s) and not(t):
                p.append(up2)
        
    # Knight Movement
    elif j.name == 'knight':
        p = knightMovement(i)

    # Rook Movement
    elif j.name == 'rook':
        p = rookMovement(i, j.colour)

    # Bishop Movement
    elif j.name == 'bishop':
        p = bishopMovement(i, j.colour)

    # Queen Movement
    elif j.name == 'queen':
        p = rookMovement(i, j.colour) + bishopMovement(i, j.colour)

    def MoveFilterer(x):
        # Make sure we don't have friendly fire (from the king or knight)
        if boardlist[x] != 0 and (pieceatsqr(x)).colour == j.colour:
            return False
        # Cannot castle out of check
        if j.name == 'king' and abs(x-i) == 2 and isInCheck(j.colour):
            return False
        legalMove = True
        MovePiece(i, x)
        # Cannot move into check
        if isInCheck(j.colour):
           legalMove = False 
        UndoMove()
        return legalMove

    return filter(MoveFilterer, p)


# Danger Functions
def PawnDanger(i, colour):
    if colour == 'white':
        if i <= 47 and i % 8 != 7 and boardlist[i+9] == id(bp):
            return True
        if i <= 47 and i % 8 != 0 and boardlist[i+7] == id(bp):
            return True
    elif colour == 'black':
        if i >= 16 and i % 8 != 0 and boardlist[i-9] == id(wp):
            return True
        if i >= 16 and i % 8 != 7 and boardlist[i-7] == id(wp):
            return True

def KnightDanger(sqr, colour):
    if colour == 'white':
        knight = id(bn)
    else:
        knight = id(wn)
    for y in knightMovement(sqr):
        if boardlist[y] == knight:
            return True

def KingDanger(sqr, colour):
    if colour == 'white':
        king = id(bk)
    else:
        king = id(wk)
    for y in kingMovement(sqr):
        if boardlist[y] == king:
            return True

def BigPieceDanger(sqr, colour):
    if colour == 'white':
        rook, bishop, queen = id(br), id(bb), id(bq)
    else:
        rook, bishop, queen = id(wr), id(wb), id(wq)
    for y in rookMovement(sqr, colour):
        if boardlist[y] == rook or boardlist[y] == queen:
            return True
    for y in bishopMovement(sqr, colour):
        if boardlist[y] == bishop or boardlist[y] == queen:
            return True

# Determines whether a move can get you killed
def isSafe(sqr, colour):
    if PawnDanger(sqr, colour):
        return False
    if KnightDanger(sqr, colour):
        return False
    if KingDanger(sqr, colour):
        return False
    if BigPieceDanger(sqr, colour):
        return False
    return True


# determines whether the 'colour' king is in check
def isInCheck(colour):
    if colour == 'white':
        kingsqr = wk.piecelist[0]
    if colour == 'black':
        kingsqr = bk.piecelist[0]
    return not(isSafe(kingsqr, colour))


# determines whether colour is in checkmate, stalemate or neither
def isMated(colour):
    if colour == 'white':
        pieces = whitepieces
    elif colour == 'black':
        pieces = blackpieces
    for y in pieces:
        for i in y.piecelist:
            if len(PieceMovement(i)) > 0:
                return False
    if isInCheck(colour):
        return 'CHECKMATE'
    return 'STALEMATE'


# Returns the boardState i states ago
def prev(i, state):
    if i == 0 or not(state):
        return None
    if i <= 1:
        return state.prevState
    return prev(i-1, state.prevState)


# Determines whether the current position has been consecutively repeated three times
def isRepitition():
    tempState = prev(3, curState)
    tempState2 = prev(4, tempState)
    if tempState and tempState2:
        if boardlist == tempState.prevBoard and boardlist == tempState2.prevBoard:
            return True
    return False


# Determines whether the game is a draw by insufficient material
def isInsufficient():
    if len(wp.piecelist) > 0 or len(bp.piecelist) > 0:
        return False
    elif len(wq.piecelist) > 0 or len(bq.piecelist) > 0:
        return False
    elif len(wr.piecelist) > 0 or len(br.piecelist) > 0:
        return False
    elif len(wb.piecelist) > 1 or len(bb.piecelist) > 1:
        return False
    elif len(wb.piecelist) > 0 and len(wn.piecelist) > 0:
        return False
    elif len(bb.piecelist) > 0 and len(bn.piecelist) > 0:
        return False
    return True

# Checks whether the game is a draw
def isDraw():
    if isInsufficient():
        return "INSUFFICIENT MATERIAL"
    if isRepitition():
        return "DRAW BY REPITITION"
    return False
    
