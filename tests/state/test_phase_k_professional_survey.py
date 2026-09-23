"""Phase K — professional survey envelope around existing Observation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.contracts.agent.enums import InputState, ObserverRole
from app.contracts.agent.input import not_provided, provided, unknown
from app.contracts.agent.survey import ProfessionalSurveyAnswer, ProfessionalSurveyResponse
from app.data.breed_knowledge import TRAIT_NAMES
from app.normalization.enums import MappingStatus
from app.state.errors import DogStateError
from app.state.models import DogCreateRequest
from app.state.observations import physical_observations_for
from app.state.store import create_dog, get_dog
from app.state.survey import record_professional_survey


def _dog(**overrides) -> DogCreateRequest:
    body = {"name": "Scout", "weight_kg": 18.0, "bcs": 5.0, "activity_level": "Moderate"}
    body.update(overrides)
    return DogCreateRequest.model_validate(body)


def _answer(observation_type: str, presence, **overrides) -> ProfessionalSurveyAnswer:
    body = {"observation_type": observation_type, "presence": presence}
    body.update(overrides)
    return ProfessionalSurveyAnswer.model_validate(body)


def _survey(dog_id: str, role: ObserverRole, answers: list[ProfessionalSurveyAnswer], **overrides) -> ProfessionalSurveyResponse:
    body = {"dog_id": dog_id, "observer_role": role, "answers": answers}
    body.update(overrides)
    return ProfessionalSurveyResponse.model_validate(body)


def test_groomer_survey_represents_established_physical_observation():
    dog = create_dog(_dog())
    survey = _survey(
        dog.dog_id,
        ObserverRole.GROOMER,
        [_answer("coat_density", provided("dense"))],
    )
    observations = survey.observations()
    assert len(observations) == 1
    assert observations[0].observer_role == ObserverRole.GROOMER
    assert observations[0].observation_type == "coat_density"
    assert observations[0].value == "dense"
    events = record_professional_survey(survey)
    assert len(events) == 1
    assert events[0].source == "GROOMER"
    assert events[0].event_type == "GROOMER_OBSERVATION"


def test_veterinarian_survey_uses_same_observation_model():
    dog = create_dog(_dog())
    survey = _survey(
        dog.dog_id,
        ObserverRole.VETERINARIAN,
        [_answer("bcs", provided("6"))],
    )
    observations = survey.observations()
    assert observations[0].observer_role == ObserverRole.VETERINARIAN
    assert observations[0].value == "6"
    events = record_professional_survey(survey)
    assert events[0].source == "VETERINARIAN"
    assert events[0].event_type == "VETERINARIAN_OBSERVATION"
    loaded = physical_observations_for(dog.dog_id)
    assert loaded[0].observer_role == ObserverRole.VETERINARIAN
    assert type(loaded[0]).__name__ == "Observation"


def test_observer_role_is_preserved_and_not_ranked():
    dog = create_dog(_dog())
    record_professional_survey(
        _survey(dog.dog_id, ObserverRole.GROOMER, [_answer("coat_density", provided("dense"))])
    )
    record_professional_survey(
        _survey(dog.dog_id, ObserverRole.VETERINARIAN, [_answer("coat_density", provided("dense"))])
    )
    roles = [item.observer_role for item in physical_observations_for(dog.dog_id)]
    assert roles == [ObserverRole.GROOMER, ObserverRole.VETERINARIAN]
    assert ObserverRole.VETERINARIAN != ObserverRole.GROOMER


def test_observed_at_stays_distinct_from_recorded_at():
    dog = create_dog(_dog())
    events = record_professional_survey(
        _survey(
            dog.dog_id,
            ObserverRole.GROOMER,
            [_answer("weight_kg", provided("20"), unit="kg", observed_at="2026-09-19T12:00:00+00:00")],
        )
    )
    assert events[0].observed_at == "2026-09-19T12:00:00+00:00"
    assert events[0].recorded_at is not None
    assert events[0].observed_at != events[0].recorded_at
    loaded = physical_observations_for(dog.dog_id)[0]
    assert loaded.observed_at == "2026-09-19T12:00:00+00:00"
    assert loaded.recorded_at == events[0].recorded_at


def test_missing_observed_at_remains_none():
    dog = create_dog(_dog())
    events = record_professional_survey(
        _survey(dog.dog_id, ObserverRole.VETERINARIAN, [_answer("skin_appearance", provided("redness"))])
    )
    assert events[0].observed_at is None
    assert events[0].recorded_at is not None
    assert physical_observations_for(dog.dog_id)[0].observed_at is None


def test_unknown_breed_dog_can_accept_professional_observations():
    dog = create_dog(_dog(breed_input_state="UNKNOWN", primary_breed=None, weight_kg=None))
    assert dog.primary_breed is None
    record_professional_survey(
        _survey(
            dog.dog_id,
            ObserverRole.GROOMER,
            [
                _answer("weight_kg", provided("22"), unit="kg"),
                _answer("coat_density", provided("dense")),
            ],
        )
    )
    types = [item.observation_type for item in physical_observations_for(dog.dog_id)]
    assert types == ["weight_kg", "coat_density"]
    loaded = get_dog(dog.dog_id)
    assert loaded is not None
    assert loaded.breed_input_state == "UNKNOWN"
    assert loaded.primary_breed is None
    assert loaded.weight_kg is None


def test_professional_observation_does_not_overwrite_persistent_dog():
    dog = create_dog(_dog(weight_kg=18.0, height_cm=50.0, bcs=5.0))
    record_professional_survey(
        _survey(
            dog.dog_id,
            ObserverRole.GROOMER,
            [_answer("weight_kg", provided("20"), unit="kg")],
        )
    )
    loaded = get_dog(dog.dog_id)
    assert loaded is not None
    assert loaded.weight_kg == 18.0
    assert loaded.height_cm == 50.0
    assert loaded.bcs == 5.0


def test_conflicting_professional_observations_remain_separate():
    dog = create_dog(_dog(weight_kg=18.0))
    record_professional_survey(
        _survey(dog.dog_id, ObserverRole.GROOMER, [_answer("weight_kg", provided("20"), unit="kg")])
    )
    record_professional_survey(
        _survey(dog.dog_id, ObserverRole.VETERINARIAN, [_answer("weight_kg", provided("22"), unit="kg")])
    )
    values = [item.value for item in physical_observations_for(dog.dog_id) if item.observation_type == "weight_kg"]
    assert values == ["20", "22"]
    assert get_dog(dog.dog_id).weight_kg == 18.0


def test_breed_derived_trait_names_are_rejected():
    with pytest.raises(ValidationError):
        _answer("coat_type", provided("Double Coat"))
    assert "coat_type" in TRAIT_NAMES


def test_unestablished_physical_type_is_rejected():
    with pytest.raises(ValidationError):
        _answer("coat_length", provided("SHORT"))


def test_unknown_and_not_provided_are_not_omega12_and_are_not_persisted():
    dog = create_dog(_dog())
    survey = _survey(
        dog.dog_id,
        ObserverRole.GROOMER,
        [
            _answer("coat_density", provided("dense")),
            _answer("skin_appearance", unknown()),
            _answer("activity_level", not_provided()),
        ],
    )
    assert survey.answers[1].presence.state == InputState.UNKNOWN
    assert survey.answers[1].presence.state != MappingStatus.UNRESOLVED
    assert survey.answers[1].presence.state != MappingStatus.AMBIGUOUS
    assert survey.answers[2].presence.state == InputState.NOT_PROVIDED
    assert survey.answers[2].presence.state != InputState.UNKNOWN
    observations = survey.observations()
    assert [item.observation_type for item in observations] == ["coat_density"]
    events = record_professional_survey(survey)
    assert len(events) == 1
    stored = physical_observations_for(dog.dog_id)
    assert [item.observation_type for item in stored] == ["coat_density"]


def test_customer_is_not_a_professional_survey_role():
    with pytest.raises(ValidationError):
        ProfessionalSurveyResponse.model_validate(
            {
                "dog_id": "dog-1",
                "observer_role": ObserverRole.CUSTOMER,
                "answers": [_answer("weight_kg", provided("20"), unit="kg").model_dump()],
            }
        )


def test_unknown_answer_cannot_carry_observed_at():
    with pytest.raises(ValidationError):
        _answer("bcs", unknown(), observed_at="2026-09-19T12:00:00+00:00")


def test_survey_does_not_import_omega12_or_core():
    import app.contracts.agent.survey as survey_mod
    import app.state.survey as persist_mod

    assert not hasattr(survey_mod, "resolve_breed")
    assert not hasattr(persist_mod, "resolve_breed")
    assert MappingStatus.UNRESOLVED != InputState.UNKNOWN
    assert "app.normalization" not in survey_mod.__dict__.get("__file__", "")
