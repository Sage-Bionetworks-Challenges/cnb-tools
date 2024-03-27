"""Class representing a challenge submission."""

from pathlib import Path

from cnb_tools.classes.base import SynapseBase
from cnb_tools.classes.queue import Queue
from cnb_tools.classes.submitter import Submitter


class Submission(SynapseBase):
    def __init__(self, sub_id):
        super().__init__()
        self.sub_id = sub_id
    def delete(self) -> None:
        self.syn.delete(self.submission)
        print(f"Submission deleted: {self.sub_id}")

    def download(self, dest) -> None:
        if "dockerDigest" in self.submission:
            print(
                f"Submission ID {self.sub_id} is a Docker image 🐳 To "
                "'download', run the following:\n\n"
                f"docker pull {self.submission.dockerRepositoryName}"
                f"@{self.submission.dockerDigest}\n\n"
                "If you receive an error, try logging in first with: "
                "docker login docker.synapse.org"
            )
        else:
            self.syn.getSubmission(self.sub_id, downloadLocation=dest)
            location = Path.cwd() if str(dest) == "." else dest
            print(f"Submission ID {self.sub_id} downloaded to: {location}")

    def view(self) -> None:
        challenge = Queue(self.submission.evaluationId).get_challenge_name()
        submitter = Submitter(self.submission.userId)
        if self.submission.get("teamId"):
            team = Submitter(self.submission.teamId)
        else:
            team = ""
        print(f"ID: {self.submission.id}")
        print(f"Challenge: {challenge}")
        print(f"Date: {self.submission.createdOn[:10]}")
        print(f"Submitter: {submitter}")
        print(f"Team (if any): {team}")
