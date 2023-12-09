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