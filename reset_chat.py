#!/usr/bin/env python3
"""
CLI Utility: Reset / Clear Chat Messages in Firestore
-----------------------------------------------------
Allows clearing chat messages for a specific match or all matches,
and resets the match preview snippet so you can cleanly re-test
and iterate on chat screenshot ingestion.

Usage:
    python reset_chat.py Aubrey
    python reset_chat.py "Sydney"
    python reset_chat.py --all
"""

import sys
import json
import urllib.request
import urllib.error

FIREBASE_PROJECT_ID = "hinge-tracker-coach"
FIREBASE_API_KEY = "AIzaSyBMojXGVQzWFrj7zQ6i28btmljMSj7e6Iw"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

# Default previews for built-in demo profiles
DEFAULT_PREVIEWS = {
    "Aubrey": "ummmmmmm how's those eyes are gonna get you in trouble. text me, i'm taking you out 240 688 9865",
    "Isadora": "Hey! Loved your hiking photo :)"
}


def api_request(url: str, method: str = "GET", data: dict = None):
    separator = "&" if "?" in url else "?"
    full_url = f"{url}{separator}key={FIREBASE_API_KEY}"
    req_data = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(full_url, data=req_data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        error_msg = e.read().decode("utf-8")
        print(f"[Error] {method} {url} failed ({e.code}): {error_msg}", file=sys.stderr)
        return None


def get_match_document(match_name: str):
    """Find the match document in the 'matches' collection by name."""
    url = f"{BASE_URL}/matches"
    resp = api_request(url)
    if not resp or "documents" not in resp:
        return None

    for doc in resp["documents"]:
        fields = doc.get("fields", {})
        doc_name = fields.get("name", {}).get("stringValue", "")
        if doc_name.lower() == match_name.lower():
            return doc
    return None


def get_all_matches():
    """List all matches in the 'matches' collection."""
    url = f"{BASE_URL}/matches"
    resp = api_request(url)
    if not resp or "documents" not in resp:
        return []
    matches = []
    for doc in resp["documents"]:
        fields = doc.get("fields", {})
        name = fields.get("name", {}).get("stringValue", "")
        if name:
            matches.append({"name": name, "doc": doc})
    return matches


def clear_match_chat(match_name: str) -> int:
    """Delete all message documents under chats/{match_name}/messages and reset preview."""
    match_doc = get_match_document(match_name)
    canonical_name = match_name
    if match_doc:
        canonical_name = match_doc.get("fields", {}).get("name", {}).get("stringValue", match_name)

    print(f"\n[Reset] Clearing messages for match: '{canonical_name}'...")
    url = f"{BASE_URL}/chats/{urllib.parse.quote(canonical_name)}/messages"
    resp = api_request(url)

    deleted_count = 0
    if resp and "documents" in resp:
        for doc in resp["documents"]:
            doc_name = doc["name"]
            del_url = f"https://firestore.googleapis.com/v1/{doc_name}"
            del_resp = api_request(del_url, method="DELETE")
            if del_resp is not None:
                deleted_count += 1
        print(f"  -> Successfully deleted {deleted_count} messages.")
    else:
        print("  -> No messages found in chat.")

    # Reset preview in matches collection
    if match_doc:
        doc_path = match_doc["name"]
        default_preview = DEFAULT_PREVIEWS.get(canonical_name, "")
        
        # Patch the document's lastMessage field
        patch_url = f"https://firestore.googleapis.com/v1/{doc_path}?updateMask.fieldPaths=lastMessage"
        patch_data = {
            "fields": {
                "lastMessage": {"stringValue": default_preview}
            }
        }
        api_request(patch_url, method="PATCH", data=patch_data)
        print(f"  -> Reset preview snippet for '{canonical_name}' to: '{default_preview}'")
    else:
        print(f"  -> Note: No matching document in 'matches' collection found for '{canonical_name}'.")

    return deleted_count


def main():
    if len(sys.argv) < 2 or sys.argv[1].strip() in ("-h", "--help", "help"):
        print("\nUsage:")
        print("  python3 reset_chat.py <MatchName>    (e.g. python3 reset_chat.py Aubrey)")
        print("  python3 reset_chat.py --all          (clears all chats across all matches)")
        print()
        sys.exit(0 if len(sys.argv) >= 2 and sys.argv[1].strip() in ("-h", "--help", "help") else 1)

    raw_target = sys.argv[1].strip()

    if raw_target.lower() in ("--all", "-all", "all"):
        confirm = input("Are you sure you want to clear chats for ALL matches? (y/N): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            sys.exit(0)

        all_matches = get_all_matches()
        if not all_matches:
            all_matches = [{"name": "Aubrey"}, {"name": "Isadora"}, {"name": "Sydney"}]

        total_deleted = 0
        for m in all_matches:
            total_deleted += clear_match_chat(m["name"])
        print(f"\n[Done] Cleared total of {total_deleted} messages across all matches.\n")
    else:
        # Strip any leading hyphens in case the user typed --Sydney or -Sydney
        target = raw_target.lstrip("-")
        clear_match_chat(target)
        print(f"\n[Done] Chat for '{target}' is now clean and ready for testing.\n")


if __name__ == "__main__":
    main()
