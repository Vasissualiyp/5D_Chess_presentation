import numpy as np

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

        self.chessboard_tm_pos = chessboard_tm_pos
        self.setup_chessboard_coords()
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
        for value,comparison_string in self.pieces_dict.items():
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
        pos_num = int(pos_num)

        # Position of letter in English alphabet
        square_loc = ord(pos_let) - ord('a') + 1

        if square_loc > 26:
            raise ValueError("More chessboard rows than letters of Latin alphabet!")
        if ((pos_num > n) or (square_loc > n)):
            raise ValueError(f"Square {pos} is outside of the chessbord of size {n}x{n}!")

        return [square_loc-1, pos_num-1]

    def matrix_to_chessform(self, pos_arr):
        """
        Converts chess format of squre to matrix chessboard positional array
        """
        n = self.chessboard_size
        if len(pos_arr) > 2:
            raise ValueError(f"Cannot have position array being more than 2 elements. Example: [2,1]. Provided: {pos_arr}")
        square_x, square_y = list(pos_arr)
        square_x += 1

        # Position of letter in English alphabet
        if 1 <= square_x <= 26:
            pos_let = chr(square_x + ord('a') - 1)
        else:
            raise ValueError(f"x matrix position number must be in the range 1-26. Provided: {square_x}.")
        pos_num = square_y + 1

        if ((square_x > n) or (square_y > n - 1)):
            raise ValueError(f"Square {pos_arr} is outside of the chessbord of size {n}x{n}!")

        return ''.join([pos_let, str(pos_num)])

    def piece_err(self, piece):
        """
        Handle errors with piece names
        """
        example_string = f"Example: kd. Provided: {piece}"
        if len(piece) > 2:
            raise ValueError(f"Cannot have piece string being more than 2 characters. {example_string}")
        if (piece[1] != "l") and (piece[1] != "d"):
            raise ValueError(f"Piece must be light or dark. {example_string}")

    def add_piece(self, piece, pos, eat_pieces=False):
        """
        Adds piece to a board

        Args:
            piece (str): piece acronym
            pos (str): position of the piece in chess notation
            eat_pieces (bool): wether to throw an error when trying to move onto another piece. Default: False.
        """
        piece_val = self.piece_to_value(piece)
        square_loc = self.chessform_to_matrix(pos)
        piece_at_pos  = self.chessboard_matrix[square_loc[0], square_loc[1]]
        if (piece_at_pos != 0) and (not eat_pieces):
            piece_at_pos_name = self.value_to_piece(piece_at_pos)
            print(f"Could not place {piece} at {pos}.")
            print(f"There is already {piece_at_pos_name} there.")
            return 1
        else:
            self.chessboard_matrix[square_loc[0], square_loc[1]] = piece_val

    def move_piece(self, pos1, pos2):
        """
        Moves a piece from pos1 to pos2 in chess notation.
        """
        piece = self.get_piece(pos1)
        target = self.get_piece(pos2)
        self.add_piece("", pos1, eat_pieces=True) # Remove the piece
        if target != "":
            print(f"{piece} at {pos1} eats {target} at {pos2}")
            self.add_piece("", pos2) # Remove the target piece
        self.add_piece(piece, pos2)


    def light_to_dark_piece(self, piece):
        """
        Converts light to dark piece and vice versa
        """
        self.piece_err(piece)
        piece_name, piece_color = list(piece)
        if piece_color == 'l':
            return ''.join([piece_name, 'd'])
        if piece_color == 'd':
            return ''.join([piece_name, 'l'])

    def mirror_v(self, pos):
        """
        Mirrors the chess square position vertically (i.e. h8 -> h1)
        """
        pos_arr = self.chessform_to_matrix(pos)
        new_pos_arr = [ pos_arr[0], self.chessboard_size - pos_arr[1] - 1 ]
        return self.matrix_to_chessform(new_pos_arr)

    def mirror_h(self, pos):
        """
        Mirrors the chess square position horizontally (i.e. h8 -> a8)
        """
        pos_arr = self.chessform_to_matrix(pos)
        new_pos_arr = [ self.chessboard_size - pos_arr[0] - 1, pos_arr[1] ]
        return self.matrix_to_chessform(new_pos_arr)

    def get_piece(self, pos):
        """
        Gets the name of the piece in the square, given in chess notation.
        """

        pos_arr = self.chessform_to_matrix(pos)
        piece_value = self.chessboard_matrix[pos_arr[0], pos_arr[1]]
        return self.value_to_piece(piece_value)

    def mirror_all_pieces(self):
        """
        Mirrors all pices vertically and switches their color.
        """
        n = self.chessboard_size

        print("Mirroring all the pieces...")
        used_squares = []
        for i in range(n):
            for j in range(n):
                square = self.matrix_to_chessform([i,j])
                piece = self.get_piece(square)
                if piece != "":
                    square_mirror = self.mirror_v(square)
                    piece_mirror = self.light_to_dark_piece(piece)
                    if square_mirror not in used_squares:
                        if self.add_piece(piece_mirror, square_mirror):
                            exit(1)
                    used_squares.append(square)

    def create_row_of_pieces(self, row_id, piece):
        """
        Creates a row of pieces of a single type

        Args:
            row_id (int): the ID of the row, 0 to n-1
            piece (str): piece acronym
        """
        for i in range(self.chessboard_size):
            square = self.matrix_to_chessform([i,row_id])
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
        if style == "regular":
            white_square = "░░"
        elif style == "full":
            white_square = "██"
        else:
            white_square = "  "
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
                piece = self.value_to_piece(val)
                if val == 0:
                    if ((i + j) % 2 == 0):
                        piece = white_square
                    else:
                        piece = black_square
                val_str = piece.rjust(2)
                print(val_str, end="│")
            print("")
            print(leftsymb,end="")
            for j in range(n-1):
                print("──"+centsymb,end="")
            print("──"+rightsymb,end="")
            print("")

