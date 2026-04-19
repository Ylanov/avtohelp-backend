"""
Compatibility layer over fcm-django 2.x / firebase-admin.

Pre-upgrade the project called `devices.send_message(title=..., body=...,
data=..., sound=..., icon=..., badge=...)` and expected back a dict with
`success` / `failure` counts. In fcm-django 2.x the API moved to
firebase-admin `Message` objects and returns a `BatchResponse` / `SendResponse`.

This wrapper accepts the old-style kwargs, builds a proper firebase-admin
`Message`, dispatches it to the given QuerySet of FCMDevice, and normalises
the response to `{"success": int, "failure": int}` so the call sites can stay
largely unchanged.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("CELERY")


def _build_message(
    *,
    title: str | None,
    body: str | None,
    data: dict[str, Any] | None,
    sound: str | None,
    icon: str | None,
    badge: int | None,
):
    """Build a firebase_admin.messaging.Message from legacy kwargs."""
    # Imports kept local: firebase_admin is optional at import time so the
    # module can be imported in environments without FCM configured (tests).
    from firebase_admin import messaging

    # Data payload must be flat str:str according to FCM.
    flat_data: dict[str, str] = {}
    if data:
        for key, value in _flatten(data).items():
            flat_data[key] = str(value)

    notification = None
    if title or body:
        notification = messaging.Notification(title=title, body=body)

    android_notification = messaging.AndroidNotification(
        sound=sound,
        icon=icon,
        notification_count=badge,
    )
    android = messaging.AndroidConfig(notification=android_notification)

    apns_aps = messaging.Aps(sound=sound, badge=badge)
    apns = messaging.APNSConfig(payload=messaging.APNSPayload(aps=apns_aps))

    return messaging.Message(
        notification=notification,
        data=flat_data or None,
        android=android,
        apns=apns,
    )


def _flatten(nested: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Collapse nested dict into flat key.subkey form (FCM data must be flat)."""
    out: dict[str, Any] = {}
    for k, v in nested.items():
        key = f"{parent_key}{sep}{k}" if parent_key else str(k)
        if isinstance(v, dict):
            out.update(_flatten(v, key, sep=sep))
        else:
            out[key] = v
    return out


def send_push(
    devices,
    *,
    title: str | None = None,
    body: str | None = None,
    data: dict[str, Any] | None = None,
    sound: str | None = "default",
    icon: str | None = None,
    badge: int | None = None,
) -> dict[str, int]:
    """
    Send a push notification to every device in the QuerySet.

    Returns a dict {"success": int, "failure": int}. Empty queryset returns
    zeros (no network call). Any exception is caught and logged — push
    notifications are best-effort and must not break the calling task.
    """
    if not devices:
        return {"success": 0, "failure": 0}

    try:
        message = _build_message(
            title=title, body=body, data=data,
            sound=sound, icon=icon, badge=badge,
        )
    except Exception:
        logger.exception("FCM message build failed")
        return {"success": 0, "failure": 0}

    try:
        response = devices.send_message(message)
    except Exception:
        logger.exception("FCM send_message failed")
        return {"success": 0, "failure": 0}

    # fcm-django 2.x returns a firebase_admin.messaging.BatchResponse when
    # called on a QuerySet, or a SendResponse on a single device.
    success = getattr(response, "success_count", None)
    failure = getattr(response, "failure_count", None)
    if success is None and failure is None:
        # Single-device SendResponse: .message_id is set on success.
        success = 1 if getattr(response, "message_id", None) else 0
        failure = 0 if success else 1
    return {"success": int(success or 0), "failure": int(failure or 0)}
