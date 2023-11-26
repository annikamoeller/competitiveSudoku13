#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        game_board = game_state.board
        N = game_board.N

        # Check if a move is possible
        def possible(board, i, j, value):
            return board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j, value) in game_state.taboo_moves
        
        # Get all legal moves in a state
        def get_legal_moves(board):
            all_moves = [Move(i, j, value) for i in range(N) for j in range(N)
                        for value in range(1, N+1) if possible(board, i, j, value)]

            all_legal_moves = []
            for move in all_moves:
                current_row, current_col, current_block = get_row_col_block_values(board, move)
                if (move.value in set(current_row)) or (move.value in set(current_col)) or (move.value in set(current_block)): continue
                else: all_legal_moves.append(move)

            return all_legal_moves

        # Helper function to return all values in the row, column, and block of the currently chosen move
        def get_row_col_block_values(board, move):
            current_row = [board.get(move.i, j) for j in range(0, N) if board.get(move.i, j) != SudokuBoard.empty] 
            current_col = [board.get(i, move.j) for i in range(0, N) if board.get(i, move.j) != SudokuBoard.empty]
            block_i = move.i // board.m * board.m # row coordinate
            block_j = move.j // board.n * board.n # column coordinate
            current_block = [board.get(i,j) for i in range(block_i, block_i + board.m) \
                             for j in range(block_j, block_j + board.n) if board.get(i,j) != SudokuBoard.empty]
            return current_row, current_col, current_block

        # Assign a score to a move
        def evaluate_move(board, move, isMaximizing):
            board.put(move.i, move.j, move.value) # make move 
            current_row, current_col, current_block = get_row_col_block_values(board, move)

            # Check if a move results in a full row/column/block and assign score accordingly
            solves_row = (len(current_row) == N)    
            solves_col = (len(current_col) == N)     
            solves_block = (len(current_block) == N) 
            truth_arr = [solves_row, solves_col, solves_block] 
            if sum(truth_arr) == 0: score = 0
            if sum(truth_arr) == 1: score = 1
            if sum(truth_arr) == 2: score = 3
            if sum(truth_arr) == 3: score = 7

            # Penalize a move that will allow the following player to complete a row/column/block
            penultimate_move = ((len(current_row)+2 == N) or (len(current_col)+2 == N) or (len(current_block)+2 == N))
            if penultimate_move: score = -2

            # Negate score for minimizing player
            if isMaximizing: return score
            else: return score * -1 

                    
        # MiniMax algorithm with pruning
        def minimax(board, depth, alpha, beta, isMaximizing=False):
            all_moves = get_legal_moves(board)

            if depth == 0 or not all_moves: return 0
                        
            if isMaximizing:
                max_eval = -float('inf')
                for move in all_moves:
                    score = evaluate_move(board, move, True)
                    eval = score + minimax(board, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    board.put(move.i, move.j, 0)
                    if beta <= alpha: break
                return max_eval

            else:
                min_eval = float('inf')
                for move in all_moves:
                    score = evaluate_move(board, move, False)
                    eval = score + minimax(board, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    board.put(move.i, move.j, 0)
                    if beta <= alpha: break
                return min_eval
        
        # Run MiniMax and propose best move
        all_legal_moves = get_legal_moves(game_board)
        for depth in range(1,N*N):
            max_eval = alpha = beta = -float('inf')
            self.propose_move(random.choice(all_legal_moves))
            for move in all_legal_moves:
                score = evaluate_move(game_board, move, True)
                eval = score + minimax(game_board, depth, alpha, beta, isMaximizing=False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                    self.propose_move(best_move)
                game_board.put(move.i, move.j, 0)