# Hyperion: Titan of Light & Context Retrieval (`Titan_Council/Hyperion/`)

Hyperion is the seeker of truth and illumination. Named after the Titan of heavenly light, Hyperion scans the internet, retrieves external API documentation, scrapes technical web pages, and synthesizes dynamic context to ground the Council's reasoning in current reality.

---

## 1. Core Responsibilities

* **Live Web Intelligence**: Executes searches via DuckDuckGo and specialized technical developer indices.
* **Documentation Scraping**: Traverses technical documentation URLs, extracting markdown-formatted code snippets and API signatures.
* **Context Condensation**: Filters out noisy web banners, navigation menus, and scripts, distilling articles into compact `KnowledgeSnippet` tokens.
* **Grounding Support**: Injects up-to-date facts into Prometheus's planning stage to eliminate hallucinations.

---

## 2. Data Schemas (`schemas.py`)

```python
class KnowledgeSnippet(BaseModel):
    title: str
    source_url: str
    summary: str
    relevance_score: float

class ResearchBrief(BaseModel):
    topic: str
    key_findings: List[str]
    snippets: List[KnowledgeSnippet]
    recommended_actions: List[str]
```

---

## 3. Public API

```python
from Titan_Council.Hyperion import Hyperion

researcher = Hyperion()

# Conduct web intelligence research
brief = researcher.research(
    query="Latest NVIDIA NIM API endpoint syntax and python SDK usage"
)
print(f"Topic: {brief.topic}")
for finding in brief.key_findings:
    print(f"- {finding}")
```
