import numpy as np

from core.daltonismo import Daltonismo


class Protanopia(Daltonismo):

    def __init__(self):

        matriz = np.array([
            [0.567, 0.433, 0.000],
            [0.558, 0.442, 0.000],
            [0.000, 0.242, 0.758]
        ])

        super().__init__(matriz)