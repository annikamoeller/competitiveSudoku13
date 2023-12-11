#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from team13_A2.heuristics import *
from team13_A2.utils import * 

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()

    def compute_best_move(self, game_state: GameState) -> None:
        N = game_state.board.N

        def minimax(game_state, depth, iter_depth, current_score, alpha, beta, isMaximizing=False):
            """
            Minimax algorithm with alpha-beta pruning, obvious single heuristic, and hidden pairs heuristic.
            """
            new_taboo_move = None
            all_legal_moves = get_legal_moves(game_state)
            moves_obvious_singles, taboo_move_obvious_singles = obvious_singles(game_state.board, all_legal_moves)
            moves_hidden_pairs, taboo_move_hidden_pairs = hidden_pairs(game_state.board, moves_obvious_singles) 

            if not moves_hidden_pairs:
                if not moves_obvious_singles: 
                    filtered_moves = all_legal_moves  # No moves found from obvious singles or hidden pairs.
                else: 
                    filtered_moves = moves_obvious_singles  # Moves found from obvious singles but not hidden pairs.
            else: 
                filtered_moves = moves_hidden_pairs  # Moves found from hidden pairs.
            
            if taboo_move_obvious_singles is not None:  
                new_taboo_move = taboo_move_obvious_singles
            elif taboo_move_hidden_pairs is not None:
                new_taboo_move = taboo_move_hidden_pairs

            random.shuffle(filtered_moves) 

            if depth == 0 or not filtered_moves: 
                return None, current_score
                        
            if isMaximizing:
                max_eval = -float('inf')
                for move in filtered_moves:
                    score = evaluate_move(game_state.board, move)
                    current_score += score
                    game_state.board.put(move.i, move.j, move.value)
                    eval = minimax(game_state, depth - 1, iter_depth, current_score, alpha, beta, isMaximizing=False)[1]
                    current_score -= score
                    game_state.board.put(move.i, move.j, SudokuBoard.empty)
                    if float(eval) > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, max_eval)
                    if beta <= alpha: break
                return best_move, max_eval, new_taboo_move

            else:
                min_eval = float('inf')
                for move in filtered_moves:
                    score = evaluate_move(game_state.board, move)
                    current_score -= score
                    game_state.board.put(move.i, move.j, move.value)
                    eval = minimax(game_state, depth - 1, iter_depth, current_score, alpha, beta, isMaximizing=True)[1]
                    current_score += score
                    game_state.board.put(move.i, move.j, SudokuBoard.empty)
                    if float(eval) < min_eval:
                        min_eval = eval
                        best_move = move
                    beta = min(beta, min_eval)
                    if beta <= alpha: break
                return best_move, min_eval, new_taboo_move
        
        # Propose a random move at the start
        all_legal_moves = get_legal_moves(game_state)
        random_move = random.choice(all_legal_moves)
        self.propose_move(random_move)
    
        for depth in range(1,N*N):
            print(depth)
            iter_depth = depth
            best_move, eval, taboo_move = minimax(game_state, depth, iter_depth, 0, float('-inf'), float('inf'), isMaximizing = True)
            print("eval ", eval)
            even = even_squares_empty(game_state.board)
            if (eval < 0 or even) and board_half_filled(game_state.board):
                if taboo_move:
                        self.propose_move(taboo_move)
                        print("proposed taboo move")
            else:
                self.propose_move(best_move)