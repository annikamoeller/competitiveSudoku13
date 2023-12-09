#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from team13_A1.hidden_twin_exclusion import hidden_twin_exclusion 

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N
        board = game_state.board
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
        def evaluate_move(board, move): 
            current_row, current_col, current_block = get_row_col_block_values(board, move)

            # Check if a move results in a full row/column/block and assign score accordingly
            solves_row = (len(current_row) == N-1)    
            solves_col = (len(current_col) == N-1)     
            solves_block = (len(current_block) == N-1) 
            truth_arr = [solves_row, solves_col, solves_block] 
            if sum(truth_arr) == 0: score = 0
            if sum(truth_arr) == 1: score = 1
            if sum(truth_arr) == 2: score = 3
            if sum(truth_arr) == 3: score = 7
            return score

        # MiniMax algorithm with pruning
        def minimax(board, depth, current_score, alpha, beta, isMaximizing=False):
            all_moves = get_legal_moves(board)
            filtered_moves, _ = hidden_twin_exclusion(board, all_legal_moves)       
            if depth == 0 or not all_moves: return None, current_score
                        
            if isMaximizing:
                max_eval = -float('inf')
                for move in filtered_moves:
                    score = evaluate_move(board, move)
                    current_score += score
                    board.put(move.i, move.j, move.value)
                    eval = minimax(board, depth - 1, current_score, alpha, beta, False)[1]
                    current_score -= score
                    board.put(move.i, move.j, SudokuBoard.empty)
                    if float(eval) > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, max_eval)
                    if beta <= alpha: break
                return best_move, max_eval

            else:
                min_eval = float('inf')
                for move in filtered_moves:
                    score = evaluate_move(board, move)
                    current_score -= score
                    board.put(move.i, move.j, move.value)
                    eval = minimax(board, depth - 1, current_score, alpha, beta, True)[1]
                    current_score += score
                    board.put(move.i, move.j, SudokuBoard.empty)
                    if float(eval) < min_eval:
                        min_eval = eval
                        best_move = move
                    beta = min(beta, min_eval)
                    if beta <= alpha: break
                return best_move, min_eval
        
        current_player = game_state.current_player()

        if current_player == 1: isMaximizing=False
        elif current_player == 2: isMaximizing=True
        
        # Run MiniMax and propose best move
        all_legal_moves = get_legal_moves(board)
        filtered_moves, _ = hidden_twin_exclusion(board, all_legal_moves)
        self.propose_move(random.choice(filtered_moves))

        for depth in range(1,N*N):
            best_move, _ = minimax(board, depth, 0, float('-inf'), float('inf'), isMaximizing)
            self.propose_move(best_move)