import importlib.metadata

__version__ = importlib.metadata.version("cnb-tools")

from cnb_tools.modules.annotation import (
    get_submission_status,
    format_annotations,
    update_annotations,
    update_annotations_from_file,
    update_submission_status,
)
from cnb_tools.modules.challenge import (
    get_challenge,
    create_challenge,
    delete_challenge,
    get_registered_teams,
)
from cnb_tools.modules.client import (
    get_synapse_client,
    SynapseLoginError,
    UnknownSynapseID,
)
try:
    from cnb_tools.modules.new_challenge import main as create_new_challenge, close_challenge
except ModuleNotFoundError as err:
    # Avoid breaking `import cnb_tools` if the optional `synapseutils` dependency
    # is not installed.
    if err.name != "synapseutils":
        raise

    def create_new_challenge(*args, **kwargs):
        raise ModuleNotFoundError(
            "Optional dependency 'synapseutils' is required for create_new_challenge(). "
            "Install it with `pip install synapseutils`."
        ) from err

    def close_challenge(*args, **kwargs):
        raise ModuleNotFoundError(
            "Optional dependency 'synapseutils' is required for close_challenge(). "
            "Install it with `pip install synapseutils`."
        ) from err
from cnb_tools.modules.participant import (
    get_participant_name,
    create_team,
    remove_team_member,
    get_team_member_count,
    lock_team,
    disable_team_email,
)
from cnb_tools.modules.permissions import (
    set_entity_permissions,
    set_evaluation_permissions,
)
from cnb_tools.modules.queue import (
    get_evaluation,
    get_evaluation_ids_by_project,
    get_challenge_name_from_evaluation,
    create_evaluation,
    create_evaluation_round,
)
from cnb_tools.modules.submission import (
    get_submission,
    delete_submission,
    download_submission,
    get_submitter_name,
    get_challenge_name,
    print_submission_info,
    get_submission_contributors,
    get_contributors,
)

__all__ = [
    # annotation
    "get_submission_status",
    "format_annotations",
    "update_annotations",
    "update_annotations_from_file",
    "update_submission_status",
    # challenge
    "get_challenge",
    "create_challenge",
    "delete_challenge",
    "get_registered_teams",
    # client
    "get_synapse_client",
    "SynapseLoginError",
    "UnknownSynapseID",
    # new_challenge
    "create_new_challenge",
    "close_challenge",
    # participant
    "get_participant_name",
    "create_team",
    "remove_team_member",
    "get_team_member_count",
    "lock_team",
    "disable_team_email",
    # permissions
    "set_entity_permissions",
    "set_evaluation_permissions",
    # queue
    "get_evaluation",
    "get_evaluation_ids_by_project",
    "get_challenge_name_from_evaluation",
    "create_evaluation",
    "create_evaluation_round",
    # submission
    "get_submission",
    "delete_submission",
    "download_submission",
    "get_submitter_name",
    "get_challenge_name",
    "print_submission_info",
    "get_submission_contributors",
    "get_contributors",
]
