"""Function-calling tools for the Fengyun Inn chat assistant."""

from datetime import timedelta

from django.db.models import Avg, Q
from django.utils import timezone

from main.models import AIoTProject, Event, NewsItem, Story
from water.models import Pond


def _shorten(text: str, limit: int = 180) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit]}..."


def _normalize_name(value: str) -> str:
    return (
        str(value)
        .strip()
        .replace(" ", "")
        .replace("\u3000", "")
        .replace("號", "")
        .replace("号", "")
    )


def _find_pond(pond_name: str) -> Pond | None:
    pond = Pond.objects.filter(name=pond_name).first()
    if pond:
        return pond

    target = _normalize_name(pond_name)
    for candidate in Pond.objects.all():
        candidate_name = _normalize_name(candidate.name)
        if target == candidate_name or target == str(candidate.id):
            return candidate
        if target and (target in candidate_name or candidate_name in target):
            return candidate
    return None


def _pond_not_found(pond_name: str) -> dict:
    ponds = list(Pond.objects.order_by("name").values_list("name", flat=True))
    return {"error": f"pond not found: {pond_name}", "available_ponds": ponds}


def list_events(category: str | None = None, limit: int = 10) -> dict:
    events = Event.objects.all()
    if category:
        events = events.filter(category=category)

    return {
        "events": [
            {
                "id": event.id,
                "title": event.title,
                "description": _shorten(event.description),
                "date": event.date.isoformat(),
                "location": event.location,
                "category": event.get_category_display(),
                "is_featured": event.is_featured,
                "is_upcoming": event.is_upcoming(),
            }
            for event in events[:limit]
        ]
    }


def get_event_detail(event_id: int | None = None, title: str | None = None) -> dict:
    event = None
    if event_id is not None:
        event = Event.objects.filter(id=event_id).first()
    elif title:
        event = Event.objects.filter(title__icontains=title).first()

    if event is None:
        return {"error": "event not found"}

    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "date": event.date.isoformat(),
        "location": event.location,
        "category": event.get_category_display(),
        "is_featured": event.is_featured,
        "is_upcoming": event.is_upcoming(),
    }


def list_stories(limit: int = 10) -> dict:
    return {
        "stories": [
            {
                "id": story.id,
                "title": story.title,
                "content": _shorten(story.content),
                "author": story.author,
                "published_date": story.published_date.isoformat(),
                "is_featured": story.is_featured,
            }
            for story in Story.objects.all()[:limit]
        ]
    }


def list_news(limit: int = 10) -> dict:
    return {
        "news": [
            {
                "id": item.id,
                "title": item.title,
                "source": item.source,
                "summary": _shorten(item.summary),
                "published_date": item.published_date.isoformat(),
                "url": item.url,
            }
            for item in NewsItem.objects.all()[:limit]
        ]
    }


def list_aiot_projects() -> dict:
    return {
        "projects": [
            {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "demo_url": project.demo_url,
                "order": project.order,
            }
            for project in AIoTProject.objects.all()
        ]
    }


def search_site_content(query: str, limit: int = 5) -> dict:
    events = Event.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )[:limit]
    stories = Story.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    )[:limit]
    news = NewsItem.objects.filter(
        Q(title__icontains=query) | Q(summary__icontains=query)
    )[:limit]
    projects = AIoTProject.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )[:limit]

    return {
        "query": query,
        "events": [
            {
                "id": event.id,
                "title": event.title,
                "description": _shorten(event.description),
                "date": event.date.isoformat(),
                "location": event.location,
                "category": event.get_category_display(),
            }
            for event in events
        ],
        "stories": [
            {
                "id": story.id,
                "title": story.title,
                "content": _shorten(story.content),
                "author": story.author,
                "published_date": story.published_date.isoformat(),
            }
            for story in stories
        ],
        "news": [
            {
                "id": item.id,
                "title": item.title,
                "source": item.source,
                "summary": _shorten(item.summary),
                "published_date": item.published_date.isoformat(),
                "url": item.url,
            }
            for item in news
        ],
        "aiot_projects": [
            {
                "id": project.id,
                "title": project.title,
                "description": _shorten(project.description),
                "tech_stack": project.tech_stack,
                "demo_url": project.demo_url,
            }
            for project in projects
        ],
    }


def list_ponds() -> dict:
    ponds = Pond.objects.order_by("name").values("id", "name", "species", "description")
    return {"ponds": list(ponds)}


def get_latest_water_quality(pond_name: str) -> dict:
    pond = _find_pond(pond_name)
    if pond is None:
        return _pond_not_found(pond_name)

    latest = pond.readings.first()
    if latest is None:
        return {"error": f"no sensor readings for pond: {pond.name}"}

    return {
        "pond": pond.name,
        "species": pond.species,
        "measured_at": latest.measured_at.isoformat(),
        "temperature_c": latest.temperature,
        "ph": latest.ph,
        "dissolved_oxygen_mg_l": latest.dissolved_oxygen,
        "salinity_ppt": latest.salinity,
    }


def get_average_do(pond_name: str, days: int = 7) -> dict:
    pond = _find_pond(pond_name)
    if pond is None:
        return _pond_not_found(pond_name)

    since = timezone.now() - timedelta(days=days)
    avg = pond.readings.filter(measured_at__gte=since).aggregate(
        avg_do=Avg("dissolved_oxygen")
    )
    return {
        "pond": pond.name,
        "days": days,
        "average_dissolved_oxygen_mg_l": round(avg["avg_do"] or 0, 2),
    }


def get_water_quality_history(pond_name: str, days: int = 7) -> dict:
    pond = _find_pond(pond_name)
    if pond is None:
        return _pond_not_found(pond_name)

    since = timezone.now() - timedelta(days=days)
    readings = pond.readings.filter(measured_at__gte=since).values(
        "measured_at",
        "temperature",
        "ph",
        "dissolved_oxygen",
        "salinity",
    )
    return {
        "pond": pond.name,
        "days": days,
        "readings": [
            {
                "measured_at": reading["measured_at"].isoformat(),
                "temperature_c": reading["temperature"],
                "ph": reading["ph"],
                "dissolved_oxygen_mg_l": reading["dissolved_oxygen"],
                "salinity_ppt": reading["salinity"],
            }
            for reading in readings
        ],
    }


def check_thresholds(pond_name: str) -> dict:
    pond = _find_pond(pond_name)
    if pond is None:
        return _pond_not_found(pond_name)

    latest = pond.readings.first()
    if latest is None:
        return {"error": f"no sensor readings for pond: {pond.name}"}

    alerts = []
    if latest.dissolved_oxygen < 4:
        alerts.append(
            {
                "metric": "dissolved_oxygen",
                "value": latest.dissolved_oxygen,
                "threshold": "< 4 mg/L",
                "message": "Dissolved oxygen is too low.",
            }
        )
    if latest.ph > 9 or latest.ph < 7:
        alerts.append(
            {
                "metric": "ph",
                "value": latest.ph,
                "threshold": "7 to 9",
                "message": "pH is outside the normal range.",
            }
        )
    if latest.temperature > 32:
        alerts.append(
            {
                "metric": "temperature",
                "value": latest.temperature,
                "threshold": "<= 32 C",
                "message": "Water temperature is too high.",
            }
        )

    return {
        "pond": pond.name,
        "measured_at": latest.measured_at.isoformat(),
        "ok": not alerts,
        "alerts": alerts,
    }


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_site_content",
            "description": "Search Fengyun Inn website content across events, stories, news, and AIoT projects.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keywords."},
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results per content type. Default is 5.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_events",
            "description": "List Fengyun Inn events. Optionally filter by category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Event category: activity, aiot, usr, workshop, or other.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of events. Default is 10.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_event_detail",
            "description": "Get event details by event id or title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "integer", "description": "Event id."},
                    "title": {
                        "type": "string",
                        "description": "Partial or full event title.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_stories",
            "description": "List Fengyun Inn stories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of stories. Default is 10.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_news",
            "description": "List Fengyun Inn news items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of news items. Default is 10.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_aiot_projects",
            "description": "List Fengyun Inn AIoT projects.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_ponds",
            "description": "List all ponds that have water quality data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_water_quality",
            "description": "Get the latest water quality reading for a pond.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pond_name": {
                        "type": "string",
                        "description": "Pond name, such as 1 號池.",
                    }
                },
                "required": ["pond_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_average_do",
            "description": "Get average dissolved oxygen for a pond over the last N days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pond_name": {
                        "type": "string",
                        "description": "Pond name, such as 1 號池.",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of recent days. Default is 7.",
                    },
                },
                "required": ["pond_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_water_quality_history",
            "description": "Get recent water quality history for a pond.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pond_name": {
                        "type": "string",
                        "description": "Pond name, such as 1 號池.",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of recent days. Default is 7.",
                    },
                },
                "required": ["pond_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_thresholds",
            "description": "Check whether the latest water quality values are abnormal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pond_name": {
                        "type": "string",
                        "description": "Pond name, such as 1 號池.",
                    }
                },
                "required": ["pond_name"],
            },
        },
    },
]


_TOOL_REGISTRY = {
    "search_site_content": search_site_content,
    "list_events": list_events,
    "get_event_detail": get_event_detail,
    "list_stories": list_stories,
    "list_news": list_news,
    "list_aiot_projects": list_aiot_projects,
    "list_ponds": list_ponds,
    "get_latest_water_quality": get_latest_water_quality,
    "get_average_do": get_average_do,
    "get_water_quality_history": get_water_quality_history,
    "check_thresholds": check_thresholds,
}


def dispatch(name: str, arguments: dict) -> dict:
    fn = _TOOL_REGISTRY.get(name)
    if fn is None:
        return {"error": f"unknown tool: {name}"}
    try:
        return fn(**arguments)
    except TypeError as e:
        return {"error": f"invalid arguments: {e}"}
    except Exception as e:  # noqa: BLE001
        return {"error": f"tool execution failed: {type(e).__name__}: {e}"}
