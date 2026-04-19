"""
AVTOHELP24 admin dashboard views.

All views are staff-only — the Unfold base template plus Django's
`staff_member_required` decorator do the access check.
"""
from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import caches
from django.core.management import call_command
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from account.models import User
from base.models import Newsletter, PushNotification
from chat.models import ChatMessage, ChatRoom
from order.choices import AVAILABLE
from order.models import AssistanceRequest
from userprofile.models import FCMDevice, Profile


# --------------------------------------------------------------------- main page
@staff_member_required
def home(request):
    """Main admin dashboard page — metrics + charts + actions."""
    today = timezone.now().date()
    week_ago = today - datetime.timedelta(days=6)   # inclusive 7 days

    metrics = [
        {
            "label": "Пользователи",
            "value": User.objects.count(),
            "icon": "person",
            "tint": "blue",
        },
        {
            "label": "Профили",
            "value": Profile.objects.count(),
            "icon": "badge",
            "tint": "indigo",
        },
        {
            "label": "Активные запросы",
            "value": AssistanceRequest.objects.filter(status=AVAILABLE).count(),
            "icon": "emergency",
            "tint": "red",
        },
        {
            "label": "Запросы за сегодня",
            "value": AssistanceRequest.objects.filter(created__date=today).count(),
            "icon": "event",
            "tint": "orange",
        },
        {
            "label": "Новые юзеры за 7 дней",
            "value": User.objects.filter(date_joined__gte=week_ago).count(),
            "icon": "trending_up",
            "tint": "green",
        },
        {
            "label": "Чат-комнаты",
            "value": ChatRoom.objects.count(),
            "icon": "chat",
            "tint": "teal",
        },
        {
            "label": "Сообщения",
            "value": ChatMessage.objects.count(),
            "icon": "forum",
            "tint": "cyan",
        },
        {
            "label": "FCM устройства",
            "value": FCMDevice.objects.filter(active=True).count(),
            "icon": "smartphone",
            "tint": "purple",
        },
    ]

    # Registrations per day, last 7 days
    registrations_chart = _series_by_day(
        User.objects.filter(date_joined__gte=week_ago),
        date_field="date_joined",
        since=week_ago,
        until=today,
    )
    requests_chart = _series_by_day(
        AssistanceRequest.objects.filter(created__gte=week_ago),
        date_field="created",
        since=week_ago,
        until=today,
    )

    # Latest activity items to seed the feed before WS kicks in
    recent = []
    for req in AssistanceRequest.objects.select_related("user").order_by("-created")[:10]:
        recent.append({
            "ts": req.created,
            "kind": "request",
            "text": f"Запрос помощи: {req.issue or 'без темы'} ({req.user.phone})",
        })
    for msg in ChatMessage.objects.select_related("sender", "room").order_by("-created")[:5]:
        recent.append({
            "ts": msg.created,
            "kind": "message",
            "text": f"Сообщение в чате #{msg.room_id} от {msg.sender.phone}",
        })
    recent.sort(key=lambda x: x["ts"], reverse=True)
    recent = recent[:15]

    return render(request, "dashboard/home.html", {
        "metrics": metrics,
        # Pre-serialise to JSON so the browser parses it; Django's default
        # dict-as-string representation is Python-literal and not valid JS.
        "registrations_chart_json": json.dumps(registrations_chart),
        "requests_chart_json": json.dumps(requests_chart),
        "recent": recent,
        "brand": "AVTOHELP24",
    })


def _series_by_day(qs, *, date_field: str, since, until):
    """Return {labels: [...], data: [...]} for a Chart.js line chart."""
    rows = {
        r["day"]: r["n"]
        for r in qs.annotate(day=TruncDate(date_field))
                   .values("day")
                   .annotate(n=Count("id"))
                   .order_by("day")
    }
    labels, data = [], []
    d = since
    while d <= until:
        labels.append(d.strftime("%d.%m"))
        data.append(int(rows.get(d, 0)))
        d += datetime.timedelta(days=1)
    return {"labels": labels, "data": data}


# --------------------------------------------------------------------- health
@staff_member_required
@require_GET
def health(request):
    """JSON health status for every external dependency."""
    import redis as redis_lib
    from django.db import connection

    status = {}

    # Database
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
        status["database"] = {"ok": True, "info": connection.vendor}
    except Exception as e:
        status["database"] = {"ok": False, "error": str(e)}

    # Redis
    try:
        caches["default"].get("__health__")
        status["redis"] = {"ok": True}
    except Exception as e:
        status["redis"] = {"ok": False, "error": str(e)}

    # Celery — ping via broker connection
    try:
        from roadhelpbackend.celery import app as celery_app
        inspect = celery_app.control.inspect(timeout=1)
        pong = inspect.ping() or {}
        status["celery"] = {
            "ok": bool(pong),
            "workers": list(pong.keys()) if pong else [],
        }
    except Exception as e:
        status["celery"] = {"ok": False, "error": str(e)}

    # Process metrics
    try:
        import psutil
        p = psutil.Process()
        status["process"] = {
            "ok": True,
            "cpu_percent": p.cpu_percent(interval=0.0),
            "rss_mb": round(p.memory_info().rss / 1024 / 1024, 1),
        }
    except Exception as e:
        status["process"] = {"ok": False, "error": str(e)}

    overall = all(v.get("ok") for v in status.values())
    return JsonResponse({"ok": overall, "services": status})


# --------------------------------------------------------------------- actions
@staff_member_required
@require_POST
def action_seed_demo(request):
    """Re-run the seed_demo management command. Idempotent."""
    try:
        call_command("seed_demo")
        _flash(request, "Демо-данные загружены/обновлены", level="success")
    except Exception as e:
        _flash(request, f"Ошибка при загрузке демо-данных: {e}", level="error")
    return redirect("dashboard:home")


@staff_member_required
@require_POST
def action_clear_cache(request):
    try:
        caches["default"].clear()
        _flash(request, "Redis кэш очищен", level="success")
    except Exception as e:
        _flash(request, f"Не удалось очистить кэш: {e}", level="error")
    return redirect("dashboard:home")


@staff_member_required
@require_POST
def action_test_push(request):
    """Dispatch a harmless test push to the current admin's FCM devices."""
    from utils.push import send_push
    devices = FCMDevice.objects.filter(user=request.user, active=True)
    if not devices.exists():
        _flash(
            request,
            "У вашего админ-пользователя нет зарегистрированных FCM-устройств — нечего тестировать",
            level="warning",
        )
        return redirect("dashboard:home")
    result = send_push(
        devices,
        title="AVTOHELP24 — тестовое уведомление",
        body="Если вы это видите, push работает ✓",
        data={"type": "admin_test"},
    )
    _flash(
        request,
        f"Push отправлен: {result['success']} успешно, {result['failure']} ошибок",
        level="success" if result["success"] else "error",
    )
    return redirect("dashboard:home")


@staff_member_required
@require_POST
def action_run_tests(request):
    """Kick off the contract test suite in a subprocess and stream the tail."""
    try:
        proc = subprocess.run(
            ["python", "-m", "pytest", "-m", "contract", "--tb=short", "-q"],
            cwd=str(Path(settings.BASE_DIR).parent),
            capture_output=True,
            text=True,
            timeout=180,
        )
        tail = "\n".join(
            (proc.stdout + proc.stderr).strip().splitlines()[-20:]
        )
        level = "success" if proc.returncode == 0 else "error"
        _flash(
            request,
            f"pytest exit={proc.returncode}\n{tail}",
            level=level,
        )
    except subprocess.TimeoutExpired:
        _flash(request, "Тесты превысили 3 минуты и были прерваны", level="error")
    except FileNotFoundError:
        _flash(
            request,
            "pytest не найден в контейнере — пересоберите образ с INSTALL_DEV=true",
            level="warning",
        )
    return redirect("dashboard:home")


def _flash(request, msg, *, level="info"):
    from django.contrib import messages
    mapping = {
        "success": messages.SUCCESS,
        "info": messages.INFO,
        "warning": messages.WARNING,
        "error": messages.ERROR,
    }
    messages.add_message(request, mapping.get(level, messages.INFO), msg)
