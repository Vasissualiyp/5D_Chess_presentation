from manim import *
from manim_slides import Slide, ThreeDSlide
from manim_5dboard import Manim_Chessboard_5D, sample_game_1
from moves import Moves

def intro_slide(self):
    title = Text("5D Chess with Multivere Time Travel\nBlack Board Talk").scale(0.8)
    author = Text("By Vasilii Pustovoit, CITA, 2025").scale(0.4)
    title.shift(0.5*UP)
    author.shift(0.5*DOWN)
    self.play(Write(title), run_time = 0.5)
    self.play(Write(author), run_time = 0.5)
    self.next_slide()
    self.play(FadeOut(title, shift=10*RIGHT), FadeOut(author, shift=10*RIGHT))

def AddMyAxes(self, origin, arrow_sizes):
    """
    Creates axes

    Args:
        self (Slide): Pass self to make sure that the stuff gets animated
        origin (array): coordinates of the origin of the axes
        arrow_sizes (array): sizes of the x and y vectors

    Returns:
        arrow_h, arrow_v: axis arrow objects
    """
    extension_fac = 0.1
    origin = np.array([origin[0], origin[1], 0])
    h_size = arrow_sizes[0]
    v_size = arrow_sizes[1]
    origin_h = np.array([- extension_fac * v_size, 0, 0])
    origin_v = np.array([0, - extension_fac * v_size, 0])
    arrow_h = Arrow(start=origin_h, end=[h_size, 0, 0]).shift(origin)
    arrow_v = Arrow(start=origin_v, end=[0, v_size, 0]).shift(origin)
    self.add(arrow_v, arrow_h)
    return arrow_h, arrow_v

def write_drs(self, piece):
    """
    Writes all dr vectors for a specific piece

    Args:
        self (Slide): Pass self to make sure that the stuff gets animated
        piece (str): piece acronym
    """
    animations_signless = [] # Array for animations for dr vectors with sign permutations
    animations_sign = [] # Array for animations for dr vectors without sign permutations
    animations_sign_ordered = [] # Array for animations for pure dr vectors
    drs_2d = []
    drs_2d_sign = []
    drs_2d_sign_ordered = []

    mv = Moves()
    drs_4d = mv.get_dr(piece[0])
    starting_pos = np.array([6.0, 4.0, 0])
    pos = starting_pos

    textsize = 0.6
    separation = 1.0 # Separation between the lines, in terms of textsize
    displacement_vec = np.array([0.0, - separation * textsize, 0.0])

    textpos1 = starting_pos - displacement_vec
    textpos1[0] = 5.0
    textpos2 = textpos1
    textpos2[0] = 5.0
    textpos3 = textpos1
    textpos3[0] = 2.0
    titletext1 = Text("Unit vectors").scale(textsize).shift(textpos1)
    titletext2 = Text("Sign-independent unit vectors").scale(textsize).shift(textpos2)
    titletext3 = Text("Sign- and permutation-independent unit vectors", color=RED
                      ).scale(textsize).shift(textpos3)

    for dr in drs_4d:
        x, y, _, _ = dr
        dr_2d = [x, y]
        if dr_2d not in drs_2d and dr_2d != [0, 0]:
            drs_2d.append(dr_2d)
            if x >=0 and y >=0:
                drs_2d_sign.append(dr_2d)
                if y <= x:
                    drs_2d_sign_ordered.append(dr_2d)

    for dr in drs_2d:
        print(f"Text: {dr}")
        text = Text(str(dr)).shift(pos).scale(textsize)
        text_red = Text(str(dr), color=RED).shift(pos).scale(textsize)
        empty_text = Text("").shift(pos).scale(textsize)
        text_anim = Write(text)
        pos += displacement_vec

        # Deal with 2nd transformation into the empty string
        if dr in drs_2d_sign:
            text2 = text
        else:
            text2 = empty_text

        if dr in drs_2d_sign_ordered:
            text3 = text_red
        else:
            text3 = empty_text

        text_anim_sign = Transform(text, text2)
        text_anim_sign_ordered = Transform(text2, text3)

        animations_signless.append(text_anim)
        animations_sign.append(text_anim_sign)
        animations_sign_ordered.append(text_anim_sign_ordered)

    animations_signless.append(Write(titletext1))
    animations_sign.append(Transform(titletext1, titletext2))
    animations_sign_ordered.append(Transform(titletext1, titletext3))

    self.play(*animations_signless, run_time = 0.5)
    self.next_slide()
    self.play(*animations_sign, run_time = 0.5)
    self.next_slide()
    self.play(*animations_sign_ordered, run_time = 0.5)



def show_piece_moves_slide(self, board_5d, piece, pos='d4', tm_loc=[0,0]):
    """
    Shows moves of a pice

    Args:
        self (ThreeDSlide): a scene where animation is happening
        board_5d (Manim_Chessboard_5D): a 5D board where to place the piece
        piece (str): piece acronym
        pos (str): position of the piece in chess notation
        tm_loc (list): position of host chessboard for the piece of interest
    """
    self.next_slide()
    board2d_id = board_5d.chess5.get_chessboard_by_tm(tm_loc)
    board2d = board_5d.manim_chessboards[board2d_id]
    board2d.recolor_board()
    board2d.remove_all_pieces()
    board2d.add_piece(piece, pos)
    board_5d.show_moves([pos,tm_loc[0],tm_loc[1]])


class Presentation1(ThreeDSlide):
    def construct(self):
        ###################
        ###### INTRO ######
        ###################
        #intro_slide(self)
        
        ######################
        ###### 2D MOVES ######
        ######################
        axes_origin = [-4.5, -4.5]
        axes_extensions = 9.5

        x_axis, y_axis = AddMyAxes(self, axes_origin, 
                                   [axes_extensions, axes_extensions])
        log = True
        board_5d = Manim_Chessboard_5D(scene=self, log=log)
        board_5d.default_chess_configuration_setup()
        board1 = board_5d.manim_chessboards[0]

        self.add(board_5d)#, board2, board3)

        show_piece_moves_slide(self, board_5d, 'rl')
        board_5d.draw_all_movement_vectors(['d4', 0, 0], False)
        self.next_slide()
        board_5d.remove_all_movement_vectors()
        board_5d.draw_all_movement_vectors(['d4', 0, 0], True)
        write_drs(self, 'rl')

        #for move in sample_game_1:
        #    start_sq, end_sq = move
        #    board1.move_piece(start_sq, end_sq, eat_pieces=True)
        #board_5d.show_moves(['g4',0,0])
        #board1.move_piece('b1', 'a3', eat_pieces=True)


