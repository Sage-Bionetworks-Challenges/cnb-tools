"""Shared pytest fixtures for cnb-tools tests."""

import os
import sys
from unittest.mock import MagicMock

import pandas as pd
import pytest
from synapseclient.models import (
    Evaluation as ModelEvaluation,
    Submission as ModelSubmission,
    SubmissionStatus as ModelSubmissionStatus,
)


def pytest_configure(config):
    """Allow test scripts to import scripts from parent folder."""
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, src_path)


@pytest.fixture
def mock_syn():
    """Fixture for mocked Synapse client."""
    return MagicMock()

# def mock_submission_status():
#     """Fixture for mocked SubmissionStatus."""
#     status = MagicMock(spec=ModelSubmissionStatus)
#     status.status = "SCORED"
#     status.submission_annotations = {"score": 0.95, "passed": True}
#     return status

@pytest.fixture
def mock_submission_status():
    """Fixture for mocked SubmissionStatus (legacy pre-OOP format)."""
    status = MagicMock()
    status.status = "SCORED"
    status.submissionAnnotations = {"score": 0.95, "passed": True}
    return status


@pytest.fixture
def mock_submission_file():
    """Fixture for mocked file submission."""
    sub = MagicMock(spec=ModelSubmission)
    sub.id = "12345"
    sub.evaluation_id = "98765"
    sub.created_on = "2025-11-26T10:30:00.000Z"
    sub.team_id = 111
    sub.user_id = 222
    sub.docker_digest = None
    sub.contributors = None
    return sub


@pytest.fixture
def mock_submission_with_contributors():
    """Fixture for mocked team submission with contributors."""
    sub = MagicMock(spec=ModelSubmission)
    sub.id = "12345"
    sub.evaluation_id = "98765"
    sub.created_on = "2025-11-26T10:30:00.000Z"
    sub.team_id = 111
    sub.user_id = None
    sub.docker_digest = None
    sub.contributors = [
        {"principalId": "333", "createdOn": "2025-11-26T10:30:00.000Z"},
        {"principalId": "444", "createdOn": "2025-11-26T10:30:00.000Z"},
    ]
    return sub


@pytest.fixture
def mock_submission_docker():
    """Fixture for mocked Docker submission."""
    sub = MagicMock(spec=ModelSubmission)
    sub.id = "12345"
    sub.evaluation_id = "98765"
    sub.docker_repository_name = "docker.synapse.org/syn12345/model"
    sub.docker_digest = "sha256:abc123"
    return sub


@pytest.fixture
def mock_evaluation():
    """Fixture for mocked Evaluation."""
    eval_obj = MagicMock(spec=ModelEvaluation)
    eval_obj.id = "98765"
    eval_obj.name = "Test Queue"
    eval_obj.content_source = "syn12345"
    return eval_obj


@pytest.fixture
def truth_ids():
    """Fixture for truth IDs."""
    return pd.Series(["id1", "id2", "id3"], name="ids")


@pytest.fixture
def pred_ids_valid():
    """Fixture for valid prediction IDs."""
    return pd.Series(["id1", "id2", "id3"], name="ids")


@pytest.fixture
def pred_ids_invalid():
    """Fixture for invalid prediction IDs."""
    return pd.Series(["id1", "id1", "id4"], name="ids")


@pytest.fixture
def pred_values_valid():
    """Fixture for valid prediction values."""
    return pd.DataFrame(
        {
            "predictions": [0, 1, 1],
            "probabilities": [0.25, 0.6, 0.83],
        }
    )


@pytest.fixture
def pred_values_invalid():
    """Fixture for invalid prediction values."""
    return pd.DataFrame(
        {
            "predictions": [0, 1, None],
            "probabilities": [-0.5, 1.0, 1.5],
        }
    )
