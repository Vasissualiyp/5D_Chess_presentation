from manim import *
import numpy as np
from chess_db_2d import Chessboard_2D, ChessUtils_2D
from chess_db_5d import Chessboard_5D
from manim_2dboard import Manim_Chessboard_2D, ChessboardColors

config.pixel_width = 480
config.pixel_height = 360
config.frame_rate = 5

class Manim_Chessboard_5D(VGroup):
    def __init__(self, square_size=0.5, 
                 board_separation=[6, 6], colors=None, 
                 board_size=8, animation_speed=0.5, 
                 log=False, **kwargs):
        """
        A 5D chessboard instance
        Args:
            tm_loc (array): a location of chessboard in time-multiverse coordinates
            square_size (float): size of individual squares
            board_separation (array): distance between the centers of the boards in 5D, 
                has time and multiverse components
            colors (array): colors of the chessboard
            board_size (int): number of squares per board dimension
            animation_speed (float): speed of each animation in sec
        """
        super().__init__(**kwargs)

        self.manim_chessboards = []
        self.board_size = board_size
        self.board_separation = board_separation
        self.colors = colors
        self.animation_speed = animation_speed
        self.square_size = square_size
        self.sphere_radius = 0.1
        self.log = log
        self.camera_center = [0, 0]

        # 0 for 1st turn to white, 1 for 1st turn to black. Important for multiverse creation directions
        self.first_turn_black = 0

        self.chess2utils = ChessUtils_2D()
        self.chess5 = Chessboard_5D(chessboard_size=self.board_size,
                                    first_turn_black=self.first_turn_black,
                                    log=self.log)

    def default_chess_configuration_setup(self):
        """
        Sets up the default 8x8 chessboard.
        """
        self.chess5.default_chess_configuration_setup()
        target_chessboard = self.chess5.chessboards[0]
        manim_new_chessboard = Manim_Chessboard_2D(tm_loc=[0,0], 
                                                   square_size=self.square_size, 
                                                   board_separation=self.board_separation, 
                                                   chessboard=target_chessboard, 
                                                   animation_speed=self.animation_speed)
        manim_new_chessboard.add_spheres_to_squares(radius=self.sphere_radius)
        self.manim_chessboards.append(manim_new_chessboard)
        self.add(manim_new_chessboard)

    def add_empty_chessboard(self, chessboard_loc):
        """
        Adds an empty chessboard in specified time-multiverse locaiton
        """
        self.chess5.add_empty_chessboard(chessboard_loc)
        target_chessboard = self.chess5.chessboards[-1]
        if self.log: print(f"List of chessboards: {self.chess5.chessboards}")
        if self.log: print(f"Target_chessboard's location: {target_chessboard.chessboard_tm_pos}")
        manim_new_chessboard = Manim_Chessboard_2D(tm_loc=chessboard_loc, 
                                                   square_size=self.square_size, 
                                                   board_separation=self.board_separation, 
                                                   chessboard=target_chessboard, 
                                                   animation_speed=self.animation_speed)
        self.manim_chessboards.append(manim_new_chessboard)
        self.add(manim_new_chessboard)

    def reorient_all_boards(self, final_orientation):
        """
        Reorient all sub-boards to the specified orientation (0, 1, or 2).
        Returns an AnimationGroup that can be passed to scene.play(...).
        """
        animations = []
        for chessboard in self.manim_chessboards:
            anim = chessboard.reorient_board(int(final_orientation))
            animations.append(anim)
    
        # Animate them all together in parallel
        return AnimationGroup(*animations)

    def change_camera_center(self, camera_center):
        """
        Move all boards to new positions in 3D schene, based on camera center position

        Args:
            camera_center (array): a location of camera center in time-multiverse coordinates
        """
        animations = []
        for chessboard in self.manim_chessboards:
            anim = chessboard.change_camera_center(camera_center)
            animations.append(anim)
    
        # Animate them all together in parallel
        return AnimationGroup(*animations)

    def change_board_separation(self, board_separation):
        """
        Move all board to new positions in 3D schene, based on new board separation array

        Args:
            board_separation (array): distance between the centers of the boards in 5D, 
                has time and multiverse components
        """
        animations = []
        for chessboard in self.manim_chessboards:
            anim = chessboard.change_board_separation(board_separation)
            animations.append(anim)
    
        # Animate them all together in parallel
        return AnimationGroup(*animations)

    def show_moves(self, pos, scene=None):
        """
        Show moves of a piece, located at the provided position.
        Can also provide scene to animate the squares lighting up.
        """
        possible_moves = self.chess5.get_list_of_possible_moves(pos)
        if self.log: print(f"Possible moves: {possible_moves}")
        if self.log: print(f"Manim chessboards: {self.chess5.chessboards}")
        for chessboard in self.chess5.chessboards:
            chessboard_loc = chessboard.chessboard_tm_pos
            if self.log: print(f"Location of chessboard: {chessboard_loc}")
            filtered_moves = [ move[0] for move in possible_moves 
                              if move[1] == chessboard_loc[0] 
                              and move[2] == chessboard_loc[1] ]
            chessboard_id = self.chess5.get_chessboard_by_tm(chessboard_loc)
            assert chessboard_id != -1, f"Failed to retireve chessboard from {chessboard_loc}"
            manim_chessboard = self.manim_chessboards[chessboard_id]
            manim_chessboard.recolor_list = filtered_moves
            manim_chessboard.recolor_board(manim_chessboard.recolor_from_list,scene=scene)

    def add_chessboard(self, chessboard_loc, origin_board):
        pass
    def add_piece(self, piece, pos, eat_pieces=False):
        pass
    def evolve_chessboard(self, chessboard_loc):
        pass
    def movie_piece(self, original_pos, final_pos):
        pass
    def move_with_evolution(self, original_pos, square2):
        pass
    def move_with_evolution_2_boards(self, original_pos, final_pos):
        pass
    def move_with_evolution_remove_piece(self, original_pos):
        pass
    def move_with_evolution_add_piece(self, final_pos, piece):
        pass


class CameraSettings_5DChessBoard():
    """Moving and setting up the camera for 5D Chessboard"""
    def __init__(self, scene):
        """Creates camera with default view """
        pass


sample_game_1 = [
    ["e2", "e4"],  # White: Pawn moves e2 -> e4
    ["e7", "e5"],  # Black: Pawn moves e7 -> e5
    ["f2", "f4"],  # White: f2 -> f4 (the actual King's Gambit move)
    ["e5", "f4"],  # Black: exf4 (pawn takes)
    ["g1", "f3"],  # White: Knight to f3
    ["g7", "g5"],  # Black: Pawn to g5 (defending the extra pawn)
    ["h2", "h4"],  # White: Pawn to h4
    ["g5", "g4"],  # Black: Pawn pushes g4
    ["f3", "e5"],  # White: Knight to e5
]


class MultipleChessBoards(ThreeDScene):
    def construct(self):
        # Create two chessboards

        log = True
        board_5d = Manim_Chessboard_5D(log=log)
        board_5d.default_chess_configuration_setup()
        board1 = board_5d.manim_chessboards[0]
        board_5d.add_empty_chessboard([0,1])
        board_5d.add_empty_chessboard([0,-1])
        
        self.add(board_5d)#, board2, board3)
        board_5d.show_moves(['b1',0,0])
        self.play(board_5d.reorient_all_boards(1))
        self.play(board_5d.reorient_all_boards(2))
        self.play(board_5d.change_board_separation([3,3]))
        self.play(board_5d.change_camera_center([0,1]))

        polar_angle = 0
        azimuthal_angle = 50
        self.set_camera_orientation(phi=azimuthal_angle*DEGREES,theta=(polar_angle-90)*DEGREES)
        self.begin_ambient_camera_rotation(rate=0.1)
        for move in sample_game_1:
            start_sq, end_sq = move
            board1.move_piece(start_sq, end_sq, scene=self, eat_pieces=True)
        board_5d.show_moves(['e5',0,0])
        self.wait()
