#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from team13_A2.hidden_twin_exclusion import *
from team13_A2.utils import * 

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

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
        def minimax(game_state, depth, iter_depth, current_score, alpha, beta, first_run, isMaximizing=False):
            all_moves = get_legal_moves(game_state)
            obvious_singles_excluded, single_taboo_move = obvious_singles(game_state.board, all_moves)
            filtered_moves, twin_taboo_move = hidden_twin_exclusion(game_state.board, obvious_singles_excluded) 
            taboo_move = None
            #filtered_moves = remove_opponent_scoring_moves(game_state.board, twin_excluded_moves)

            if single_taboo_move is not None:
                taboo_move = single_taboo_move
            elif twin_taboo_move is not None:
                taboo_move = twin_taboo_move
            
            elif not filtered_moves:
                filtered_moves = all_moves

            random.shuffle(filtered_moves)
  
            if depth == 0 or not all_moves: return None, current_score
                        
            if isMaximizing:
                max_eval = -float('inf')
                for move in filtered_moves:
                    score = evaluate_move(game_state.board, move)
                    current_score += score
                    game_state.board.put(move.i, move.j, move.value)
                    eval = minimax(game_state, depth - 1, iter_depth, current_score, alpha, beta, first_run = False, isMaximizing=False)[1]
                    current_score -= score
                    game_state.board.put(move.i, move.j, SudokuBoard.empty)
                    if float(eval) > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, max_eval)
                    if beta <= alpha: break
                return best_move, max_eval, taboo_move

            else:
                min_eval = float('inf')
                for move in filtered_moves:
                    score = evaluate_move(game_state.board, move)
                    current_score -= score
                    game_state.board.put(move.i, move.j, move.value)
                    eval = minimax(game_state, depth - 1, iter_depth, current_score, alpha, beta, first_run = False, isMaximizing=True)[1]
                    current_score += score
                    game_state.board.put(move.i, move.j, SudokuBoard.empty)
                    if float(eval) < min_eval:
                        min_eval = eval
                        best_move = move
                    beta = min(beta, min_eval)
                    if beta <= alpha: break
                return best_move, min_eval, taboo_move
        
        # Run MiniMax and propose best move
        all_legal_moves = get_legal_moves(game_state)
        random_move = random.choice(all_legal_moves)
        self.propose_move(random_move)
    
        for depth in range(1,N*N):
            print(depth)
            iter_depth = depth
            best_move, eval, taboo_move = minimax(game_state, depth, iter_depth, 0, float('-inf'), float('inf'), first_run = True, isMaximizing = True)
            print("eval ", eval)
            even = even_squares_left(game_state.board)
            if (eval < 0 or even) and board_half_filled(game_state.board):
                if taboo_move:
                        self.propose_move(taboo_move)
                        print("proposed taboo move")
            else:
                self.propose_move(best_move)