from manim import *
import numpy as np
from chess_db_2d import Chessboard_2D, ChessUtils_2D

config.pixel_width = 640
config.pixel_height = 480
config.frame_rate = 30

class Manim_Chessboard_2D(VGroup):
    def __init__(self, tm_loc=[0,0], square_size=0.5, 
                 board_separation=6, colors=[WHITE, GREY], board_size=8, 
                 animation_speed=0.5, **kwargs):
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


        self.squares = []
        self.orientation = 0 # 0 for regular, 1 for time-normal, 2 for multiverse-normal
        self.colors = colors
        self.board_size = board_size
        self.square_size = 0.5
        self.prism_height = 0.1
        self.animation_speed = animation_speed
        self.board_loc=np.array([tm_loc[0]*board_separation, tm_loc[1]*board_separation, 0])
        self.chessboard = Chessboard_2D(chessboard_tm_pos=tm_loc, n=board_size)
        self.chessutils = ChessUtils_2D()

        self.board_tiles = []
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
        for row in range(n):
            for col in range(n):
                # Choose color by alternating
                color_index = (row + col) % 2
                fill_color = self.colors[color_index]

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
                # row -> y dimension (increasing upwards),
                # col -> x dimension (increasing to the right).
                x = (col - n/2 + 0.5) * self.square_size
                y = (row - n/2 + 0.5) * self.square_size
                # The bottom of the prism will be at z=0, top at z=prism_height
                position_vec = np.array([x, y, 0])
                square_prism.move_to(position_vec)
                self.square_pos[row, col, :] = position_vec

                self.board_tiles.append(square_prism)
        self.add(*self.board_tiles)

    def add_spheres_to_squares(self, radius=0.2, log=False):
        """Add spheres to the center of each square."""
        epsilon = 0.05 # A small value to displace the sphere
        #if log: print(f"The array of tile cuboids has shape: {np.shape(self.square_pos)}")
        for row_idx in range(self.board_size):
            row_spheres = []
            for col_idx in range(self.board_size):
                chessform_pos = self.chessutils.matrix_to_chessform([col_idx, row_idx])
                if log: print(f"Checking piece at location {chessform_pos}...")
                piece = self.chessboard.get_piece(chessform_pos)
                if log: print(f"piece is: {piece}")
                if piece in [ "", "a0" ]:
                    if log: print(f"Not adding sphere at {chessform_pos}")
                    pass
                elif (piece not in ["Ml", "Md"]):
                    square_center = self.square_pos[row_idx, col_idx, :]
                    if log: print(f"Adding {piece} at {chessform_pos}")
                    sphere = Sphere(radius=radius)
                    # Position the sphere at the same center as the square
                    sphere_center = square_center
                    sphere_center[2] = 2 * radius + epsilon
                    sphere.move_to(sphere_center)
                    sphere.set_z_index(1)
                    row_spheres.append(sphere)
                    self.add(sphere)
            self.spheres.append(row_spheres)

    def rotate_board(self, angle, axis=np.array([0,0,1])):
        """
        Rotates the entire board by a specified angle around a given axis in 3D.
        Args:
            angle (float): The angle to rotate in radians.
            axis (array): The axis of rotation (default is the Z-axis).
        """
        self.rotate(angle, axis=axis, about_point=self.board_loc)

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
        if o1==o2: 
            axis = x_axis
            angle = 0.0
        elif o1==0:
            if o2==1:
                axis = np.array([ axis_sum, axis_sum, axis_sum ])
                angle = angle_sum
            elif o2==2:
                axis = x_axis
                angle = np.pi / 2
            else:
                raise ValueError(f"Cannot have o2 value of {o2}. Only 1,2 values are allowed.")
        elif o1==1:
            if o2==0:
                axis = np.array([ axis_sum, axis_sum, axis_sum ])
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
        axis, angle = self.calculate_rotation_vector(self.orientation, 
                                                     final_orientation)
        self.orientation = final_orientation
        return Rotate(self, angle=angle, axis=axis, 
                      about_point=list(self.board_loc), run_time=self.animation_speed)

class ChessPiece(Dot):
    def __init__(self, color=BLUE, **kwargs):
        super().__init__(color=color, **kwargs)
        self.current_row = None
        self.current_col = None

    def place_at(self, board, row, col):
        """
        board: Manim_Chessboard_2D instance
        row, col: Int
        """
        target_square = board.squares[row][col]
        self.move_to(target_square.get_center())
        self.current_row = row
        self.current_col = col

class MultipleChessBoards(ThreeDScene):
    def construct(self):
        # Create two chessboards

        board1 = Manim_Chessboard_2D(tm_loc=[0,0])
        board1.chessboard.default_chess_configuration_setup()
        board1.add_spheres_to_squares(radius=0.1, log=True)
        #board3 = Manim_Chessboard_2D(tm_loc=[1,1])
        #board2.shift(3*RIGHT) # move it right
        
        self.add(board1)#, board2, board3)

        # Create pieces
        #piece1 = ChessPiece(color=RED)
        #piece2 = ChessPiece(color=YELLOW)

        # Place pieces on board1
        #piece1.place_at(board1, 0, 0)
        #piece2.place_at(board2, 1, 1)
        #self.add(piece1, piece2)

        # Animate movement
        #self.play(piece1.animate.place_at(board1, 7, 7))  # Move piece1 to another square
        self.play(board1.reorient_board(1))
        self.play(board1.reorient_board(2))
        #self.play(board1.reorient_board(1))
        self.play(board1.reorient_board(0))
        #self.play(piece2.animate.shift(UP))               # Or any other standard Manim transform
        #self.play(piece2.animate.place_at(board2, 7, 7))  # Move piece1 to another square
        #self.play(piece2.animate.shift(UP))               # Or any other standard Manim transform
        self.wait()
