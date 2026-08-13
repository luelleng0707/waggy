from __future__ import annotations

from repository.engine.biology.service import BiologyEngineService
from repository.engine.epidemiology.service import EpidemiologyEngineService
from repository.engine.estimation.service import EstimationEngineService


def test_engine_services_are_constructible():
    assert BiologyEngineService() is not None
    assert EpidemiologyEngineService() is not None
    assert EstimationEngineService() is not None
