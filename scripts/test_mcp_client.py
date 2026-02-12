"""
Test the MCP server by sending HTTP requests mimicking a ChatGPT client.
Server must be running on port 8787 before running this script.
"""

import json
import httpx


BASE_URL = "http://localhost:8787/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def parse_sse_response(text: str) -> dict | None:
    """Parse the first data event from an SSE response."""
    for line in text.split("\n"):
        if line.startswith("data: "):
            return json.loads(line[6:])
    return None


def main():
    client = httpx.Client(timeout=30)

    # Step 1: Initialize
    print("1. Initializing MCP session...")
    r = client.post(BASE_URL, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }, headers=HEADERS)
    assert r.status_code == 200, f"Init failed: {r.status_code}"
    session_id = r.headers.get("mcp-session-id", "")
    print(f"   Session: {session_id[:20]}...")
    HEADERS["mcp-session-id"] = session_id

    # Step 2: Notify initialized
    client.post(BASE_URL, json={
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }, headers=HEADERS)

    # Step 3: List tools
    print("\n2. Listing tools...")
    r = client.post(BASE_URL, json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }, headers=HEADERS)
    data = parse_sse_response(r.text)
    tools = data["result"]["tools"]
    print(f"   Found {len(tools)} tools:")
    for t in tools:
        desc = t["description"][:80]
        print(f"   - {t['name']}: {desc}...")

    # Step 4: Test search_revenue_content
    print("\n3. Testing search_revenue_content...")
    r = client.post(BASE_URL, json={
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "search_revenue_content",
            "arguments": {"query": "how should I price my hotel rooms for summer season"}
        }
    }, headers=HEADERS)
    data = parse_sse_response(r.text)
    text = data["result"]["content"][0]["text"]
    # Print first 600 chars
    print(f"   Response ({len(text)} chars):")
    print("   " + text[:600].replace("\n", "\n   "))

    # Step 5: Test calculate_roi
    print("\n4. Testing calculate_roi...")
    r = client.post(BASE_URL, json={
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "calculate_roi",
            "arguments": {
                "num_rooms": 25,
                "avg_room_rate": 120,
                "avg_occupancy_pct": 68,
                "manual_hours_per_week": 6
            }
        }
    }, headers=HEADERS)
    data = parse_sse_response(r.text)
    text = data["result"]["content"][0]["text"]
    print(f"   Response ({len(text)} chars):")
    print("   " + text[:600].replace("\n", "\n   "))

    # Step 6: Test get_glossary_term
    print("\n5. Testing get_glossary_term...")
    r = client.post(BASE_URL, json={
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "get_glossary_term",
            "arguments": {"term": "RevPAR"}
        }
    }, headers=HEADERS)
    data = parse_sse_response(r.text)
    text = data["result"]["content"][0]["text"]
    print(f"   Response ({len(text)} chars):")
    print("   " + text[:400].replace("\n", "\n   "))

    # Step 7: Test book_demo
    print("\n6. Testing book_demo...")
    r = client.post(BASE_URL, json={
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "book_demo",
            "arguments": {
                "property_type": "B&B",
                "num_rooms": 12,
                "specific_interest": "automated pricing"
            }
        }
    }, headers=HEADERS)
    data = parse_sse_response(r.text)
    text = data["result"]["content"][0]["text"]
    print(f"   Response ({len(text)} chars):")
    print("   " + text[:500].replace("\n", "\n   "))

    print("\n" + "=" * 60)
    print("ALL MCP CLIENT TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
