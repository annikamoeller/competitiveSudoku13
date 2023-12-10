from competitive_sudoku.sudoku import SudokuBoard
from team13_A2.utils import * 
import random 
from itertools import chain

def calculate_region_index(board: SudokuBoard, m, n):
    row_region_index = (m // board.m) * board.m
    column_region_index = (n // board.n) * board.n

    return row_region_index, column_region_index

def remove_unwanted_moves_list(board, moves, intersection, k, k_):
    moves_to_remove = []
    same_row = same_col = False
    value1 = list(intersection)[0]
    value2 = list(intersection)[1]
    if k[0] == k_[0]: same_row = True
    if k[1] == k_[1]: same_col = True 
    if same_row: index_to_check = 0
    if same_col: index_to_check = 1

    for move in moves: 
        if (move.i == k[0] and move.j == k[1]) or (move.i == k_[0] and move.j == k_[1]):
            if move.value != value1 and move.value != value2:
                moves_to_remove.append(move)
        else:
            if move.i == k[index_to_check]: # check row or column 
                if move.value == value1 or move.value == value2:
                    moves_to_remove.append(move)
            if calculate_region_index(board, move.i, move.j) == calculate_region_index(board, k[0], k[1]): # check block 
                if move.value == value1 or move.value == value2: 
                    moves_to_remove.append(move)
    return moves_to_remove

# def remove_unwanted_moves(board, moves_dict, intersection, k, k_):
#     moves_to_remove = []
#     same_row = same_col = False
#     value1 = intersection[0]
#     value2 = intersection[1]
#     if k[0] == k_[0]: same_row = True
#     if k[1] == k_[1]: same_col = True 
#     if same_row: index_to_check = 0
#     if same_col: index_to_check = 1

#     for key, values in moves_dict: 
#         if key == (k[0], k[1]) and key == (k_[0], k_[1]):  
#             for v in values: 
#                 if v!= value1 or v!=value2:
#                     moves_dict[key].remove(v)
#         else:
#             if key[index_to_check] == k[index_to_check]: # check row or column
#                 for v in values: 
#                     if v == value1 or v == value2:
#                         moves_dict[key].remove(v)
#             if calculate_region_index(board, key[0], key[1]) == calculate_region_index(board, k[0], k[1]): # check block 
#                 for v in values: 
#                     if v == value1 or v == value2:
#                         moves_dict[key].remove(v)
#     return moves_dict

def pair_appears_in_row_or_block(board, moves_dict, intersection, k, k_):
    same_row = same_col = False
    value1 = list(intersection)[0]
    value2 = list(intersection)[1]
    if k[0] == k_[0]: same_row = True
    if k[1] == k_[1]: same_col = True 
    if same_row: index_to_check = 0
    if same_col: index_to_check = 1

    for key, values, in moves_dict.items(): 
        if key != (k[0], k[1]) and key != (k_[0], k_[1]):  # exclude twin moves from being checked
            if key[index_to_check] == k[index_to_check]: 
                if value1 in values and value2 in values:
                    return True
            if calculate_region_index(board, key[0], key[1]) == calculate_region_index(board, k[0], k[1]): # check block 
                if value1 in values and value2 in values:
                    return True      
    return False
    
def hidden_twin_exclusion(board: SudokuBoard, moves: list):
    """
    Returns a filtered list of moves using the hidden twin exclusion.
    @param board: A sudoku board. It contains the current position of a game.
    @param moves: A list of moves to evaluate.
    """
    filtered_moves = []
    moves_to_remove = []
    taboo_move = None
    moves_dict = {}

    # Store the moves in a dictionary where the key is the position of the move
    # and the value is a list of possible values
    for m in moves:
        position = (m.i, m.j)
        if position in moves_dict:
            moves_dict[position].append(m.value)
        else:
            moves_dict[position] = [m.value]

    # Check if the potential twins are valid by comparing for each position the possible values
    for k, v in moves_dict.items():
        for k_, v_ in moves_dict.items():
            # Check if the two positions are not the same and that they are in the same region
            if (k != k_) and (calculate_region_index(board, k[0], k[1]) == calculate_region_index(board, k_[0], k_[1]) and (k[0] == k_[0] or k[1] == k_[1])):
                intersection = set(v) & set(v_)
                if len(intersection) == 2 and not pair_appears_in_row_or_block(board, moves_dict, intersection, k, k_):
                    moves_to_remove.append(remove_unwanted_moves_list(board, moves, intersection, k, k_))
    
    moves_to_remove = list(chain.from_iterable(moves_to_remove))
    if moves_to_remove:
        filtered_moves = [move for move in moves if move not in moves_to_remove]
        taboo_move = random.choice(moves_to_remove)
        return filtered_moves, taboo_move

    return moves, taboo_move

def remove_opponent_scoring_moves(board: SudokuBoard, moves: list):
    filtered_moves = []

    for move in moves:
        current_row, current_col, current_block = get_row_col_block_values(board, move)
        # Check if a move results in a full row/column/block and assign score accordingly
        if (len(current_row) == board.N-2 or len(current_col) == board.N-2 or len(current_block) == board.N-2): continue
        else: filtered_moves.append(move)

    return filtered_moves