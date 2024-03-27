"""Class representing annotations of a challenge submission."""

import sys

from pathlib import Path
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.classes.base import SynapseBase
from cnb_tools.classes.queue import Queue
from cnb_tools.classes.submitter import Submitter


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

    def update():
        pass

    def reset():
        pass

    def update_status():
        pass

    def reset_status():
        pass
