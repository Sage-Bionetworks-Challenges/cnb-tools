"""Class representing annotations of a challenge submission."""

import sys

from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.classes.base import SynapseBase


class Annotation(SynapseBase):
    def __init__(self, sub_id):
        super().__init__()
        self.sub_id = sub_id
        try:
            self.annotations = self.syn.getSubmissionStatus(sub_id)
        except SynapseHTTPError as err:
            print(
                f"⛔ {err.response.json().get('reason')}. "
                "Check the ID and try again."
            )
            sys.exit(1)

    def update(self):
        pass

    def reset(self):
        pass

    def update_status(self, new_status):
        self.annotations.status = new_status
        self.syn.store(self.annotations)
        print(f"Updated submission ID {self.sub_id} to status: {new_status}")
