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
        def minimax(game_state, depth, current_score, alpha, beta, isMaximizing=False):
            all_moves = get_legal_moves(game_state)
            twin_excluded_moves, taboo_move = hidden_twin_exclusion(game_state.board, all_moves) 
            filtered_moves = remove_opponent_scoring_moves(game_state.board, twin_excluded_moves)
            if should_play_taboo(game_state.board, filtered_moves):
                #print("should play taboo")
                if taboo_move:
                    print(taboo_move.i, taboo_move.j, taboo_move.value)
                    print("proposed taboo move") 
                    self.propose_move(taboo_move)
                    if isMaximizing:
                        return taboo_move, float('inf')
                    elif not isMaximizing:
                        return taboo_move, -float('inf')
            elif not filtered_moves:
                filtered_moves = twin_excluded_moves

            #print("TABOO MOVE ", taboo_move.i, taboo_move.j, taboo_move.value)
            random.shuffle(filtered_moves)
  
            if depth == 0 or not filtered_moves: return None, current_score
                        
            if isMaximizing:
                max_eval = -float('inf')
                for move in filtered_moves:
                    score = evaluate_move(game_state.board, move)
                    current_score += score
                    game_state.board.put(move.i, move.j, move.value)
                    eval = minimax(game_state, depth - 1, current_score, alpha, beta, False)[1]
                    current_score -= score
                    game_state.board.put(move.i, move.j, SudokuBoard.empty)
                    if float(eval) > max_eval:
                        max_eval = eval
                        best_move = move
                        print("best move ", best_move.i, best_move.j, best_move.value)
                    alpha = max(alpha, max_eval)
                    if beta <= alpha: break
                return best_move, max_eval

            else:
                min_eval = float('inf')
                for move in filtered_moves:
                    score = evaluate_move(game_state.board, move)
                    current_score -= score
                    game_state.board.put(move.i, move.j, move.value)
                    eval = minimax(game_state, depth - 1, current_score, alpha, beta, True)[1]
                    current_score += score
                    game_state.board.put(move.i, move.j, SudokuBoard.empty)
                    if float(eval) < min_eval:
                        min_eval = eval
                        best_move = move
                        print("best move ", best_move.i, best_move.j, best_move.value)
                    beta = min(beta, min_eval)
                    if beta <= alpha: break
                return best_move, min_eval
        
        current_player = game_state.current_player()

        if current_player == 1: isMaximizing=False
        elif current_player == 2: isMaximizing=True
        
        # Run MiniMax and propose best move
        all_legal_moves = get_legal_moves(game_state)
        #filtered_moves, taboo_move = hidden_twin_exclusion(game_state.board, all_legal_moves)
        #filtered_moves = remove_opponent_scoring_moves(game_state.board, filtered_moves)
        random_move = random.choice(all_legal_moves)
        print(random_move.i, random_move.j, random_move.value)
        self.propose_move(random_move)
    
        for depth in range(1,N*N):
            best_move, _ = minimax(game_state, depth, 0, float('-inf'), float('inf'), isMaximizing)
            self.propose_move(best_move)