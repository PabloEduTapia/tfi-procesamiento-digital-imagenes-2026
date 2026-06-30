from pathlib import Path

import cv2
import numpy as np

from core.color_marker import ColorMarker
from core.daltonism_engine import DaltonismEngine
from core.matrix_repository import MatrixRepository
from core.models import ProcessingOptions
from core.orchestrator import ProcessingOrchestrator


ROOT_DIR = Path(__file__).resolve().parents[1]


def test_corrected_marked_pipeline_changes_image():
    image = cv2.imread(str(ROOT_DIR / "input" / "imagen.jpg"))
    repository = MatrixRepository(ROOT_DIR / "data" / "matrices" / "machado.xlsx")
    orchestrator = ProcessingOrchestrator(DaltonismEngine(repository), ColorMarker())

    options = ProcessingOptions(
        tipos=["deutan"],
        severidad=8,
        resultado="corrected_marked",
        incluir_leyenda=False,
    )
    result = orchestrator.process(image, options)

    assert result.current.shape == image.shape
    assert not np.array_equal(result.current, image)
