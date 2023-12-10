import random
from competitive_sudoku.sudoku import GameState, Move, SudokuBoard, TabooMove
import competitive_sudoku.sudokuai

# Check if a move is possible
def possible(game_state, i, j, value):
    return game_state.board.get(i, j) == SudokuBoard.empty and not TabooMove(i, j, value) in game_state.taboo_moves

# Get all legal moves in a state
def get_legal_moves(game_state):
    all_moves = [Move(i, j, value) for i in range(game_state.board.N) for j in range(game_state.board.N)
                for value in range(1, game_state.board.N +1) if possible(game_state, i, j, value)]

    all_legal_moves = []
    for move in all_moves:
        current_row, current_col, current_block = get_row_col_block_values(game_state.board, move)
        if (move.value in set(current_row)) or (move.value in set(current_col)) or (move.value in set(current_block)): continue
        else: all_legal_moves.append(move)

    return all_legal_moves

# Helper function to return all values in the row, column, and block of the currently chosen move
def get_row_col_block_values(board, move):
    current_row = [board.get(move.i, j) for j in range(0, board.N) if board.get(move.i, j) != SudokuBoard.empty] 
    current_col = [board.get(i, move.j) for i in range(0, board.N) if board.get(i, move.j) != SudokuBoard.empty]
    block_i = move.i // board.m * board.m # row coordinate
    block_j = move.j // board.n * board.n # column coordinate
    current_block = [board.get(i,j) for i in range(block_i, block_i + board.m) \
                        for j in range(block_j, block_j + board.n) if board.get(i,j) != SudokuBoard.empty]
    return current_row, current_col, current_block

def should_play_taboo(board, moves, n_empties):
    can_score = False
    even_squares_left = n_empties % 2 == 0
    for move in moves:
        current_row, current_col, current_block = get_row_col_block_values(board, move)

        if (len(current_row) == board.N-1 or len(current_col) == board.N-1 or len(current_block) == board.N-1):
            can_score = True

        if even_squares_left and board_half_filled(board):
            return True
        else: return False 

def calculate_n_empties(board):
    n_empties = 0
    for i in range(board.N):
        for j in range(board.N):
            if board.get(i, j) is SudokuBoard.empty:
                n_empties += 1  
    return n_empties  

def even_squares_left(board):
    n_empties = 0
    for i in range(board.N):
        for j in range(board.N):
            if board.get(i, j) is SudokuBoard.empty:
                n_empties += 1  
    return n_empties % 2 == 0

def board_half_filled(board):
    n_full = 0
    total_cells = board.N * board.N
    for i in range(board.N):
        for j in range(board.N):
            if board.get(i, j) is not SudokuBoard.empty:
                n_full += 1
    return n_full/total_cells > 0.5
    