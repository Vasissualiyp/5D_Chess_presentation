import numpy as np
import itertools
from chess_db_2d import Chessboard_2D
from chess_db_5d import Chessboard_5D

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

        self.moveset = {
            "r": self.orth, # rook
            "b": self.diag, # bishop
            "u": self.tri,  # unicorn
            "d": self.quad, # dragon
            "n": self.knight, # knight
            "P": self.orth + self.diag, # princess
            "q": self.orth + self.diag + self.tri + self.quad, # queen
            "k": self.orth + self.diag + self.tri + self.quad, # king
            "p": [], # pawn has special moves
            "B": [], # brawn has special moves
        }

    def generate_perms(self, array) -> list:
        """
        Generates a list of all possible permutations of an array
        """
        permutations = list(itertools.permutations(array))
        unique_permutations = list(set(permutations))
        return unique_permutations.sort()
    

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
        utils = Chessboard_2D()
        square = utils.matrix_to_chessform([x,y])
        return [square, t, m]

    def get_dr(self, piece_type):
        """
        Retrieves the list moves for a given piece in dr notation.

        Args:
            piece_type (str): Name of the piece (no color).

        Returns:
            list: Moveset for the piece.
        """
        return self.moveset.get(piece_type, [])

    def get_all_movable_spaces(self, check_if_move_possible, piece, pos):
        """
        Gets a list of all spaces, where a piece can move to

        Args:
            check_if_move_possible (func): Function that checks if performing a move is possible
            piece (str): name of the piece to be moved
            pos (list): 3-list that gives a position of the piece to be moved

        Returns:
            moves_list (list): list of 3-lists of all possible moves
        """
        moves_list = []

        return moves_list

