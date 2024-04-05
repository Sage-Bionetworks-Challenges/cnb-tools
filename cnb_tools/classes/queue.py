"""Class representing a challenge submission evaluation queue."""

from synapseclient import Evaluation
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.classes.base import SynapseBase, UnknownSynapseID


class Queue(SynapseBase):
    def __init__(self, uid):
        super().__init__(uid)
        try:
            self._queue = self.syn.getEvaluation(uid)
        except SynapseHTTPError as err:
            raise UnknownSynapseID(
                f"⛔ {err.response.json().get('reason')}. "
                "Check the ID and try again."
            ) from err

    @property
    def queue(self) -> Evaluation:
        """Synapse evaluation queue."""
        return self._queue

    @queue.setter
    def queue(self, value: Evaluation) -> None:
        self._queue = value

    def __str__(self) -> str:
        return self.queue.name

    def get_challenge_name(self) -> str:
        parent_id = self.queue.contentSource
        return self.syn.get(parent_id).name
