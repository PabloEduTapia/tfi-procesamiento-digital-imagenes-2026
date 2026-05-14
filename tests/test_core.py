import numpy as np

from core.daltonismo import Daltonismo
from core.pipeline import PipelineImagen


def test_simular_devuelve_misma_forma():
    imagen = np.zeros((40, 60, 3), dtype=np.uint8)
    imagen[:, :, 2] = 255  # rojo en BGR

    resultado = Daltonismo("protanopia").simular(imagen)

    assert resultado.shape == imagen.shape
    assert resultado.dtype == np.uint8


def test_pipeline_encadenado():
    imagen = np.full((40, 60, 3), 120, dtype=np.uint8)

    resultado = (
        PipelineImagen(imagen=imagen)
        .brillo(1.1)
        .contraste(1.2)
        .simular_daltonismo("deuteranopia")
        .imagen
    )

    assert resultado.shape == imagen.shape
