from manim import *
from manim.utils.color.XKCD import AQUABLUE
from manim_slides import Slide, ThreeDSlide
from manim_5dboard import Manim_Chessboard_5D, sample_game_1
from chess_db_2d import ChessUtils_2D
from moves import Moves

central_square = 'e4'
central_square_plus1 = 'f3'
central_square_3vec = [central_square, 0, 0]

# Slides

accent_color = TEAL
accent_color2 = BLACK
dict_3d_moveset = {
    "rl" : Tex("Rook: ", r"$[1,0,0]^\infty_\delta$").set_color(accent_color),
    "bl" : Tex("Bishop: ", r"$[1,1,0]^\infty_\delta$").set_color(accent_color),
    "ul" : Tex("Unicorn: ", r"$[1,1,1]^\infty_\delta$").set_color(accent_color),
    "nl" : Tex("Knight: ", r"$[1,2,0]^1_\delta$").set_color(accent_color),

    "ql" : Tex("Queen: ", r"$[1,0,0]^\infty_\delta$", 
                         r"$\cup$",
                         r"$[1,1,0]^\infty_\delta$", 
                         r"$\cup$", 
                         r"$[1,1,1]^\infty_\delta$").set_color(accent_color),

    "Pl" : Tex("Princess: ", r"$[1,0,0]^\infty_\delta$", 
                         r"$\cup$",
                         r"$[1,1,0]^\infty_\delta$").set_color(accent_color),

    "kl" : Tex("King: ", r"$[1,0,0]^1_\delta$", 
                         r"$\cup$",
                         r"$[1,1,0]^1_\delta$", 
                         r"$\cup$", 
                         r"$[1,1,1]^1_\delta$").set_color(accent_color),
}
dict_4d_moveset = {
    "rl" : Tex("Rook: ", r"$[1,0,0,0]^\infty_\delta$").set_color(accent_color2),
    "bl" : Tex("Bishop: ", r"$[1,1,0,0]^\infty_\delta$").set_color(accent_color2),
    "ul" : Tex("Unicorn: ", r"$[1,1,1,0]^\infty_\delta$").set_color(accent_color2),
    "dl" : Tex("Dragon: ", r"$[1,1,1,1]^\infty_\delta$").set_color(accent_color2),
    "nl" : Tex("Knight: ", r"$[1,2,0,0]^1_\delta$").set_color(accent_color2),

    "ql" : Tex("Queen: ", r"$[1,0,0,0]^\infty_\delta$", 
                         r"$\cup$",
                         r"$[1,1,0,0]^\infty_\delta$", 
                         r"$\cup$", 
                         r"$[1,1,1,0]^\infty_\delta$", 
                         r"$\cup$", 
                         r"$[1,1,1,1]^\infty_\delta$").set_color(accent_color2),
    "Pl" : Tex("Princess: ", r"$[1,0,0,0]^\infty_\delta$", 
                         r"$\cup$",
                         r"$[1,1,0,0]^\infty_\delta$").set_color(accent_color2),

    "kl" : Tex("King: ", r"$[1,0,0,0]^1_\delta$", 
                         r"$\cup$",
                         r"$[1,1,0,0]^1_\delta$", 
                         r"$\cup$", 
                         r"$[1,1,1,0]^1_\delta$", 
                         r"$\cup$", 
                         r"$[1,1,1,1]^1_\delta$").set_color(accent_color2),
    "pl" : Tex("Pawn: ", r"$[0,1,0,0]^*, [0,0,0,1]^*$").set_color(accent_color2)
}
def intro_slide(self, run_time):
    title = Text("Chessmology:\n5D Chess with Multivere Time Travel Introduction\nBlack Board Talk").scale(0.8)
    author = Text("By Vasilii Pustovoit, CITA, 2025").scale(0.4)
    title.shift(0.5*UP)
    author.shift(0.5*DOWN)
    self.play(Write(title), run_time = run_time)
    self.play(Write(author), run_time = run_time)
    self.next_slide()
    self.play(FadeOut(title, shift=10*RIGHT), FadeOut(author, shift=10*RIGHT))

def show_queen_moves(self, run_time):
    """
    Show moves of queen, and some other slides
    """

    axes_origin = [-4.5, -4.5]
    axes_extensions = 9.5
    piece_loc = [central_square, 0, 0]
    piece_loc_plus1 = [central_square_plus1, 0, 0]
    axes_origin_vec = np.array([*axes_origin, 0])

    x_axis, y_axis = AddMyAxes(self, axes_origin, 
                               [axes_extensions, axes_extensions])
    log = False
    board_5d = Manim_Chessboard_5D(scene=self, log=log)
    board_5d.default_chess_configuration_setup()
    board1 = board_5d.manim_chessboards[0]

    self.add(board_5d)#, board2, board3)

    piece = 'ql'
    show_piece_moves_slide(self, board_5d, piece)
    board_5d.draw_all_movement_vectors(piece_loc, False) # All movement vectors
    self.next_slide()
    board_5d.remove_all_movement_vectors()
    board_5d.draw_all_movement_vectors(piece_loc, True) # Unit vectors

    show_vector_difference(self, board_5d, [5.5, -3, 0], axes_origin_vec, run_time, 
                           [ PINK, RED, GOLD ], piece_loc, piece_loc_plus1)

    write_drs(self, piece)
    board_5d.remove_all_movement_vectors()
    board1.delete_board()
    rm_axes_anim = FadeOut(*[x_axis, y_axis], run_time = run_time/2)
    t1_anim = []
    t1_anim.append(rm_axes_anim)
    self.play(*t1_anim, run_time = run_time/2)
    board_5d.remove_all_boards()
    self.remove(board_5d, x_axis, y_axis)

def full_dr_explanation_slide(self, run_time):
    """
    A slide with full dr explanations in 2D
    """
    top_pos = np.array([0,3,0])

    dpos_vec = np.array([0,-1.0,0])
    accent_color = GOLD

    pos0 = top_pos + dpos_vec
    dr_title = Tex(r"$\delta$-vector notation definition:").shift(top_pos)
    self.play(Write(dr_title), run_time = run_time)
    self.next_slide()

    dr_def = MathTex(r"\mathbf{[ x_1, x_2, ..., x_n ]^{m}_{\delta} ",
                     r"= \left\{ \forall \Vec{v} \, | \,  \Vec{v} \in ",
                     r"\sigma \left( ",
                     r"[ \pm x_1, \pm x_2, ..., \pm x_n ]",
                     r"\right) ",
                     r"\times k, \left| k \right| \le m \right\}}").shift(pos0)
    dr_def.set_color_by_tex("x_1", accent_color)
    self.play(Write(dr_def), run_time = run_time)

    possigma = pos0 + dpos_vec
    dr_sigma = Tex(r"$\sigma(\Vec{a})$ - set of all vectors, resulting \\",
                 r"from permutations of components of $\Vec{a}$").shift(possigma)
    self.play(Write(dr_sigma), run_time = run_time)
    self.next_slide()

    pos1 = possigma + 2 * dpos_vec
    dr_ex1 = Tex(r"Ex. 1: ",
                 r"$[1, 0]^\infty_\delta$",
                 r"$ = \{ $",
                 r"$[+k, 0], [-k, 0], [0, +k], [0, -k] $",
                 r"$, k \in \mathbf{Z}_+ \}$").shift(pos1)
    dr_ex1.set_color_by_tex("[", accent_color)
    self.play(Write(dr_ex1), run_time = run_time)
    self.next_slide()

    pos2 = pos1 + dpos_vec
    dr_ex2 = Tex(r"Ex. 2: ",
                 r"$[1, 1]^\infty_\delta$",
                 r"$ = \{ $",
                 r"$[+k, +k], [-k, +k], [-k, +k], [-k, -k] $",
                 r"$, k \in \mathbf{Z}_+ \}$").shift(pos2)
    dr_ex2.set_color_by_tex("[", accent_color)
    self.play(Write(dr_ex2), run_time = run_time)
    self.next_slide()

    pos3 = pos2 + dpos_vec
    dr_ex3 = Tex(r"Ex. 3: ",
                 r"$[1, 2]^1_\delta$",
                 r"$ = \{ $",
                 r"$[\pm 1, +2], [\pm 1, -2], [\pm 2, +1], [\pm 2, -1] $",
                 r"$\}$").shift(pos3)
    dr_ex3.set_color_by_tex("[", accent_color)
    self.play(Write(dr_ex3), run_time = run_time)
    self.next_slide()
    
    # Define new positions for math snippets and pieces
    img_width = 0.5
    top_y = 1.5  # Vertical position
    math_positions = [
        np.array([-4, top_y, 0]),  # Left
        np.array([0, top_y, 0]),   # Center
        np.array([4, top_y, 0])    # Right
    ]
    piece_offset = LEFT * 1.5  # Distance between piece and text
    
    # Extract just the math parts from each example
    math_ex1 = dr_ex1[1].copy()
    math_ex2 = dr_ex2[1].copy()
    math_ex3 = dr_ex3[1].copy()
    math_group = VGroup(math_ex1, math_ex2, math_ex3)
    
    # Animate: fade out all text except math snippets, move math to top
    self.play(
        # Fade out all non-math elements
        *[FadeOut(obj) for obj in [dr_title, dr_def, dr_sigma,
                                   dr_ex1, dr_ex2, dr_ex3]],
        # Move math snippets to new positions
        math_ex1.animate.move_to(math_positions[0]),
        math_ex2.animate.move_to(math_positions[1]),
        math_ex3.animate.move_to(math_positions[2]),
        run_time=run_time*3
    )
    
    # Add chess pieces next to math snippets
    piece_codes = ["rl", "bl", "nl"]
    piece_imgs = []
    utils = ChessUtils_2D()
    
    for i, (code, math_pos) in enumerate(zip(piece_codes, math_positions)):
        # Get piece image
        img_path_svg, img_scale = utils.get_piece_image(code)
        piece_img = SVGMobject(img_path_svg)
        piece_img.set(width=img_width * img_scale)
        
        # Position to left of math snippet
        piece_img.next_to(math_group[i], LEFT, buff=0.3)
        
        # Animate appearance
        self.play(FadeIn(piece_img), run_time=run_time)
        piece_imgs.append(piece_img)
        
    # ======================
    # Second Row: ql, kl, pl
    # ======================
    second_row_y = top_y - 3.0  # Position below first row
    second_math_positions = [
        np.array([-4, second_row_y, 0]),
        np.array([1, second_row_y, 0]),
        np.array([5, second_row_y, 0])
    ]
    
    # Create moveset definitions for second row
    moveset_ql = MathTex(r"[1,0]^\infty_\delta", r"\cup", r"[1,1]^\infty_\delta").set_color(accent_color)
    moveset_kl = MathTex(r"[1,0]^1_\delta", r"\cup", r"[1,1]^1_\delta").set_color(accent_color)
    moveset_pl = MathTex(r"[0,1]^*").set_color(accent_color)
    movesets_list = [ moveset_ql, moveset_kl, moveset_pl ]
    
    # Position movesets
    for moveset, pos in zip([moveset_ql, moveset_kl, moveset_pl], second_math_positions):
        moveset.move_to(pos)
    
    # Animate second row appearing
    #self.play(
    #    FadeIn(moveset_ql),
    #    FadeIn(moveset_kl),
    #    FadeIn(moveset_pl),
    #    run_time=run_time
    #)
    
    # Add chess pieces for second row
    second_piece_codes = ["ql", "kl", "pl"]
    second_piece_imgs = []
    
    for i, (code, moveset, math_pos) in enumerate(zip(second_piece_codes, movesets_list, second_math_positions)):
        img_path_svg, img_scale = utils.get_piece_image(code)
        piece_img = SVGMobject(img_path_svg)
        piece_img.set(width=img_width * img_scale)
        piece_img.next_to(moveset_ql if i==0 else moveset_kl if i==1 else moveset_pl, LEFT, buff=0.3)
        
        self.play(FadeIn(piece_img), FadeIn(moveset), run_time=run_time)
        second_piece_imgs.append(piece_img)
    
    self.next_slide()
    # ======================
    # Final Cleanup
    # ======================
    self.play(
        *[FadeOut(obj) for obj in [
            *math_group, *piece_imgs,          # First row
            *second_piece_imgs, moveset_ql, moveset_kl, moveset_pl  # Second row
        ]],
        run_time=run_time
    )
    self.remove(*math_group, *piece_imgs, *second_piece_imgs, moveset_ql, moveset_kl, moveset_pl)

# Utils

def draw_vector_to_square(self, board, vec_start, pos_5d, color, run_time):
    """
    Draws a vector arrow to a point on the board, starting from the point passed

    Args:
        self (Slide): Pass self to make sure that the stuff gets animated
        board (Manim_Chessboard_5D): a board to draw the vector towards
        vec_start (np.array): start of the vector
        pos_5d (list): 3-list of final vector position
        color (Manim Color): color of the arrow
        run_time (float): how fast the animation should happen

    Returns:
        Arrow: arrow object
    """
    square, time, mult = pos_5d
    tm_loc = [time, mult]
    board_id = board.chess5.get_chessboard_by_tm(tm_loc)
    board1 = board.manim_chessboards[board_id]
    vec_end = board1.get_square_pos_in_3d(square)

    vec = Arrow(start=vec_start, end=vec_end, buff=0.0).set_color(color).set_z_index(1000)
    self.play(FadeIn(vec, run_time = run_time))
    return vec

def draw_vector_between_squares(self, board, pos_5d1, pos_5d2, color, run_time):
    """
    Draws a vector arrow between 2 points on the board

    Args:
        self (Slide): Pass self to make sure that the stuff gets animated
        board (Manim_Chessboard_5D): a board to draw the vector towards
        pos_5d1 (list): 3-list of starting vector position
        pos_5d2 (list): 3-list of final vector position
        color (Manim Color): color of the arrow
        run_time (float): how fast the animation should happen

    Returns:
        Arrow: arrow object
    """
    square1, time1, mult1 = pos_5d1
    square2, time2, mult2 = pos_5d2
    tm_loc1 = [time1, mult1]
    tm_loc2 = [time2, mult2]
    board_id1 = board.chess5.get_chessboard_by_tm(tm_loc1)
    board_id2 = board.chess5.get_chessboard_by_tm(tm_loc2)
    board1 = board.manim_chessboards[board_id1]
    board2 = board.manim_chessboards[board_id2]
    vec_start = board1.get_square_pos_in_3d(square1)
    vec_end = board2.get_square_pos_in_3d(square2)

    vec = Arrow(start=vec_start, end=vec_end, buff=0.0).set_color(color).set_z_index(1000)
    self.play(FadeIn(vec, run_time = run_time))
    return vec

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
    Writes all dr vectors for a specific piece.

    Args:
        self (Slide): Pass self to make sure that the stuff gets animated
        piece (str): piece acronym
    """
    animations_signless = [] # Array for animations for dr vectors with sign permutations
    animations_sign = [] # Array for animations for dr vectors without sign permutations
    animations_sign_ordered = [] # Array for animations for pure dr vectors
    animations_delete = [] # Array for animations for deleting of dr vectors
    drs_2d = []
    drs_2d_sign = []
    drs_2d_sign_ordered = []
    text_objs = []
    animation_speed = 0.5

    mv = Moves()
    drs_4d = mv.get_dr(piece[0])
    starting_pos = np.array([6.0, 4.0, 0.0])
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
            #text2 = empty_text
            text2 = text.copy().scale(0.5).set_color(GREY)

        if dr in drs_2d_sign_ordered:
            text3 = text_red
        else:
            #text3 = empty_text
            text3 = text.copy().scale(0.5).set_color(GREY)

        text_objs.append(text)
        text_objs.append(text2)
        text_objs.append(text3)
        text_anim_sign = Transform(text, text2)
        text_anim_sign_ordered = Transform(text2, text3)
        text_anim_delete = Transform(text, empty_text)
        text_anim_delete2 = Transform(text2, empty_text)
        text_anim_delete3 = Transform(text3, empty_text)

        animations_signless.append(text_anim)
        animations_sign.append(text_anim_sign)
        animations_sign_ordered.append(text_anim_sign_ordered)
        animations_delete.append(text_anim_delete)
        animations_delete.append(text_anim_delete2)
        animations_delete.append(text_anim_delete3)

    animations_signless.append(Write(titletext1))
    animations_sign.append(Transform(titletext1, titletext2))
    animations_sign_ordered.append(Transform(titletext1, titletext3))
    animations_delete.append(Transform(titletext1, Text("")))
    animations_delete.append(Transform(titletext2, Text("")))
    animations_delete.append(Transform(titletext3, Text("")))

    self.play(*animations_signless, run_time = animation_speed)
    self.next_slide()
    self.play(*animations_sign, run_time = animation_speed)
    self.next_slide()
    self.play(*animations_sign_ordered, run_time = animation_speed)
    self.next_slide()
    self.play(*animations_delete, run_time = animation_speed)
    self.remove(titletext1, titletext2, titletext3, *text_objs)

def show_vector_difference(self, board_5d, text_pos, axes_origin_vec, run_time, colors, piece_loc, piece_loc_plus1):
    """
    Shows vector equation of the form r2 = r1 + delta(r)

    Args:
        self (Slide): Pass self to make sure that the stuff gets animated
        colors (list): list of colors
        ...
    """
    text_pos = np.array(text_pos)
    color1, color2, color3 = colors

    arrow1 = draw_vector_to_square(self, board_5d, axes_origin_vec, piece_loc, color1, run_time/4)
    arrow2 = draw_vector_between_squares(self, board_5d, piece_loc, piece_loc_plus1, color2, run_time/4)
    arrow3 = draw_vector_to_square(self, board_5d, axes_origin_vec, piece_loc_plus1, color3, run_time/4)
    dr_tex = MathTex(r"\mathbf{r_2}", r"\mathbf{ = }", r"\mathbf{r_1}", r"\mathbf{+ }",r"\mathbf{\delta r}", 
                     font_size=50).shift(text_pos)
    dr_tex.set_color_by_tex('r_1', color1)
    dr_tex.set_color_by_tex('elta', color2)
    dr_tex.set_color_by_tex('r_2', color3)
    self.play(Write(dr_tex))

    self.next_slide()
    arrows = [ arrow1, arrow2, arrow3 ]
    vec_arrows_anim: list[Animation] = [ FadeOut(arrow) for arrow in arrows ]
    vec_arrows_anim.append(Transform(dr_tex, MathTex("")))
    self.play(*vec_arrows_anim, run_time = run_time)

def show_piece_moves_slide(self, board_5d, piece, pos=central_square, tm_loc=[0,0]):
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
    self.play(board2d.add_piece(piece, pos))
    self.play(AnimationGroup(*board_5d.show_moves([pos,tm_loc[0],tm_loc[1]])))

def show_4d_moves(self, piece, board_5d, time_loc, arrows=True):
    """
    Shows moves of a piece on 4d board

    Args:
        self (ThreeDSlide): a scene where animation is happening
        piece (str): piece acronym
        board_5d (Manim_Chessboard_5D): a 5D board object
        arrows (bool): whether show arrows. True by default
    """
    central_square_4d = [central_square, time_loc, 0]
    #moveset = dict_4d_moveset[piece]
    #self.add_fixed_in_frame_mobjects(moveset)
    #moveset.to_corner(UL)
    board2d_id = board_5d.chess5.get_chessboard_by_tm([time_loc,0])
    board_2d = board_5d.manim_chessboards[board2d_id]
    self.play(board_2d.add_piece(piece, central_square, force_center=True))
    self.play(AnimationGroup(*board_5d.show_moves(central_square_4d)))
    if arrows: board_5d.draw_all_movement_vectors(central_square_4d)
    self.next_slide()
    if arrows: board_5d.remove_all_movement_vectors()
    board_5d.recolor_all_boards()
    board_2d.remove_all_pieces()
    #self.remove(moveset)

def show_moves_3d(self, board_5d, piece, piece_pos, time_of_rotation):
    """
    Show moves of a piece on a 3D cube

    Args:
        self (ThreeDSlide): a scene where animation is happening
        board_5d (Manim_Chessboard_5D): a 5D board object
        piece (str): the name of the piece
        piece_pos (list): 3-list of where to place the piece
        time_of_rotation (float): time between the start and end of rotation of camera
    """
    run_time = 0.5
    print(f"{piece} has begun")
    moveset = dict_3d_moveset[piece]
    self.add_fixed_in_frame_mobjects(moveset)
    moveset.to_corner(UR)
    board2d_id = board_5d.chess5.get_chessboard_by_tm([0,0])
    board_2d = board_5d.manim_chessboards[board2d_id]
    board_2d.add_piece(piece, central_square, force_center=True)
    self.play(AnimationGroup(*board_5d.show_moves(piece_pos, recolor_scheme="color-opacity")))
    self.wait(time_of_rotation)
    self.next_slide()
    board_2d.remove_all_pieces()
    board_5d.recolor_all_boards()
    self.remove(moveset)

def cube_moves_3d_slide(self, queen_only=False):
    """
    Showes moves on a 3D cube
    """
    run_time = 0.5
    log = True
    board_5d = Manim_Chessboard_5D(square_size=0.5, board_separation=[5,5],
                                   mode_3d=True,
                                   scene=self, log=log)

    # Setting up the cube
    piece_pos = [central_square, 0, 0]
    chessboard_locs = []
    for i in range(-3,5):
        chessboard_locs.append([0, -i])

    board_5d.add_several_empty_chessboards(chessboard_locs)

    self.move_camera(phi=60*DEGREES, theta=-60*DEGREES)
    print("Assembling the cube...")
    board_5d.assemble_the_cube(0.03, orientation=2)
    print("Assembled the cube")
    self.next_slide()
    board_5d.set_animation_speed(run_time)
    #board_5d.disassemble_the_cube()

    # Cycling through moves
    accent_color = GOLD
    self.begin_ambient_camera_rotation(rate=0.2)
    if not queen_only:
        show_moves_3d(self, board_5d, 'rl', piece_pos, 10)
        show_moves_3d(self, board_5d, 'bl', piece_pos, 10)
        show_moves_3d(self, board_5d, 'nl', piece_pos, 10)
        show_moves_3d(self, board_5d, 'ul', piece_pos, 10)
        show_moves_3d(self, board_5d, 'Pl', piece_pos, 10)
    show_moves_3d(self, board_5d, 'ql', piece_pos, 10)
    if not queen_only:
        show_moves_3d(self, board_5d, 'kl', piece_pos, 5)
    self.stop_ambient_camera_rotation()
    board_5d.disassemble_the_cube(orientation=2)
    self.move_camera(phi=60*DEGREES, theta=-60*DEGREES)
    return board_5d

def noncube_moves_3d_slide(self, board_5d, time_loc=0, queen_only=False, no_pawn=True, arrows=True):
    """
    Moves of all pieces not in a cube
    """
    if not queen_only:
        show_4d_moves(self, 'rl', board_5d, time_loc, arrows)
        show_4d_moves(self, 'bl', board_5d, time_loc, arrows)
        show_4d_moves(self, 'nl', board_5d, time_loc, arrows)
        show_4d_moves(self, 'Pl', board_5d, time_loc, arrows)
    show_4d_moves(self, 'ql', board_5d, time_loc, arrows)
    if not queen_only:
        show_4d_moves(self, 'kl', board_5d, time_loc, arrows)
    if not no_pawn:
        show_4d_moves(self, 'pl', board_5d, time_loc, arrows)

def slide5(self, log, run_time, queen_only):
    """
    5th slide - 4D moves
    """
    board_5d = Manim_Chessboard_5D(square_size=0.5, board_separation=[5,5],
                                   mode_3d=False,
                                   scene=self, log=log)
    self.add(board_5d)
    chessboard_locs = []
    num_of_boards_per_dim = 2 # 2*n + 1 is the actual num_of_boards_per_dim
    for i in range(-num_of_boards_per_dim, num_of_boards_per_dim + 1):
        for j in range(0, 2 * num_of_boards_per_dim + 2):
            chessboard_locs.append([j, i])
    board_5d.add_several_empty_chessboards(chessboard_locs)
    self.play(board_5d.change_camera_center([num_of_boards_per_dim,0]), run_time=run_time)

    ######################
    ###### 4D MOVES ######
    ######################

    # TODO: the piece isn't being put in the central board!
    # TODO: bug: piece doesn't move with the camera
    self.next_slide()
    self.move_camera(phi=60*DEGREES, theta=-60*DEGREES)
    self.play(board_5d.reorient_all_boards(2))
    noncube_moves_3d_slide(self, board_5d, time_loc=num_of_boards_per_dim, 
                           queen_only=queen_only,
                           no_pawn=False, arrows=False)
    self.next_slide()

    # Currently there is a bug in removing the board...
    self.play(board_5d.reorient_all_boards(0))
    #self.next_slide()
    board_5d.remove_all_boards()
    #self.move_camera(phi=0*DEGREES, theta=-90*DEGREES)

class PresentationSlides1_2(ThreeDSlide):
    def construct(self):
        run_time = 0.5
        log = False
        ###################
        ###### INTRO ######
        ###################
        intro_slide(self, run_time)
        
        ######################
        ###### 2D MOVES ######
        ######################
        # Introduction to how to get delta r
        show_queen_moves(self, run_time)
        full_dr_explanation_slide(self, run_time)

class PresentationSlides3_4(ThreeDSlide):
    def construct(self):
        ######################
        ###### 3D MOVES ######
        ######################
        board_5d = cube_moves_3d_slide(self)

        # 3D Moves not on a cube
        noncube_moves_3d_slide(self, board_5d)
        self.play(board_5d.reorient_all_boards(0))
        board_5d.remove_all_boards()
        self.move_camera(phi=0*DEGREES, theta=-90*DEGREES)

class PresentationSlides5(ThreeDSlide):
    def construct(self):
        run_time = 0.5
        log = True
        queen_only=True
        slide5(self, log, run_time, queen_only)

class PresentationSlides6(ThreeDSlide):
    def construct(self):
        #########################
        ###### TIME TRAVEL ######
        #########################
        log = True
        self.next_slide()
        board_5d = Manim_Chessboard_5D(square_size=0.5, board_separation=[5,5],
                                       mode_3d=False,
                                       scene=self, log=log)
        self.add(board_5d)
        board_5d.default_chess_configuration_setup()
        self.next_slide()
        self.play(*board_5d.move_piece(['e2',0,0], ['e4',0,0]))
        self.play(*board_5d.move_piece(['e7',1,0], ['e5',0,0]))
        #self.play(board_5d.evolve_chessboard([0,0], no_anim=True))

class PresentationSlidesAll(ThreeDSlide):
    def construct(self):
        run_time = 0.5
        log = False
        ###################
        ###### INTRO ######
        ###################
        intro_slide(self, run_time)
        
        ######################
        ###### 2D MOVES ######
        ######################
        # Introduction to how to get delta r
        show_queen_moves(self, run_time)
        full_dr_explanation_slide(self, run_time)

        ######################
        ###### 3D MOVES ######
        ######################
        board_5d = cube_moves_3d_slide(self)

        # 3D Moves not on a cube
        noncube_moves_3d_slide(self, board_5d)
        self.play(board_5d.reorient_all_boards(0))
        board_5d.remove_all_boards()
        self.move_camera(phi=0*DEGREES, theta=-90*DEGREES)
        self.next_slide()

        ######################
        ###### 4D MOVES ######
        ######################
        slide5(self, log, run_time, queen_only=False)
