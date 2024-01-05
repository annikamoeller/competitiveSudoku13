import numpy as np
from team13_A3.utils import *
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import random 
import copy 

class MonteCarloTreeSearchNode():
    def __init__(self, state: GameState, is_player_1, parent=None, parent_action=None):
        self.state = state
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self._results = []
        for _ in range(3):
            self._results.append(0)
        self.n_legal_moves = len(get_legal_moves(self.state))
        self.untried_actions = get_legal_moves(self.state)
        self.uct = float('inf')
        self.is_player_1 = is_player_1
        return
    
    def q(self):
        if self.is_player_1:
            wins = self._results[1]
            losses = self._results[2]
        else: 
            wins = self._results[2]
            losses = self._results[1]
        return wins - losses
    
    def n(self):
        return self._number_of_visits
    
    def is_terminal_node(self):
        return is_game_over(self.state) or self.n_legal_moves == 0
    
    def rollout(self):
        print("rollout")
        print("n times visited ", self.n())
        current_rollout_state = copy.deepcopy(self.state)
        while True:
            game_over = is_game_over(current_rollout_state)
            if game_over:
                print("successful sim, winner is ", get_game_winner(current_rollout_state))
                print("scores ", current_rollout_state.scores)
                return True, get_game_winner(current_rollout_state)
            possible_moves = get_legal_moves(current_rollout_state)
            if not possible_moves and not game_over:
                print("unsuccessful sim")
                return False, 0
            move = random.choice(possible_moves)
            current_rollout_state = simulate_move(current_rollout_state, move)
            #print("current rollout state \n", current_rollout_state)

    def backpropagate(self, result):
        #print("backpropagating")
        self.increment_n_visits()
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0
    
    def increment_n_visits(self):
        self._number_of_visits += 1

    def expand(self):
        print("Expand")
        print("untried actions: ", len(self.untried_actions))
        random.shuffle(self.untried_actions)
        action = self.untried_actions.pop()
        next_state = simulate_move(self.state, action)
        child_node = MonteCarloTreeSearchNode(
            next_state, self.is_player_1, parent=self, parent_action=action)

        self.children.append(child_node)
        return child_node
    
    def calculate_uct(self, c_param):
        if self.n() == 0:
            uct = float('inf')
        else:
            average_leaf_score = self.q() / self.n()
            frequent_visit_penalty = c_param \
                                        * np.sqrt(np.log(self.parent.n()) / self.n())

            uct = average_leaf_score + frequent_visit_penalty
        return uct
    
    def highest_uct_child(self):
        #print("calculating highest uct child")
        print("children ", len(self.children))
        child_uct_list = [child.calculate_uct(c_param=100) for child in self.children]
        child_uct_action_list = [([child.parent_action.i, child.parent_action.j, child.parent_action.value], child.calculate_uct(c_param=0.1)) for child in self.children]
        child_uct_list = np.array(child_uct_list)
        print(child_uct_action_list)
        return self.children[np.random.choice(np.flatnonzero(child_uct_list == child_uct_list.max()))]

        #return self.children[np.argmax(child_uct_list)]
    
    def best_child(self):
        child_visit_list = [([child.parent_action.i, child.parent_action.j, child.parent_action.value], child.n()) for child in self.children]
        print(child_visit_list)
        return self.children[np.argmax(child.n() for child in self.children)]
    
    def _tree_policy(self):
        layers_down = 0
        current_node = self
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                #print(len(current_node.untried_actions), " unvisited children")
                return current_node.expand()
            else:
                layers_down +=1 
                #print("is game over ", is_game_over(current_node.state))
                current_node = current_node.highest_uct_child()
                print(layers_down, " layers down")
        #print(len(current_node.untried_actions), " unvisited children")
        return current_node