import numpy as np
import manim

class 5D_Chessboard:
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
        

class 2D_Chessboard:
    """
    A class that contains all info about a single 2D chessboard
    """
    def __init__(self, chessboard_size=8):
        self.chessboard_size = chessboard_size
        self.pieces_dict = {0: "",
                            1: "lk", # Light King
                            2: "lq", # Light Queen
                            3: "lb", # Light Bishop
                            4: "ln", # Light Knight
                            5: "lr", # Light Rook
                            6: "lp", # Light Pawn
                            7: "ld", # Light Dragon
                            8: "lu", # Light Unicorn
                            9: "lB", # Light Brawn
                            10:"lP", # Light Princess
                            11:"lc", # Light Common King
                            12:"lR", # Light Royal Queen
                            21:"dk", # Dark King
                            22:"dq", # Dark Queen
                            23:"db", # Dark Bishop
                            24:"dn", # Dark Knight
                            25:"dr", # Dark Rook
                            26:"dp", # Dark Pawn
                            27:"dd", # Dark Dragon
                            28:"du", # Dark Unicorn
                            29:"dB", # Dark Brawn
                            30:"dP", # Dark Princess
                            31:"dc", # Dark Common King
                            32:"dR", # Dark Royal Queen
                           }

    def setup_chessboard_coords(self):
        """
        Sets up matrix, containing info about all squares of chessboard
        """
        n = self.chessboard_size
        self.chessboard_matrix = np.zeros([n, n])

    def piece_to_value(self, str)
        """
        Converts piece acronym to value, understandable by class

        Args:
            string (str): piece name

        Returns:
            value (int): value of the piece 
        """

