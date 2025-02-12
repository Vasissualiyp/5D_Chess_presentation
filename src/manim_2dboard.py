from manim import *
import numpy as np
from chess_db_2d import Chessboard_2D, ChessUtils_2D
from typing import Optional
from manim_slides import ThreeDSlide


class ChessboardColors():
    """Colors of chessboard"""
    def __init__(self, square_light=LIGHTER_GREY, square_dark=GREY, 
                 piece_light=WHITE, piece_dark=BLACK, 
                 move_light=GREEN_B, move_dark=GREEN_E,
                 chosen_piece=TEAL_C):
        """Creates an instance of the class with all colors assigned"""
        self.square_light = square_light
        self.square_dark = square_dark
        self.piece_light = piece_light
        self.piece_dark = piece_dark
        self.move_light = move_light
        self.move_dark = move_dark
        self.chosen_piece = chosen_piece


class Manim_Chessboard_2D(VGroup):
    def __init__(self, tm_loc=[0,0], square_size=1.0, 
                 board_separation=[6, 6], colors=None, 
                 chessboard=None,
                 board_size=8, animation_speed=0.5, 
                 camera_center=[0,0],
                 scene: Optional[ThreeDSlide] = None,
                 non_const_color_parity = False,
                 log=False, **kwargs):
        """
        A single 2D chessboard instance
        Args:
            tm_loc (array): a location of chessboard in time-multiverse coordinates
            square_size (float): size of individual squares
            board_separation (array): distance between the centers of the boards in 5D, 
                has time and multiverse components
            colors (array): colors of the chessboard
            chessboard (Chessboard_2D): a dataset, containing 2D chessboard class
            board_size (int): number of squares per board dimension
            camera_center (array): a location of camera center in time-multiverse coordinates
            scene (Scene): A scene in which the animations should be happening
            non_const_color_parity (bool): if set to True, will switch color parity based on tm_loc
            animation_speed (float): speed of each animation in sec
        """
        # Needed for animations?
        super().__init__(**kwargs)

        #image = ImageMobject("/home/vasilii/research/anim/5DChess/resources/Chess_bdt60.png")
        ##self.add(image)
        #image.scale(1)
        #image.rotate(PI/4, axis=UP)

        # Colors
        if colors == None:
            chesscolors = ChessboardColors()
        else:
            chesscolors = colors
        self.board_colors = [ chesscolors.square_dark, chesscolors.square_light ]
        self.board_colors_moves = [ chesscolors.move_dark, chesscolors.move_light ]
        self.mlight = chesscolors.piece_light
        self.mdark = chesscolors.piece_dark
        self.special_color = chesscolors.chosen_piece
        if non_const_color_parity:
            self.color_parity = ( tm_loc[0] + tm_loc[1] ) % 2
        else:
            self.color_parity = 0 # Whether the square colors are regular (0) or inverted (1)

        # Board geometry
        self.board_size = board_size
        self.square_size = square_size
        self.prism_height = 0.1
        self.orientation = 0 # 0 for regular, 1 for time-normal, 2 for multiverse-normal

        # Chessboard database and utils class
        if chessboard==None:
            self.chessboard = Chessboard_2D(chessboard_tm_pos=tm_loc, n=board_size)
        else:
            self.chessboard = chessboard
        self.chessutils = ChessUtils_2D()

        # Other parameters
        self.delta = 0.01 # A small value to displace the sphere
        self.empty_squares = [ "", " ", "  ", "Ml", "Md" ]
        self.log = log
        self.col_major_matrix = 1
        self.recolor_list = []

        # Animations and visuals
        self.scene = scene
        self.camera_center = camera_center
        self.animation_speed = animation_speed
        self.appearance_anim = "Scale" # Scale or FadeIn
        self.disappearance_anim = "Scale" # Scale or FadeOut
        self.recolor_animation_speed = self.animation_speed / 5
        self.board_opacity = 1

        # Board properties relative to other boards
        self.tm_loc = tm_loc
        self.board_separation = board_separation
        self.board_loc=self.get_updated_board_pos()
        self.board_z_index  = tm_loc[1] * 3
        self.arrows_z_index = self.board_z_index + 1
        self.pieces_z_index = self.board_z_index + 2

        self.create_prism_board()
        self.spheres = []  # Keep track of all spheres if you want to animate them later

    def create_prism_board(self):
        """
        Creates a square chessboard from rectangular prisms
        """
        appearance_anim = self.appearance_anim
        scene = self.scene
        n = self.board_size
        # An array of positions of each chess grid square, 
        # i.e. [0,2,1] gives y component of a3 square
        self.square_pos = np.zeros([n, n, 3])
        self.board_tiles = []
        for row in range(n):
            for col in range(n):
                idx_1, idx_2 = self.get_matrix_indecies(row, col)
                # Choose color by alternating
                color_index = (idx_1 + idx_2 + self.color_parity) % 2
                fill_color = self.board_colors[color_index]

                # Create a Prism from that square
                square_prism = Prism(
                    dimensions=(self.square_size, self.square_size, self.prism_height),
                )
                square_prism.set_fill(fill_color, opacity=self.board_opacity)
                square_prism.set_stroke(width=0)

                square = self.chessutils.matrix_to_chessform([idx_1, idx_2])
                position_vec = self.get_square_pos_in_3d(square)
                square_prism.move_to(position_vec)
                self.square_pos[idx_1, idx_2, :] = position_vec

                self.board_tiles.append(square_prism)
        if scene is None:
            self.add(*self.board_tiles)
        else:
            if appearance_anim == "FadeIn": scene.play(FadeIn(*self.board_tiles), run_time=self.animation_speed)
            elif appearance_anim == "Scale": self.blowup_anim(self.board_tiles)
            else: raise ValueError(f"Unknown appearance animation: {appearance_anim}")

    def change_prism_height(self, new_height):
        """
        Updates the height of all prisms on the chessboard and animates the change.
        """
        animations = []
        n = self.board_size
        
        for row in range(n):
            for col in range(n):
                idx_1, idx_2 = self.get_matrix_indecies(row, col)
                color_index = (idx_1 + idx_2 + self.color_parity) % 2
                fill_color = self.board_colors[color_index]

                tile_index = row * n + col
                old_prism = self.board_tiles[tile_index]
                
                # Instead of creating a new prism, modify the existing one
                new_dimensions = (self.square_size, self.square_size, new_height)
                axis, angle = self.calculate_rotation_vector(0, self.orientation)
                anim = old_prism.animate.become(
                    Prism(dimensions=new_dimensions)
                    .set_fill(fill_color, opacity=self.board_opacity)
                    .set_stroke(width=0)
                    .rotate(angle, axis=axis)
                    .move_to(old_prism.get_center())
                )
                animations.append(anim)
        
        return animations

    def delete_board(self):
        """
        Removes a square chessboard and pieces from it
        """
        appearance_anim = self.appearance_anim
        scene = self.scene
        self.remove_all_pieces()
        if scene is None:
            self.remove(*self.board_tiles)
        else:
            if appearance_anim == "FadeIn": scene.play(FadeOut(*self.board_tiles), run_time=self.animation_speed)
            elif appearance_anim == "Scale": self.collapse_anim(self.board_tiles)
            else: raise ValueError(f"Unknown appearance animation: {appearance_anim}")

        print(f"Keep in mind that the board for now is still present in memory, "+
              "even though it's not present in the scene!")

    # Board 3D scene manipulation: rotation

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
        board_group = Group(*self.board_tiles)
        return Rotate(
            board_group, 
            angle=angle, 
            axis=axis, 
            about_point=list(self.board_loc),  # can be np.array or list
            run_time=self.animation_speed
        )

    # Board 3D scene manipulation: translation

    def move_board_to_new_loc(self, new_loc):
        """
        Move board to new position in 3D schene

        Args:
            new_loc (array): a 3D array that gives new position
        Returns:
            self.animate: A Manim animation object
        """
        old_loc = self.board_loc
        self.board_loc = new_loc
        delta_loc = new_loc - old_loc
        if self.log: print(f"old_loc: {old_loc}")
        if self.log: print(f"new_loc: {new_loc}")
        board_group = Group(*self.board_tiles)
        return board_group.animate.shift(delta_loc)

    def change_camera_center(self, camera_center):
        """
        Move board to new position in 3D schene, based on camera center position

        Args:
            camera_center (array): a location of camera center in time-multiverse coordinates
        Returns:
            self.animate: A Manim animation object
        """
        self.camera_center = camera_center
        new_board_loc=self.get_updated_board_pos()
        return self.move_board_to_new_loc(new_board_loc)

    def change_board_separation(self, board_separation):
        """
        Move board to new position in 3D schene, based on new board separation array

        Args:
            board_separation (array): distance between the centers of the boards in 5D, 
                has time and multiverse components
        Returns:
            self.animate: A Manim animation object
        """
        if self.log: print(f"board_separation before reassignment: {self.board_separation}")
        self.board_separation = board_separation
        if self.log: print(f"board_separation after reassignment: {self.board_separation}")
        new_board_loc=self.get_updated_board_pos()
        return self.move_board_to_new_loc(new_board_loc)

    # Piece manimulation

    def move_piece(self, square_start, square_finish, eat_pieces=False):
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

        if remove_flag: move_speed = self.animation_speed/2
        else: move_speed = self.animation_speed

        if remove_flag: 
            self.remove_piece(square_finish)
        if self.scene==None:
            sphere.shift(delta_vector)
        else:
            self.scene.play(ApplyMethod(sphere.shift, delta_vector),run_time=move_speed)
        self.chessboard.move_piece(square_start, square_finish, eat_pieces=eat_pieces, log=self.log)
        if self.log: print(f"Sphere IDs array:")
        if self.log: print(self.sphere_ids.T)
        initial_id = self.sphere_ids[start_matrix[1], start_matrix[0]]
        self.sphere_ids[start_matrix[1], start_matrix[0]] = -1
        self.sphere_ids[finish_matrix[1], finish_matrix[0]] = initial_id

    def add_spheres_to_squares(self, radius=0.2):
        """Add spheres to the center of each square with a piece."""
        id = 0
        n = self.board_size
        self.pieces = [] # deepseek
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
                    if self.log: print(f"Adding {piece} at {chessform_pos}")
                    id = self.add_sphere_to_square(idx_1, idx_2, radius, piece, id)

        if self.scene is None:
            for sphere in self.spheres:
                self.add(sphere)
        else:
            self.blowup_anim(self.spheres)

    def add_sphere_to_square(self, idx_1, idx_2, radius, piece, id):
            """
            Adds a sphere or a piece svg to a specific square
    
            Args:
                idx_1 (int): 1st index of a square
                idx_2 (int): 2nd index of a square
                radius (float): radius of the sphere to be added
                piece (str): the name of the piece
                id (int): largest id
            """
            piece_mesh = "svg" # svg or sphere

            square_center = self.square_pos[idx_1, idx_2, :]
            sphere_center = square_center

            if piece_mesh == "sphere":
                sphere = Sphere(radius=radius)
                sphere_center_delta_mag = radius * self.delta
            elif piece_mesh == "svg":
                img_path_svg, img_scale = self.chessutils.get_piece_image(piece)
                sphere = SVGMobject(img_path_svg)
                sphere.set(width=self.square_size * 0.5 * img_scale)
                sphere_center_delta_mag = self.square_size * 0.1 + self.delta
            else:
                raise ValueError(f"Unknown piece_mesh: {piece_mesh}")

            # Displace the piece, normal to the board
            forward, right, normal = self.get_board_directions()
            sphere_center_delta_vec = [ sphere_center_delta_mag * n_i for n_i in normal]
            sphere_center += sphere_center_delta_vec

            sphere.move_to(sphere_center)
            sphere.set_z_index(self.pieces_z_index)
            if piece_mesh == "sphere":
                sphere_color = self.get_object_color_from_piece(piece)
                sphere.set_color(sphere_color)
            self.spheres.append(sphere)
            self.sphere_ids[idx_1, idx_2] = id
            if self.log: print(f"Sphere IDs array:")
            if self.log: print(self.sphere_ids.T)
            id += 1
            return id

    def add_piece(self, piece, pos, radius=0.2, eat_pieces=False):
        """
        Adds piece to square

        Args:
            piece (str): the name of the piece
            pos (str): position of the piece in chess notation
            radius (float): radius of the sphere to be added
            eat_pieces (bool): whether to throw an error when trying to move 
                onto another piece. Default: False.
        """
        self.chessboard.add_piece(piece, pos, eat_pieces=eat_pieces)
        idx_1, idx_2 = self.chessutils.chessform_to_matrix(pos)
        newpiece_id = np.max(self.sphere_ids) + 1
        id = self.add_sphere_to_square(idx_1, idx_2, radius, piece, newpiece_id)
        if self.log: print(f"Sphere ids: {self.sphere_ids}")
        self.blowup_anim(self.spheres[-1])

    def remove_piece(self, square, animation_speed=None):
        """
        Remove the piece and its sphere at the given square.

        Args:
            square (str): The chess notation (e.g., 'a2', 'e4', etc.) of the piece to remove.
            animation_speed (float): speed of each animation in sec. Set to 0 to not perform animation.
        """
        if animation_speed == None:
            animation_speed = self.animation_speed/2
        piece, sphere = self.get_piece(square)
        if piece == "" or sphere is None:
            if self.log: print(f"No piece to remove at {square}")
            return

        # 2) Animate removing the sphere if a scene is provided
        if self.scene is not None and animation_speed != 0:
            if self.disappearance_anim == "Scale":
                self.collapse_anim([sphere], anim_speed=animation_speed)
            elif self.disappearance_anim == "FadeIn":
                self.scene.play(FadeOut(sphere), run_time=animation_speed)
            else: raise ValueError(f"Unknown appearance animation: {self.disappearance_anim}")
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
        self.chessboard.remove_piece(square)

        # 6) Decrement all sphere IDs greater than removed_id
        mask = self.sphere_ids > removed_id
        self.sphere_ids[mask] -= 1

    def remove_all_pieces(self):
        """
        Removes all the pieces, empties the board
        """
        n = self.board_size
        spheres_to_remove = []
        piece_pos_to_remove = []
        for row_idx in range(n):
            for col_idx in range(n):
                idx_1, idx_2 = self.get_matrix_indecies(row_idx, col_idx)
                chessform_pos = self.chessutils.matrix_to_chessform([idx_1, idx_2])
                if self.log: print(f"Checking piece at location {chessform_pos}...")
                piece, sphere = self.get_piece(chessform_pos)
                if self.log: print(f"piece is: {piece}")
                if piece in [ "", "a0" ]:
                    if self.log: print(f"Nothing to do at {chessform_pos}")
                elif (piece not in ["Ml", "Md"]):
                    if self.log: print(f"Removing {piece} at {chessform_pos}")
                    spheres_to_remove.append(sphere)
                    piece_pos_to_remove.append(chessform_pos)

        self.collapse_anim(spheres_to_remove)
        for piece_pos in piece_pos_to_remove:
            self.remove_piece(piece_pos, animation_speed=0)

    # Obtaining data about objects

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

    def get_piece_image(self, square):
        """
        Obtains image for the piece at a given square (in chess notation)

        Args:
            square (str): location of the square in chess notation
        
        Returns:
            str: full path to the file of the piece
            float: scale factor for the piece image size 
        """
        piece_name = self.get_piece(square)
        return self.chessutils.get_piece_image(piece_name)

    def get_sphere_id(self, square):
        """
        Obtains id of the sphere located in square (chess notation)
        in the self.spheres list. If not present, returns -1.
        """
        square_matrix = self.chessutils.chessform_to_matrix(square)
        idx_1, idx_2 = self.get_matrix_indecies(square_matrix[1], square_matrix[0])
        id = self.sphere_ids[idx_1, idx_2]
        return id

    def get_matrix_indecies(self, row_idx, col_idx):
        """
        Returns potentially reordered matrix indecies based on whether the order is
        row or column-major.
        """
        if self.col_major_matrix:
            return col_idx, row_idx
        else: # Row-major
            return row_idx, col_idx

    # Coloring

    def recolor_from_list(self, idx_1, idx_2, special_squares=[]):
        """
        Determines which squares to recolor based on self.recolor_list values

        Args:
            idx_1 (int): 1st index of a square
            idx_2 (int): 2nd index of a square
            special_squares (list): special squares to color different color

        Returns:
            Manim_Color: a new color for the square
        """

        square = self.chessutils.matrix_to_chessform([idx_1, idx_2])
        if square in self.recolor_list:
            return self.board_colors_moves[(idx_1 + idx_2) % 2]
        elif square in special_squares:
            return self.special_color
        else:
            return self.board_colors[(idx_1 + idx_2 + self.color_parity) % 2]

    def recolor_board(self, color_rule=None, special_squares=[], return_anim=False):
        """
        Recolors every square prism on the board.

        Args:
            color_rule(idx_1, idx_2, special_squares) (function): 
                A callable that takes (row, col) or (idx_1, idx_2)
                and returns a valid Manim color. If None, just invert
                the black/white pattern, for example.
            special_squares (list): list of special squares to color different color
            retrun_anim (bool): if set to False (default), recolors the board 
                itself. If set to True, passes recoloring animation list

        Returns:
            list: list of animations, or empty list if coloring happened automatically
        """
        n = self.board_size
        animations = []

        # If no custom color rule is provided, here's a simple default that flips black/white:
        # (Just an example; you can define your own logic.)
        if color_rule is None:
            def color_rule(idx_1, idx_2, special_squares=[]):
                return self.board_colors[(idx_1 + idx_2 + self.color_parity) % 2]

        for row in range(n):
            for col in range(n):
                # Convert (row, col) into the same indexing you used to place the squares
                idx_1, idx_2 = self.get_matrix_indecies(row, col)

                # figure out which tile from your board_tiles list corresponds to (idx_1, idx_2)
                tile_index = row * n + col  # or row * n + col, if that’s how you appended them
                prism_tile = self.board_tiles[tile_index]

                # Apply the rule
                new_color = color_rule(idx_1, idx_2, special_squares=special_squares)
                if self.scene == None:
                    prism_tile.set_fill(new_color, opacity=self.board_opacity)
                else:
                    anim = prism_tile.animate.set_fill(new_color, opacity=self.board_opacity)
                    animations.append(anim)
        if self.scene is not None and animations and not return_anim:
            self.scene.play(*animations,run_time=self.recolor_animation_speed)
            return []
        elif return_anim:
            return animations
        else:
            print(f"Failed to recolor the board properly")
            return []

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

    def change_board_opacity(self, new_opacity):
        """
        Changes the board opacity to provided value, returns list of animations
        """
        self.board_opacity = new_opacity
        anims = self.recolor_board(return_anim=True)
        return anims


    # Animations

    def blowup_anim(self, targets_list, anim_speed=None):
        """
        Performs blow-up animation for Mojbects in list

        Args:
            targets_list (list): list of objects, targets for animation
            anim_speed (float): speed of each animation in sec
        """
        if anim_speed is None:
            anim_speed = self.animation_speed
        for tile in targets_list:
            tile.scale(0.01)
        if self.scene is not None:
            self.scene.play(FadeIn(*targets_list), run_time=0.1)
            self.scene.play(*(tile.animate.scale(100) for tile in targets_list),
                       run_time=anim_speed)
        else:
            raise TypeError(f"Cannot deploy animation for scene of type None")

    def collapse_anim(self, targets_list, anim_speed=None):
        """
        Performs inverse-blow-up animation for Mojbects in list

        Args:
            targets_list (list): list of objects, targets for animation
            anim_speed (float): speed of each animation in sec
        """
        if anim_speed is None:
            anim_speed = self.animation_speed
        if self.scene is not None:
            self.scene.play(*(tile.animate.scale(0.01) for tile in targets_list),
                       run_time=anim_speed)
            self.scene.play(FadeOut(*targets_list), run_time=0.1)
        else:
            raise TypeError(f"Cannot deploy animation for scene of type None")

    # Utility functions

    def get_board_directions(self, force_renorm=False):
        """
        Returns directional vectors based on current orientation

        Args:
            force_renorm (bool): whether to output a vector with the magnitude of 
                square size (False, default) or unit magnitude (True)

        Returns:
            forward (np.array): forward unit vector (i.e. a1->a2)
            right (np.array): right unit vector (i.e. a1->b1)
            normal (np.array): unit vector, normal to the board (|n|=1)
        """
        if force_renorm:
            side = 1
        else:
            side = self.square_size
        if self.orientation == 0:
            forward = np.array([0, side, 0])
            right = np.array([side, 0, 0])
            normal = np.array([0, 0, 1])
        elif self.orientation == 1:
            forward = np.array([0, 0, side])
            right = np.array([0, side, 0])
            normal = np.array([-1, 0, 0])
        elif self.orientation == 2:
            forward = np.array([0, 0, side])
            right = np.array([side, 0, 0])
            normal = np.array([0, -1, 0])
        else:
            raise ValueError(f"Unknown orientation: {self.orientation}")
        return forward, right, normal

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

    def get_updated_board_pos(self):
        """
        Obtain updated board location vector in the 3D scene

        Returns:
            array: new location vector
        """
        time_sep, mult_sep = self.board_separation
        if self.log: print(f"Updated t/m separation: {time_sep, mult_sep}")
        if self.log: print(f"tm_loc: {self.tm_loc}")
        if self.log: print(f"camera_center: {self.camera_center}")
        new_board_loc=np.array([(self.tm_loc[0] - self.camera_center[0])*time_sep, 
                                (self.tm_loc[1] - self.camera_center[1])*mult_sep, 0])
        if self.log: print(f"Updated board location: {new_board_loc}")
        return new_board_loc

    def get_square_pos_in_3d(self, square):
        """
        Gets np array of 3D coordinates for position of a given square for use in Manim
        """
        n = self.board_size
        board_center = self.board_loc
        forward, right, normal = self.get_board_directions(force_renorm=True)

        col, row = self.chessutils.chessform_to_matrix(square)
        idx_1, idx_2 = self.get_matrix_indecies(row, col)

        # x/y position from the center of the board
        x_from_c = (idx_1 - n/2 + 0.5) * self.square_size
        y_from_c = (idx_2 - n/2 + 0.5) * self.square_size

        # Displacement vector from the board center
        dx_vec = np.array([ x_from_c * i for i in right   ])
        dy_vec = np.array([ y_from_c * i for i in forward ])
        return self.board_loc + dx_vec + dy_vec

