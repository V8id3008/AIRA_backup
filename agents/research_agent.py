"""Source collection for A.I.R.A. research workflows."""

from __future__ import annotations

from dataclasses import dataclass

from search.web_search import search_web


@dataclass(frozen=True)
class ResearchSource:
    title: str
    summary: str
    url: str


class ResearchAgent:
    """Collect and normalize web sources without inventing conclusions."""

    def search(self, query: str, max_results: int = 5) -> list[ResearchSource]:
        if not isinstance(query, str) or not query.strip():
            return []
        results = search_web(query.strip(), max_results=max_results)
        return [
            ResearchSource(
                title=str(item.get("title", "Untitled")),
                summary=str(item.get("body", "")),
                url=str(item.get("href", "")),
            )
            for item in results
            if isinstance(item, dict)
        ]

    def format_sources(self, sources: list[ResearchSource]) -> str:
        if not sources:
            return "No research sources found."
        sections = []
        for index, source in enumerate(sources, 1):
            sections.append(
                f"[{index}] {source.title}\n"
                f"Summary: {source.summary}\n"
                f"Source: {source.url}"
            )
        return "\n\n".join(sections)

    def research(self, query: str, max_results: int = 5) -> str:
        return self.format_sources(self.search(query, max_results=max_results))
