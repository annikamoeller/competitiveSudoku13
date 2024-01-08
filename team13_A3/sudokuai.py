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
        
        # Load root node from saved if possible
        #root_node = self.load()
        
        # if root_node is None:
        #     print("initialized new node")
        #     root_node = MonteCarloTreeSearchNode(game_state, is_player_1)

        # if root_node.state.board.squares != game_state.board.squares:
        #     old_board_filled_squares = [x for x in root_node.state.board.squares if x != 0]
        #     new_board_filled_squares = [x for x in game_state.board.squares if x != 0]
        #     n_current = len(new_board_filled_squares)
        #     n_old = len(old_board_filled_squares)
        #     moves_placed = n_current - n_old
        #     previous_moves = game_state.moves[-moves_placed:]
        #     print("previous moves \n", previous_moves)

            # first_child = None
            # for child in root_node.children:
            #     if child.parent_action == previous_moves[0]:
            #         first_child = child
            #         print("first child found")
            #         break
            # if not first_child:
            #     new_state = simulate_move(game_state, previous_moves[0])
            #     first_child = MonteCarloTreeSearchNode(new_state, is_player_1)
            #     print("creating root node first child")
            # root_node = first_child
            # root_node.state.scores = game_state.scores
            # root_node.state.taboo_moves = game_state.taboo_moves
            # root_node.refresh_state(game_state)
            # print("first child root node \n", root_node.state)
            # self.save(root_node)

            # if moves_placed == 2:
            #     second_child = None
            #     for child in first_child.children: # loop through children of first move
            #         if child.parent_action == previous_moves[1]:
            #             second_child = child
            #             print("second child found")
            #             break
            #     if not second_child: # first move has not been expanded enough yet, check legal moves instead
            #         new_state = simulate_move(game_state, previous_moves[1])
            #         second_child = MonteCarloTreeSearchNode(new_state, is_player_1)
            #         print("create root node second child")
            #     root_node = second_child
            #     root_node.state.scores = game_state.scores
            #     root_node.state.taboo_moves = game_state.taboo_moves
            #     root_node.refresh_state(game_state)
            #     print("second child root node \n", root_node.state)
            #     self.save(root_node)

        #Determine whether we should play a taboo move
        if should_play_taboo(root_node.state):
            if root_node.taboo_move:
                self.propose_move(root_node.taboo_move)
                print("playing taboo move")
                self.save(root_node)
                return
        else:
            #Run monte carlo tree search
            while True:
                print("\n \nNEW ITERATION ")
                selected_node = root_node._tree_policy()
                selected_node.print_parent_actions()
                print("selected node ",selected_node.parent_action) #, "\n", selected_node.state)
                for _ in range(1):
                    completed_simulation, score = selected_node.simulate_random_playout()
                    if completed_simulation:
                        selected_node.backpropagate(score)
                        best_move = root_node.best_child().parent_action
                        print("proposing move ", best_move)
                        self.propose_move(best_move)
                        self.save(root_node)
                    else:
                        #selected_node.backpropagate(-0.01)
                        selected_node.increment_n_visits()
