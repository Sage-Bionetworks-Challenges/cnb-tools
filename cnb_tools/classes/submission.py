"""Class representing a challenge submission."""

from cnb_tools.classes.base import SynapseBase
from cnb_tools.classes.submitter import Submitter


class Submission(SynapseBase):
    def __init__(self, sub_id):
        super().__init__()
        self.sub_id = sub_id
        self.submission = self.syn.getSubmission(sub_id, downloadFile=False)

    def download(self, dest):
        if "dockerDigest" in self.submission:
            print("Pulling Docker image...")
        else:
            location = "working directory" if dest == "." else dest
            print(f"Downloading {self.sub_id} to {location}...")
            self.syn.getSubmission(self.sub_id, downloadLocation=dest)

    def view(self):
        challenge = self.syn.get(
            self.syn.getEvaluation(self.submission.evaluationId).contentSource
        ).name
        submitter = Submitter(self.submission.userId)
        if self.submission.get("teamId"):
            team = Submitter(self.submission.teamId)
        else:
            team = ""
        print(f"ID: {self.submission.id}")
        print(f"Challenge: {challenge}")
        print(f"Date: {self.submission.createdOn[:10]}")
        print(f"Submitter: {submitter.pretty_print()}")
        print(f"Team (if any): {team}")
