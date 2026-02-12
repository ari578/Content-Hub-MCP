"""
Content loader: reads all scraped JSON files and provides them
as structured data to the rest of the application.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field


CONTENT_DIR = Path(__file__).parent.parent.parent / "content"


@dataclass
class ContentItem:
    """A single piece of content (article, glossary term, case study, etc.)."""
    title: str
    url: str
    description: str
    content: str
    chunks: list[str]
    category: str  # articles, glossary, case_studies, guides, pages
    filename: str  # source JSON filename without extension

    @property
    def word_count(self) -> int:
        return len(self.content.split())


@dataclass
class ContentStore:
    """All loaded content, organized by category."""
    articles: list[ContentItem] = field(default_factory=list)
    glossary: list[ContentItem] = field(default_factory=list)
    case_studies: list[ContentItem] = field(default_factory=list)
    guides: list[ContentItem] = field(default_factory=list)
    pages: list[ContentItem] = field(default_factory=list)

    @property
    def all_items(self) -> list[ContentItem]:
        return self.articles + self.glossary + self.case_studies + self.guides + self.pages

    @property
    def stats(self) -> dict:
        return {
            "articles": len(self.articles),
            "glossary": len(self.glossary),
            "case_studies": len(self.case_studies),
            "guides": len(self.guides),
            "pages": len(self.pages),
            "total": len(self.all_items),
            "total_chunks": sum(len(item.chunks) for item in self.all_items),
        }


def load_content() -> ContentStore:
    """Load all content JSON files into a ContentStore."""
    store = ContentStore()

    category_map = {
        "articles": ("articles", store.articles),
        "glossary": ("glossary", store.glossary),
        "case-studies": ("case_studies", store.case_studies),
        "guides": ("guides", store.guides),
        "pages": ("pages", store.pages),
    }

    for dir_name, (category_name, item_list) in category_map.items():
        content_path = CONTENT_DIR / dir_name
        if not content_path.exists():
            continue

        for json_file in sorted(content_path.glob("*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                item = ContentItem(
                    title=data.get('title', ''),
                    url=data.get('url', ''),
                    description=data.get('description', ''),
                    content=data.get('content', ''),
                    chunks=data.get('chunks', []),
                    category=category_name,
                    filename=json_file.stem,
                )

                # Only include items with meaningful content
                if item.word_count >= 5:
                    item_list.append(item)

            except Exception as e:
                print(f"Warning: Failed to load {json_file}: {e}")

    return store
