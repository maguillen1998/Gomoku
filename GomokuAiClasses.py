import random


class FirstLevelNode:
    def __init__(self,data=1, row=0, column=0):
        self.connections = []
        self.AIData = data
        self.enemyData = 1
        self.row = row
        self.column = column

class SecondLevelNode:
    def __init__(self, connections):
        self.connections = connections
        for firstLevelNode in self.connections:
            firstLevelNode.connections.append(self)

    # def __generateFromCoords(self, winningSet):
    #     for coordinate in winningSet:
    #             self.connections.append(#board[row][column].node)
    def getAIScore(self):
        output = 1
        numInARow = []
        numInARowCount = 0
        for firstLevelNode in self.connections:
            if firstLevelNode.AIData == 1.2:
                numInARowCount += 1
            numInARow.append(firstLevelNode)
            output *= firstLevelNode.AIData

        if numInARowCount == 3 and numInARow[0].AIData == 1 and numInARow[4].AIData == 1:
            return 5000
        # elif numInARowCount == 3:
        #     return numInARowCount * output
        if numInARowCount == 4:
            return 100000
        # if numInARow == 0:
        #     return output
        return output * numInARowCount

    def getEnemyScore(self):
        output = 1
        numInARow = []
        numInARowCount = 0
        for firstLevelNode in self.connections:
            if firstLevelNode.enemyData == 1.2:
                numInARowCount += 1
            numInARow.append(firstLevelNode)
            output *= firstLevelNode.enemyData


        if numInARowCount == 3 and numInARow[0].enemyData == 1 and numInARow[4].enemyData == 1:
            return 8000
        # elif numInARowCount == 3:
        #     return numInARowCount * output
        if numInARowCount == 4:
            return 10000
        # if numInARow == 0:
        #     return output
        return output * numInARowCount

class ThirdLevelNode:
    def __init__(self, connections):
        self.connections = connections
    def getAIScore(self):
        output = 0
        for secondLevelNode in self.connections:
            output += secondLevelNode.getAIScore()
        return output
    def getEnemyScore(self):
        output = 0
        for secondLevelNode in self.connections:
            output += secondLevelNode.getEnemyScore()
        return output
    def connect(self, secondLevelNode):
        self.connections.append(secondLevelNode)


class Space:
    def updateScore(self):
        self.AIscore = self.network.getAIScore()
        self.enemyScore = self.network.getEnemyScore()
        self.totalScore = self.AIscore + self.enemyScore
    def __init__(self, condition = 'e', row=0, column=0):
        self.row = row
        self.column = column
        self.condition = condition
        self.network = ThirdLevelNode([])
        self.node = FirstLevelNode(row = row, column = column)
        self.AIscore = 0
        self.enemyScore = 0
        self.totalScore = 0

class Board:
    def __calculateWinningSetList(self):
        b = []
        ### Horizontal
        for r in range(19):
            for c in range(15):
                b.append([(r, c), (r, c + 1), (r, c + 2), (r, c + 3), (r, c + 4)])

        ### Vertical
        for r in range(15):
            for c in range(19):
                b.append([(r, c), (r + 1, c), (r + 2, c), (r + 3, c), (r + 4, c)])

        ### Up
        for r in range(15):
            for c in range(15):
                b.append([(r, c), (r + 1, c + 1), (r + 2, c + 2), (r + 3, c + 3), (r + 4, c + 4)])

        ### Down
        for r in range(15):
            for c in range(4, 19):
                b.append([(r, c), (r + 1, c - 1), (r + 2, c - 2), (r + 3, c - 3), (r + 4, c - 4)])

        return b

    def generateNetworks(self):
        secondLevelNodesList = []
        for winningSet in self.winningSetList:
            referenceToFirstLevelNodesList = []
            # convert coords to list of firstLevelNodes
            for coordinate in winningSet:
                referenceToFirstLevelNodesList.append(self.matrix[coordinate[0]][coordinate[1]].node)
            secondLevelNodesList.append(SecondLevelNode(connections=referenceToFirstLevelNodesList))
        list = []
        #problem area. all top level connected to all second level
        for row in self.matrix:
            for space in row:
                for secondLevelNode in secondLevelNodesList:
                    if secondLevelNode.connections.__contains__(space.node):
                        space.network.connect(secondLevelNode)
        # for secondLevelNode in secondLevelNodesList:
        #     for firstLevelNode in secondLevelNode.connections:
        #         self.matrix[firstLevelNode.row][firstLevelNode.column].network.connect(secondLevelNode)
        #         list.append(secondLevelNode)
            # take each coordinate in a winning set and add the node containing that
            # index to the network of the space at that index
        self.updateAllScores()

    def __init__(self):
        #e=empty, b=black, w=white
        #set 19x19 matrix with all spaces empty
        self.height = 19
        self.width = 19
        self.matrix = [[Space(condition = 'e', row=i,column=j) for i in range(self.height)]for j in range(self.width)]

        ### Contains all the possible winning combinations
        self.winningSetList = self.__calculateWinningSetList()
        self.generateNetworks()

    def printBoard(self):
        print()
        for row in self.matrix:
            for space in row:
                score = space.totalScore
                if score < 10:
                    print(score, end='  ')
                else:
                    print(score, end=' ')
            print()
        print()

        print()
        for row in self.matrix:
            for space in row:
                print(space.condition, end= ' ')
            print()
        print()

    def betterPlaceEnemy(self, row, column):
        self.matrix[row][column].condition = 'b'
        self.matrix[row][column].node.setData(0)


    def placeEnemy(self,row,column):
        space = self.matrix[row][column]
        space.condition = 'b'
        space.node.AIData = 0
        space.node.enemyData = 1.2

        self.updateAllScores()

    def placeSelf(self,row,column):
        space = self.matrix[row][column]
        space.condition = 'w'
        space.node.AIData = 1.2
        space.node.enemyData = 0
        self.updateAllScores()
    def updateAllScores(self):
        for row in self.matrix:
            for space in row:
                space.updateScore()
    def bestMove(self):
        #trying to use already used spaces as bestMove
        #self.updateAllScores()
       # maxConditionList = []
        max = Space(row = -1, column= -1)
        for row in self.matrix:
            for space in row:
                if space.AIscore > max.AIscore and space.condition == 'e':
                    max = space
        maxList = []
        maxList.append(max)
        for row in self.matrix:
            for space in row:
                if space.AIscore == max.AIscore and space.condition == 'e':
                    maxList.append(space)
        max = maxList[random.randint(0,maxList.__len__()-1)]
        #workaround
        return max.column, max.row

    def newBestMove(self):
        # trying to use already used spaces as bestMove
        # self.updateAllScores()
        # maxConditionList = []
        max = Space(row=-1, column=-1)
        for row in self.matrix:
            for space in row:
                if space.totalScore > max.totalScore and space.condition == 'e':
                    max = space
        maxList = []
        maxList.append(max)
        for row in self.matrix:
            for space in row:
                if space.totalScore == max.totalScore and space.condition == 'e':
                    maxList.append(space)
        max = maxList[random.randint(0, maxList.__len__() - 1)]
        # workaround
        return max.column, max.row

    def boardInfo(self):
        black = []
        white = []
        empty = []
        for row in self.matrix:
            for space in row:
                if space.condition == 'b':
                    black.append(space)
                elif space.condition == 'w':
                    white.append(space)
                elif space.condition == 'e':
                    empty.append(space)
        info = [black, white, empty]
        return info
gameBoard = Board()
gameBoard.printBoard()
whiteMoveList = []
for i in range(5):
    row, col = gameBoard.bestMove()
    whiteMoveList.append([row, col])
    gameBoard.placeSelf(row, col)
   # gameBoard.placeEnemy(i,i)

    gameBoard.printBoard()
print(whiteMoveList)
print ('black:', gameBoard.boardInfo()[0].__len__(), "white:" ,gameBoard.boardInfo()[1].__len__(), "empty:",gameBoard.boardInfo()[2].__len__())

'''so we still need to: 
add in opponent score calculation, 
fix play second, 
fix turn passing after a click even if no piece is placed, account for open n vs closed n,
figurw out defense plays using playerScore vs AI score'''

'''change each member from self.score to self.aiScore and self.opponetScore representing the scores for each accordingly.'''
