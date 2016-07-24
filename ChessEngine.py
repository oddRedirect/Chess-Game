import sys
import PieceMovement as pm
from PieceMovement import PieceMovement, isSafe

# Global Constants:
Pval = 1
Nval = 3
Bval = 3.2
Rval = 5
Qval = 9
Kval = 100

# Assign a value to each piece
for y in pm.allpieces:
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

# Rename Piece objects from PieceMovement.py
wk, wq, wb, wn, wr, wp = pm.wk, pm.wq, pm.wb, pm.wn, pm.wr, pm.wp
bk, bq, bb, bn, br, bp = pm.bk, pm.bq, pm.bb, pm.bn, pm.br, pm.bp

boardlist = pm.boardlist


# Gives a numerical value for how good colour's position is
def EvaluatePosition(colour):
    evalu = 0

    if colour == 'white':
        kingSqr = bk.piecelist[0]
        opp = 'black'
    else:
        kingSqr = wk.piecelist[0]
        opp = 'white'

    for y in pm.whitepieces:
        evalu += y.value * len(y.piecelist)
    for y in pm.blackpieces:
        evalu -= y.value * len(y.piecelist)

    for y in wp.piecelist:
        # Add incentives for centred pawns
        if y == 27 or y == 28:
            evalu += 0.4
        # Add incentives for making use of outposts for knights
        if y > 24 and y < 48:
            f = y % 8
            if boardlist[y+9] == id(wn) or boardlist[y+7] == id(wn):
                if f > 0 and f < 7:
                    evalu += 0.35
        # Passed pawns are GREAT
        #TODO: improve alorithm for determining value of passed pawns
        if y > 32 and pm.pieceatsqr(y+8) == 0:
            if y <= 54 and boardlist[y+9] != id(bp) and boardlist[y+7] != id(bp):
                evalu += y/8 - 3
        # Doubled pawns are BAD
        if y < 56 and boardlist[y + 8] == id(wp):
            evalu -= 0.5
        # Don't let pawns drop off like flies
        if not(isSafe(y, 'white')) and isSafe(y, 'black'):
            evalu -= 0.4

    for y in bp.piecelist:
        if y == 35 or y == 36:
            evalu -= 0.4
        if y > 24 and y < 48:
            f = y % 8
            if boardlist[y-9] == id(bn) or boardlist[y-7] == id(bn):
                if f > 0 and f < 7:
                    evalu -= 0.35
        if y < 31 and pm.pieceatsqr(y-8) == 0:
            if y >= 9 and boardlist[y-9] != id(wp) and boardlist[y-7] != id(wp):
                evalu -= 4 - y/8
        if y < 56 and boardlist[y + 8] == id(bp):
            evalu += 0.5
        if not(isSafe(y, 'black')) and isSafe(y, 'white'):
            evalu += 0.4

    for y in wn.piecelist:
        # Add incentives for development / attacking w knights
        if y == 18 or y == 21:
            evalu += 0.3
        # Don't hang your knights
        if not(isSafe(y, 'white')):
            evalu -= 1.2

    for y in bn.piecelist:
        if y == 42 or y == 45:
            evalu -= 0.3
        if not(isSafe(y, 'black')):
            evalu += 1.2

    for y in wb.piecelist:
        # Fianchetto
        if y == 9 or y == 14:
            evalu += 0.35
        # Don't hang your bishops
        if not(isSafe(y, 'white')):
            evalu -= 1.3

    for y in bb.piecelist:
        if y == 49 or y == 54:
            evalu += 0.35
        if not(isSafe(y, 'black')):
            evalu += 1.3

    for y in wr.piecelist:
        f = y % 8
        # Centralize rooks
        if f == 3 or f == 4:
            evalu += 0.25
        # Rooks behind passed pawns or on open files
        for x in [f+8, f+16, f+24, f+32, f+40, f+48, f+56]:
            if boardlist[x] == id(wp):
                evalu -= 0.5
                break
        r = y/8
        # Rook on seventh rank is good
        if r == 7:
            evalu += 0.35
        # Make sure you don't make a ROOKie mistake
        if not(isSafe(y, 'white')):
            evalu -= 2.1

    for y in br.piecelist:
        f = y % 8
        if f == 3 or f == 4:
            evalu -= 0.25
        for x in [f+8, f+16, f+24, f+32, f+40, f+48, f+56]:
            if boardlist[x] == id(wp):
                evalu += 0.5
                break
        r = y/8
        # Rook on second rank is good
        if r == 7:
            evalu -= 0.35
        if not(isSafe(y, 'black')):
            evalu += 2.1

    # Add incentives for castling
    hs = wk.piecelist[0]
    ls = bk.piecelist[0]
    if hs == 2 or hs == 6:
        evalu += 0.7
    if ls == 57 or ls == 62:
        evalu -= 0.7

    # Make sure bae is safe
    if colour == 'white':
        for y in wq.piecelist:
            if not(isSafe(y, 'white')):
               evalu -= 4.2
    elif colour == 'black':
        for y in bq.piecelist:
            if not(isSafe(y, 'black')):
                evalu += 4.2

    # Try to corner the king
    kingpos = kingSqr
    kingCanMove = False
    rekt = False
    if not isSafe(kingpos, opp):
        rekt = True
        if colour == 'white':
            evalu += 0.5
        else:
            evalu -= 0.5
    for y in pm.kingMovement(kingpos):
        if isSafe(y, opp):
            kingCanMove = True
    if not(kingCanMove) and rekt:
        if pm.isMated(opp) == 'CHECKMATE':
            return Kval

    if colour == 'black':
        evalu *= -1
        
    return evalu


class Position:
    evaluation = 0
    movestart = 0
    moveend = 0
    

# Returns the "best" move for colour
def FindBest(colour, plies):
    if colour == 'white':
        pieces = pm.whitepieces
        opp = 'black'
    elif colour == 'black':
        pieces = pm.blackpieces
        opp = 'white'

    topMoves = range(5)
    for i in range(5):
        a = topMoves[i] = Position()
        a.evaluation = -1000

    bestsofar, nextbest = Position(), Position()
    bestsofar.evaluation, nextbest.evaluation = -1000, -1000

    for p in pieces:
        for start in p.piecelist:
            moveslist = PieceMovement(start)
            for end in moveslist:
                cur = Position()
                cur.movestart = start
                cur.moveend = end
                i = pm.pieceatsqr(end)
                j = pm.pieceatsqr(start)

                pm.MovePiece(start, end)
                if not(i) and not(isSafe(end, colour)) and isSafe(end, opp):
                        # Don't hang pieces unless you need to
                        cur.evaluation -= j.value
                cur.evaluation += EvaluatePosition(colour)
                pm.UndoMove()

                # No kamikaze allowed
                if i and i.value < j.value:
                    if not(isSafe(end, colour)):
                        # Unless absolutely necessary
                        cur.evaluation -= j.value

                if cur.evaluation >= bestsofar.evaluation:
                    x = len(topMoves)-1
                    for i in range(x):
                        topMoves[i] = topMoves[i+1]
                    topMoves[x] = bestsofar = cur

    if plies > 1:
        plies -= 1
        for pos in topMoves:
            if pos.movestart != pos.moveend:
                pm.MovePiece(pos.movestart, pos.moveend)
                oppTop = FindBest(opp, plies)
                oppeval = oppTop.evaluation
                pos.evaluation = oppeval*(-1)
                print oppTop.movestart, "->", oppTop.moveend
                pm.UndoMove()

    for pos in topMoves:
        print pos.evaluation
        if pos.evaluation > bestsofar.evaluation:
            bestsofar = pos
    return bestsofar
            


# returns the file or rank that colour can use to attack the enemy king
def hasOpposition(kingpos, opp_pos):
    a, b = kingpos, opp_pos
    #TODO: check opposition for corners (if b in corners...)
    corners = [0, 7, 56, 63]
    if a/8 == b/8 and abs(a-b) == 2:
        return (b%8, "file") 
    elif a%8 == b%8 and abs(a-b) == 16:
        return ((b/8) * 8, "rank")
    return False, ""

# Opposes the enemy king (returns the square to move the king to)
def getOpposition(kingpos, opp_pos):
    b = opp_pos
    kingMoves = PieceMovement(kingpos)
    for y in kingMoves:
        if abs(y-b) == 16 or (y/8 == b/8 and abs(y-b) == 2):
            return y
    for y in kingMoves:
        if abs(y-b) == 32 or (y/8 == b/8 and abs(y-b) == 4):
            return y
    for y in kingMoves:
        if abs(y-b) == 48 or (y/8 == b/8 and abs(y-b) == 6):
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
        kingpos, opp_pos = wk.piecelist[0], bk.piecelist[0]
        rooks = wr.piecelist + wq.piecelist
        queen = wq.piecelist
    elif colour == 'black':
        kingpos, opp_pos = bk.piecelist[0], wk.piecelist[0]
        rooks = br.piecelist + bq.piecelist
        queen = bq.piecelist
    
    # 2 Rook Checkmate
    if len(rooks) >= 2:
        kf = opp_pos % 8
        kr = opp_pos / 8
        for y in rooks:
            for x in PieceMovement(y):
                if not(isSafe(y, colour)) and isSafe(x, colour):
                    if y / 8 == kr + 1:
                        if x / 8 != kr+1 or x%8 == kf+2 or x%8 == kf-2:
                            continue
                    return y, x
        if rooks[0] / 8 == kr + 1 or rooks[1] / 8 == kr + 1:
            for y in rooks:
                for x in PieceMovement(y):
                    if isSafe(x, colour) and x / 8 == kr:
                        if y / 8 != kr + 1 or (rooks[0]/8 == kr+1 and rooks[1]/8 == kr+1):
                            return y, x
        else:
            for y in rooks:
                for x in PieceMovement(y):
                    if isSafe(x, colour) and x / 8 == kr + 1:
                        return y, x

    # King and Queen Checkmate
    elif len(queen) > 0:
        start = queen[0]
        k, opr = hasOpposition(kingpos, opp_pos)
        if k:
            for end in PieceMovement(start):
                if opr == "file" and end%8 == k and isSafe(y, colour):
                    return start, end
                elif opr == "rank" and end/8 == k and isSafe(y, colour):
                    return start , end
        elif opp_pos + 15 == kingpos or opp_pos + 17 == kingpos:
            for y in PieceMovement(start):
                if y == opp_pos + 8:
                    return start, y
        elif opp_pos - 15 == kingpos or opp_pos - 17 == kingpos:
            for y in PieceMovement(start):
                if y == opp_pos - 8:
                    return start, y
        elif opp_pos - 10 == kingpos or opp_pos + 6 == kingpos:
            for y in PieceMovement(start):
                if y == opp_pos - 1:
                    return start, y
        elif opp_pos - 6 == kingpos or opp_pos + 10 == kingpos:
            for y in PieceMovement(start):
                if y == opp_pos + 1:
                    return start, y
        else:
            v = getOpposition(kingpos, opp_pos)
            if v:
                return kingpos, v

    # King and Rook Checkmate
    elif len(rooks) == 1:
        k, opr = hasOpposition(kingpos, opp_pos)
        kf = opp_pos % 8
        kr = opp_pos / 8
        if k:
            start = rooks[0]
            for end in PieceMovement(start):
                if opr == "file" and end%8 == k and isSafe(y, colour):
                    return start, end
                elif opr == "rank" and end/8 == k and isSafe(y, colour):
                    return start , end
        elif rooks[0] / 8 != kr + 1 or not(isSafe(rooks[0], colour)):
            start = rooks[0]
            for y in PieceMovement(start):
                if y/8 == kr+1 and isSafe(y, colour):
                    if start / 8 == kr + 1:
                        if y / 8 != kr+1 or y%8 == kf+2 or y%8 == kf-2:
                            continue
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
                    
    default = FindBest(colour, 2)
    return default.movestart, default.moveend
                

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
        if boardlist[26] == id(wp):
            if randnum < 0.75:
                return 50, 34 #c5
            else:
                return 52, 36 #e5
        elif boardlist[27] == id(wp):
            if randnum < 0.25:
                return 62, 45 #Nf6
            else:
                return 51, 35 #d5
        elif boardlist[28] == id(wp):
            if randnum < 0.5:
                return 50, 34
            else:
                return 52, 36

    elif movenum == 2 and colour == 'black':
        if boardlist[27] == id(wp) and boardlist[26] == id(wp):
            if boardlist[35] == id(bp):
                if randnum < 0.5:
                    return 35, 26 #dxc4
                else:
                    return 52, 44 #e6
            elif boardlist[45] == id(bk):
                return 52, 44
        if boardlist[28] == id(wp) and boardlist[21] == id(wn):
            if boardlist[51] == id(bp) and boardlist[34] == id(bp):
                return 51, 43 #d6
            if boardlist[57] == id(bn) and boardlist[36] == id(bp):
                return 57, 42 #Nc6

    elif movenum >= 3 and colour == 'black':
        if boardlist[27] == id(wn) and boardlist[62] == id(bn):
            if boardlist[34] != id(bp) and boardlist[36] != id(bp):
                return 62, 45
        if boardlist[27] == id(wp) and boardlist[26] == id(wp):
            if boardlist[62] == id(bn):
                return 62, 45
    default = FindBest(colour, 2)
    return default.movestart, default.moveend
    
