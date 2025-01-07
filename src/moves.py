import numpy as np
import itertools
from chess_db_2d import ChessUtils_2D

class Moves():
    """Class containing moves of all chess pieces"""
    def __init__(self):
        """Create a new instance of class"""
        # dr vectors for moves
        self.orth = self.generate_perms_with_signs([1, 0, 0, 0])
        self.diag = self.generate_perms_with_signs([1, 1, 0, 0])
        self.tri =  self.generate_perms_with_signs([1, 1, 1, 0])
        self.quad = self.generate_perms_with_signs([1, 1, 1, 1])
        self.knight = self.generate_perms_with_signs([2, 1, 0, 0])
        self.dr = {
            "r": self.orth, # rook
            "b": self.diag, # bishop
            "u": self.tri,  # unicorn
            "d": self.quad, # dragon
            "n": self.knight, # knight
            "P": self.orth + self.diag, # princess
            "q": self.orth + self.diag + self.tri + self.quad, # queen
            "k": self.orth + self.diag + self.tri + self.quad, # king
            "R": self.orth + self.diag + self.tri + self.quad, # royal queen
            "c": self.orth + self.diag + self.tri + self.quad, # common king
            "p": [], # pawn has special moves
            "B": [], # brawn has special moves
        }

        self.utils2d = ChessUtils_2D()

    def generate_perms(self, array):
        """
        Generates a list of all possible permutations of an array
        """
        permutations = list(itertools.permutations(array))
        unique_permutations = list(set(permutations))
        return sorted(unique_permutations)  # Return the sorted list
    
    def generate_perms_with_signs(self, array) -> list:
        """
        Generates a list of all possible permutations of an array with sign variations
        """
        perms = self.generate_perms(array)
        signed_perms = []
        for move in perms:
           for signs in itertools.product([-1, 1], repeat=4):
               signed_perms.append(tuple(sign * component for sign, component in zip(signs, move)))
        return sorted(set(signed_perms))  # Remove duplicates

    def convert_4d_vec_to_3list(self, vec) -> list:
        """
        Converts a 4d vector to a 3-element list representation (i.e. [1,2,4,5]->['b3',4,5]) 
        """

        x,y,t,m = vec
        square = self.utils2d.matrix_to_chessform([x,y])
        return [square, t, m]

    def convert_3list_to_4d_vec(self, list3):
        """
        Converts a 3-element list representation to a 4d vector (i.e. ['b3',4,5]->[1,2,4,5]) 
        """

        square,t,m = list3
        square_mx = self.utils2d.chessform_to_matrix(square)
        return [square_mx[0], square_mx[1], t, m]

    def get_dr(self, piece_type):
        """
        Retrieves the list moves for a given piece in dr notation.

        Args:
            piece_type (str): Name of the piece (no color).

        Returns:
            list: Moveset for the piece.
        """
        return self.dr.get(piece_type, [])

    def get_all_movable_spaces(self, check_if_move_possible, piece, pos, log=False):
        """
        Gets a list of all spaces, where a piece can move to

        Args:
            check_if_move_possible (func): Function that checks if performing a move is possible
            piece (str): name of the piece to be moved
            pos (list): 3-list that contains a position of the piece to be moved
            log (bool): whether to output log into the terminal

        Returns:
            moves_list (list): list of 3-lists of all possible moves
        """
        self.utils2d.piece_err(piece)
        piece_type, piece_color = list(piece)
        list_dr = self.get_dr(piece_type)
        pos_4d = self.convert_3list_to_4d_vec(pos)

        if piece_type in ['k', 'c']: # Set of moves for king-like pieces (one-space move)
            return self.get_all_single_moves(check_if_move_possible, piece_color, 
                                             list_dr, pos_4d, log)
        elif piece_type in ['n']: # Set of moves for knight-like pieces (jump over)
            return self.get_all_single_moves(check_if_move_possible, piece_color, 
                                             list_dr, pos_4d, log)
        elif piece_type in ['p', 'B']: # Set of moves for pawn-like pieces (special)
            return []
        else: # Set of moves for pieces that move in a line, i.e. all other pieces
            return self.get_all_linear_moves(check_if_move_possible, piece_color, 
                                             list_dr, pos_4d, log)

    def get_all_linear_moves(self, check_if_move_possible, piece_color, list_dr, pos_4d, log):
        """
        Obtains movable spaces for pieces that move in straight lines (rooks, queens, bishops, etc.)

        Args:
            check_if_move_possible (func): Function that checks if performing a move is possible
            piece_color (str): color of the piece to be moved
            list_dr (list): list of dr base vectors for a given piece
            pos_4d (array): a 4d vector that gives the position of the piece to be moved
            log (bool): whether to output log into the terminal

        Returns:
            moves_list (list): list of 3-lists of all possible moves
        """
        moves_list = []
        for base_dr in list_dr:
            empty = 2 # This variable tracks if one can move to a next tile in line
            prev_pos = pos_4d # Start counting from the piece itself
            while empty==2:
                empty, prev_pos = self.test_single_tile(check_if_move_possible, prev_pos, base_dr, 
                                                        piece_color, moves_list, log)
        return moves_list

    def get_all_single_moves(self, check_if_move_possible, piece_color, list_dr, pos_4d, log):
        """
        Obtains movable spaces for pieces that move in straight lines (rooks, queens, bishops, etc.)

        Args:
            check_if_move_possible (func): Function that checks if performing a move is possible
            piece_color (str): color of the piece to be moved
            list_dr (list): list of dr base vectors for a given piece
            pos_4d (array): a 4d vector that gives the position of the piece to be moved
            log (bool): whether to output log into the terminal

        Returns:
            moves_list (list): list of 3-lists of all possible moves
        """
        moves_list = []
        for base_dr in list_dr:
            prev_pos = pos_4d # Start counting from the piece itself
            _, prev_pos = self.test_single_tile(check_if_move_possible, prev_pos, base_dr, 
                                                piece_color, moves_list, log)
        return moves_list

    def test_single_tile(self, check_if_move_possible, prev_pos, base_dr, piece_color, moves_list, log=False):
        """
        Args:
            check_if_move_possible (func): Function that checks if performing a move is possible
            prev_pos (array): previous position in a line, or starting position if not in a line
            base_dr (tuple): 4-element tuple, which contains the next step for tile position increment
            piece_color (str): color of the piece to be moved
            moves_list (list): list of moves found up to this point

        Returns:
            move_possible (int): whether the move is possible. Values:
                0 if impossible
                1 if possible with eating a piece
                2 if possible without eating a piece
            prev_pos (array): modified prev_pos value
        """
        if log: print(prev_pos, base_dr)
        new_pos = [0,0,0,0]
        for i in range(len(base_dr)):
            new_pos[i] = int(prev_pos[i]) + int(base_dr[i])
        new_pos = self.convert_4d_vec_to_3list(new_pos)
        move_possible = check_if_move_possible(new_pos, piece_color)
        if move_possible: # 1 to eat enemy piece, 2 for moving through
            moves_list.append(new_pos)
            if log: print("Attaching this move...")
        prev_pos=self.convert_3list_to_4d_vec(new_pos)
        return move_possible, prev_pos
