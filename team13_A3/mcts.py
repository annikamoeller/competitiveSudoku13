import numpy as np
from team13_A3.utils import *
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import random 
import copy 

class MonteCarloTreeSearchNode():
    def __init__(self, state: GameState, is_player_1, parent=None, parent_action=None):
        """ 
        Initialize Monte Carlo tree search node.
        """
        self.state = state
        self.is_player_1 = is_player_1
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self.q_score = 0
        self._number_of_visits = 0
        self.uct = float('inf')
        self.legal_moves, self.taboo_move = get_heuristic_moves(self.state)
        self.n_legal_moves = len(self.legal_moves)
        self.untried_actions = self.legal_moves
        return
    
    def select_node(self):
        """
        Perform selection step of MCTS algorithm.
        """
        current_node = self
        
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.highest_uct_child(c_param=2)
        return current_node

    def expand(self):
        """
        Perform expansion step of MCTS algorithm.
        """
        random.shuffle(self.untried_actions)
        action = self.untried_actions.pop()
        next_state = simulate_move(self.state, action)
        child_node = MonteCarloTreeSearchNode(
            next_state, self.is_player_1, parent=self, parent_action=action)
        self.children.append(child_node)
        return child_node
    
    def simulate_random_playout(self):
        """
        Perform simulation step of MCTS algorithm.
        """
        current_rollout_state = copy.deepcopy(self.state)
        while True:
            game_over = is_game_over(current_rollout_state)
            if game_over:
                return True, get_game_result(current_rollout_state, self.is_player_1, scale_by_score=False)
            possible_moves, _ = get_heuristic_moves(current_rollout_state)
            if not possible_moves and not game_over:
                return False, 0
            move = random.choice(possible_moves)
            current_rollout_state = simulate_move(current_rollout_state, move)

    def backpropagate(self, result):
        """
        Perform backpropagation step of MCTS algorithm.
        """
        self.increment_n_visits()
        self.q_score += result
        if self.parent:
            self.parent.backpropagate(result)

    def highest_uct_child(self, c_param):
        """
        Find child node with the highest UCT score. 
        """
        child_uct_list = np.array([child.calculate_uct(c_param) for child in self.children])
        return self.children[random.choice(np.where(child_uct_list == child_uct_list.max())[0])]

    def calculate_uct(self, c_param):
        """
        Calculate UCT score based on q, n, and N. 
        """
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

    def robust_child(self):
        """
        Find most robust child (highest n value). 
        """
        child_n_list = np.array([child.n() for child in self.children])
        return self.children[random.choice(np.where(child_n_list == child_n_list.max())[0])].parent_action
      
    def q(self):
        return self.q_score
    
    def n(self):
        return self._number_of_visits
    
    def is_terminal_node(self):
        """
        Return whether a node is terminal (either full board
        or unfinished with no legal moves possible).  
        """
        return is_game_over(self.state) or self.n_legal_moves == 0

    def is_fully_expanded(self):
        """ 
        Check whether all legal actions have been tried.
        """
        return len(self.untried_actions) == 0
    
    def increment_n_visits(self):
        self._number_of_visits += 1
 

    

    


