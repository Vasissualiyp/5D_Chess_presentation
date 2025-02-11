import numpy as np
import os


class Chessboard_2D:
    """
    A class that contains all info about a single 2D chessboard
    """
    def __init__(self, chessboard_tm_pos=[0,0], n=8, origin=-1):
        """
        Sets up 2D chessboard variables

        Args:
            chessboard_tm_pos (array): position of chessboard in time-multiverse space. Defaults to [0,0]
            n (int): size of chessbaord. Defaults to 8.
        """
        if n > 26:
            raise ValueError("More chessboard rows than letters of Latin alphabet!")
        self.chessboard_size = n
        self.origin = origin
        self.utils = ChessUtils_2D()

        self.chessboard_tm_pos = chessboard_tm_pos
        self.setup_chessboard_coords()

    def setup_chessboard_coords(self):
        """
        Sets up matrix, containing info about all squares of chessboard
        """
        n = self.chessboard_size
        self.chessboard_matrix = np.zeros([n, n])

    def add_piece(self, piece, pos, eat_pieces=False):
        """
        Adds piece to a board

        Args:
            piece (str): piece acronym
            pos (str): position of the piece in chess notation
            eat_pieces (bool): wether to throw an error when trying to move onto another piece. Default: False.
        """
        piece_val = self.utils.piece_to_value(piece)
        square_loc = self.utils.chessform_to_matrix(pos, chessboard_size=self.chessboard_size)
        piece_at_pos  = self.chessboard_matrix[square_loc[0], square_loc[1]]
        if (piece_at_pos != 0) and (not eat_pieces):
            piece_at_pos_name = self.utils.value_to_piece(piece_at_pos)
            print(f"Could not place {piece} at {pos}.")
            print(f"There is already {piece_at_pos_name} there.")
            return 1
        else:
            self.chessboard_matrix[square_loc[0], square_loc[1]] = piece_val

    def move_piece(self, pos1, pos2, eat_pieces=False, log=False):
        """
        Moves a piece from pos1 to pos2 in chess notation.
        """
        piece = self.get_piece(pos1)
        target = self.get_piece(pos2)
        self.add_piece("", pos1, eat_pieces=True) # Remove the piece
        if target != "":
            if log: print(f"{piece} at {pos1} eats {target} at {pos2}")
            self.add_piece("", pos2) # Remove the target piece
        self.add_piece(piece, pos2, eat_pieces=eat_pieces)

    def mirror_v(self, pos):
        """
        Mirrors the chess square position vertically (i.e. h8 -> h1)
        """
        pos_arr = self.utils.chessform_to_matrix(pos, chessboard_size=self.chessboard_size)
        new_pos_arr = [ pos_arr[0], self.chessboard_size - pos_arr[1] - 1 ]
        return self.utils.matrix_to_chessform(new_pos_arr, self.chessboard_size)

    def mirror_h(self, pos):
        """
        Mirrors the chess square position horizontally (i.e. h8 -> a8)
        """
        pos_arr = self.utils.chessform_to_matrix(pos, chessboard_size=self.chessboard_size)
        new_pos_arr = [ self.chessboard_size - pos_arr[0] - 1, pos_arr[1] ]
        return self.utils.matrix_to_chessform(new_pos_arr, self.chessboard_size)

    def get_piece(self, pos, log=False):
        """
        Gets the name of the piece in the square, given in chess notation.
        """

        pos_arr = self.utils.chessform_to_matrix(pos, chessboard_size=self.chessboard_size)
        piece_value = self.chessboard_matrix[pos_arr[0], pos_arr[1]]
        if log: print(f"matrix notation for square {pos_arr}: {piece_value}")
        return self.utils.value_to_piece(piece_value)

    def mirror_all_pieces(self):
        """
        Mirrors all pices vertically and switches their color.
        """
        n = self.chessboard_size

        print("Mirroring all the pieces...")
        used_squares = []
        for i in range(n):
            for j in range(n):
                square = self.utils.matrix_to_chessform([i,j], self.chessboard_size)
                piece = self.get_piece(square)
                if piece != "":
                    square_mirror = self.mirror_v(square)
                    piece_mirror = self.utils.light_to_dark_piece(piece)
                    if square_mirror not in used_squares:
                        if self.add_piece(piece_mirror, square_mirror): exit(1)
                    used_squares.append(square)

    def remove_piece(self, pos):
        """
        Removes a piece at a given position, given in chess notation
        """
        idx_1, idx_2 = self.utils.chessform_to_matrix(pos)
        self.chessboard_matrix[idx_1, idx_2] = 0

    def create_row_of_pieces(self, row_id, piece):
        """
        Creates a row of pieces of a single type

        Args:
            row_id (int): the ID of the row, 0 to n-1
            piece (str): piece acronym
        """
        for i in range(self.chessboard_size):
            square = self.utils.matrix_to_chessform([i,row_id], chessboard_size=self.chessboard_size)
            self.add_piece(piece, square)

    def add_mirrored_pieces(self, piece, square):
        """
        Creates 2 pieces, one at a square noted, and another one at a horizontally mirrored square.
        """
        square_mirror = self.mirror_h(square)
        self.add_piece(piece, square)
        self.add_piece(piece, square_mirror)

    def default_chess_configuration_setup(self):
        """
        Sets up the default 8x8 chessboard.
        """
        n = self.chessboard_size
        if n != 8:
            raise ValueError(f"Cannot create a default chessboard on a {n}x{n} board")

        self.add_mirrored_pieces('rl', 'a1')
        self.add_mirrored_pieces('nl', 'b1')
        self.add_mirrored_pieces('bl', 'c1')
        self.add_piece('ql','d1')
        self.add_piece('kl','e1')
        self.create_row_of_pieces(1,'pl')
        self.mirror_all_pieces()

    def print_chessboard(self, style="regular"):
        """
        Prints out the current chessboard state to the terminal

        Args:
            style (str): style of the board. Values are: regular (d), full, none
        """
        n = self.chessboard_size
        black_square = "  "
        move_symb_black = " □"
        if style == "regular":
            white_square = "░░"
            move_symb_white = "░▣"
        elif style == "full":
            white_square = "██"
            move_symb_white = "█▣"
        else:
            white_square = "  "
            move_symb_white = "  "
        # First line
        print("┌",end="")
        for i in range(n-1):
            print("──┬",end="")
        print("──┐")
        for i in range(n):
            print("│",end="")
            if i == 7:
                leftsymb = "└"
                rightsymb = "┘"
                centsymb = "┴"
            else:
                leftsymb = "├"
                rightsymb = "┤"
                centsymb = "┼"
            for j in range(n):
                val = int(self.chessboard_matrix[j,self.chessboard_size - i - 1])
                piece = self.utils.value_to_piece(val)
                if val == 0:
                    if ((i + j) % 2 == 0):
                        piece = white_square
                    else:
                        piece = black_square
                if val > 60:
                    if ((i + j) % 2 == 0):
                        piece = move_symb_white
                    else:
                        piece = move_symb_black
                val_str = piece.rjust(2)
                print(val_str, end="│")
            print("")
            print(leftsymb,end="")
            for j in range(n-1):
                print("──"+centsymb,end="")
            print("──"+rightsymb,end="")
            print("")


class ChessUtils_2D():
    """DocString"""
    def __init__(self):
        """Create a new instance"""

        self.img_type = "svg"
        self.pieces_scales_dict = {
                                   # ----------------------
                                   "k": 1.6, # Light King
                                   "q": 1.5, # Light Queen
                                   "b": 1.4, # Light Bishop
                                   "n": 1.4, # Light Knight
                                   "r": 1.1, # Light Rook
                                   "p": 0.9, # Light Pawn
                                   "d": 1.0, # Light Dragon
                                   "u": 1.0, # Light Unicorn
                                  }
        self.pieces_dict = {0: "",
                            # ----------------------
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
                            # ----------------------
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
                            # ----------------------
                            60:"Ml", # Movement allowed light
                            61:"Md", # Movement allowed dark
                           }

    def matrix_to_chessform(self, pos_arr, chessboard_size=8):
        """
        Converts chess format of squre to matrix chessboard positional array.
        Returns a0 if outside of the chessboard.
        """
        n = chessboard_size
        if len(pos_arr) > 2:
            return 'a0'
        square_x, square_y = list(pos_arr)
        square_x += 1

        # Position of letter in English alphabet
        if 1 <= square_x <= 26:
            pos_let = chr(square_x + ord('a') - 1)
        else:
            return 'a0'
        pos_num = square_y + 1

        if ((square_x > n) or (square_y > n - 1) or (square_x < 0) or (square_y < 0)):
            return 'a0'

        return ''.join([pos_let, str(pos_num)])

    def chessform_to_matrix(self, pos, chessboard_size=8):
        """
        Converts chess format of squre to matrix chessboard positional array.
        Returns [-1, -1] if outside of the chessboard.
        """
        n = chessboard_size
        if len(pos) > 2:
            return [-1, -1]
        pos_let, pos_num = list(pos)
        pos_num = int(pos_num)

        # Position of letter in English alphabet
        square_loc = ord(pos_let) - ord('a') + 1

        if (square_loc > 26) or (square_loc < 1):
            return [-1, -1]
        if ((pos_num > n) or (square_loc > n)):
            return [-1, -1]

        return [square_loc-1, pos_num-1]

    def piece_err(self, piece):
        """
        Handle errors with piece names
        """
        example_string = f"Example: kd. Provided: {piece}"
        if len(piece) > 2:
            raise ValueError(f"Cannot have piece string being more than 2 characters. {example_string}")
        if (piece[1] != "l") and (piece[1] != "d"):
            raise ValueError(f"Piece must be light or dark. {example_string}")

    def get_piece_image(self, piece):
        """
        Obtains image path for a piece

        Args:
            piece (str): piece acronym

        Returns:
            str: full path to the file of the piece
            float: scale factor for the piece image size 
        """
        if self.img_type == "svg":
            postfix = "v60.svg"
        elif self.img_type == "png":
            postfix = "t60.png"
        else:
            raise ValueError(f"Unknown image type: {self.img_type}")

        # Treatment of identical pieces
        if piece[0] == 'R': # Royal queen
            piece_img_str = 'q' + piece[1]
        elif piece[0] == 'c': # Common king
            piece_img_str = 'k' + piece[1]
        elif piece[0] == 'B': # Brawn
            piece_img_str = 'p' + piece[1]
        elif piece[0] == 'P': # Princess
            piece_img_str = 'q' + piece[1]
        else:
            piece_img_str = piece

        if piece_img_str[0] in ['b', 'k', 'n', 'p', 'q', 'r']:
            filename = "Chess_" + piece_img_str + postfix
        else: # For 5D Chess special pieces
            filename = "Chess_" + "p" + piece_img_str[1] + postfix

        scaling = self.pieces_scales_dict[piece_img_str[0]]

        current_directory = os.path.dirname(__file__)
        parent_directory = os.path.dirname(current_directory)
        resources_dir = os.path.join(parent_directory, "resources")
        return os.path.join(resources_dir, filename), scaling

    def light_to_dark_piece(self, piece):
        """
        Converts light to dark piece and vice versa
        """
        self.piece_err(piece)
        piece_name, piece_color = list(piece)
        if piece_color == 'l': return ''.join([piece_name, 'd'])
        if piece_color == 'd': return ''.join([piece_name, 'l'])

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
        for value,comparison_string in self.pieces_dict.items():
            if comparison_string == string:
                return value
        raise ValueError(f"{string} is not a valid piece.")
