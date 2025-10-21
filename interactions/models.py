"""Domain models and fake data for the interactions app."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


@dataclass
class InteractionRecord:
    """Represents a resource the MCP server can expose to clients."""

    id: int
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    sample_prompt: str = ""


# A tiny in-memory data store that simulates database records the MCP server can
# reason about. In a production deployment this would be backed by a real
# database model, but the fake data keeps the repository easy to bootstrap.
_FAKE_INTERACTIONS: Dict[int, InteractionRecord] = {
    1: InteractionRecord(
        id=1,
        name="Welcome Message",
        description="Provides a friendly greeting using the OpenAI MCP pipeline.",
        tags=["greeting", "onboarding"],
        sample_prompt="Create a short welcome message for a new MCP integration.",
    ),
    2: InteractionRecord(
        id=2,
        name="Status Summary",
        description=(
            "Summarises the latest platform activity and highlights actionable items."
        ),
        tags=["status", "summary"],
        sample_prompt="Summarise the latest MCP server activity for the ops team.",
    ),
    3: InteractionRecord(
        id=3,
        name="Debug Assistant",
        description="Helps developers triage MCP server issues and suggest fixes.",
        tags=["debugging", "support"],
        sample_prompt="Offer guidance for diagnosing a misbehaving MCP tool call.",
    ),
}


def list_interactions() -> Iterable[InteractionRecord]:
    """Return all known interaction records."""

    return _FAKE_INTERACTIONS.values()


def get_interaction(record_id: int) -> Optional[InteractionRecord]:
    """Fetch a single interaction by its identifier."""

    return _FAKE_INTERACTIONS.get(record_id)
