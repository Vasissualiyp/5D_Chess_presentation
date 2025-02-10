from manim import *
from manim_slides import Slide, ThreeDSlide
from manim_5dboard import Manim_Chessboard_5D, sample_game_1

def IntroSlide(self):
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

class Presentation1(ThreeDSlide):
    def construct(self):
        ###################
        ###### INTRO ######
        ###################
        #IntroSlide(self)
        
        ######################
        ###### 2D MOVES ######
        ######################
        x_axis, y_axis = AddMyAxes(self, [-4.5, -4.5], [9.5, 9.5])
        log = True
        board_5d = Manim_Chessboard_5D(scene=self, log=log)
        board_5d.default_chess_configuration_setup()
        board1 = board_5d.manim_chessboards[0]

        self.add(board_5d)#, board2, board3)
        board_5d.show_moves(['b1',0,0])

        self.next_slide()
        for move in sample_game_1:
            start_sq, end_sq = move
            board1.move_piece(start_sq, end_sq, eat_pieces=True)
        board_5d.show_moves(['g4',0,0])
        board1.move_piece('b1', 'a3', eat_pieces=True)
        #IntroSlide(self)


