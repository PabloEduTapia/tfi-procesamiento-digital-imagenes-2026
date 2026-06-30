from __future__ import annotations

from abc import ABC, abstractmethod

from core.color_marker import ColorMarker
from core.daltonism_engine import DaltonismEngine
from core.models import ProcessingContext


class PipelineStep(ABC):

    @abstractmethod
    def execute(self, context: ProcessingContext) -> None:
        pass


class SimulationStep(PipelineStep):

    def __init__(self, engine: DaltonismEngine):
        self.engine = engine

    def execute(self, context: ProcessingContext) -> None:
        context.simulated = self.engine.simulate(
            context.original,
            context.options.tipos,
            context.options.severidad,
        )
        context.current = context.simulated


class CorrectionStep(PipelineStep):

    def __init__(self, engine: DaltonismEngine):
        self.engine = engine

    def execute(self, context: ProcessingContext) -> None:
        context.corrected = self.engine.correct(
            context.original,
            context.options.tipos,
            context.options.severidad,
            context.options.intensidad_correccion,
        )
        context.current = context.corrected


class ColorMarkerStep(PipelineStep):

    def __init__(self, marker: ColorMarker):
        self.marker = marker

    def execute(self, context: ProcessingContext) -> None:
        context.current = self.marker.apply(
            context.current,
            spacing=context.options.espacio_marcadores,
            size=context.options.tamano_marcadores,
            include_legend=context.options.incluir_leyenda,
        )


class ImagePipeline:

    def __init__(self, steps: list[PipelineStep]):
        self.steps = steps

    def run(self, context: ProcessingContext) -> ProcessingContext:
        for step in self.steps:
            step.execute(context)

        return context
