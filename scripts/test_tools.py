"""
Quick test script to verify content loading, search index,
and tool responses work correctly.
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.content.loader import load_content
from src.content.search_index import SearchIndex


async def main():
    print("=" * 60)
    print("RoomPriceGenie Content Hub - Tool Tests")
    print("=" * 60)

    # 1. Test content loading
    print("\n--- Test 1: Content Loading ---")
    store = load_content()
    stats = store.stats
    print(f"Stats: {stats}")
    assert stats['total'] > 0, "No content loaded!"
    assert stats['articles'] > 0, "No articles loaded!"
    print("PASS: Content loaded successfully")

    # 2. Test search index
    print("\n--- Test 2: Search Index ---")
    index = SearchIndex()
    index.build(store)
    assert index.num_docs > 0, "Index is empty!"
    print("PASS: Search index built successfully")

    # 3. Test search queries
    print("\n--- Test 3: Search Queries ---")
    test_queries = [
        "how to set hotel room prices",
        "what is RevPAR",
        "dynamic pricing strategy",
        "forecasting hotel demand",
        "OTA vs direct bookings",
        "revenue management for small hotels",
    ]
    for query in test_queries:
        results = index.search(query, top_k=3)
        print(f"  Query: '{query}' -> {len(results)} results")
        if results:
            print(f"    Top: \"{results[0].item.title}\" (score: {results[0].score:.2f})")
        assert len(results) > 0, f"No results for '{query}'!"
    print("PASS: All search queries returned results")

    # 4. Test category filtering
    print("\n--- Test 4: Category Filtering ---")
    article_results = index.search("pricing", top_k=3, category="articles")
    print(f"  Articles about 'pricing': {len(article_results)} results")
    for r in article_results:
        assert r.item.category == "articles", f"Wrong category: {r.item.category}"
    print("PASS: Category filtering works correctly")

    # 5. Test glossary lookup
    print("\n--- Test 5: Glossary ---")
    glossary_items = store.glossary
    print(f"  Glossary terms: {len(glossary_items)}")
    for item in glossary_items:
        print(f"    - {item.title} ({item.word_count} words)")
    assert len(glossary_items) > 0, "No glossary items!"
    print("PASS: Glossary loaded")

    # 6. Test case studies
    print("\n--- Test 6: Case Studies ---")
    case_studies = store.case_studies
    print(f"  Case studies: {len(case_studies)}")
    for item in case_studies[:5]:
        print(f"    - {item.title} ({item.word_count} words)")
    assert len(case_studies) > 0, "No case studies!"
    print("PASS: Case studies loaded")

    # 7. Verify pages
    print("\n--- Test 7: Feature/Product Pages ---")
    pages = store.pages
    print(f"  Pages: {len(pages)}")
    for item in pages:
        print(f"    - {item.title} ({item.word_count} words)")
    print("PASS: Pages loaded")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
