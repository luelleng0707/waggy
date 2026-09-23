"""Persist a professional survey by adapting PROVIDED answers to Observation.

Uses existing record_physical_observation / ProfileEvent. No second log.
Does not overwrite PersistentDog scalars. Does not enable HTTP veterinarian events.
"""

from __future__ import annotations

from app.ai.models import ProfileEvent
from app.contracts.agent.survey import ProfessionalSurveyResponse
from app.state.errors import DogStateError
from app.state.observations import record_physical_observation
from app.state.store import require_dog


def record_professional_survey(survey: ProfessionalSurveyResponse) -> list[ProfileEvent]:
    """Append PROVIDED professional observations. Does not persist UNKNOWN/NOT_PROVIDED."""
    dog_id = (survey.dog_id or "").strip()
    if not dog_id:
        raise DogStateError("INVALID_EVENT_PAYLOAD", "dog_id is required", field="dog_id")
    require_dog(dog_id)
    events: list[ProfileEvent] = []
    for observation in survey.observations():
        events.append(record_physical_observation(observation))
    return events
