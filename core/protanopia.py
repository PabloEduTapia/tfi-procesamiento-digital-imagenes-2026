import numpy as np

from core.daltonismo import Daltonismo


class Protanopia(Daltonismo):

    def __init__(self):

        matriz = np.array([
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281,  0.099216],
            [0.000000, 0.000000,  1.000000]
        ])

        super().__init__(matriz, "protanopia")