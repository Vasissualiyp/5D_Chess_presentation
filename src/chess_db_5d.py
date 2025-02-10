import numpy as np
from chess_db_2d import Chessboard_2D, ChessUtils_2D
from moves import Moves
import string, manim, copy


class Chessboard_5D:
    """
    A class that contains all info about 5D chessboards and pieces
    """
    def __init__(self, chessboard_size=8, first_turn_black=0, log=False):
        """
        Create a new instance of class
        """
        self.chessboards = []
        self.timemult_coords = []
        self.chessboard_size = chessboard_size
        self.present = 0
        self.max_mult_black = 0
        self.max_mult_white = 0
        self.moves = Moves()
        self.log = log

        # 0 for 1st turn to white, 1 for 1st turn to black. Important for multiverse creation directions
        self.first_turn_black = first_turn_black

    def default_chess_configuration_setup(self):
        """
        Sets up the default 8x8 chessboard.
        """
        base_chessboard = Chessboard_2D()
        base_chessboard.default_chess_configuration_setup()
        self.chessboards.append(base_chessboard)
        self.timemult_coords.append([0,0])

    def add_empty_chessboard(self, chessboard_loc):
        """
        Adds an empty chessboard in specified time-multiverse locaiton
        """
        base_chessboard = Chessboard_2D(chessboard_tm_pos=chessboard_loc)
        self.chessboards.append(base_chessboard)
        self.timemult_coords.append(chessboard_loc)
    
    def print_chessboard(self, chessboard_loc, style="regular"):
        """
        Outputs the board state into the terminal based on its time-multiverse position
        """
        id = self.get_chessboard_by_tm(chessboard_loc)
        if id != -1:
            print(f"Printing chessboard at {chessboard_loc}")
            chessboard = self.chessboards[id]
            chessboard.print_chessboard(style=style)
        else:
            print(f"Couldn't find chessboard at {chessboard_loc}")

    def get_chessboard_by_tm(self, chessboard_loc, log=False):
        """
        Get the chessboard id by its time-multiverse coordinate.
        Returns -1 if not present.
        """
        if log: print(chessboard_loc)
        for i, element in enumerate(self.timemult_coords):
            if log: print(element)
            if (element == chessboard_loc):
                return i
        return -1

    def add_chessboard(self, chessboard_loc, origin_board):
        """
        Add chessboard at time/multiverse location

        Args:
            chessboard_loc (array): location of chessboard in time-multiverse coordinates
            origin_board (array): board of origin, from which the this one is created
                                  either by multiverse branching or time passing
        """
        chessboard = Chessboard_2D(chessboard_tm_pos=chessboard_loc, n=self.chessboard_size, origin=origin_board)
        if chessboard_loc not in self.timemult_coords:
            self.chessboards.append(chessboard)
            self.timemult_coords.append(chessboard_loc)
        else:
            raise ValueError(f"Could not add a chessboard at tm coordinate of {chessboard_loc}: the space is occupied")

    def get_piece(self, pos):
        """
        Get piece at given position

        Args:
            pos (list): 3-list of target space

        Returns:
            piece (str): piece name acronym or NaN if board doesn't exist
        """
        self.movement_list_5d_err(pos, list_name="pos")
        square, time, mult = pos
        id = self.get_chessboard_by_tm([time, mult])
        if id == -1: return "NaN" # Handling a case of non-existent board
        chessboard = self.chessboards[id]
        return chessboard.get_piece(square)

    def add_piece(self, piece, pos, eat_pieces=False):
        """
        Adds piece to a board

        Args:
            piece (str): piece acronym
            pos (3-list): position of the piece in 3-list format
            eat_pieces (bool): wether to throw an error when trying to move onto another piece. Default: False.
        """
        self.movement_list_5d_err(pos, list_name="pos")
        square, time, mult = pos
        id = self.get_chessboard_by_tm([time, mult])
        assert id != -1, f"Chessboard at time-multiverse coordinates {[time, mult]} doesn't exist!"
        target_chessboard = self.chessboards[id]
        target_chessboard.add_piece(piece, square, eat_pieces=eat_pieces)

    def evolve_chessboard(self, chessboard_loc):
        """
        Makes a copy of chessboard forwards in time, and create a new multiverse if needed

        Args:
            chessboard_loc (array): location of chessboard in time-multiverse coordinates
        """
        id = -1
        timeline_times = []
        for i, element in enumerate(self.timemult_coords):
            if element[1] == chessboard_loc[1]:
                timeline_times.append(element[0])
                if element[0] == chessboard_loc[0]:
                    id = i
        if id == -1:
            raise ValueError(f"No chessboard was found at location {chessboard_loc}")

        if max(timeline_times) == chessboard_loc[0]: # Time evolution only
            chessboard_loc = [ chessboard_loc[0] + 1, chessboard_loc[1] ]
        else: # Multiverse creation
            is_white = (chessboard_loc[0] + chessboard_loc[1] + self.first_turn_black) % 2
            if is_white: # 1st turn is white
                new_mult = self.max_mult_white + 1
            else: # 1st turn is black
                new_mult = self.max_mult_black - 1
            chessboard_loc = [ chessboard_loc[0] + 1, new_mult ]

        final_chessboard = copy.deepcopy(self.chessboards[id])
        final_chessboard.origin = id
        self.chessboards.append(final_chessboard)
        self.timemult_coords.append(chessboard_loc)
    
    def get_max_time_from_multi(self, mult):
        """
        Get a maximum existing time coordinate for a certain timeline (multiverse id) value.
        """
        timeline_times = []
        for element in self.timemult_coords:
            if element[1] == mult:
                timeline_times.append(element[0])
        return max(timeline_times)

    def movie_piece(self, original_pos, final_pos):
        """
        Moves a piece between 2 squares

        Args:
            original_pos (list): original position, i.e. ['a1', 2, 3]
            final_pos (list): final position (before multiverse branching/time moving forward), i.e. ['a1', 2, 3]
        """
        self.movement_list_5d_err(original_pos, "original_pos")
        self.movement_list_5d_err(final_pos,    "final_pos")

        square1, time1, mult1 = original_pos
        square2, time2, mult2 = final_pos

        if (time1 == time2) and (mult1 == mult2): # Normal move - advances timeline if no future boards exist
            self.move_with_evolution(original_pos, square2)
        elif (time1 < time2) and (mult1 == mult2): # Moving to the future is impossible
            raise ValueError("Cannot move to the future on the same timeline")
        else: # Other moves
            self.move_with_evolution_2_boards(original_pos, final_pos)

    def move_with_evolution(self, original_pos, square2):
        """
        Moves a single piece and evolves the board 

        Args:
            original_pos (list): original position, i.e. ['a1', 2, 3]
            square2 (array): final square of a piece
        """
        square1, time1, mult1 = original_pos
        self.evolve_chessboard([time1, mult1])
        target_chessboard = self.chessboards[-1]
        target_chessboard.move_piece(square1, square2, eat_pieces=True)
        self.chessboards[-1] = target_chessboard

    def move_with_evolution_2_boards(self, original_pos, final_pos):
        """
        Moves a single piece and evolves the board 

        Args:
            original_pos (list): original position, i.e. ['a1', 2, 3]
            final_pos (list): final position (before multiverse branching/time moving forward), i.e. ['a1', 2, 3]
        """
        # Evolve original board - remove the piece
        piece = self.move_with_evolution_remove_piece(original_pos)
        # Evolve target board - add the piece
        self.move_with_evolution_add_piece(final_pos, piece)

    def move_with_evolution_remove_piece(self, original_pos):
        """
        Moves a single piece and evolves the board 

        Args:
            original_pos (list): original position, i.e. ['a1', 2, 3]
            square2 (array): final square of a piece

        Returns:
            piece (str): an acronym for the removed piece
        """
        square1, time1, mult1 = original_pos
        self.evolve_chessboard([time1, mult1])
        target_chessboard = self.chessboards[-1]
        piece = target_chessboard.get_piece(square1)
        target_chessboard.add_piece("", square1, eat_pieces=True)
        self.chessboards[-1] = target_chessboard
        return piece

    def move_with_evolution_add_piece(self, final_pos, piece):
        """
        Moves a single piece and evolves the board 

        Args:
            final_pos (list): final position (before multiverse branching/time moving forward), i.e. ['a1', 2, 3]
            piece (str): an acronym for the piece to be added
        """
        square2, time2, mult2 = final_pos
        self.evolve_chessboard([time2, mult2])
        target_chessboard = self.chessboards[-1]
        target_chessboard.add_piece(piece, square2, eat_pieces=True)
        self.chessboards[-1] = target_chessboard

    def movement_list_5d_err(self, list_5d, list_name="list_5d"):
        """
        Handles errors for lists of coordinates for 5D chess.

        Args:
            list_5d (list): list of values itself
            list_name (str): name of the variable. Needed for better error messages
        """
        if len(list_5d) != 3:
            raise ValueError(f"{list_name} should be a list_5d of 3 elements. You have: {list_5d}")
        if type(list_5d[0]) != str:
            raise ValueError(f"1st entry of {list_name} should be a string. You have: {type(list_5d[0])}")
        if type(list_5d[1]) != int:
            raise ValueError(f"2nd entry of {list_name} should be an integer. You have: {type(list_5d[1])}")
        if type(list_5d[2]) != int:
            raise ValueError(f"3rd entry of {list_name} should be an integer. You have: {type(list_5d[2])}")

    def check_if_move_possible(self, pos, kind):
        """
        Checks if movement to specified position is possible

        Args:
            pos (list): 3-list of target space
            kind (str): wether the piece we're moving is light or dark

        Returns:
            int: 
                0 if impossible
                1 if possible with eating a piece
                2 if possible without eating a piece
        """
        assert kind in ["l", "d"], f"A piece can only be light or dark, you have provided {kind}"
        if pos[0] == "a0": # Cannot move outside of the board
            return 0
        target_piece = self.get_piece(pos)
        if target_piece == "NaN": # Cannot move onto a board that doesn't exist
            return 0
        elif target_piece == "": # Can move through empty spaces
            return 2
        _, target_color = list(target_piece)
        if target_color == kind: # Cannot eat own pieces
            return 0
        else: # Can eat enemy pieces
            return 1

    def get_list_of_possible_moves(self, pos, force_single_moves=False):
        """
        Finds possible moves for a piece on the predefined square
        and returns a Chessboard_5D object containing that info

        Args:
            pos (list): 3-list of target space
            force_single_moves (bool): whether to force single-space moves for pieces 
                that move >1 square in a line (i.e. rook)

        Returns:
            list of all possible moves
        """
        possible_moves = self.moves.get_all_movable_spaces(self.check_if_move_possible, 
                                                           self.get_piece(pos), pos, 
                                                           log=self.log, 
                                                           force_single_moves=force_single_moves)
        return possible_moves

    def get_board_of_possible_moves(self, pos, force_single_moves=False):
        """
        Finds possible moves for a piece on the predefined square
        and returns a Chessboard_5D object containing that info

        Args:
            pos (list): 3-list of target space
            force_single_moves (bool): whether to force single-space moves for pieces 

        Returns:
            Chessboard_5D: a 5D chessboard object, containing possible moves
        """
        piece = self.get_piece(pos)
        _, piece_color = list(piece)
        piece_to_add = "M" + piece_color
        possible_moves = self.get_list_of_possible_moves(pos, force_single_moves)
        self_copy = copy.deepcopy(self)
        for move in possible_moves:
            if log: print(f"Looking at move {move}...")
            self_copy.add_piece(piece_to_add, move, eat_pieces=True)
        return self_copy


class ChessTests():
    """Various tests for 2D/5D chessboard"""
    def __init__(self):
        self.chess2 = Chessboard_2D()
        self.chess2utils = ChessUtils_2D()
        self.chess5 = Chessboard_5D()
        self.moves = Moves()

    def pawn_jumping_multiverse(self):
        """
        Test with standard bord, that is supposed to check if the time evolution 
        and multiverse creation work properly
        """
        self.chess5.default_chess_configuration_setup()
        self.chess5.movie_piece(['e2', 0, 0], ['e4', 0, 0])
        self.chess5.movie_piece(['e7', 1, 0], ['e5', 0, 0])
        self.chess5.print_chessboard([0,0])
        self.chess5.print_chessboard([1,0])
        self.chess5.print_chessboard([2,0])
        self.chess5.print_chessboard([1,-1])
        self.chess5.print_chessboard([1,1])
        exit(0)
    
    def test_movement(self, piece, pawns_row=False, log=False):
        """
        Create empty boards and see if the piece is moving properly.
        Has an option to add a pawn row to check if eating pieces works.
        """
        n = 1 # How many chessboards to add in positive direction - total is 2n+1
        pos = ['d5', 2*n, 0] # position of the piece
        pawns_row_chessboard = [ pos[1], pos[2] ]
        pawns_row_square = pos[0]
        pawns_row_increment = 1
        for i in range(-n, n+1):
            for j in range(2*n+1):
                self.chess5.add_empty_chessboard([j,i])
                print([j,i])
        self.chess5.add_piece(piece, pos)
        _, piece_color = list(piece)
        if pawns_row:
            pawn = self.chess2utils.light_to_dark_piece("p" + piece_color)
            if piece_color == 'd':
                pawns_row_increment = -pawns_row_increment
            row_loc = self.chess2utils.chessform_to_matrix(pawns_row_square)
            row_id = row_loc[0] + pawns_row_increment + 1
            target_id = self.chess5.get_chessboard_by_tm(pawns_row_chessboard)
            print(pawns_row_chessboard)
            target_chessboard = self.chess5.chessboards[target_id]
            target_chessboard.create_row_of_pieces(row_id, pawn)
        self.moves_board = self.chess5.get_board_of_possible_moves(pos)
        for t in range(0, 2*n + 1):
            self.moves_board.print_chessboard([t, -1])
            self.moves_board.print_chessboard([t, 0])
            self.moves_board.print_chessboard([t, 1])

    def chessboard2d(self):
        """
        Tests if the default chess setup works for 2D chessboard
        """
        self.chess2.default_chess_configuration_setup()
        self.chess2.print_chessboard()


if __name__ == "__main__":
    tests = ChessTests()
    log = False
    tests.test_movement('pd', pawns_row=True, log=log)

