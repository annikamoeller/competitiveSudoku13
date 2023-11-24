#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import time
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai


class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    
    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

        def evaluate_move():
            pass

        def get_legal_moves(game_state):
            def possible(i, j, value):
                return game_state.board.get(i, j) == SudokuBoard.empty \
                    and not TabooMove(i, j, value) in game_state.taboo_moves
            
            all_moves = [Move(i, j, value) for i in range(N) for j in range(N)
                        for value in range(1, N+1) if possible(i, j, value)]

            all_legal_moves = []
            
            for move in all_moves:
                legal = True

                # Check if value is repeated in column
                for column_row in range(N):
                    if game_state.board.get(column_row, move.j) == move.value:
                        legal = False
                        break

                    if game_state.board.get(move.i, column_row) == move.value:
                        legal = False
                        break

                if legal:
                    # Find the coordinates of the upper left corner of the block in which the current possible move is positioned
                    block_row_coordinate = move.i // game_state.board.m * game_state.board.m
                    block_column_coordinate = move.j // game_state.board.n * game_state.board.n
                    # Loop through rows and columns in block that contains current move
                    for row in range(block_row_coordinate, block_row_coordinate + game_state.board.m): # Loop from current coordinate to size of block in row direction (m)
                        for column in range(block_column_coordinate, block_column_coordinate + game_state.board.n): # Loop from current coordinate to size of block in column direction (n)
                            if game_state.board.get(row, column) == move.value:
                                legal = False
                                break
                else:
                    continue

                # If all checks are passed add the move to the list of legal moves
                if legal:
                    all_legal_moves.append(move)
                else:
                    continue

            return all_legal_moves

        def minimax(game_state, depth ,isMaximizing=False):
            cloned_game_state = game_state
            moves = get_legal_moves(cloned_game_state)

            if depth == 0 or moves == []:
                return  evaluate_move(game_state)
            
            if isMaximizing:
                max_eval = float('-inf')
                eval = minimax(cloned_game_state, depth - 1, False)
                max_eval = max(max_eval, eval)


            else:
                min_eval = float('inf')
                eval = minimax(cloned_game_state, depth - 1, True)
                min_eval = min(min_eval, eval)  
        

        
        move = minimax(game_state, depth=3, isMaximizing=True)

        
        move = random.choice(all_legal_moves)
        self.propose_move(move)
        while True:
            time.sleep(0.2)
            self.propose_move(random.choice(all_legal_moves))

