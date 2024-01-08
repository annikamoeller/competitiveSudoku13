import random
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai
import copy
from team13_A3.heuristics import *

def get_legal_heuristic_moves(game_state):
    new_taboo_move = None
    all_legal_moves = get_legal_moves(game_state)
    moves_obvious_singles, taboo_move_obvious_singles = obvious_singles(game_state, all_legal_moves)
    moves_hidden_pairs, taboo_move_hidden_pairs = hidden_pairs(game_state, moves_obvious_singles) 

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
    return filtered_moves, new_taboo_move

def get_legal_moves(game_state):
    """ 
    Get all legal moves in a state.
    """
    all_moves = [Move(i, j, value) for i in range(game_state.board.N) for j in range(game_state.board.N)
                for value in range(1, game_state.board.N +1) if possible(game_state, i, j, value)]
    all_legal_moves = []
    for move in all_moves:
        current_row, current_col, current_block = get_row_col_block_values(game_state.board, move)
        if (move.value in set(current_row)) or (move.value in set(current_col)) or (move.value in set(current_block)): continue
        else: 
            all_legal_moves.append(move)

    return all_legal_moves

def possible(game_state, i, j, value):
    """ 
    Check if a move is possible.
    """
    return game_state.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j, value) in game_state.taboo_moves

def get_row_col_block_values(board, move):
    """
    Helper function to return all values in the 
    row, column, and block of the currently chosen move.
    """
    current_row = [board.get(move.i, j) for j in range(0, board.N) if board.get(move.i, j) != SudokuBoard.empty] 
    current_col = [board.get(i, move.j) for i in range(0, board.N) if board.get(i, move.j) != SudokuBoard.empty]
    block_i = move.i // board.m * board.m # row coordinate
    block_j = move.j // board.n * board.n # column coordinate
    current_block = [board.get(i,j) for i in range(block_i, block_i + board.m) \
                        for j in range(block_j, block_j + board.n) if board.get(i,j) != SudokuBoard.empty]
    return current_row, current_col, current_block

def simulate_move(game_state, move):    
    simulated_player = len(game_state.moves) %2 
    game_state_copy = copy.deepcopy(game_state)
    game_state_copy.board.put(move.i, move.j, move.value)
    game_state_copy.moves.append(move)
    score = evaluate_move(game_state_copy.board, move)
    if simulated_player == 0:
        game_state_copy.scores[0] += score
    else:
        game_state_copy.scores[1] += score
    return game_state_copy

def evaluate_move(board, move): 
    """
    Assign a score to a given move. 
    """
    N = board.N
    current_row, current_col, current_block = get_row_col_block_values(board, move)
    # Check if a move results in a full row/column/block and assign score accordingly
    solves_row = (len(current_row) == N)    
    solves_col = (len(current_col) == N)     
    solves_block = (len(current_block) == N) 
    truth_arr = [solves_row, solves_col, solves_block] 
    if sum(truth_arr) == 0: score = 0
    if sum(truth_arr) == 1: score = 1
    if sum(truth_arr) == 2: score = 3
    if sum(truth_arr) == 3: score = 7
    return score

def get_game_result(game_state, is_player_1, scale_by_score):
    scores = game_state.scores
    if is_player_1: 
        net_score = scores[0] - scores[1]
    else:
        net_score = scores[1] - scores[0]

    if net_score > 0:
        if scale_by_score:
            score = 1 + net_score*0.01
        else: score = 1
    elif net_score < 0:
        if scale_by_score:
            score = -1 - net_score*0.01
        else: score = -1
    else:
        score = 0
    return score

def is_game_over(game_state):
    n_full = 0
    board = game_state.board
    total_cells = board.N * board.N
    for i in range(board.N):
        for j in range(board.N):
            if board.get(i, j) is not SudokuBoard.empty:
                n_full += 1
    return n_full == total_cells

def should_play_taboo(game_state):
    if even_squares_empty(game_state.board) and board_half_filled(game_state.board):
        # We can't score, we are not playing from a position we want to be in, so use this
        #   chance to swap turns
        return True
    else:
        return False
    
def even_squares_empty(board):
    """
    Helper function that returns whether 
    there are an even number of squares empty. 
    """
    n_empties = 0
    for i in range(board.N):
        for j in range(board.N):
            if board.get(i, j) is SudokuBoard.empty:
                n_empties += 1  
    return n_empties % 2 == 0

def board_half_filled(board):
    """
    Helper function that returns 
    whether the board is half-filled.
    """
    n_full = 0
    total_cells = board.N * board.N
    for i in range(board.N):
        for j in range(board.N):
            if board.get(i, j) is not SudokuBoard.empty:
                n_full += 1
    return n_full/total_cells > 0.5
    

