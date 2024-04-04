"""Class representing a challenge."""

from synapseclient import Project

from cnb_tools.classes.base import SynapseBase
from cnb_tools.classes.participant import Participant


class Challenge(SynapseBase):
    def __init__(self, project_id=None, name=None):
        super().__init__(project_id)
        self._name = name

    @property
    def name(self) -> str:
        """Synapse entity's unique ID."""
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
