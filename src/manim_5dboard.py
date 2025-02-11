from manim import *
import numpy as np
from chess_db_2d import Chessboard_2D, ChessUtils_2D
from chess_db_5d import Chessboard_5D
from manim_2dboard import Manim_Chessboard_2D, ChessboardColors
from manim_slides import ThreeDSlide

config.pixel_width = 480
config.pixel_height = 360
config.frame_rate = 24

class Manim_Chessboard_5D(VGroup):
    def __init__(self, square_size=1.0, 
                 board_separation=[6, 6], colors=None, 
                 board_size=8, animation_speed=0.5, 
                 scene=None,
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
            scene (Scene): A scene in which the animations should be happening
            log (bool): Whether to enable logging
        """
        super().__init__(**kwargs)

        self.manim_chessboards = []
        self.board_size = board_size
        self.board_separation = board_separation
        self.animation_speed = animation_speed
        self.square_size = square_size
        self.sphere_radius = 0.1
        self.log = log
        self.scene = scene
        self.camera_center = [0, 0]
        self.vec_arrows = []

        if colors is not None:
            self.colors = colors
        else:
            self.colors = ChessboardColors()

        # 0 for 1st turn to white, 1 for 1st turn to black. Important for multiverse creation directions
        self.first_turn_black = 0

        self.chess2utils = ChessUtils_2D()
        self.chess5 = Chessboard_5D(chessboard_size=self.board_size,
                                    first_turn_black=self.first_turn_black,
                                    log=self.log)

    # Adding chessboards 

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
                                                   scene=self.scene,
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
                                                   scene=self.scene,
                                                   animation_speed=self.animation_speed)
        self.manim_chessboards.append(manim_new_chessboard)
        self.add(manim_new_chessboard)

    # Change board/camera positions/rotations

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

    # Drawing vectors

    def draw_vector_between_positions(self, pos1, pos2):
        """
        Draws vector between 2 3-list positions

        Args:
            pos1 (list): position of the start of the vector
            pos2 (list): position of the end of the vector

        Returns:
            Arrow: Manim vector arrow object to plot
        """
        square1 = pos1[0]
        tm_loc1 = [ pos1[1], pos1[2] ]
        square2 = pos2[0]
        tm_loc2 = [ pos2[1], pos2[2] ]

        id1 = self.chess5.get_chessboard_by_tm(tm_loc1)
        id2 = self.chess5.get_chessboard_by_tm(tm_loc2)
        z_index = self.manim_chessboards[id1].arrows_z_index

        vec_start = self.manim_chessboards[id1].get_square_pos_in_3d(square1)
        vec_end   = self.manim_chessboards[id2].get_square_pos_in_3d(square2)

        vec_arrow = Arrow(start=vec_start, end=vec_end, buff=0, 
                          #stroke_width=5 * self.square_size,
                          max_stroke_width_to_length_ratio=5,
                          max_tip_length_to_length_ratio=0.15)
        vec_arrow.color = WHITE
        vec_arrow.set_z_index(z_index)
        return vec_arrow

    def draw_all_movement_vectors(self, pos, normals_only=False):
        """
        Draws all arrows of vectors of movement for a piece at a particular position

        Args:
            pos1 (list): position of the start of the vector
            normals_only (bool): whether to output a vector with the magnitude of 
                square size (False, default) or unit magnitude (True)
        """
        possible_moves = self.chess5.get_list_of_possible_moves(pos, normals_only)
        animations = []
        for move in possible_moves:
            vec_arrow = self.draw_vector_between_positions(pos, move)
            self.vec_arrows.append(vec_arrow)
            anim = FadeIn(vec_arrow, run_time = self.animation_speed)
            animations.append(anim)
        if self.scene is not None:
            self.scene.play(*animations)
        else:
            raise TypeError(f"Cannot play animation when scene is None")

    def remove_all_movement_vectors(self):
        """
        Removes all arrows of vectors of movement
        """
        animations = []
        for vec_arrow in self.vec_arrows:
            anim = FadeOut(vec_arrow, run_time = self.animation_speed)
            animations.append(anim)

        if self.scene is not None:
            self.scene.play(*animations)
            self.scene.remove(*self.vec_arrows)
        else:
            raise TypeError(f"Cannot play animation when scene is None")

    def show_moves(self, pos, force_single_moves=False):
        """
        Show moves of a piece, located at the provided position.
        """
        possible_moves = self.chess5.get_list_of_possible_moves(pos, force_single_moves)
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
            manim_chessboard.recolor_board(manim_chessboard.recolor_from_list, special_squares=[pos[0]])


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
    ["h2", "h4"],  # White: Pawn to h4
    ["g7", "g5"],  # Black: Pawn to g5 (defending the extra pawn)
    ["h1", "h3"],  # White: Rook to h3
    ["g5", "g4"],  # Black: Pawn pushes g4
    ["d1", "g4"],  # White: Queen to g4
    ["f4", "f3"],  # Black: Pawn pushes f3
]


class MultipleChessBoards(ThreeDSlide):
    def construct(self):
        # Create two chessboards

        log = True
        board_5d = Manim_Chessboard_5D(log=log)
        board_5d.default_chess_configuration_setup()
        board1 = board_5d.manim_chessboards[0]
        board_5d.add_empty_chessboard([0,1])
        board_5d.add_empty_chessboard([0,-1])
        self.next_slide()
        
        self.add(board_5d)#, board2, board3)
        board_5d.show_moves(['b1',0,0])
        self.play(board_5d.reorient_all_boards(1))
        self.next_slide()
        self.play(board_5d.reorient_all_boards(2))
        self.next_slide()
        self.play(board_5d.change_board_separation([3,3]))
        self.play(board_5d.change_camera_center([0,1]))

        polar_angle = 0
        azimuthal_angle = 50
        self.set_camera_orientation(phi=azimuthal_angle*DEGREES,theta=(polar_angle-90)*DEGREES)
        self.begin_ambient_camera_rotation(rate=0.1)
        for move in sample_game_1:
            start_sq, end_sq = move
            board1.move_piece(start_sq, end_sq, eat_pieces=True)
        board_5d.show_moves(['e5',0,0])
        self.wait()
