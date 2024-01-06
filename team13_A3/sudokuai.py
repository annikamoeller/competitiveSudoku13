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
        self.first_move = True
        self.bob = "yo mama"

    def compute_best_move(self, game_state: GameState) -> None:
        # Propose a random move at the start
        print(self.first_move)
        all_legal_moves = get_legal_moves(game_state)
        random_move = random.choice(all_legal_moves)
        self.propose_move(random_move)

        # Determine if we are player 1
        if len(game_state.moves)%2 == 0:
            is_player_1 = True
        else: is_player_1 = False

        # Load root node from saved if possible
        if self.first_move:
            print("initialized new node")
            root_node = MonteCarloTreeSearchNode(game_state, is_player_1)
            self.first_move = False
            self.bob = "jabra elite"
        else:
            print("loaded node")
            root_node = self.load()
            print(type(root_node))

        # Determine whether we should play a taboo move
        if should_play_taboo(root_node.state, root_node.untried_actions):
            if root_node.taboo_move:
                self.propose_move(root_node.taboo_move)
                print("playing taboo move")
                return
        else:
            # Run monte carlo tree search
            while True:
                print("\n \nNEW ITERATION ")
                selected_node = root_node._tree_policy()
                if selected_node.parent:
                    if selected_node.parent.parent_action:
                        previous_action = selected_node.parent.parent_action
                        #print("previous action ", previous_action.i, previous_action.j, previous_action.value)
                print("selected node ",selected_node.parent_action, "\n", selected_node.state)
                for _ in range(1):
                    completed_simulation, score = selected_node.rollout()
                    if completed_simulation:
                        selected_node.backpropagate(score)
                        best_move = root_node.best_child().parent_action
                        print("proposing move ", best_move)
                        self.propose_move(best_move)
                    else:
                        #selected_node.backpropagate(-0.1)
                        selected_node.increment_n_visits()
                self.save(root_node)
                print("saved node")