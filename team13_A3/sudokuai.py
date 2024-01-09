#  (C) Copyright Wieger Wesselink 2021. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
from team13_A2.heuristics import *
from team13_A2.utils import * 
from team13_A3.mcts import *

class SudokuAI(competitive_sudoku.sudokuai.SudokuAI):
    """
    Sudoku AI that computes a move for a given sudoku configuration.
    """

    def __init__(self):
        super().__init__()
        
    def compute_best_move(self, game_state: GameState) -> None:

        # Propose a random move at the start
        all_legal_moves = get_legal_moves(game_state) 
        random_move = random.choice(all_legal_moves)
        self.propose_move(random_move) 

        # Determine if we are player 1
        is_player_1 = len(game_state.moves)%2 == 0  
        root_node = MonteCarloTreeSearchNode(game_state, is_player_1)

        # Determine whether we should play a taboo move
        if should_play_taboo(root_node.state): 
            if root_node.taboo_move:
                self.propose_move(root_node.taboo_move)
                return
        else:
            # Run Monte Carlo tree search
            while True: 
                selected_node = root_node.select_node()
                completed_simulation, score = selected_node.simulate_random_playout()
                if completed_simulation:
                    selected_node.backpropagate(score)
                    best_move = root_node.robust_child()
                    self.propose_move(best_move)
                else:
                    selected_node.increment_n_visits()
