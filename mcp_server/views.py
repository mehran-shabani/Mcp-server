from __future__ import annotations

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound


def serve_frontend(_request):
    """Serve the compiled frontend build if it exists."""

    index_path = settings.FRONTEND_BUILD_DIR / "index.html"
    if not index_path.exists():
        return HttpResponseNotFound(
            "Frontend build not found. Run `npm run build:django` to generate it."
        )

    return HttpResponse(index_path.read_text(encoding="utf-8"), content_type="text/html")
