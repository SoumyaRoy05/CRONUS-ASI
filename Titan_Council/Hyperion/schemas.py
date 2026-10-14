"""
Hyperion Schemas (Pydantic V2)
Intelligence dossiers, research findings, and technical evidence.
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResearchSource(str, Enum):
    LOCAL_DOC = "local_doc"
    WEB_SEARCH = "web_search"
    CODEBASE_AST = "codebase_ast"
    SYSTEM_INSPECTION = "system_inspection"


class IntelligenceItem(BaseModel):
    """An individual piece of technical intelligence."""
    source_type: ResearchSource = Field(description="Origin of the intelligence item")
    title: str = Field(description="Title of document or discovery")
    uri_or_path: str = Field(description="URI, file path, or reference source")
    key_findings: List[str] = Field(default_factory=list, description="Bullet points of verified facts")
    relevance_score: float = Field(default=1.0, description="Relevance from 0.0 to 1.0")
    snippet: str = Field(default="", description="Exemplary quote or code snippet")


class IntelligenceDossier(BaseModel):
    """A comprehensive research dossier produced by Hyperion."""
    topic: str = Field(description="Target research query or topic")
    executive_summary: str = Field(description="Synthesis of facts and findings")
    findings: List[IntelligenceItem] = Field(default_factory=list, description="Curated intelligence items")
    recommended_approach: str = Field(description="Hyperion recommended implementation path")
    technical_constraints: List[str] = Field(default_factory=list, description="Identified technical barriers or prerequisites")
