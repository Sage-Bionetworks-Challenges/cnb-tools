"""Class representing annotations of a challenge submission."""

import sys
import json

from synapseclient.core.exceptions import SynapseHTTPError
from synapseclient.core.retry import with_retry

from cnb_tools.classes.base import SynapseBase


class Annotation(SynapseBase):
    def __init__(self, sub_id):
        super().__init__(sub_id)
        try:
            self.curr_annotations = self.syn.getSubmissionStatus(sub_id)
        except SynapseHTTPError as err:
            print(
                f"⛔ {err.response.json().get('reason')}. "
                "Check the ID and try again."
            )
            sys.exit(1)

    def __str__(self) -> str:
        to_print = f"Status: {self.curr_annotations.status}\n"
        to_print += "Annotations:\n"
        to_print += json.dumps(self.curr_annotations.submissionAnnotations, indent=2)
        return to_print

    def _annotate(self, new_annots, verbose) -> None:
        self.curr_annotations.submissionAnnotations.update(new_annots)
        curr_annotations = self.syn.store(self.curr_annotations)
        print(f"Submission ID {self.uid} annotations updated.")

        if verbose:
            print("Annotations:")
            print(json.dumps(curr_annotations.submissionAnnotations, indent=2))

    def update(self, anots_file, verbose) -> None:
        with open(anots_file, encoding="utf-8") as f:
            new_annots = json.load(f)

        # Filter annotations with null and empty-list values
        new_annots = {
            key: value
            for key, value in new_annots.items()
            if value not in [None, []]
        }
        new_annots = with_retry(
            lambda: self._annotate(new_annots, verbose),
            wait=3,
            retries=10,
            retry_status_codes=[412, 429, 500, 502, 503, 504],
            verbose=True,
        )

    def update_status(self, new_status) -> None:
        self.curr_annotations.status = new_status
        self.syn.store(self.curr_annotations)
        print(f"Updated saubmission ID {self.uid} to status: {new_status}")
