from manim import *

class TwoChessboardsIn3D(ThreeDScene):
    def construct(self):
        # Parameters
        self.n = 8               # number of squares along one dimension
        self.square_size = 1.0   # length of each square
        self.color1 = GRAY_E       # color for one set of squares
        self.color2 = BLUE_A      # color for the alternating squares
        self.board_spacing = 1.5 # horizontal spacing between the two boards

        # Create first chessboard
        board1 = self.create_chessboard()

        # Create second chessboard
        board2 = board1.copy()

        # Shift the second board horizontally to the right
        # so the two boards are side by side.
        total_width = self.n * self.square_size
        board2.shift(RIGHT * (total_width + board_spacing))

        # Add both boards to the scene
        self.play(Create(board1), Create(board2))
        self.wait()

        # Rotate both boards so that they face each other:
        #  - board1 rotates +90° around the y-axis
        #  - board2 rotates -90° around the y-axis
        self.play(
            board1.animate.rotate(PI / 2, axis=UP),
            board2.animate.rotate(-PI / 2, axis=UP),
            run_time=2
        )
        self.wait()

        # Move the camera so we can see both boards from the side
        # (instead of just looking edge-on).
        # For example, rotate the camera 70° "down" (phi) and
        # keep theta=0 to look from above or adjust to taste.
        self.move_camera(phi=70 * DEGREES, theta=0 * DEGREES, run_time=2)
        self.wait(2)

    def create_chessboard(self):
        """
        Creates a VGroup containing:
          - 9 vertical & 9 horizontal grid lines
          - 8x8 squares in a chess pattern
        Centered such that (0,0) is roughly the board’s center.
        """
        board_group = VGroup()
        line_color = GRAY

        # --- Create grid lines ---
        lines = VGroup()

        # half the total width/height
        half_size = (self.n * self.square_size) / 2

        # Horizontal lines (n+1 = 9 lines for an 8x8 board)
        for i in range(self.n + 1):
            y = i * self.square_size - half_size
            line = Line(
                start=LEFT * half_size + UP * y,
                end=RIGHT * half_size + UP * y,
                stroke_width=2,
                color=line_color,
            )
            lines.add(line)

        # Vertical lines
        for j in range(n + 1):
            x = j * self.square_size - half_size
            line = Line(
                start=DOWN * half_size + RIGHT * x,
                end=UP * half_size + RIGHT * x,
                stroke_width=2,
                color=line_color,
            )
            lines.add(line)

        board_group.add(lines)

        # --- Create colored squares ---
        squares = VGroup()
        for row in range(self.n):
            for col in range(self.n):
                sq = Square(side_length=self.square_size)
                # Shift square so the board is centered
                # (col+0.5, row+0.5) in grid space, minus half_size in each direction
                sq.shift(
                    RIGHT * ((col + 0.5) * self.square_size - half_size)
                    + UP    * ((row + 0.5) * self.square_size - half_size)
                )

                # Chess pattern
                if (row + col) % 2 == 0:
                    sq.set_fill(self.color1, opacity=1.0)
                else:
                    sq.set_fill(self.color2, opacity=1.0)
                # No outline for each square, to avoid visual double-lines
                sq.set_stroke(width=0)
                squares.add(sq)

        board_group.add(squares)

        return board_group
