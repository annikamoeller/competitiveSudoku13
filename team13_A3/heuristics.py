from competitive_sudoku.sudoku import SudokuBoard
from itertools import chain

def hidden_pairs(game_state, moves: list):
    """
    Returns a filtered list of moves using the hidden twin exclusion.
    """
    board = game_state.board
    filtered_moves = []
    taboo_moves = []
    store_taboo_move = None
    moves_dict = {}

    # Store the moves in a dictionary where the key is the position of the move
    # and the value is a list of possible values
    for m in moves:
        position = (m.i, m.j)
        if position in moves_dict:
            moves_dict[position].append(m.value)
        else:
            moves_dict[position] = [m.value]

    for k, v in moves_dict.items():
        for k_, v_ in moves_dict.items():
            if (k != k_) and (calculate_region_index(board, k[0], k[1]) == calculate_region_index(board, k_[0], k_[1]) and (k[0] == k_[0] or k[1] == k_[1])):
                intersection = set(v) & set(v_)
                if len(intersection) == 2 and not pair_appears_in_row_or_block(board, moves_dict, intersection, k, k_):
                    taboo_moves.append(calculate_taboo_moves(board, moves, intersection, k, k_))
    
    taboo_moves = list(chain.from_iterable(taboo_moves))
    if taboo_moves:
        filtered_moves = [move for move in moves if move not in taboo_moves]
        for move in taboo_moves:
            if move not in game_state.taboo_moves: 
                store_taboo_move = move
                break
        return filtered_moves, store_taboo_move

    return moves, store_taboo_move

def calculate_taboo_moves(board, moves, intersection, k, k_):
    """ 
    Helper function for hidden pairs that calculates 
    the taboo moves on a board given two hidden pairs.
    """
    taboo_moves = []
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
                taboo_moves.append(move)
        else:
            if move.i == k[index_to_check]: # check row or column 
                if move.value == value1 or move.value == value2:
                    taboo_moves.append(move)
            if calculate_region_index(board, move.i, move.j) == calculate_region_index(board, k[0], k[1]): # check block 
                if move.value == value1 or move.value == value2: 
                    taboo_moves.append(move)
    return taboo_moves

def pair_appears_in_row_or_block(board, moves_dict, intersection, k, k_):
    """ 
    Helper function for hidden pairs heuristic that checks whether 
    a hidden pair appears in a row/block or column/block.
    """
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
    

def obvious_singles(game_state, moves):
    """ 
    Obvious singles heuristic that identifies moves as taboo when a square 
    in the same row, block, or column has only one possible value. 
    """
    board = game_state.board
    taboo_moves = []
    store_taboo_move = None
    moves_dict = {}

    for m in moves:
        position = (m.i, m.j)
        if position in moves_dict:
            moves_dict[position].append(m.value)
        else:
            moves_dict[position] = [m.value]

    for k, v in moves_dict.items():
        if len(v) == 1:
            for move in moves: 
                if move.i == k[0] or move.j == k[1] or \
                calculate_region_index(board, k[0], k[1]) == calculate_region_index(board, move.i, move.j):
                    if (move.i != k[0] or move.j != k[1]) and move.value == v[0]:
                        taboo_moves.append(move)
    if taboo_moves:
        filtered_moves = [move for move in moves if move not in taboo_moves]
        for move in taboo_moves:
            if move not in game_state.taboo_moves: 
                store_taboo_move = move
                break
        return filtered_moves, store_taboo_move
    
    return moves, store_taboo_move

def calculate_region_index(board: SudokuBoard, m, n):
    """ 
    Helper function to calculate the block 
    that a square with coordinates (m,n) is in.
    """
    row_region_index = (m // board.m) * board.m
    column_region_index = (n // board.n) * board.n

    return row_region_index, column_region_index

