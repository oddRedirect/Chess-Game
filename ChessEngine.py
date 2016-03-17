import sys

# Global Constants:
Pval = 1
Nval = 3
Bval = 3.2
Rval = 5
Qval = 9
Kval = 1000

class Piece:
    piecelist = []
    colour = ""
    name = ""
    picture = ""
    value = 0
    lastcapture = False
    
    # For Kings only
    cancastleshort = True
    cancastlelong = True

    # For Pawns only
    justpromoted = False

    def loop(self, num):
        for y in self.piecelist:
            if num == y:
                boardlist[num] = self.colour + self.name

    def changeSqr(self, start, end):
        i = 0
        j = self.piecelist
        while i < len(j):
            if j[i] == start:
                j[i] = end
            i += 1

    def removeSqr(self, sqr):
        i = 0
        j = self.piecelist
        while i < len(j):
            if j[i] == sqr:
                j.remove(j[i])
            i += 1


class captureState:
    lastcapture = False
    lcsqr = False
    epcolour = False
    epsqr = False
    ep_prev = False


# White pieces:
wk = Piece()
wk.name = "king"
wk.picture = "WhiteKing.png"

wq = Piece()
wq.name = "queen"
wq.picture = "WhiteQueen.png"

wb = Piece()
wb.name = "bishop"
wb.picture = "WhiteBishop.png"

wn = Piece()
wn.name = "knight"
wn.picture = "WhiteKnight.png"

wr = Piece()
wr.name = "rook"
wr.picture = "WhiteRook.png"

wp = Piece()
wp.name = "pawn"
wp.picture = "WhitePawn.png"

whitepieces = [wk, wq, wb, wn, wr, wp]
for y in whitepieces:
    y.colour = 'white'

# Black pieces:
bk = Piece()
bk.name = "king"
bk.picture = "BlackKing.png"

bq = Piece()
bq.name = "queen"
bq.picture = "BlackQueen.png"

bb = Piece()
bb.name = "bishop"
bb.picture = "BlackBishop.png"

bn = Piece()
bn.name = "knight"
bn.picture = "BlackKnight.png"

br = Piece()
br.name = "rook"
br.picture = "BlackRook.png"

bp = Piece()
bp.name = "pawn"
bp.picture = "BlackPawn.png"

blackpieces = [bk, bq, bb, bn, br, bp]
for y in blackpieces:
    y.colour = 'black'

# Misc.
allpieces = whitepieces + blackpieces
boardlist = range(64)


# Clears the board of all pieces
def emptyboard():
    i = 0
    while i < 64:
        boardlist[i] = i
        i += 1


# Finds the positions of all pieces on the board
def updateboard():
    emptyboard()
    x = 0
    while x < 64:
        for y in allpieces:
            y.loop(x)
        x += 1


# Reverts the board to the starting position
def resetboard():
    wk.piecelist = [4]
    wq.piecelist = [3]
    wb.piecelist = [2, 5]
    wn.piecelist =[1, 6]
    wr.piecelist = [0, 7]
    wp.piecelist = range(8, 16)
    bk.piecelist = [60]
    bq.piecelist = [59]
    bb.piecelist = [61, 58]
    bn.piecelist = [62, 57]
    br.piecelist = [63, 56]
    bp.piecelist = range(48, 56)
    updateboard()

resetboard()


# Resets the board and initializes some values
def resetgame():
    resetboard()
    wk.cancastleshort = True
    wk.cancastlelong = True
    bk.cancastleshort = True
    bk.cancastllong = True


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
    updateboard()
    s = boardlist[num]
    for y in allpieces:
        if y.colour + y.name == s:
            return y
    return "empty"


# Changes the value of the piece on start to end
def ChangeVar(start, end):
    for y in allpieces:
        y.changeSqr(start, end)


# Removes the piece on sqr from the board
def RemovePiece(sqr):
    for y in allpieces:
        y.removeSqr(sqr)


# Adds piece onto the board on square sqr
def AddPiece(piece, sqr):
    piece.piecelist.append(sqr)


# Checks if a pawn has made it to the eighth/first rank
def pawnPromoted():
    for y in wp.piecelist:
        s = numtocoord(y)
        if s[1] == '8':
            return True
    for y in bp.piecelist:
        s = numtocoord(y)
        if s[1] == '1':
            return True
    return False


# Moves the piece on start to end
def MovePiece(start, end):
    j = pieceatsqr(start)
    m = pieceatsqr(end)

    if j == 'empty':
        return 'Invalid start square'
    elif m == 'empty':
        captureState.lastcapture = False
        ChangeVar(start,end)
    elif j.colour == m.colour:
        return 'Invalid move'
    else:
        RemovePiece(end)
        captureState.lastcapture = m
        captureState.lcsqr = end
        ChangeVar(start, end)

    # Move the rook if the king castled
    if j.name == 'king' and (end - start) == 2:
        ChangeVar(end + 1, start + 1)
    elif j.name == 'king' and (start - end) == 2:
        ChangeVar(end - 2, start - 1)

    # Turn a promoted pawn into a queen
    if pawnPromoted():
        RemovePiece(end)
        if j.colour == 'white':
            AddPiece(wq, end)
        if j.colour == 'black':
            AddPiece(bq, end)
        j.justpromoted = True
    else:
        for y in [wp, bp]:
            y.justpromoted = False

   # captureState.ep_prev = captureState.epcolour
    #captureState.epcolour = False
    # Checks if En Passant is valid (work in progress)
##    if j.name == 'pawn':
##        s, e = start, end
##        if s-e == 16 or e-s == 16:
##            if j.colour == 'black':
##                captureState.epcolour = 'white'
##                captureState.epsqr = end+8
##            if j.colour == 'white':
##                captureState.epcolour = 'black'
##                captureState.epsqr = end-8
##        if s-e == 7 or e-s == 7 or s-e == 9 or e-s == 9:
##            if m == 'empty':
##                if j.colour == 'white':
##                    RemovePiece(e-8)
##                    captureState.lastcapture = bp
##                    captureState.lcsqr = e-8
##                elif j.colour == 'black':
##                    RemovePiece(e+8)
##                    captureState.lastcapture = wp
##                    captureState.lcsqr = e+8

    updateboard()


# Checks if each side can still castle
def updateCastlingRights():
    if boardlist[4] != 'whiteking':
        wk.cancastleshort, wk.cancastlelong = False, False
    if boardlist[60] != 'blackking':
        bk.cancastlshort, bk.cancastlelong = False, False
    if boardlist[0] != 'whiterook':
        wk.cancastlelong = False
    if boardlist[56] != 'blackrook':
        bk.cancastlelong = False
    if boardlist[7] != 'whiterook':
        wk.cancastleshort = False
    if boardlist[63] != 'blackrook':
        bk.cancastleshort = False


# Undoes the previous move made
def UndoMove(end, start):
    j = pieceatsqr(end)
    ChangeVar(end, start)
    if captureState.lastcapture:
        AddPiece(captureState.lastcapture, captureState.lcsqr)
    captureState.lastcapture = False

    if j.name == 'king' and (end - start) == 2:
        ChangeVar(start + 1, end + 1)
    elif j.name == 'king' and (start - end) == 2:
        ChangeVar(start - 1, end - 2)

    for y in [wp, bp]:
        if y.justpromoted:
            RemovePiece(start)
            AddPiece(y, start)
            y.justpromoted = False

    # More En Passant stuff
    #captureState.epcolour = captureState.ep_prev

    updateboard()

    
#helper
def rookMovement(i, colour):
    p = []
    x = i - 8
    while x >= 0:
        if isinstance(boardlist[x], str):
            if (boardlist[x])[0:5] != colour:
                p.append(x)
            break
        p.append(x)
        x -= 8
    x = i + 8
    while x < 64:
        if isinstance(boardlist[x], str):
            if (boardlist[x])[0:5] != colour:
                   p.append(x)
            break
        p.append(x)
        x += 8
    x = i
    while x % 8 > 0:
        if isinstance(boardlist[x-1], str):
            if (boardlist[x-1])[0:5] != colour:
                p.append(x -1)
            break
        p.append(x - 1)
        x -= 1
    x = i + 1
    while x % 8 > 0:
        if isinstance(boardlist[x], str):
            if (boardlist[x])[0:5] != colour:
                p.append(x)
            break
        p.append(x)
        x += 1
    return p

#helper
def bishopMovement(i, colour):
    p =[]
    x = i - 9
    while x % 8 < 7 and x > 0:
        if isinstance(boardlist[x], str):
            if (boardlist[x])[0:5] != colour:
                p.append(x)
            break
        p.append(x)
        x -= 9
    x = i + 9
    while x % 8 > 0 and x < 64:
        if isinstance(boardlist[x], str):
            if (boardlist[x])[0:5] != colour:
                p.append(x)
            break
        p.append(x)
        x += 9
    x = i - 7
    while x % 8 > 0 and x > 0:
        if isinstance(boardlist[x], str):
            if (boardlist[x])[0:5] != colour:
                p.append(x)
            break
        p.append(x)
        x -= 7
    x = i + 7
    while x % 8 < 7 and x < 64:
        if isinstance(boardlist[x], str):
            if (boardlist[x])[0:5] != colour:
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

# Returns a list of squares that are valid moves for the piece on num
def PieceMovementHelp(num):
    i = num
    j = pieceatsqr(num)
    sqr = numtocoord(num)
    m = sqr[0]
    n = sqr[1]
    p = []
    q = []

    if j == 'empty':
        return 'Invalid start square'

    # King Movement
    elif j.name == 'king':
        p = kingMovement(i)
        # Castling
        if j.cancastleshort and i <= 61:
            a = pieceatsqr(i + 1)
            b = pieceatsqr(i + 2)
            if a == 'empty' and b == 'empty':
                p.append(i + 2)
        if j.cancastlelong and i >= 3:
            a = pieceatsqr(i - 1)
            b = pieceatsqr(i - 2)
            c = pieceatsqr(i - 3)
            if a == 'empty' and b == 'empty' and c == 'empty':
                p.append(i - 2)    

    # Pawn Movement
    elif j.name == 'pawn':
        if j.colour == 'white':
            u = 1
            startrank = '2'
            endrank = '8'
            leftfile = 'a'
            rightfile = 'h'
        elif j.colour == 'black':
            u = -1
            startrank = '7'
            endrank = '1'
            leftfile = 'h'
            rightfile = 'a'
        # u is used to signify direction of pawn movement
        if n != endrank:
            s = pieceatsqr(i + 8*u)
            if s == 'empty':
                q.append(i + 8*u)
            z = pieceatsqr(i + 7*u)
            if z != 'empty' and z.colour != j.colour and m != leftfile:
                q.append(i + 7*u)
            if i <= 54:
                y = pieceatsqr(i + 9*u)
                if y != 'empty' and y.colour != j.colour and m != rightfile:
                    q.append(i + 9*u)
        if n == startrank:
            t = pieceatsqr(i + 16*u)
            if s == 'empty' and t == 'empty':
                q.append(i + 16*u)
        #if captureState.epcolour == j.colour:
         #   sqr = captureState.epsqr
          #  if sqr == i + 9*u or sqr == i + 7*u:
           #     q.append(sqr)
        
    # Knight Movement
    elif j.name == 'knight':
        p = knightMovement(i)

    # Rook Movement
    elif j.name == 'rook':
        q = rookMovement(i, j.colour)

    # Bishop Movement
    elif j.name == 'bishop':
        q = bishopMovement(i, j.colour)

    # Queen Movement
    elif j.name == 'queen':
        q = rookMovement(i, j.colour) + bishopMovement(i, j.colour)

    # Make sure we don't have friendly fire (from the king or knight)
    for x in p:
        if isinstance(boardlist[x], str) and (boardlist[x])[0:5] == j.colour:
            continue
        else:
            q.append(x)

    return q


# Determines whether a move can get you killed
def isSafe(sqr, colour, opp):
    i = sqr
    # Pawn danger?
    if colour == 'white':
        if i <= 47 and i % 8 != 7 and boardlist[i+9] == 'blackpawn':
            return False
        if i <= 47 and i % 8 != 0 and boardlist[i+7] == 'blackpawn':
            return False
    elif colour == 'black':
        if i >= 16 and i % 8 != 0 and boardlist[i-9] == 'whitepawn':
            return False
        if i >= 16 and i % 8 != 7 and boardlist[i-7] == 'whitepawn':
            return False
    # Knight danger?
    for y in knightMovement(sqr):
        if boardlist[y] == opp+ 'knight':
            return False
    # King danger?
    for y in kingMovement(sqr):
        if boardlist[y] == opp+ 'king':
            return False
    # Rooks, and bishops, and queens, oh my!
    for y in rookMovement(sqr, colour):
        if boardlist[y] == opp+ 'rook' or boardlist[y] == opp+ 'queen':
            return False
    for y in bishopMovement(sqr, colour):
        if boardlist[y] == opp+ 'bishop' or boardlist[y] == opp+ 'queen':
            return False
    return True


# determines whether the 'colour' king is in check
def isInCheck(colour):
    if colour == 'white':
        opp = 'black'
        kingsqr = wk.piecelist[0]
    if colour == 'black':
        opp = 'white'
        kingsqr = bk.piecelist[0]
    return not(isSafe(kingsqr, colour, opp))


# determines whether colour is in checkmate, stalemate or neither
def isMated(colour):
    if colour == 'white':
        dn = whitepieces
    elif colour == 'black':
        dn = blackpieces
    for y in dn:
        for i in y.piecelist:
            if len(PieceMovement(i)) > 0:
                return False
    if isInCheck(colour):
        return 'checkmate'
    return 'stalemate'


# Determines whether the game is a draw by insufficient material
def isDraw():
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


# (see PieceMovementHelper)
def PieceMovement(sqr):
    j = pieceatsqr(sqr)
    q = []
    for move in PieceMovementHelp(sqr):
        # Cannot castle out of check
        if isInCheck(j.colour) and j.name == 'king' and (move == sqr+2 or move  == sqr-2):
            continue
        MovePiece(sqr, move)
        if not isInCheck(j.colour):
            q.append(move)
        UndoMove(move, sqr)
    return q


# Slap some values on errthing
for y in allpieces:
    if y.name == 'pawn':
        y.value = Pval
    elif y.name == 'knight':
        y.value = Nval
    elif y.name == 'bishop':
        y.value = Bval
    elif y.name == 'rook':
        y.value = Rval
    elif y.name == 'queen':
        y.value = Qval


# Gives a numerical value for how good colour's position is
def EvaluatePosition(colour):
    evalu = 0

    if colour == 'white':
        opp = 'black'
        folder = whitepieces
        xfolder = blackpieces
        u = 1
        
    elif colour == 'black':
        opp = 'white'
        folder = blackpieces
        xfolder = whitepieces
        u = -1

    pawns = folder[5]
    knights = folder[3]
    bishops = folder[2]
    rooks = folder[4]
    queen = folder[1]
    king = folder[0]
        
    evalu += Pval * len(pawns.piecelist)
    evalu += Nval * len(knights.piecelist)
    evalu += Bval * len(bishops.piecelist)
    evalu += Rval * len(rooks.piecelist)
    evalu += Qval * len(queen.piecelist)

    for y in pawns.piecelist:
        # Add incentives for centred pawns
        if y == 27 or y == 28 or y == 35 or y == 36:
            evalu += 0.4

        # Add incentives for making use of outposts for knights
        if y > 24 and y < 48:
            if boardlist[y+9*u] == colour + 'knight' or boardlist[y+7*u] == colour + 'knight':
                evalu += 0.35

        # Passed pawns are GREAT
        if colour == 'white' and y > 32 and pieceatsqr(y+8) == 'empty':
            if y <= 54 and boardlist[y+9] != 'blackpawn' and boardlist[y+7] != 'blackpawn':
                evalu += y/8 - 3
        if colour == 'black' and y < 31 and pieceatsqr(y-8) == 'empty':
            if y >= 9 and boardlist[y-9] != 'whitepawn' and boardlist[y-7] != 'whitepawn':
                evalu += 4 - y/8

        # Doubled pawns are BAD
        if boardlist[y + 8] == colour + 'pawn':
            evalu -= 0.5

        # Don't let pawns drop off like flies
        if not(isSafe(y, colour, opp)) and isSafe(y, opp, colour):
            evalu -= 0.4

    for y in knights.piecelist:
        # Add incentives for development / attacking w knights
        if y == 18 or y == 21 or y == 42 or y == 45:
            evalu += 0.3
        # Don't hang your knights
        if not(isSafe(y, colour, opp)):
            evalu -= 1.2

    for y in bishops.piecelist:
        # Fianchetto
        if colour == 'white' and (y == 9 or y == 14):
            evalu += 0.35
        if colour == 'black' and (y == 49 or y == 54):
            evalu += 0.35
        # Don't hang your bishops
        if not(isSafe(y, colour, opp)):
            evalu -= 1.3

    for y in rooks.piecelist:
        f = y % 8
        # Centralize rooks
        if f == 3 or f == 4:
            evalu += 0.25
        # Rooks behind passed pawns or on open files
        for x in [f+8, f+16, f+24, f+32, f+40, f+48, f+56]:
            if boardlist[x] == colour + 'pawn':
                evalu -= 0.5
        # Make sure you don't make a ROOKie mistake
        if not(isSafe(y, colour, opp)):
            evalu -= 2.1

    # Add incentives for castling
    hs = king.piecelist[0]
    if hs == 2 or hs == 6 or hs == 57 or hs == 62:
        evalu += 0.7

    # Subtract brownie points for pieces attacked by pawns
    for i in xfolder[5].piecelist:
        if i <= 54 and i >= 9:
            j = pieceatsqr(i - 9*u)
            if (j != 'empty' and j.colour == colour):
                evalu -= 0.6
        if i <= 55 and i >= 7:
            k = pieceatsqr(i - 7*u)
        if (k != 'empty' and k.colour == colour):
            evalu -= 0.6

    # Make sure bae is safe
    for y in queen.piecelist:
        if not(isSafe(y, colour, opp)):
           evalu -= 4.2

    # Get that mate doe -- sketch sketch sketch
    #if isMated(opp) == 'checkmate':
     #   evalu += 1000
    TheWorst = king.piecelist[0]
    if not isSafe(TheWorst, colour, opp):
        rekt = True
        evalu -= 0.5
        for y in kingMovement(TheWorst):
            if isSafe(y, colour, opp):
                rekt = False
        if rekt:
            xq = xfolder[1]
            if len(xq.piecelist) > 0 and isSafe(xq.piecelist[0], colour, opp):
                evalu -= 500

    return evalu


class Position:
    evaluation = 0
    movestart = 0
    moveend = 0
    

# Returns the ~best~ move for colour
def FindBest(colour):
    if colour == 'white':
        k = whitepieces
        opp = 'black'
    elif colour == 'black':
        k = blackpieces
        opp = 'white'

    bestsofar = Position()
    bestsofar.evaluation = -1000

    for y in k:
        for start in y.piecelist:
            moveslist = PieceMovement(start)
            for end in moveslist:
                cur = Position()
                cur.movestart = start
                cur.moveend = end
                i = pieceatsqr(end)
                j = pieceatsqr(start)
                uwotm8 = isInCheck(colour)

                MovePiece(start, end)
                if i == 'empty' and not(isSafe(end, colour, opp)) and isSafe(end, opp, colour):
                    if not uwotm8:
                        UndoMove(end, start)
                        continue
                cur.evaluation = EvaluatePosition(colour) - EvaluatePosition(opp)
                UndoMove(end, start)

                # No kamikaze allowed
                if i != 'empty' and i.value < j.value:
                    if not(isSafe(end, colour, opp)) and not uwotm8:
                        continue

                if cur.evaluation >= bestsofar.evaluation:
                    bestsofar = cur

    print bestsofar.evaluation
    return bestsofar.movestart, bestsofar.moveend


# returns the file or rank that colour can use to attack the enemy king
def hasOpposition(kingpos, opp_pos):
    a, af, ar = kingpos, kingpos%8, kingpos/8
    b, bf, br = opp_pos, opp_pos%8, opp_pos/8
    if a == b + 2 or b == a + 2:
        f = b % 8
        return [f, f+8, f+16, f+24, f+32, f+40, f+48, f+56]
    elif a == b + 16 or b == a + 16 or (bf == 0 and a == b+17):
        r = (b / 8) * 8
        return [r, r+1, r+2, r+3, r+4, r+5, r+6, r+7]
    return False

# Opposes the enemy king (returns the square to move ur king to)
def getOpposition(kingpos, opp_pos):
    b = opp_pos
    for y in PieceMovement(kingpos):
        if y == b + 16 or b == y + 16 or (y/8 == b/8 and (y == b + 2 or b == y + 2)):
            return y
    for y in PieceMovement(kingpos):
        if y == b + 32 or b == y + 32 or (y/8 == b/8 and (y == b + 4 or b == y + 4)):
            return y
    for y in PieceMovement(kingpos):
        if y == b + 48 or b == y + 48 or (y/8 == b/8 and (y == b + 6 or b == y + 6)):
            return y
    return False


# Returns true if the position seems to be an endgame
def isEndgame():
    if len(wp.piecelist) == 0 or len(bp.piecelist) == 0:
        return True
    elif len(wq.piecelist) == 0 and len(bq.piecelist) == 0:
        return True
    elif len(wb.piecelist) == 0 and len(wn.piecelist) == 0:
        if len(bb.piecelist) == 0 and len(bn.piecelist) == 0:
            return True
    return False


# Returns a move to maybe get closer to destroying the player
def BasicMates(colour):
    if colour == 'white':
        opp = 'black'
        king = wk.piecelist
        rooks = wr.piecelist + wq.piecelist
        queen = wq.piecelist
        xking = bk.piecelist
    elif colour == 'black':
        opp = 'white'
        king = bk.piecelist
        rooks = br.piecelist + bq.piecelist
        queen = bq.piecelist
        xking = wk.piecelist
    kingpos = king[0]
    opp_pos = xking[0]
    
    # 2 Rook Checkmate
    if len(rooks) >= 2:
        kf = opp_pos % 8
        kr = opp_pos / 8
        for y in rooks:
            for x in PieceMovement(y):
                if not(isSafe(y, colour, opp)) and isSafe(x, colour, opp):
                    if y / 8 == kr + 1:
                        if x / 8 == kr+1 and x%8 != kf+2 and x%8 != kf-2:
                            return y, x
                    else:
                        return y, x
        if rooks[0] / 8 == kr + 1 or rooks[1] / 8 == kr + 1:
            for y in rooks:
                for x in PieceMovement(y):
                    if isSafe(x, colour, opp) and x / 8 == kr:
                        if y / 8 != kr + 1 or (rooks[0]/8 == kr+1 and rooks[1]/8 == kr+1):
                            return y, x
        else:
            for y in rooks:
                for x in PieceMovement(y):
                    if isSafe(x, colour, opp) and x / 8 == kr + 1:
                        return y, x

    # King and Queen Checkmate
    elif len(queen) > 0:
        k = hasOpposition(kingpos, opp_pos)
        if k:
            start = queen[0]
            for y in k:
                for end in PieceMovement(start):
                    if end == y and isSafe(y, colour, opp):
                        return start, end
        elif opp_pos + 15 == kingpos or opp_pos + 17 == kingpos:
            for y in PieceMovement(queen[0]):
                if y == opp_pos + 8:
                    return queen[0], y
        elif opp_pos - 15 == kingpos or opp_pos - 17 == kingpos:
            for y in PieceMovement(queen[0]):
                if y == opp_pos - 8:
                    return queen[0], y
        elif opp_pos - 10 == kingpos or opp_pos + 6 == kingpos:
            for y in PieceMovement(queen[0]):
                if y == opp_pos - 1:
                    return queen[0], y
        elif opp_pos - 6 == kingpos or opp_pos + 10 == kingpos:
            for y in PieceMovement(queen[0]):
                if y == opp_pos + 1:
                    return queen[0], y
        else:
            v = getOpposition(kingpos, opp_pos)
            if v:
                return kingpos, v

    # King and Rook Checkmate
    elif len(rooks) == 1:
        k = hasOpposition(kingpos, opp_pos)
        kf = opp_pos % 8
        kr = opp_pos / 8
        if k:
            start = rooks[0]
            for y in k:
                for end in PieceMovement(start):
                    if end == y and isSafe(y, colour, opp):
                        return start, end
        elif rooks[0] / 8 != kr + 1 or not(isSafe(rooks[0], colour, opp)):
            start = rooks[0]
            for y in PieceMovement(start):
                if y/8 == kr+1 and isSafe(y, colour, opp):
                    if start / 8 == kr + 1:
                        if y / 8 == kr+1 and y%8 != kf+2 and y%8 != kf-2:
                            return start, y
                    else:
                        return start, y
        elif kingpos / 8 > kr + 2:
            for y in PieceMovement(kingpos):
                if y == kingpos - 8:
                    return kingpos, kingpos - 8
        for y in PieceMovement(kingpos):
            if y / 8 == kr + 2:
                if opp_pos + 15 == y or opp_pos + 17 == y or opp_pos + 16 == y:
                    return kingpos, y
        for y in PieceMovement(kingpos):
            if y / 8 == kr + 2:
                if opp_pos + 14 == y or opp_pos + 18 == y:
                    return kingpos, y
                    
    return FindBest(colour)
                

# Finds possible opening moves for black
def OpeningMoves(colour, movenum, randnum):
    #randnum = random.random()
    if movenum == 0 and colour == 'white':
        if randnum < 0.3:
            return 11, 27 #d4
        elif randnum < 0.6:
            return 12, 28 #e4
        elif randnum < 0.9:
            return 10, 26 #c4
        else:
            return 14, 22 #g3

    if movenum == 1 and colour == 'black':
        if boardlist[26] == 'whitepawn':
            if randnum < 0.75:
                return 50, 34 #c5
            else:
                return 52, 36 #e5
        elif boardlist[27] == 'whitepawn':
            if randnum < 0.25:
                return 62, 45 #Nf6
            else:
                return 51, 35 #d5
        elif boardlist[28] == 'whitepawn':
            if randnum < 0.5:
                return 50, 34
            else:
                return 52, 36

    elif movenum == 2 and colour == 'black':
        if boardlist[27] == 'whitepawn' and boardlist[26] == 'whitepawn':
            if boardlist[35] == 'blackpawn':
                if randnum < 0.5:
                    return 35, 26 #dxc4
                else:
                    return 52, 44 #e6
            elif boardlist[45] == 'blackknight':
                return 52, 44
        if boardlist[28] == 'whitepawn' and boardlist[21] == 'whiteknight':
            if boardlist[51] == 'blackpawn' and boardlist[34] == 'blackpawn':
                return 51, 43 #d6
            if boardlist[57] == 'blackknight' and boardlist[36] == 'blackpawn':
                return 57, 42 #Nc6

    elif movenum >= 3 and colour == 'black':
        if boardlist[27] == 'whiteknight' and boardlist[62] == 'blackknight':
            if boardlist[34] != 'blackpawn' and boardlist[36] != 'blackpawn':
                return 62, 45
        if boardlist[27] == 'whitepawn' and boardlist[26] == 'whitepawn':
            if boardlist[62] == 'blackknight':
                return 62, 45
    return FindBest(colour)
    

# Anything below this line is utter and complete nonsense
#----------------------------------------------------------------------


# Finds a pos (very slow)
def FindPos(folder):
    for y in folder:
        for start in y.piecelist:
            moveslist = PieceMovement(start)
            for end in moveslist:
                return start, end
            

# Returns a decent move for colour
def FindDecent(colour):
    if colour == 'white':
        k = whitepieces
        opp = 'black'
    elif colour == 'black':
        k = blackpieces
        opp = 'white'

    for x in range(len(k)):
        cur = EvaluatePosition(colour) - EvaluatePosition(opp)
        pos = Position()

        start, end = FindPos(k)
        pos.movestart, pos.moveend = start, end

        MovePiece(start, end)
        pos.evaluation = EvaluatePosition(colour) - EvaluatePosition(opp)

        jkk = isSafe(end, colour)
        UndoMove(end, start)

        if pos.evaluation > cur and jkk == True:               
            return pos.movestart, pos.moveend
    return pos.movestart, pos.moveend
            
