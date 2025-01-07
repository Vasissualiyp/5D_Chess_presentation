import numpy as np
import itertools

class Moves():
    """Class containing moves of all chess pieces"""
    def __init__(self):
        """Create a new instance of class"""
        # dr vectors for moves
        self.orth = self.generate_perms([1, 0, 0, 0])
        self.diag = self.generate_perms([1, 1, 0, 0])
        self.tri =  self.generate_perms([1, 1, 1, 0])
        self.quad = self.generate_perms([1, 1, 1, 1])
        self.knight = self.generate_perms([2, 1, 0, 0])

    def generate_perms(self, array):
        """
        Generates a list of all possible permutations of an array

        Args:
            array (array)

        Returns:
            unique_permutations (list): list of all permutations
        """
        permutations = list(itertools.permutations(array))
        unique_permutations = list(set(permutations))
        return unique_permutations.sort()
