"""Class representing a challenge submission."""

import sys

from pathlib import Path
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.classes.annotation import Annotation
from cnb_tools.classes.base import SynapseBase
from cnb_tools.classes.queue import Queue
from cnb_tools.classes.submitter import Submitter


class Submission(SynapseBase):
    def __init__(self, sub_id):
        super().__init__(sub_id)
        try:
            self.submission = self.syn.getSubmission(sub_id, downloadFile=False)
        except SynapseHTTPError as err:
            print(
                f"⛔ {err.response.json().get('reason')}. "
                "Check the ID and try again."
            )
            sys.exit(1)

    def delete(self) -> None:
        self.syn.delete(self.submission)
        print(f"Submission deleted: {self.uid}")

    def download(self, dest) -> None:
        if "dockerDigest" in self.submission:
            print(
                f"Submission ID {self.uid} is a Docker image 🐳 To "
                "'download', run the following:\n\n"
                f"docker pull {self.submission.dockerRepositoryName}"
                f"@{self.submission.dockerDigest}\n\n"
                "If you receive an error, try logging in first with: "
                "docker login docker.synapse.org"
            )
        else:
            self.syn.getSubmission(self.uid, downloadLocation=dest)
            location = Path.cwd() if str(dest) == "." else dest
            print(f"Submission ID {self.uid} downloaded to: {location}")

    def info(self) -> None:
        challenge = Queue(self.submission.evaluationId).get_challenge_name()
        submitter = Submitter(self.submission.userId)
        annotations = Annotation(self.uid)
        if self.submission.get("teamId"):
            team = Submitter(self.submission.teamId)
        else:
            team = ""
        print(f"ID: {self.uid}")
        print(f"Challenge: {challenge}")
        print(f"Date: {self.submission.createdOn[:10]}")
        print(f"Submitter: {submitter}")
        print(f"Team (if any): {team}")
        print(f"Annotations:\n{annotations}")
