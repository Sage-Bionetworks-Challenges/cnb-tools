"""Module for managing Synapse entity and evaluation permissions.

Provides convenience functions that map human-readable permission levels
(e.g. ``"admin"``, ``"edit"``, ``"view"``) to the underlying Synapse ACL
access types, using the new synapseclient OOP models where available.
"""

from synapseclient.models import (
    Dataset,
    DatasetCollection,
    EntityView,
    Evaluation,
    File,
    Folder,
    MaterializedView,
    Project,
    SubmissionView,
    Table,
)

from cnb_tools.modules.client import get_synapse_client

# Entity permission levels
_ENTITY_PERMS: dict[str, list[str]] = {
    "view": ["READ"],
    "download": ["READ", "DOWNLOAD"],
    "moderate": ["READ", "DOWNLOAD", "MODERATE"],
    "edit": ["DOWNLOAD", "UPDATE", "READ", "CREATE"],
    "edit_and_delete": ["DOWNLOAD", "UPDATE", "READ", "CREATE", "DELETE"],
    "admin": [
        "DELETE",
        "CHANGE_SETTINGS",
        "MODERATE",
        "CREATE",
        "READ",
        "DOWNLOAD",
        "UPDATE",
        "CHANGE_PERMISSIONS",
    ],
    "remove": [],
}

# Evaluation-specific permission levels
_EVAL_PERMS: dict[str, list[str]] = {
    "view": ["READ"],
    "submit": ["READ", "SUBMIT"],
    "score": ["READ", "UPDATE_SUBMISSION", "READ_PRIVATE_SUBMISSION"],
    "admin": [
        "DELETE_SUBMISSION",
        "DELETE",
        "SUBMIT",
        "UPDATE",
        "CREATE",
        "READ",
        "UPDATE_SUBMISSION",
        "READ_PRIVATE_SUBMISSION",
        "CHANGE_PERMISSIONS",
    ],
    "remove": [],
}

# Map synapse-model class names → factory so we can resolve ``str`` IDs.
_OOP_CLASSES = {
    "dataset": Dataset,
    "datasetcollection": DatasetCollection,
    "entityview": EntityView,
    "file": File,
    "folder": Folder,
    "materializedview": MaterializedView,
    "project": Project,
    "submissionview": SubmissionView,
    "table": Table,
}


def _valid_entity_level(level: str) -> None:
    if level not in _ENTITY_PERMS:
        raise ValueError(
            f"permission_level must be one of {sorted(_ENTITY_PERMS)}. "
            f"Got '{level}'."
        )


def _valid_eval_level(level: str) -> None:
    if level not in _EVAL_PERMS:
        raise ValueError(
            f"permission_level must be one of {sorted(_EVAL_PERMS)}. " f"Got '{level}'."
        )


def set_entity_permissions(
    entityid: str,
    principal_id: str | int,
    permission_level: str = "download",
) -> None:
    """Set ACL permissions on a Synapse entity.

    Uses the new ``synapseclient.models`` OOP ``set_permissions`` method,
    which is the preferred approach in synapseclient 4.x.

    Args:
        entityid: Synapse ID of the entity (e.g. ``"syn12345"``).
        principal_id: Synapse user or team ID to grant permissions to.
            Pass ``None`` for public access.
        permission_level: One of ``"view"``, ``"download"``, ``"moderate"``,
            ``"edit"``, ``"edit_and_delete"``, ``"admin"``, or ``"remove"``.
    """
    _valid_entity_level(permission_level)
    syn = get_synapse_client()
    entity_dict = syn.restGET(f"/entity/{entityid}")
    concrete_type = entity_dict.get("concreteType", "").split(".")[-1].lower()
    cls = _OOP_CLASSES.get(concrete_type, File)
    entity = cls(id=entityid)
    entity.set_permissions(
        principal_id=principal_id,
        access_type=_ENTITY_PERMS[permission_level],
    )


def set_evaluation_permissions(
    evaluation_id: int | str,
    principal_id: str | int,
    permission_level: str = "view",
) -> None:
    """Set ACL permissions on a Synapse evaluation queue.

    Args:
        evaluation_id: Evaluation queue ID.
        principal_id: Synapse user or team ID.
        permission_level: One of ``"view"``, ``"submit"``, ``"score"``,
            ``"admin"``, or ``"remove"``.
    """
    _valid_eval_level(permission_level)
    get_synapse_client()  # ensure authentication
    evaluation = Evaluation(id=str(evaluation_id)).get()
    evaluation.update_acl(
        principal_id=principal_id,
        access_type=_EVAL_PERMS[permission_level],
    )
