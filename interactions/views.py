"""HTTP views that expose MCP-style endpoints."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from django.conf import settings
from django.http import HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

from .models import InteractionRecord, get_interaction, list_interactions


def _jsonrpc_response(
    *, result: Optional[Dict[str, Any]] = None, error: Optional[Dict[str, Any]] = None, request_id: Any = None
) -> JsonResponse:
    """Generate a JSON-RPC-style response payload."""

    payload: Dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result or {}
    return JsonResponse(payload, status=200)


def _serialize_record(record: InteractionRecord) -> Dict[str, Any]:
    return {
        "type": "resource",
        "id": record.id,
        "name": record.name,
        "description": record.description,
        "tags": record.tags,
        "sample_prompt": record.sample_prompt,
    }


def _call_openai(prompt: str) -> Dict[str, Any]:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    response = client.responses.create(model=settings.OPENAI_MODEL, input=prompt)
    # The OpenAI client returns a pydantic model, which exposes ``model_dump`` to
    # produce a JSON-serialisable payload.
    return response.model_dump()


@csrf_exempt
def mcp_entrypoint(request):
    """Main HTTP entrypoint that translates HTTP requests into MCP responses."""

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return _jsonrpc_response(
            error={"code": 400, "message": "Invalid JSON payload"},
            request_id=None,
        )

    request_id = payload.get("id")
    method = payload.get("method")
    params = payload.get("params", {})

    if method == "interactions.list":
        resources = [_serialize_record(record) for record in list_interactions()]
        return _jsonrpc_response(
            result={
                "type": "resources.list",
                "resources": resources,
            },
            request_id=request_id,
        )

    if method == "interactions.get":
        record_id = params.get("record_id")
        if record_id is None:
            return _jsonrpc_response(
                error={"code": 400, "message": "Missing required param: record_id"},
                request_id=request_id,
            )
        record = get_interaction(int(record_id))
        if record is None:
            return _jsonrpc_response(
                error={"code": 404, "message": "Interaction not found"},
                request_id=request_id,
            )
        return _jsonrpc_response(
            result={
                "type": "resources.get",
                "resource": _serialize_record(record),
            },
            request_id=request_id,
        )

    if method == "interactions.generate":
        record_id = params.get("record_id")
        prompt = params.get("prompt")
        if record_id is None:
            return _jsonrpc_response(
                error={"code": 400, "message": "Missing required param: record_id"},
                request_id=request_id,
            )
        record = get_interaction(int(record_id))
        if record is None:
            return _jsonrpc_response(
                error={"code": 404, "message": "Interaction not found"},
                request_id=request_id,
            )

        prompt_to_use = prompt or record.sample_prompt
        if not prompt_to_use:
            return _jsonrpc_response(
                error={"code": 400, "message": "No prompt provided and no default available"},
                request_id=request_id,
            )

        try:
            openai_response = _call_openai(prompt_to_use)
        except RuntimeError as exc:
            return _jsonrpc_response(
                error={"code": 503, "message": str(exc)},
                request_id=request_id,
            )

        return _jsonrpc_response(
            result={
                "type": "interactions.generate",
                "resource": _serialize_record(record),
                "openai_response": openai_response,
            },
            request_id=request_id,
        )

    return _jsonrpc_response(
        error={"code": 400, "message": f"Unsupported method: {method}"},
        request_id=request_id,
    )
