#!/usr/bin/env python3
"""
CLI Utility: Reset / Wipe Matches & Chats in Firestore
------------------------------------------------------
Purges all documents in the 'matches' collection and all messages
under 'chats/{match}/messages', giving a clean slate (0 matches, 0 chats).
Preserves 'coachDialogue' (coach/client advice history) completely intact.

Usage:
    python3 reset_db.py          (interactive confirmation)
    python3 reset_db.py --yes    (skip confirmation)
    python3 reset_db.py -y
"""

import sys
import json
import urllib.request
import urllib.error

FIREBASE_PROJECT_ID = "hinge-tracker-coach"
FIREBASE_API_KEY = "AIzaSyBMojXGVQzWFrj7zQ6i28btmljMSj7e6Iw"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"


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
    except Exception as e:
        print(f"[Error] Network exception: {e}", file=sys.stderr)
        return None


def get_all_messages():
    """Find all message documents in any 'messages' subcollection using collectionGroup query."""
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents:runQuery"
    query = {
        "structuredQuery": {
            "from": [{"collectionId": "messages", "allDescendants": True}]
        }
    }
    resp = api_request(url, method="POST", data=query)
    if not resp or not isinstance(resp, list):
        return []
    
    docs = []
    for item in resp:
        if "document" in item and "name" in item["document"]:
            docs.append(item["document"]["name"])
    return docs


def get_all_coach_messages():
    """Find all coach dialogue documents in any 'coachDialogue' subcollection using collectionGroup query."""
    url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents:runQuery"
    query = {
        "structuredQuery": {
            "from": [{"collectionId": "coachDialogue", "allDescendants": True}]
        }
    }
    resp = api_request(url, method="POST", data=query)
    if not resp or not isinstance(resp, list):
        return []
    
    docs = []
    for item in resp:
        if "document" in item and "name" in item["document"]:
            docs.append(item["document"]["name"])
    return docs


def get_all_matches():
    """List all documents in the 'matches' collection."""
    url = f"{BASE_URL}/matches"
    resp = api_request(url)
    if not resp or "documents" not in resp:
        return []
    return resp["documents"]


def delete_doc(doc_name: str) -> bool:
    """Delete a document by its full resource path."""
    url = f"https://firestore.googleapis.com/v1/{doc_name}"
    resp = api_request(url, method="DELETE")
    return resp is not None


def main():
    skip_confirm = False
    wipe_coach = False
    for arg in sys.argv[1:]:
        if arg in ("--yes", "-y", "--force", "-f"):
            skip_confirm = True
        elif arg == "--wipe-coach":
            wipe_coach = True
        elif arg == "--preserve-coach":
            wipe_coach = False
        elif arg in ("--help", "-h", "help"):
            print(__doc__)
            print("Options:")
            print("  --wipe-coach       Also delete all coach & client dialogue messages")
            print("  --preserve-coach   Preserve coach dialogue messages (default)")
            sys.exit(0)

    print("=" * 60)
    print(" Hinge Tracker — Database Reset Tool")
    print("=" * 60)
    print("Targeted collections for deletion:")
    print("  • matches/                 (All match cards)")
    print("  • chats/*/messages/        (All chat message bubbles)")
    if wipe_coach:
        print("  • chats/*/coachDialogue/   (Coach/client advice messages) [WIPING]")
    else:
        print("Protected collections (PRESERVED):")
        print("  • chats/*/coachDialogue/   (Coach/client advice messages)")
    print("=" * 60)

    # 1. Inspect existing records
    print("\nScanning database...")
    matches = get_all_matches()
    messages = get_all_messages()
    coach_messages = get_all_coach_messages()

    print(f"Found {len(matches)} match document(s) in 'matches'.")
    print(f"Found {len(messages)} message document(s) in chats.")
    print(f"Found {len(coach_messages)} coach message document(s) in chats/*/coachDialogue.")

    if not matches and not messages and (not wipe_coach or not coach_messages):
        print("\nDatabase is already completely clean. Nothing to do.")
        sys.exit(0)

    # 2. Confirmation
    if not skip_confirm:
        confirm = input("\nAre you sure you want to permanently delete these matches and chats? (y/N): ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Aborted by user.")
            sys.exit(0)
        if not wipe_coach and coach_messages:
            ask_coach = input("Do you also want to wipe all Coach & Client dialogue? (y/N): ").strip().lower()
            if ask_coach in ("y", "yes"):
                wipe_coach = True

    # 3. Delete messages
    print(f"\nDeleting {len(messages)} chat message(s)...")
    deleted_msgs = 0
    for idx, doc_name in enumerate(messages, 1):
        if delete_doc(doc_name):
            deleted_msgs += 1
            if idx % 10 == 0 or idx == len(messages):
                print(f"  [{idx}/{len(messages)}] messages deleted...")

    # 4. Delete coach dialogue if requested
    deleted_coach_msgs = 0
    if wipe_coach and coach_messages:
        print(f"\nDeleting {len(coach_messages)} coach message(s)...")
        for idx, doc_name in enumerate(coach_messages, 1):
            if delete_doc(doc_name):
                deleted_coach_msgs += 1
                if idx % 10 == 0 or idx == len(coach_messages):
                    print(f"  [{idx}/{len(coach_messages)}] coach messages deleted...")

    # 5. Delete matches
    print(f"\nDeleting {len(matches)} match card(s)...")
    deleted_matches = 0
    for idx, doc in enumerate(matches, 1):
        doc_name = doc["name"]
        match_name = doc.get("fields", {}).get("name", {}).get("stringValue", "Unknown")
        if delete_doc(doc_name):
            deleted_matches += 1
            print(f"  [{idx}/{len(matches)}] Deleted match: {match_name}")

    print("\n" + "=" * 60)
    print(" Reset Complete!")
    print(f"  • Deleted {deleted_matches} match document(s)")
    print(f"  • Deleted {deleted_msgs} chat message(s)")
    if wipe_coach:
        print(f"  • Deleted {deleted_coach_msgs} coach message(s)")
    else:
        print(f"  • Preserved {len(coach_messages)} coachDialogue message(s) intact")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
