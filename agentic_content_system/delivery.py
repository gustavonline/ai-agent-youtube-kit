"""Normalize and validate ACS-owned per-channel delivery intent."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .errors import ACSUserError
from .io import canonical_hash
from .project import ProjectContracts, channels_by_id, enabled_channels


def _default_delivery_intent(contracts: ProjectContracts) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "routes": [
            {"channel": channel["id"], "delivery_mode": "manual"}
            for channel in enabled_channels(contracts.brand)
        ],
    }


def _validate_scheduled_route(route: dict[str, Any]) -> None:
    mode = route.get("delivery_mode")
    if mode == "manual":
        if "scheduled_at" in route or "timezone" in route:
            raise ACSUserError(
                f"Manual delivery intent for {route.get('channel', '<unknown>')} must not include a date or timezone."
            )
        return
    if mode != "scheduled":
        raise ACSUserError(f"Unsupported delivery mode for {route.get('channel', '<unknown>')!r}.")
    scheduled_at = route.get("scheduled_at", "")
    timezone = route.get("timezone", "")
    if not isinstance(scheduled_at, str) or not scheduled_at.strip():
        raise ACSUserError(f"Scheduled delivery for {route.get('channel', '<unknown>')} requires scheduled_at.")
    if not isinstance(timezone, str) or not timezone.strip():
        raise ACSUserError(f"Scheduled delivery for {route.get('channel', '<unknown>')} requires timezone.")
    if "T" not in scheduled_at and " " not in scheduled_at:
        raise ACSUserError(
            f"Scheduled delivery for {route.get('channel', '<unknown>')} requires a date and time, not only a date."
        )
    try:
        datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ACSUserError(
            f"Scheduled delivery for {route.get('channel', '<unknown>')} has an invalid ISO date/time: {scheduled_at!r}."
        ) from exc


def current_delivery_intent(contracts: ProjectContracts) -> dict[str, Any]:
    """Return the one canonical delivery intent for this ACS project.

    ``project.json`` owns the run-specific intent. New scaffolds always write
    it explicitly; the fallback keeps a useful error message for older local
    projects until their project contract is refreshed. No caller notes or
    upstream system files are consulted.
    """

    intent = contracts.project.get("delivery_intent") or _default_delivery_intent(contracts)

    channels = channels_by_id(contracts.brand)
    enabled_ids = [channel["id"] for channel in enabled_channels(contracts.brand)]
    seen: set[str] = set()
    normalized_routes: list[dict[str, Any]] = []
    for route in intent.get("routes", []):
        channel_id = route.get("channel")
        policy = channels.get(channel_id)
        if policy is None:
            raise ACSUserError(f"Delivery intent references unknown channel {channel_id!r}.")
        if not policy.get("enabled"):
            # A policy change may disable a route that was previously selected.
            # It is no longer active and must never reach a publisher. Keeping
            # it in the project file is harmless local history; re-enabling the
            # channel still requires a fresh approval and package.
            continue
        if channel_id in seen:
            raise ACSUserError(f"Delivery intent contains duplicate channel {channel_id!r}.")
        seen.add(channel_id)
        _validate_scheduled_route(route)
        normalized = {
            "channel": channel_id,
            "delivery_mode": route["delivery_mode"],
        }
        if route["delivery_mode"] == "scheduled":
            normalized["scheduled_at"] = route["scheduled_at"]
            normalized["timezone"] = route["timezone"]
        normalized_routes.append(normalized)

    missing = [channel_id for channel_id in enabled_ids if channel_id not in seen]
    if missing:
        raise ACSUserError(
            "Delivery intent must specify every enabled channel; missing: " + ", ".join(missing)
        )
    order = {channel_id: index for index, channel_id in enumerate(enabled_ids)}
    normalized_routes.sort(key=lambda item: order[item["channel"]])
    return {"schema_version": "1.0", "routes": normalized_routes}


def current_delivery_intent_hash(contracts: ProjectContracts) -> str:
    return canonical_hash(current_delivery_intent(contracts))


def delivery_routes_by_channel(contracts: ProjectContracts) -> dict[str, dict[str, Any]]:
    return {route["channel"]: route for route in current_delivery_intent(contracts)["routes"]}
