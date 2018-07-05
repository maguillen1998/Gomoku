from tkinter import *
import numpy as np
import math
from random import randint

# import Eval_Func as AI
import GomokuAiClasses as BM

###	Gomoku utilizing Monte Carlo Tree Search (MCTS) + Alpha Beta Pruning
### 盤面サイズ 19 * 19
ROWS = 19
COLS = 19

# EMPTY = 0 ### 盤面にある石 なし
# BLACK = 1 ### 盤面にある石 黒
# WHITE = 2 ### 盤面にある石 白

###　石を置ける場所
ALL_POS_COUNT = 361


# ### 盤面の白石の数
# w_num_board = 0
# ### 盤面の黒石の数
# b_num_board = 0

# ### 現在どちらのターンなのかを格納する配列
# which_turn = BLACK

# ###########################################################


class Gomoku():
    def __init__(self, root):

        self.root = root
        self.root.title("Gomoku game")

        ### 現在のプレーヤー
        ### 1 : black's turn
        ### 2 : white's turn
        self.turn = 0

        # self.depth = 2

        self.frame = Frame(self.root, width=900, heigh=800)
        self.frame.pack()

        self.create_menu()

        self.white_turn = 0

        ### 1 = black win  2 = white win
        self.result = 0

        ##########
        self.board = BM.Board()
        self.board.printBoard()

    ##########

    ### メニュー Menu
    def create_menu(self):
        self.menubar = Menu(self.root)
        self.subMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='New Game', menu=self.subMenu)
        self.subMenu.add_command(label="Play First", command=lambda: self.initBoard('player', 'computer'))
        self.subMenu.add_command(label="Play Second", command=lambda: self.initBoard('computer', 'player'))
        self.subMenu.add_separator()
        self.subMenu.add_command(label="Exit", command=self.root.quit)

        ### メニューの表示
        self.root.config(menu=self.menubar)

    ### 盤面初期化 initializing the game board
    def initBoard(self, player_one, player_two):
        self.setPlayer(player_one, player_two)

        self.canvas = Canvas(self.frame, width=800, height=800, bg="bisque", highlightthickness=0)
        self.canvas.pack()

        self.init_board_points()
        self.init_board_canvas()

        if self.player_one == "player":
            self.canvas.bind("<Button-1>", self.gameLoop)

        elif self.player_one == "computer":
            self.gameLoop2()

    ### プレイヤーの設定: {player|computer : BLACK|WHITE}
    def setPlayer(self, p1, p2):
        self.player_one = p1
        self.player_two = p2

    def init_board_points(self):

        ### Create 2D lists where [][] = 0 (empty), 1(Black), 2(white)
        self.board_points = [[0 for i in range(ROWS)] for j in range(COLS)]

    ### Other module get initialized
    # self.ef = AI.Evaluation(self.board_points)

    def init_board_canvas(self):
        ### Vertical line
        for i in range(ROWS):
            start_pixel_x = (i + 1) * 40
            start_pixel_y = (0 + 1) * 40
            end_pixel_x = (i + 1) * 40
            end_pixel_y = (18 + 1) * 40
            self.canvas.create_line(start_pixel_x, start_pixel_y, end_pixel_x, end_pixel_y)

        ### Horizontal line
        for j in range(COLS):
            start_pixel_x = (0 + 1) * 40
            start_pixel_y = (j + 1) * 40
            end_pixel_x = (18 + 1) * 40
            end_pixel_y = (j + 1) * 40
            self.canvas.create_line(start_pixel_x, start_pixel_y, end_pixel_x, end_pixel_y)

        ### Dots to place intersections
        for i in range(ROWS):
            for j in range(COLS):
                start_pixel_x = (i + 1) * 40 - 2
                start_pixel_y = (j + 1) * 40 - 2
                end_pixel_x = (i + 1) * 40 + 2
                end_pixel_y = (j + 1) * 40 + 2
                self.canvas.create_oval(start_pixel_x, start_pixel_y, end_pixel_x, end_pixel_y)

    ### Draw a stone on a given intersection
    ### Specify the color of the stone depending on the turn.
    ### 碁石を置くだけ
    def draw_stone(self, row, col):
        start_pixel_x = (row + 1) * 40 - 15
        start_pixel_y = (col + 1) * 40 - 15
        end_pixel_x = (row + 1) * 40 + 15
        end_pixel_y = (col + 1) * 40 + 15

        if self.turn == 1:  ### 黒石
            self.canvas.create_oval(start_pixel_x, start_pixel_y, end_pixel_x, end_pixel_y, fill='black')

        elif self.turn == 2:  ### 白石
            self.canvas.create_oval(start_pixel_x, start_pixel_y, end_pixel_x, end_pixel_y, fill='white')

    ######################################################
    def check_row(self, x, y):  # 右の確認
        if self.board_points[x][y] == 1 and self.board_points[x + 1][y] == 1 and self.board_points[x + 2][y] == 1 and \
                self.board_points[x + 3][y] == 1 and self.board_points[x + 4][y] == 1:
            return 1

        elif self.board_points[x][y] == 2 and self.board_points[x + 1][y] == 2 and self.board_points[x + 2][y] == 2 and \
                self.board_points[x + 3][y] == 2 and self.board_points[x + 4][y] == 2:
            return 2

        else:
            return 0

    def check_col(self, x, y):
        if self.board_points[x][y] == 1 and self.board_points[x][y + 1] == 1 and self.board_points[x][y + 2] == 1 and \
                self.board_points[x][y + 3] == 1 and self.board_points[x][y + 4] == 1:
            return 1

        elif self.board_points[x][y] == 2 and self.board_points[x][y + 1] == 2 and self.board_points[x][y + 2] == 2 and \
                self.board_points[x][y + 3] == 2 and self.board_points[x][y + 4] == 2:
            return 2

        else:
            return 0

    def check_up(self, x, y):
        if self.board_points[x][y] == 1 and self.board_points[x + 1][y + 1] == 1 and self.board_points[x + 2][
            y + 2] == 1 and self.board_points[x + 3][y + 3] == 1 and self.board_points[x + 4][y + 4] == 1:
            return 1

        elif self.board_points[x][y] == 2 and self.board_points[x + 1][y + 1] == 2 and self.board_points[x + 2][
            y + 2] == 2 and self.board_points[x + 3][y + 3] == 2 and self.board_points[x + 4][y + 4] == 2:
            return 2

        else:
            return 0

    def check_down(self, x, y):
        if self.board_points[x][y] == 1 and self.board_points[x + 1][y - 1] == 1 and self.board_points[x + 2][
            y - 2] == 1 and self.board_points[x + 3][y - 3] == 1 and self.board_points[x + 4][y - 4] == 1:
            return 1

        elif self.board_points[x][y] == 2 and self.board_points[x + 1][y - 1] == 2 and self.board_points[x + 2][
            y - 2] == 2 and self.board_points[x + 3][y - 3] == 2 and self.board_points[x + 4][y - 4] == 2:
            return 2

        else:
            return 0

    ######################################################

    ### 四方向（縦、横、斜め上下）の確認
    def check_result(self):
        result = 0
        for i in range(ROWS - 4):
            for j in range(COLS):
                # if no stone is on the position, don't need to consider this position
                if self.board_points[i][j] == 0:
                    continue

                result = self.check_row(i, j)
                if result != 0:
                    return result

        for i in range(ROWS):
            for j in range(COLS - 4):
                if self.board_points[i][j] == 0:
                    continue

                result = self.check_col(i, j)
                if result != 0:
                    return result

        for i in range(ROWS - 4):
            for j in range(COLS - 4):
                if self.board_points[i][j] == 0:
                    continue

                result = self.check_up(i, j)
                if result != 0:
                    return result

        for i in range(ROWS - 4):
            for j in range(4, COLS):
                if self.board_points[i][j] == 0:
                    continue

                result = self.check_down(i, j)
                if result != 0:
                    return result

        return result

    ### 引き分けか確認
    def check_tie(self):
        ### 0 means empty
        ### Returns True if there is 0
        return any(0 in x for x in self.board_points)

    ### Player1 = self, Player2 = computer
    def gameLoop(self, event):
        ### プレーヤーのどちらかが勝つまで

        self.turn = 1

        ### Place stone #############################
        for i in range(ROWS):
            for j in range(COLS):
                pixel_x = (i + 1) * 40
                pixel_y = (j + 1) * 40
                square_distance = math.pow((event.x - pixel_x), 2) + math.pow((event.y - pixel_y), 2)
                square_distance = math.sqrt(square_distance)

                if (square_distance < 20) and (self.board_points[i][j] == 0):
                    self.draw_stone(i, j)
                    # self.player_pos.append((i,j))
                    # unbind to ensure the user cannot click anywhere until the program
                    # has placed a white stone already
                    self.canvas.unbind("<Button-1>")
                    # Place a black stone after determining the position
                    self.board_points[i][j] = 1
                    # print(i,j)

                    self.board.placeEnemy(i, j)
                    self.board.printBoard()
                    break

            else:
                continue
            break

        ### Every time after one move, check the board
        self.result = self.check_result()

        ### Black wins
        if self.result == 1:
            self.canvas.create_text(400, 20, font=("Purisa", 25), text="Black Wins")
            self.canvas.unbind('<Button-1>')
            return 0

        ### Check if the game is tie
        elif self.check_tie() == False:
            self.canvas.create_text(400, 20, font=("Purisa", 25), text="GAME TIE")
            self.canvas.unbind('<Button-1>')
            return 0

        ### AI's Turn ###############################
        self.turn = 2
        ### For the AI's first turn, it must place stone in the middle 3 * 3 range
        if self.white_turn == 0:
            self.firstmove()
            self.white_turn = 1


        else:
            row, col = self.board.bestMove()
            self.board_points[row][col] = 2
            self.draw_stone(row, col)
            self.board.placeSelf(row, col)
        ##########################################
        self.board.printBoard()

        ### Every time after one move, check the board
        self.result = self.check_result()

        ### White wins
        if self.result == 2:
            self.canvas.create_text(400, 20, font=("Purisa", 25), text="White Wins")
            self.canvas.unbind('<Button-1>')
            return 0

        elif self.check_tie() == False:
            self.canvas.create_text(400, 20, font=("Purisa", 25), text="GAME TIE")
            self.canvas.unbind('<Button-1>')
            return 0

        ### bind after the program makes its move so that the user can continue to play
        self.canvas.bind("<Button-1>", self.gameLoop)

    ### For the first turn of AI, it should put somewhere in middle
    def firstmove(self):
        while True:
            middleRow = randint(8, 11)
            middleCol = randint(8, 11)
            if self.board_points[middleRow][middleCol] == 0:
                self.draw_stone(middleRow, middleCol)
                # self.AI_pos.append((middleRow,middleCol))
                self.board.placeSelf(middleRow, middleCol)
                self.board_points[middleRow][middleCol] = 2
                return

            ### FIX ME

    ### Player1 = Computer, Player2 = self
    def gameLoop2(self, *args):
        while True:
            ### AI first
            self.turn = 2

            if self.white_turn == 0:
                self.firstmove()
                self.white_turn = 1
            else:
                pass
            #### AI's turn
            ##########################

            ### Every time after one move, check the board
            self.result = self.check_result()

            ### Black wins
            if self.result == 2:
                self.canvas.create_text(400, 20, font=("Purisa", 25), text="Black Wins")
                self.canvas.unbind('<Button-1>')
                return 0

            ### Check if the game is tie
            elif self.check_tie() == False:
                self.canvas.create_text(400, 20, font=("Purisa", 25), text="GAME TIE")
                self.canvas.unbind('<Button-1>')
                return 0

            self.canvas.bind("<Button-1>", self.gameLoop2)

            self.turn = 1

            ### Place stone #############################
            for i in range(ROWS):
                for j in range(COLS):
                    pixel_x = (i + 1) * 40
                    pixel_y = (j + 1) * 40
                    square_distance = math.pow((event.x - pixel_x), 2) + math.pow((event.y - pixel_y), 2)
                    square_distance = math.sqrt(square_distance)

                    if (square_distance < 20) and (self.board_points[i][j] == 0):
                        self.draw_stone(i, j)
                        # unbind to ensure the user cannot click anywhere until the program
                        # has placed a white stone already
                        self.canvas.unbind("<Button-1>")
                        # Place a black stone after determining the position
                        self.board_points[i][j] = 1
                        # print(i,j)
                        break

                else:
                    continue
                break


if __name__ == "__main__":
    game = Tk()
    gomoku = Gomoku(game)
    game.mainloop()

# function alphaBeta(node, alpha, beta, maximisingPlayer) {
#     var bestValue;
#     if (node.children.length === 0) {
#         bestValue = node.data;
#     }
#     else if (maximisingPlayer) {
#         bestValue = alpha;

#         // Recurse for all children of node.
#         for (var i=0, c=node.children.length; i<c; i++) {
#             var childValue = alphaBeta(node.children[i], bestValue, beta, false);
#             bestValue = Math.max(bestValue, childValue);
#             if (beta <= bestValue) {
#                 break;
#             }
#         }
#     }
#     else {
#         bestValue = beta;

#         // Recurse for all children of node.
#         for (var i=0, c=node.children.length; i<c; i++) {
#             var childValue = alphaBeta(node.children[i], alpha, bestValue, true);
#             bestValue = Math.min(bestValue, childValue);
#             if (bestValue <= alpha) {
#                 break;
#             }
#         }
#     }
#     return bestValue;
# }


# function minimax(position, depth, alpha, beta, maximizingPlayer)
#     if depth == 0 or game over in position
#         return static evaluation of position

#     if maximizingPlayer
#         maxEval = -infinity
#         for each child of position
#             eval = minimax(child, depth - 1, alpha, beta false)
#             maxEval = max(maxEval, eval)
#             alpha = max(alpha, eval)
#             if beta <= alpha
#                 break
#         return maxEval

#     else
#         minEval = +infinity
#         for each child of position
#             eval = minimax(child, depth - 1, alpha, beta true)
#             minEval = min(minEval, eval)
#             beta = min(beta, eval)
#             if beta <= alpha
#                 break
#         return minEval


# // initial call
# minimax(currentPosition, 3, -∞, +∞, true)