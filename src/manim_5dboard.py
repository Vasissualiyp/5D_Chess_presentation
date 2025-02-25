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
                 mode_3d=False,
                 log=False, **kwargs):
        """
        A 5D chessboard instance
        Args:
            square_size (float): size of individual squares
            board_separation (array): distance between the centers of the boards in 5D, 
                has time and multiverse components
            colors (array): colors of the chessboard
            board_size (int): number of squares per board dimension
            animation_speed (float): speed of each animation in sec
            scene (Scene): A scene in which the animations should be happening
            mode_3d (bool): whether the board is in 2D/4D mode (False) or 3D mode 
                for cube animations (True)
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
        self.mode_3d = mode_3d
        self.board_orientation = 0

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
                                                   non_const_color_parity=self.mode_3d,
                                                   animation_speed=self.animation_speed)
        board_creation_anims_list = manim_new_chessboard.creation_animations_list
        animations_list = manim_new_chessboard.add_spheres_to_squares(radius=self.sphere_radius)
        animations_list.extend(board_creation_anims_list)
        self.scene.play(animations_list)
        self.manim_chessboards.append(manim_new_chessboard)
        self.add(manim_new_chessboard)

    def add_empty_chessboard(self, chessboard_loc, no_anim=False):
        """
        Adds an empty chessboard in specified time-multiverse locaiton.
        Args:
            chessboard_loc (2-list): location of chessboard in time-multiverse coordinates
            no_anim (bool): set to True to only pass a list of animations, and not run animations automatically

        Returns:
            list: animations to perform with self.play(...) in Manim scene
        """
        self.chess5.add_empty_chessboard(chessboard_loc)
        target_chessboard = self.chess5.chessboards[-1]
        #if self.log: print(f"List of chessboards: {self.chess5.chessboards}")
        if self.log: print(f"Target_chessboard's location: {target_chessboard.chessboard_tm_pos}")
        manim_new_chessboard = Manim_Chessboard_2D(tm_loc=chessboard_loc, 
                                                   square_size=self.square_size, 
                                                   board_separation=self.board_separation, 
                                                   chessboard=target_chessboard, 
                                                   scene=self.scene,
                                                   non_const_color_parity=self.mode_3d,
                                                   animation_speed=self.animation_speed)
        self.manim_chessboards.append(manim_new_chessboard)
        animations_list = manim_new_chessboard.creation_animations_list
        if no_anim:
            return animations_list
        else:
            self.scene.play(animations_list)
            return []

        #self.add(manim_new_chessboard)

    def add_several_empty_chessboards(self, chessboard_locs):
        """
        Adds a set of empty chessboards at provided locations, all at the same time
        """
        animations_list = []
        for chessboard_loc in chessboard_locs:
            chessboard_anim = self.add_empty_chessboard(chessboard_loc, no_anim=True)
            animations_list.extend(chessboard_anim)
            print(animations_list)

        self.scene.play(*animations_list, run_time = self.animation_speed)

    def remove_all_boards(self):
        """
        Removes all boards from the scene
        """
        anims = []
        for chessboard in self.manim_chessboards:
            anims.extend(chessboard.delete_board())

        self.scene.play(*anims)

    # Change board/camera positions/rotations

    def reorient_all_boards(self, final_orientation):
        """
        Reorient all sub-boards to the specified orientation.
        
        Args:
            final_orientation (int): Target orientation (0, 1, or 2)
            
        Returns:
            AnimationGroup: Group of all rotation animations
        """
        # Convert final_orientation to int to ensure type consistency
        final_orientation = int(final_orientation)
        self.board_orientation = final_orientation
        
        # Collect animations from all chessboards
        animations = []
        for chessboard in self.manim_chessboards:
            try:
                anim = chessboard.reorient_board(final_orientation)
                animations.append(anim)
            except Exception as e:
                print(f"Error rotating chessboard: {e}")
                continue
        
        # Return empty AnimationGroup if no animations were created
        if not animations:
            return AnimationGroup()
            
        # Return the group of animations
        return AnimationGroup(*animations)

    def change_camera_center(self, camera_center, return_list=False):
        """
        Move all boards to new positions in 3D schene, based on camera center position

        Args:
            camera_center (array): a location of camera center in time-multiverse coordinates
            return_list (bool): whether to return a list of animations (true) or a group of animations (False)

        Returns:
            list: 
        """
        animations = []
        if self.log: print(f"CHANGING CAMERA CENTER: from {self.camera_center} to {camera_center}")
        for chessboard in self.manim_chessboards:
            if self.log: print(f"Recentering camera for chessboard at {chessboard.tm_loc}")
            anim = chessboard.change_camera_center(camera_center)
            # If we got a single animation, put it in a list
            if not isinstance(anim, list):
                anim = [anim]
            # Extend our animations list
            animations.extend(anim)
    
        # Animate them all together in parallel
        if return_list:
            return animations
        else:
            return AnimationGroup(*animations)

    def change_board_separation(self, board_separation):
        """
        Change the separation between boards in the 5D space
        
        Args:
            board_separation (list): New separation values
            
        Returns:
            AnimationGroup: A group of animations to be played
        """
        animations = []
        for chessboard in self.manim_chessboards:
            # Get the animation for each chessboard
            anim = chessboard.change_board_separation(board_separation)
            # If we got a single animation, put it in a list
            if not isinstance(anim, list):
                anim = [anim]
            # Extend our animations list
            animations.extend(anim)
        
        # Return all animations grouped together
        return AnimationGroup(*animations)

    def change_boards_opacity(self, new_opacity):
        """
        Changes the opacity values for all boards
        """
        animations = []
        for chessboard in self.chess5.chessboards:
            chessboard_loc = chessboard.chessboard_tm_pos
            if self.log: print(f"Location of chessboard: {chessboard_loc}")
            chessboard_id = self.chess5.get_chessboard_by_tm(chessboard_loc)
            assert chessboard_id != -1, f"Failed to retireve chessboard from {chessboard_loc}"
            manim_chessboard = self.manim_chessboards[chessboard_id]
            anims = manim_chessboard.change_board_opacity(new_opacity)
            animations.extend(anims)

        if self.scene is not None:
            self.scene.play(*animations, run_time = self.animation_speed)
        else:
            raise TypeError(f"Failed to change board opacity, when no scene is passed")

    def assemble_the_cube(self, new_opacity, orientation=2):
        """
        Assembles the cube in given orientation.
    
        Args:
            new_opacity (float): opacity of the boards
            orientation (int): orientation of the cube
                1 - time-normal
                2 - multiverse-normal
        """
        animations1 = []
        animations2 = []
    
        orientation = int(orientation)
        self.old_board_separation = self.board_separation
        self.old_board_orientation = self.board_orientation
    
        if orientation == 1:
            new_board_separation = [self.square_size, self.board_separation[1]]
        elif orientation == 2:
            new_board_separation = [self.board_separation[0], self.square_size]
        else:
            raise ValueError(f"Orientation value of {orientation} is not allowed!")
    
        self.scene.play(self.reorient_all_boards(orientation))
        self.scene.play(self.change_board_separation(new_board_separation))
    
        for chessboard in self.chess5.chessboards:
            chessboard_loc = chessboard.chessboard_tm_pos
            if self.log: print(f"Location of chessboard: {chessboard_loc}")
            chessboard_id = self.chess5.get_chessboard_by_tm(chessboard_loc)
            assert chessboard_id != -1, f"Failed to retrieve chessboard from {chessboard_loc}"
            manim_chessboard = self.manim_chessboards[chessboard_id]
            anims_opacity = manim_chessboard.change_board_opacity(new_opacity)
            anims_extrude = manim_chessboard.change_prism_height(self.square_size)
            animations1.extend(anims_extrude)
            animations2.extend(anims_opacity)
    
        self.scene.play(*animations1)
        self.scene.play(*animations2)

    def disassemble_the_cube(self, orientation=None):
        """
        Disassembles the cube, using previously saved values for orientation and separation
        Args:
            orientation (int): orientation in which to disassemble the cube.
                By default if nothing is set, it will default to orientation before 
                the cube was assembled
        """
        animations1 = []
        animations2 = []

        for chessboard in self.chess5.chessboards:
            chessboard_loc = chessboard.chessboard_tm_pos
            if self.log: print(f"Location of chessboard: {chessboard_loc}")
            chessboard_id = self.chess5.get_chessboard_by_tm(chessboard_loc)
            assert chessboard_id != -1, f"Failed to retrieve chessboard from {chessboard_loc}"
            manim_chessboard = self.manim_chessboards[chessboard_id]
            anims_opacity = manim_chessboard.change_board_opacity(1.0)
            anims_extrude = manim_chessboard.change_prism_height(manim_chessboard.prism_height)
            animations1.extend(anims_opacity)
            animations2.extend(anims_extrude)

        self.scene.play(*animations1)
        self.scene.play(*animations2)
        self.scene.play(self.change_board_separation(self.old_board_separation))
        if orientation == None:
            self.scene.play(self.reorient_all_boards(self.old_board_orientation))
        else:
            self.scene.play(self.reorient_all_boards(orientation))

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

        self.vec_arrows.clear()

    def show_moves(self, pos, special_moves_recolor="", recolor_scheme="color", force_single_moves=False):
        """
        Show moves of a piece, located at the provided position.
        Args:
            pos (list): 3-list of position of the target piece that "moves"
            special_moves_recolor (str): scheme of recoloring special moves. Vales:
                "" - no highlight, other than piece at pos
                "board" - the same board as piece at pos
                "piece_type_#" - piece of a type # (i.e. piece_type_r will highlight rook moves)
            recolor_scheme (str): scheme for recoloring. Values:
                color - change color only
                color-opacity - change color and opacity
            force_single_moves (bool): whether to show only 1st move
                (i.e. for queen, it will be king's moves)
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
            manim_chessboard.recolor_scheme = recolor_scheme

            # Highlight the position of the piece with a different color
            if chessboard_loc == [pos[1], pos[2]]:
                special_squares=[pos[0]]
            else:
                special_squares=[]

            manim_chessboard.recolor_board(manim_chessboard.recolor_from_list, 
                                           special_squares=special_squares)

    def recolor_all_boards(self):
        """
        Resets coloring for all boards
        """
        for chessboard in self.chess5.chessboards:
            chessboard_loc = chessboard.chessboard_tm_pos
            chessboard_id = self.chess5.get_chessboard_by_tm(chessboard_loc)
            assert chessboard_id != -1, f"Failed to retireve chessboard from {chessboard_loc}"
            manim_chessboard = self.manim_chessboards[chessboard_id]
            manim_chessboard.recolor_board()

    def set_animation_speed(self, animation_speed):
        """
        Sets animation speed
        """
        self.animation_speed = animation_speed
        for chessboard in self.manim_chessboards:
            chessboard.animation_speed = animation_speed

    # Moving pieces

    def copy_board(self, tm_loc, no_anim=False):
        """
        Creates a complete copy of the board at given time-multiverse location
        Args: 
            tm_loc (array): a location of chessboard in time-multiverse coordinates
            no_anim (bool): set to True to only pass a list of animations, and not run animations automatically
        """
        chessboard_id = self.chess5.get_chessboard_by_tm(tm_loc)
        if chessboard_id == -1:
            print(f"Failed to copy board at {chessboard_id}: board doesn't exist")
            exit(1)

        target_chessboard_db = self.chess5.chessboards[chessboard_id]

        #if self.log: print(f"List of chessboards: {self.chess5.chessboards}")
        manim_new_chessboard = Manim_Chessboard_2D(tm_loc=tm_loc, 
                                                   square_size=self.square_size, 
                                                   board_separation=self.board_separation, 
                                                   chessboard=target_chessboard_db, 
                                                   scene=self.scene,
                                                   non_const_color_parity=self.mode_3d,
                                                   appearance_anim = "FadeIn", # Need to not create visual artifacts
                                                   animation_speed=self.animation_speed)
        # Append to the list of manim boards
        self.manim_chessboards.append(manim_new_chessboard)
        #self.chess5.chessboards.append(manim_new_chessboard)

        # Get creation animations list and return it
        board_creation_anims_list = manim_new_chessboard.creation_animations_list
        animations_list = manim_new_chessboard.add_spheres_to_squares(radius=self.sphere_radius)
        animations_list.extend(board_creation_anims_list)
        manim_new_chessboard.appearance_anim = "Scale"
        if no_anim:
            return animations_list
        else:
            self.scene.play(animations_list)
            return []

    def evolve_copied_board(self, id_original, id_copy):
        """
        Evolves copied board, based on id of the original board and copy board
        """
        manim_original_board = self.manim_chessboards[id_original]
        manim_copy_board = self.manim_chessboards[id_copy]
        original_board = self.chess5.chessboards[id_original]
        copy_board = self.chess5.chessboards[id_copy]

        original_tm = original_board.chessboard_tm_pos
        copy_tm = copy_board.chessboard_tm_pos
        if original_tm != copy_tm:
            raise ValueError(f"tm-coordinates of copy board are not the same as original board!")

        # More to be done...

    def evolve_chessboard(self, tm_loc, no_anim=False):
        """
        Evolves chessboard at a certain tm_loc coordinate with animation
        """

        # This appends chessboard info to 5D chess db
        self.chess5.evolve_chessboard(tm_loc)
        id_of_destination_chessboard = len(self.chess5.chessboards) - 1

        # This appends chessboard info to manim_chessboards
        animations_list = self.copy_board(tm_loc, no_anim)
        chessboard_copy_db = self.chess5.chessboards[id_of_destination_chessboard]
        manim_chessboard_copy = self.manim_chessboards[id_of_destination_chessboard]
        destination_tm = chessboard_copy_db.chessboard_tm_pos
        manim_chessboard_copy.tm_loc = destination_tm
        animations_list.extend(self.change_camera_center(destination_tm, return_list=True))
        return AnimationGroup(*animations_list)


    def add_chessboard(self, chessboard_loc, origin_board):
        pass
    def add_piece(self, piece, pos, eat_pieces=False):
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
