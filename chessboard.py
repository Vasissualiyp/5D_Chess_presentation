from manim import *

class ChessboardScene(Scene):
    def construct(self):
        squares = []
        
        # Create 8x8 grid of squares
        for row in range(8):
            for col in range(8):
                square = Square(side_length=1)
                # Shift the square so that the center of the board is at the origin
                square.shift(RIGHT*(col - 3.5) + UP*(3.5 - row))
                
                # Color squares alternately black and white
                if (row + col) % 2 == 0:
                    square.set_fill(BLACK, 1.0)
                else:
                    square.set_fill(WHITE, 1.0)
                
                # Set a black stroke for the squares
                square.set_stroke(color=BLACK, width=1)
                squares.append(square)
        
        # Group squares and animate
        board = VGroup(*squares)
        self.play(Create(board))
        self.wait(2)
