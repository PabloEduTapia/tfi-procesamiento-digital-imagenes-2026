from pathlib import Path

import numpy as np

from core.matrix_repository import MatrixRepository


ROOT_DIR = Path(__file__).resolve().parents[1]


def test_loads_all_machado_matrices():
    repository = MatrixRepository(ROOT_DIR / "data" / "matrices" / "machado.csv")
    available = repository.available()

    assert set(available) == {"protanomaly", "deuteranomaly", "tritanomaly"}
    assert all(len(levels) == 11 for levels in available.values())


def test_interpolates_intermediate_severity():
    repository = MatrixRepository(ROOT_DIR / "data" / "matrices" / "machado.csv")
    matrix = repository.get_matrix("protan", 7.3)

    assert matrix.shape == (3, 3)
    assert matrix.dtype == np.float32
