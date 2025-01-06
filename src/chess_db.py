import numpy as np
import manim

class Chessboard_5D:
    """
    A class that contains all info about 5D chessboards and pieces
    """
    def __init__(self, chessboard_size = 8):
        """
        Create a new instance of class
        """
        self.chessboards = []
        self.chessboard_size = chessboard_size

    def add_chessboard(self, chessboard_loc):
        """
        Add chessboard at time/multiverse location
        """
        

class Chessboard_2D:
    """
    A class that contains all info about a single 2D chessboard
    """
    def __init__(self, chessboard_tm_pos=[0,0], n=8):
        """
        Sets up 2D chessboard variables

        Args:
            chessboard_tm_pos (array): position of chessboard in time-multiverse space. Defaults to [0,0]
            n (int): size of chessbaord. Defaults to 8.
        """
        if n > 26:
            raise ValueError("More chessboard rows than letters of Latin alphabet!")
        self.chessboard_size = n

        self.chessboard_tm_pos = chessboard_tm_pos
        self.pieces_dict = {0: "",
                            1: "kl", # Light King
                            2: "ql", # Light Queen
                            3: "bl", # Light Bishop
                            4: "nl", # Light Knight
                            5: "rl", # Light Rook
                            6: "pl", # Light Pawn
                            7: "dl", # Light Dragon
                            8: "ul", # Light Unicorn
                            9: "Bl", # Light Brawn
                            10:"Pl", # Light Princess
                            11:"cl", # Light Common King
                            12:"Rl", # Light Royal Queen
                            21:"kd", # Dark King
                            22:"qd", # Dark Queen
                            23:"bd", # Dark Bishop
                            24:"nd", # Dark Knight
                            25:"rd", # Dark Rook
                            26:"pd", # Dark Pawn
                            27:"dd", # Dark Dragon
                            28:"ud", # Dark Unicorn
                            29:"Bd", # Dark Brawn
                            30:"Pd", # Dark Princess
                            31:"cd", # Dark Common King
                            32:"Rd", # Dark Royal Queen
                           }

    def setup_chessboard_coords(self):
        """
        Sets up matrix, containing info about all squares of chessboard
        """
        n = self.chessboard_size
        self.chessboard_matrix = np.zeros([n, n])

    def value_to_piece(self, value):
        """
        Converts value, understandable by class, to piece acronym
        """
        try:
            return self.pieces_dict[value]
        except KeyError:
            raise ValueError(f"Value '{value}' does not correspond to a valid piece.")

    def piece_to_value(self, string):
        """
        Converts piece acronym to value, understandable by class
        """
        for comparison_string,value in self.pieces_dict.items():
            if comparison_string == string:
                return value
        raise ValueError(f"{string} is not a valid piece.")

    def chessform_to_matrix(self, pos):
        """
        Converts chess format of squre to matrix chessboard positional array
        """
        n = self.chessboard_size
        if len(pos) > 2:
            raise ValueError(f"Cannot have position string being more than 2 characters. Example: h8. Provided: {pos}")
        pos_let, pos_num = list(pos)

        # Position of letter in English alphabet
        square_loc = ord(pos_let) - ord('a') + 1

        if square_loc > 26:
            raise ValueError("More chessboard rows than letters of Latin alphabet!")
        if ((pos_num > n) or (square_loc > n)):
            raise ValueError(f"Square {pos} is outside of the chessbord of size {n}x{n}!")

        return [square_loc-1, pos_num-1]


    def add_piece(self, piece, pos):
        """
        Adds piece to a board

        Args:
            piece (str): piece acronym
            pos (str): position of the piece in chess notation
        """
        piece_val = self.piece_to_value(piece)
        square_loc = self.chessform_to_matrix(pos)
        piece_at_pos  = self.chessboard_matrix[square_loc[0], square_loc[1]]
        if piece_at_pos != 0:
            piece_at_pos_name = self.value_to_piece(piece_at_pos)
            print(f"Could not place {piece} at {pos}.")
            print(f"There is already {piece_at_pos_name} there.")
            return 1
        else:
            self.chessboard_matrix[square_loc[0], square_loc[1]] = piece_val

