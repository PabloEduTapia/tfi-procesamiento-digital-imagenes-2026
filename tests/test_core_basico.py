import numpy as np

from core.combinado import Combinado


def crear_imagen_prueba():
    imagen = np.zeros((100, 100, 3), dtype=np.uint8)

    imagen[:, :33] = [0, 0, 255]      # rojo en BGR
    imagen[:, 33:66] = [0, 255, 0]    # verde en BGR
    imagen[:, 66:] = [255, 0, 0]      # azul en BGR

    return imagen


def test_core_simula_y_corrige_imagen():
    imagen = crear_imagen_prueba()

    procesador = Combinado(["protan"], 1.0)

    simulada = procesador.simular(imagen)
    corregida = procesador.corregir(imagen)

    assert simulada is not None
    assert corregida is not None

    assert simulada.shape == imagen.shape
    assert corregida.shape == imagen.shape

    assert simulada.dtype == np.uint8
    assert corregida.dtype == np.uint8

    assert np.mean(np.abs(simulada.astype(float) - imagen.astype(float))) > 0
    assert np.mean(np.abs(corregida.astype(float) - imagen.astype(float))) > 0