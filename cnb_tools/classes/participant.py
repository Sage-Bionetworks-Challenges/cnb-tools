"""Class representing a submission team or individual participant."""

import sys

import typer
from synapseclient import Team
from synapseclient.core.exceptions import SynapseHTTPError

from cnb_tools.classes.base import SynapseBase


class Participant(SynapseBase):
    def __str__(self) -> str:
        try:
            return self.syn.getTeam(self.uid).get("name")
        except SynapseHTTPError:
            return self.syn.getUserProfile(self.uid).get("userName")

    # pylint: disable=unsupported-binary-operation
    def create_team(
        self,
        name: str,
        description: str | None = None,
        can_public_join: bool = False
    ) -> Team:
        try:
            team = self.syn.getTeam(name)
            use_team = typer.confirm(f"Team '{name}' already exists. Use this team?")
            if not use_team:
                sys.exit("OK. Try again with a new challenge name.")
        except ValueError:
            team = Team(
                name=name, description=description, canPublicJoin=can_public_join
            )
            # team = self.syn.store(team)
        return team
