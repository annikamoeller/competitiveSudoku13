import numpy as np
from team13_A3.utils import *
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import random 
import copy 

class MonteCarloTreeSearchNode():
    def __init__(self, state: GameState, parent=None, parent_action=None):
        self.state = state
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self._results = []
        for _ in range(3):
            self._results.append(0)
        self.untried_actions = get_legal_moves(self.state)
        self.uct = float('inf')
        return
    
    # def untried_actions(self):
    #     self.untried_actions = get_legal_moves(self.state)
    #     return self.untried_actions
    
    def q(self):
        wins = self._results[1]
        losses = self._results[2]
        return wins - losses
    
    def n(self):
        return self._number_of_visits
    
    def calculate_uct(self, c_param=0.1):
        if self.n() == 0:
            uct = float('inf')
        else:
            average_leaf_score = self.q() / self.n()
            frequent_visit_penalty = c_param \
                                        * np.sqrt(np.log(self.parent.n()) / self.n())

            uct = average_leaf_score + frequent_visit_penalty
        return uct
    
    def is_terminal_node(self):
        "terminal node found'"
        return is_game_over(self.state)
    
    def rollout(self):
        print("rollout")
        current_rollout_state = copy.deepcopy(self.state)
        while True:
            game_over = is_game_over(current_rollout_state)
            if game_over:
                print("successful sim, winner is ", get_game_winner(current_rollout_state))
                return True, get_game_winner(current_rollout_state)
            possible_moves = get_legal_moves(current_rollout_state)
            if not possible_moves and not game_over:
                print("unsuccessful sim")
                return False, 0
            move = random.choice(possible_moves)
            current_rollout_state = simulate_move(current_rollout_state, move)
            #print("current rollout state \n", current_rollout_state)

    def backpropagate(self, result):
        print("backpropagating")
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0
    
    def expand(self):
        print("Expand")
        action = self.untried_actions.pop()
        #print("untried actions: ", len(self.untried_actions))
        next_state = simulate_move(self.state, action)
        child_node = MonteCarloTreeSearchNode(
            next_state, parent=self, parent_action=action)
        child_node._number_of_visits += 1

        self.children.append(child_node)
        return child_node 
    
    def best_child(self, c_param=0.1):
        print("calculating best child")
        child_uct_list = [child.calculate_uct(c_param) for child in self.children]
        child_action_list = [(child.parent_action.i, child.parent_action.j, child.parent_action.value) for child in self.children]
        print(child_action_list)
        print(child_uct_list)
        return self.children[np.argmax(child_uct_list)]
    
    def _tree_policy(self):
        current_node = self
        use_new_node = False
        terminal_node = False
        print("untried actions ", len(current_node.untried_actions))  

        if current_node.is_terminal_node():
            terminal_node = True
            return current_node, use_new_node, terminal_node
        
        if not current_node.is_fully_expanded():
            return current_node.expand(), use_new_node, terminal_node
        
        current_node = current_node.best_child()
        use_new_node = True
        print("node fully expanded, best child is ", current_node.parent_action)

        return current_node, use_new_node, terminal_node