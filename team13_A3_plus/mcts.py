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
        self.legal_moves, self.taboo_move = get_legal_heuristic_moves(self.state)
        self.q_score = 0
        self.n_legal_moves = len(self.legal_moves)
        self.untried_actions = self.legal_moves
        self.uct = float('inf')
        self.is_player_1 = is_player_1
        return
    
    def refresh_state(self, new_game_state):
        #self.state.scores = new_game_state.scores
        #self.state.taboo_moves = new_game_state.taboo_moves
        self.legal_moves, self.taboo_move = get_legal_heuristic_moves(self.state)
        self.n_legal_moves = len(self.legal_moves)

    def q(self):
        return self.q_score
    
    def n(self):
        return self._number_of_visits
    
    def is_terminal_node(self):
        return is_game_over(self.state) or self.n_legal_moves == 0
    
    def simulate_random_playout(self):
        print("rollout")
        print("n times visited ", self.n())
        current_rollout_state = copy.deepcopy(self.state)
        while True:
            game_over = is_game_over(current_rollout_state)
            if game_over:
                #print("successful sim, net score is ", get_game_result(current_rollout_state, self.is_player_1, scale_by_score=False))
                return True, get_game_result(current_rollout_state, self.is_player_1, scale_by_score=True)
            possible_moves, _ = get_legal_heuristic_moves(current_rollout_state)
            if not possible_moves and not game_over:
                print("unsuccessful sim")
                return False, 0
            move = random.choice(possible_moves)
            current_rollout_state = simulate_move(current_rollout_state, move)

    def backpropagate(self, result):
        print("backpropagating")
        self.increment_n_visits()
        self.q_score += result
        print("q-score ", self.q_score)
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
            if self.parent.n() == 0:
                uct = float('inf')
            else:
                average_leaf_score = self.q() / self.n()
                frequent_visit_penalty = c_param * np.sqrt(np.log(self.parent.n()) / self.n())
                uct = average_leaf_score + frequent_visit_penalty
        return uct
    
    def highest_uct_child(self, c_param):
        child_uct_list = np.array([child.calculate_uct(c_param) for child in self.children])
        return self.children[random.choice(np.where(child_uct_list == child_uct_list.max())[0])]
    
    def best_child(self):
        child_n_div_q = np.array([child.n()/child.q() if child.q() != 0 else 0 for child in self.children])
        child_n_list = np.array([child.n() for child in self.children])
        return self.children[random.choice(np.where(child_n_div_q == child_n_div_q.max())[0])]
    
    def print_uct_and_action_vals(self, c_param):
        child_uct_action_list = [([child.parent_action.i, child.parent_action.j, child.parent_action.value], child.calculate_uct(c_param), child.n()) for child in self.children]
        print(child_uct_action_list)

    def _tree_policy(self):
        layers_down = 0
        current_node = self
        
        self.print_uct_and_action_vals(2)
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                print(len(current_node.untried_actions), " unvisited children")
                return current_node.expand()
            else:
                layers_down +=1 
                current_node = current_node.highest_uct_child(c_param=2)
                print(layers_down, " layers down")
        print(len(current_node.untried_actions), " unvisited children")
        return current_node
    
    def print_parent_actions(self):
        copy_node = self
        while copy_node.parent:
            previous_action = copy_node.parent_action
            print("previous action ", previous_action.i, previous_action.j, previous_action.value)
            copy_node = copy_node.parent
