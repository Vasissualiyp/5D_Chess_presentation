from manim import *
import numpy as np
from chess_db_2d import Chessboard_2D, ChessUtils_2D
from chess_db_5d import Chessboard_5D

config.pixel_width = 480
config.pixel_height = 360
config.frame_rate = 5

class ChessboardColors():
    """Colors of chessboard"""
    def __init__(self, square_light=LIGHTER_GREY, square_dark=GREY, 
                 piece_light=WHITE, piece_dark=BLACK, 
                 move_light=GREEN_B, move_dark=GREEN_E):
        """Creates an instance of the class with all colors assigned"""
        self.square_light = square_light
        self.square_dark = square_dark
        self.piece_light = piece_light
        self.piece_dark = piece_dark
        self.move_light = move_light
        self.move_dark = move_dark

class Manim_Chessboard_2D(VGroup):
    def __init__(self, tm_loc=[0,0], square_size=0.5, 
                 board_separation=6, colors=None, 
                 chessboard=None,
                 board_size=8, animation_speed=0.5, 
                 log=False, **kwargs):
        """
        A single 2D chessboard instance
        Args:
            tm_loc (array): a location of chessboard in time-multiverse coordinates
            square_size (float): size of individual squares
            board_separation (float): distance between the centers of the boards in 5D
            colors (array): colors of the chessboard
            board_size (int): number of squares per board dimension
            animation_speed (float): speed of each animation in sec
        """
        super().__init__(**kwargs)
        #tm_loc[0]-=1

        image = ImageMobject("/home/vasilii/research/anim/5DChess/resources/Chess_bdt60.png")
        #self.add(image)
        image.scale(1)
        #image.rotate(PI/4, axis=UP)
        if colors == None:
            chesscolors = ChessboardColors()
        else:
            chesscolors = colors
        self.board_colors = [ chesscolors.square_dark, chesscolors.square_light ]

        self.squares = []
        self.orientation = 0 # 0 for regular, 1 for time-normal, 2 for multiverse-normal
        self.mlight = chesscolors.piece_light
        self.mdark = chesscolors.piece_dark
        self.board_size = board_size
        self.square_size = square_size
        self.prism_height = 0.1
        self.animation_speed = animation_speed
        self.board_separation = board_separation
        self.board_loc=np.array([tm_loc[0]*board_separation, tm_loc[1]*board_separation, 0])
        if chessboard==None:
            self.chessboard = Chessboard_2D(chessboard_tm_pos=tm_loc, n=board_size)
        else:
            self.chessboard = chessboard
        self.chessutils = ChessUtils_2D()
        self.empty_squares = [ "", " ", "  ", "Ml", "Md" ]
        self.log = log
        self.col_major_matrix = 1

        self.create_prism_board()
        #for row in range(board_size):
        #    row_squares = []
        #    for col in range(board_size):
        #        color_index = (row + col) % 2
        #        square = Square(side_length=square_size, fill_color=colors[color_index], 
        #                        fill_opacity=1)
        #        # Position each square:
        #        square_pos_x = (col - board_size/2 + 0.5) * square_size
        #        square_pos_y = (board_size/2 - row - 0.5) * square_size
        #        square_pos = np.array([
        #            square_pos_x,
        #            square_pos_y,
        #            0
        #        ])
        #        square.set_z_index(0)
        #        square.move_to(square_pos)
        #        row_squares.append(square)
        #        self.add(square)
        #    self.squares.append(row_squares)

        #self.shift(self.board_loc) # Move the board to its expected location
        # Now call the separate method to add spheres
        self.spheres = []  # Keep track of all spheres if you want to animate them later

    def create_prism_board(self):
        """
        Creates a square chessboard from rectangular prisms
        """
        n = self.board_size
        # An array of positions of each chess grid square, 
        # i.e. [0,2,1] gives y component of a3 square
        self.square_pos = np.zeros([n, n, 3])
        self.board_tiles = []
        for row in range(n):
            for col in range(n):
                idx_1, idx_2 = self.get_matrix_indecies(row, col)
                # Choose color by alternating
                color_index = (idx_1 + idx_2) % 2
                fill_color = self.board_colors[color_index]

                # Create a Prism from that square
                # direction=OUT means it extrudes "up" (in +z) from the base
                square_prism = Prism(
                    dimensions=(self.square_size, self.square_size, self.prism_height),
                )
                square_prism.set_fill(fill_color, opacity=1)
                square_prism.set_stroke(width=0)

                # By default, a Square lies in the XY plane at z=0,
                # so the Prism is extruded upward (in z).
                # We just need to shift it into position:
                # Let's treat the "board" as lying in the XY plane, so
                # idx_1 -> y dimension (increasing upwards),
                # idx_2 -> x dimension (increasing to the right).
                x = (idx_1 - n/2 + 0.5) * self.square_size + self.board_loc[0]
                y = (idx_2 - n/2 + 0.5) * self.square_size + self.board_loc[1]
                # The bottom of the prism will be at z=0, top at z=prism_height
                position_vec = np.array([x, y, 0])
                square_prism.move_to(position_vec)
                self.square_pos[idx_1, idx_2, :] = position_vec

                self.board_tiles.append(square_prism)
        self.add(*self.board_tiles)

    def recolor_board(self, color_rule=None):
        """
        Recolors every square prism on the board.

        Args:
            color_rule: A callable that takes (row, col) or (idx_1, idx_2)
                        and returns a valid Manim color. If None, just invert
                        the black/white pattern, for example.
        """
        n = self.board_size

        # If no custom color rule is provided, here's a simple default that flips black/white:
        # (Just an example; you can define your own logic.)
        if color_rule is None:
            def color_rule(idx_1, idx_2):
                return self.board_colors[(idx_1 + idx_2) % 2]

        for row in range(n):
            for col in range(n):
                # Convert (row, col) into the same indexing you used to place the squares
                idx_1, idx_2 = self.get_matrix_indecies(row, col)

                # figure out which tile from your board_tiles list corresponds to (idx_1, idx_2)
                tile_index = row * n + col  # or row * n + col, if that’s how you appended them
                prism_tile = self.board_tiles[tile_index]

                # Apply the rule
                new_color = color_rule(idx_1, idx_2)
                prism_tile.set_fill(new_color, opacity=1)

    def get_object_color_from_piece(self, piece, 
                                    dark_color=None, 
                                    light_color=None):
        """Gets a manim color based on the piece color"""
        _, piece_color = list(piece)
        if dark_color==None:
            dark_color = self.mdark
        if light_color==None:
            light_color = self.mlight
        if piece_color == 'l':
            return light_color
        elif piece_color == 'd':
            return dark_color
        else:
            raise ValueError(f"Not allowed color: {piece_color}. Allowed vaues: l, d.")

    def add_spheres_to_squares(self, radius=0.2):
        """Add spheres to the center of each square with a piece."""
        epsilon = 0.01 # A small value to displace the sphere
        id = 0
        n = self.board_size
        # Matrix that gets ID of a sphere from its position on the board
        self.sphere_ids = np.zeros((n,n), dtype=int) 

        # If we're using column-majaor matrix:
        for row_idx in range(n):
            for col_idx in range(n):
                idx_1, idx_2 = self.get_matrix_indecies(row_idx, col_idx)
                chessform_pos = self.chessutils.matrix_to_chessform([idx_1, idx_2])
                self.sphere_ids[idx_1, idx_2] = -1
                if self.log: print(f"Checking piece at location {chessform_pos}...")
                piece = self.chessboard.get_piece(chessform_pos)
                if self.log: print(f"piece is: {piece}")
                if piece in [ "", "a0" ]:
                    if self.log: print(f"Not adding sphere at {chessform_pos}")
                elif (piece not in ["Ml", "Md"]):
                    square_center = self.square_pos[idx_1, idx_2, :]
                    if self.log: print(f"Adding {piece} at {chessform_pos}")
                    sphere = Sphere(radius=radius)
                    # Position the sphere at the same center as the square
                    sphere_center = square_center
                    sphere_center[2] = radius + epsilon
                    sphere.move_to(sphere_center)
                    sphere_color = self.get_object_color_from_piece(piece)
                    sphere.set_color(sphere_color)
                    sphere.set_z_index(1)
                    self.spheres.append(sphere)
                    self.sphere_ids[idx_1, idx_2] = id
                    if self.log: print(f"Sphere IDs array:")
                    if self.log: print(self.sphere_ids.T)
                    id += 1
                    self.add(sphere)

    def rotate_board(self, angle, axis=np.array([0,0,1])):
        """
        Rotates the entire board by a specified angle around a given axis in 3D.
        Args:
            angle (float): The angle to rotate in radians.
            axis (array): The axis of rotation (default is the Z-axis).
        """
        self.rotate(angle, axis=axis, about_point=self.board_loc)

    def get_matrix_indecies(self, row_idx, col_idx):
        """
        Returns potentially reordered matrix indecies based on whether the order is
        row or column-major.
        """
        if self.col_major_matrix:
            return col_idx, row_idx
        else: # Row-major
            return row_idx, col_idx

    def calculate_rotation_vector(self, o1, o2):
        """
        Calculates the axis and angle of rotation from orientation o1 to orientation o2

        Args:
            o1, o2 (int): orientation before/after reorientation:
                0 - regular
                1 - time-normal
                2 - multiverse-normal

        Returns:
            axis (np.array): axis of rotation
            angle (float): angle of rotation
        """
        x_axis=np.array([1.0,0.0,0.0])
        y_axis=np.array([0.0,1.0,0.0])
        z_axis=np.array([0.0,0.0,1.0])
        # Angles below are for combined double-rotation
        axis_sum = 1 / np.sqrt(3)
        angle_sum = 2 * np.pi / 3
        axis_triag = np.array([ axis_sum, axis_sum, axis_sum ])
        if o1==o2: 
            axis = x_axis
            angle = 0.0
        elif o1==0:
            if o2==1:
                axis = axis_triag
                angle = angle_sum
            elif o2==2:
                axis = x_axis
                angle = np.pi / 2
            else:
                raise ValueError(f"Cannot have o2 value of {o2}. Only 1,2 values are allowed.")
        elif o1==1:
            if o2==0:
                axis = axis_triag
                angle = -angle_sum
            elif o2==2:
                axis = z_axis
                angle = -np.pi / 2
            else:
                raise ValueError(f"Cannot have o2 value of {o2}. Only 0,2 values are allowed.")
        elif o1==2:
            if o2==0:
                axis = x_axis
                angle = -np.pi / 2
            elif o2==1:
                axis = z_axis
                angle = np.pi / 2
            else:
                raise ValueError(f"Cannot have o2 value of {o2}. Only 0,1 values are allowed.")
        else:
            raise ValueError(f"Cannot have o1 value of {o1}. Only 0,1,2 values are allowed.")
        return axis, angle

    def reorient_board(self, final_orientation):
        """
        Reorient the board to regular, multiverse-normal, or time-normal view.
    
        Args:
            final_orientation (int): final orientation after reorientation:
                0 - regular
                1 - time-normal
                2 - multiverse-normal
    
        Returns:
            Rotate: A Manim Rotate animation object
        """
        axis, angle = self.calculate_rotation_vector(self.orientation, final_orientation)
        self.orientation = final_orientation
        return Rotate(
            self, 
            angle=angle, 
            axis=axis, 
            about_point=list(self.board_loc),  # can be np.array or list
            run_time=self.animation_speed
        )

    def get_piece(self, square):
        """
        Obtains parameters for the piece at a given square (in chess notation)

        Args:
            square (str): location of the square in chess notation
        
        Returns:
            piece (str): the name of the piece
            sphere (Manim): Manim object, on which one can perform transformations.
                            If piece=="", it returns None.
        """
        square_matrix = self.chessutils.chessform_to_matrix(square)
        if self.log: print(f"Matrix notation for square {square}: {square_matrix}")
        id = int(self.sphere_ids[square_matrix[0], square_matrix[1]])
        sphere = self.spheres[id]
        piece = self.chessboard.get_piece(square, self.log)
        if id == -1:
            print(f"No piece present at {square}")
            return "", None
        return piece, sphere

    def get_sphere_id(self, square):
        """
        Obtains id of the sphere located in square (chess notation)
        in the self.spheres list. If not present, returns -1.
        """
        square_matrix = self.chessutils.chessform_to_matrix(square)
        idx_1, idx_2 = self.get_matrix_indecies(square_matrix[1], square_matrix[0])
        id = self.sphere_ids[idx_1, idx_2]
        return id

    def move_piece(self, square_start, square_finish, eat_pieces=False, scene=None):
        """
        Moves a piece form start square to finish square (in chess notation).
        Pass scene to trigger animation.
        """

        start_matrix = np.array(self.chessutils.chessform_to_matrix(square_start))
        finish_matrix = np.array(self.chessutils.chessform_to_matrix(square_finish))
        start_matrix = np.array([start_matrix[1], start_matrix[0]])
        finish_matrix = np.array([finish_matrix[1], finish_matrix[0]])
        if self.log: self.chessboard.print_chessboard()
        piece, sphere = self.get_piece(square_start)
        if piece in self.empty_squares:
            raise ValueError(f"No piece found at square {square_start}")
        delta_matrix = finish_matrix - start_matrix
        forward, right, normal = self.get_board_directions()
        delta_vector = delta_matrix[0] * forward + delta_matrix[1] * right
        piece_f, sphere_f = self.get_piece(square_finish)
        remove_flag = False
        if piece_f not in self.empty_squares:
            if not eat_pieces:
                raise ValueError(f"Cannot move into {square_finish}: {piece_f} is present there. Try moving with eat_pieces=True.")
            else:
                _, piece_color = list(piece)
                _, piece_color_f = list(piece_f)
                if piece_color_f == piece_color:
                    raise ValueError(f"Cannot eat own piece at {square_finish}")
                else:
                    remove_flag = True
        assert sphere != None, "This part of the code wasn't supposed to be reached if sphere==None"
        if scene==None:
            sphere.shift(delta_vector)
        else:
            scene.play(ApplyMethod(sphere.shift, delta_vector),run_time=self.animation_speed)
        if remove_flag: self.remove_piece(square_finish)
        self.chessboard.move_piece(square_start, square_finish, eat_pieces=eat_pieces)
        if self.log: print(f"Sphere IDs array:")
        if self.log: print(self.sphere_ids.T)
        initial_id = self.sphere_ids[start_matrix[1], start_matrix[0]]
        self.sphere_ids[start_matrix[1], start_matrix[0]] = -1
        self.sphere_ids[finish_matrix[1], finish_matrix[0]] = initial_id

    def remove_piece(self, square, scene=None):
        """
        Remove the piece and its sphere at the given square.

        Args:
            square (str): The chess notation (e.g., 'a2', 'e4', etc.) of the piece to remove.
            scene (Scene): If provided, animate the removal in this scene. Otherwise, remove instantly.
        """
        # 1) Lookup piece & sphere
        piece, sphere = self.get_piece(square)
        if piece == "" or sphere is None:
            print(f"No piece to remove at {square}")
            return

        # 2) Animate removing the sphere if a scene is provided
        if scene is not None:
            scene.play(FadeOut(sphere), run_time=self.animation_speed)
        # If you don't want a fade-out animation, you could do:
        # scene.play(sphere.animate.scale(0.0).fade(1.0), ...)
        # or any other creative effect.

        # 3) Remove sphere from the scene or group 
        #    (e.g., if your board is a VGroup, you might do self.remove(sphere) as well)
        if sphere in self.submobjects:
            self.remove(sphere)

        # 4) Remove the sphere from the self.spheres list
        #    First we need the index (id)
        square_matrix = self.chessutils.chessform_to_matrix(square)
        removed_id = int(self.sphere_ids[square_matrix[0], square_matrix[1]])

        # Make sure we found a valid id
        if removed_id == -1:
            print(f"Something is off; sphere_ids already shows no piece at {square}.")
            return

        # Actually pop the sphere out of the self.spheres list
        removed_sphere = self.spheres.pop(removed_id)

        # Confirm we removed the correct object
        assert removed_sphere == sphere, "Mismatch between popped sphere and the expected sphere."

        # 5) Mark this square as empty
        self.sphere_ids[square_matrix[0], square_matrix[1]] = -1

        # 6) Decrement all sphere IDs greater than removed_id
        #    Because the list is now shorter, those IDs must shift by -1
        #    so that they still point to the correct sphere object.
        mask = self.sphere_ids > removed_id
        self.sphere_ids[mask] -= 1

    def get_board_directions(self):
        """
        Returns directional vectors based on current orientation

        Returns:
            forward (np.array): forward unit vector (i.e. a1->a2)
            right (np.array): right unit vector (i.e. a1->b1)
            normal (np.array): unnit vector, normal to the board
        """
        side = self.square_size # sidelength of square
        time_sep = self.board_separation
        if self.orientation == 0:
            forward = np.array([0, side, 0])
            right = np.array([side, 0, 0])
            normal = np.array([0, 0, time_sep])
        elif self.orientation == 1:
            forward = np.array([0, 0, side])
            right = np.array([0, side, 0])
            normal = np.array([-time_sep, 0, 0])
        elif self.orientation == 2:
            forward = np.array([0, 0, side])
            right = np.array([side, 0, 0])
            normal = np.array([0, -time_sep, 0])
        else:
            raise ValueError(f"Unknown orientation: {self.orientation}")
        return forward, right, normal

class Manim_Chessboard_5D(VGroup):
    def __init__(self, square_size=0.5, 
                 board_separation=6, colors=None, 
                 board_size=8, animation_speed=0.5, 
                 log=False, **kwargs):
        """
        A 5D chessboard instance
        Args:
            tm_loc (array): a location of chessboard in time-multiverse coordinates
            square_size (float): size of individual squares
            board_separation (float): distance between the centers of the boards in 5D
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

    def add_chessboard(self, chessboard_loc, origin_board):
        pass
    def get_piece(self, pos):
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

        log = False
        board_5d = Manim_Chessboard_5D(log=log)
        board_5d.default_chess_configuration_setup()
        board1 = board_5d.manim_chessboards[0]
        board_5d.add_empty_chessboard([1,0])
        #board1 = Manim_Chessboard_2D(tm_loc=[0,0], log=log)
        #board1.chessboard.default_chess_configuration_setup()
        #board1.add_spheres_to_squares(radius=0.1)
        #board3 = Manim_Chessboard_2D(tm_loc=[1,1])
        #board2.shift(3*RIGHT) # move it right
        
        self.add(board_5d)#, board2, board3)
        self.play(board_5d.reorient_all_boards(1))
        self.play(board_5d.reorient_all_boards(2))

        #self.play(board1.reorient_board(1))
        #self.play(board1.reorient_board(2))
        #self.play(board1.reorient_board(0))
        polar_angle = 0
        azimuthal_angle = 50
        self.set_camera_orientation(phi=azimuthal_angle*DEGREES,theta=(polar_angle-90)*DEGREES)
        self.begin_ambient_camera_rotation(rate=0.1)
        for move in sample_game_1:
            start_sq, end_sq = move
            board1.move_piece(start_sq, end_sq, scene=self, eat_pieces=True)
        self.wait()
