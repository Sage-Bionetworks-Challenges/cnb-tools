"""Shared pytest fixtures for cnb-tools tests."""

import os
import sys
from unittest.mock import MagicMock

import pandas as pd
import pytest
from synapseclient import Evaluation, SubmissionStatus


def pytest_configure(config):
    """Allow test scripts to import scripts from parent folder."""
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, src_path)


@pytest.fixture
def mock_syn():
    """Fixture for mocked Synapse client."""
    return MagicMock()


@pytest.fixture
def mock_submission_status():
    """Fixture for mocked SubmissionStatus."""
    status = MagicMock(spec=SubmissionStatus)
    status.status = "SCORED"
    status.submissionAnnotations = MagicMock()
    status.submissionAnnotations.__getitem__ = lambda self, key: {
        "score": 0.95,
        "passed": True,
    }.get(key)
    return status


@pytest.fixture
def mock_submission_file():
    """Fixture for mocked file submission."""
    sub = MagicMock()
    sub.id = "12345"
    sub.evaluationId = "98765"
    sub.createdOn = "2025-11-26T10:30:00.000Z"
    sub.get.side_effect = lambda key: {"teamId": 111, "userId": 222}.get(key)
    return sub


@pytest.fixture
def mock_submission_docker():
    """Fixture for mocked Docker submission."""
    sub = MagicMock()
    sub.id = "12345"
    sub.evaluationId = "98765"
    sub.dockerRepositoryName = "docker.synapse.org/syn12345/model"
    sub.dockerDigest = "sha256:abc123"
    sub.__contains__ = lambda self, key: key == "dockerDigest"
    return sub


@pytest.fixture
def mock_evaluation():
    """Fixture for mocked Evaluation."""
    eval_obj = MagicMock(spec=Evaluation)
    eval_obj.id = "98765"
    eval_obj.name = "Test Queue"
    eval_obj.contentSource = "syn12345"
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
