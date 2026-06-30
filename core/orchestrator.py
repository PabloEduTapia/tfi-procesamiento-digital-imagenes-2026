from __future__ import annotations

import numpy as np

from core.color_marker import ColorMarker
from core.daltonism_engine import DaltonismEngine
from core.models import ProcessingContext, ProcessingOptions
from core.pipeline import ColorMarkerStep, CorrectionStep, ImagePipeline, SimulationStep


VALID_RESULTS = {
    "simulated",
    "corrected",
    "marked",
    "simulated_marked",
    "corrected_marked",
}


class ProcessingOrchestrator:

    def __init__(self, engine: DaltonismEngine, marker: ColorMarker | None = None):
        self.engine = engine
        self.marker = marker or ColorMarker()

    def process(self, image: np.ndarray, options: ProcessingOptions) -> ProcessingContext:
        result = options.resultado.strip().lower()

        if result not in VALID_RESULTS:
            valid = ", ".join(sorted(VALID_RESULTS))
            raise ValueError(f"Resultado no válido. Use: {valid}")

        context = ProcessingContext(
            original=image,
            current=image.copy(),
            options=options,
        )
        pipeline = self._build_pipeline(result)
        context.metadata["result"] = result
        context.metadata["types"] = options.tipos
        context.metadata["severity"] = options.severidad
        return pipeline.run(context)

    def _build_pipeline(self, result: str) -> ImagePipeline:
        steps = []

        if result.startswith("simulated"):
            steps.append(SimulationStep(self.engine))
        elif result.startswith("corrected"):
            steps.append(CorrectionStep(self.engine))

        if result == "marked" or result.endswith("_marked"):
            steps.append(ColorMarkerStep(self.marker))

        return ImagePipeline(steps)
