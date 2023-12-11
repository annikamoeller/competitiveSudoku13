import random
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

def possible(game_state, i, j, value):
    """ 
    Check if a move is possible.
    """
    return game_state.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j, value) in game_state.taboo_moves

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
        else: all_legal_moves.append(move)

    return all_legal_moves

def evaluate_move(board, move): 
    """
    Assign a score to a given move. 
    """
    current_row, current_col, current_block = get_row_col_block_values(board, move)

    # Check if a move results in a full row/column/block and assign score accordingly
    solves_row = (len(current_row) == board.N-1)    
    solves_col = (len(current_col) == board.N-1)     
    solves_block = (len(current_block) == board.N-1) 
    truth_arr = [solves_row, solves_col, solves_block] 
    if sum(truth_arr) == 0: score = 0
    if sum(truth_arr) == 1: score = 1
    if sum(truth_arr) == 2: score = 3
    if sum(truth_arr) == 3: score = 7
    return score

def calculate_region_index(board: SudokuBoard, m, n):
    """ 
    Helper function to calculate the block 
    that a square with coordinates (m,n) is in.
    """
    row_region_index = (m // board.m) * board.m
    column_region_index = (n // board.n) * board.n

    return row_region_index, column_region_index

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