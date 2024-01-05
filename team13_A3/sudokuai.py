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
        if len(game_state.moves)%2 == 0:
            is_player_1 = True
        else: is_player_1 = False
        # Propose a random move at the start
        all_legal_moves = get_legal_moves(game_state)
        random_move = random.choice(all_legal_moves)
        self.propose_move(random_move)
        root_node = MonteCarloTreeSearchNode(game_state, is_player_1)
        
        while True:
            print("\n \nNEW ITERATION ")
            selected_node = root_node._tree_policy()
            if selected_node.parent.parent_action:
                previous_action = selected_node.parent.parent_action
                print("previous action ", previous_action.i, previous_action.j, previous_action.value)
            print("selected node ",selected_node.parent_action, "\n", selected_node.state)
            completed_simulation, winner = selected_node.rollout()
            if completed_simulation:
                selected_node.backpropagate(winner)
                best_move = root_node.best_child().parent_action
                print("proposing move ", best_move)
                self.propose_move(best_move)
            else:
                selected_node.increment_n_visits()