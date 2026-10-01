# 63 — Replace Relative Chat Timestamps ("Today" / "Yesterday") with File Birth/Creation Date

## Goal

Automatically resolve relative chat timestamp headers (`Today` and `Yesterday`, such as `Today 7:10 PM` in Sakshi's chat) into formatted calendar dates (e.g. `Tue, Sep 29 7:10 PM`) using the screenshot's OS creation / birth date, while preserving the original time string.

---

## Design Decisions (from `/grill-me` alignment)

1. **Timestamp Format**:
   - Matches Hinge's native timestamp style: `<DayOfWeek>, <Month> <Day> <Time>` (e.g., `Sat, Sep 19 11:30 AM`).
   - For `Today 7:10 PM` with a birth date of September 29, 2026: resolves to **`Tue, Sep 29 7:10 PM`**.
   - Original time string (e.g. `7:10 PM`) is strictly preserved; only the relative prefix (`Today` / `Yesterday`) is substituted.
   - If standalone `Today` (no time), resolves to `Tue, Sep 29`.
   - If standalone `Yesterday` (no time), resolves to `Mon, Sep 28`.

2. **Scope**:
   - Replaces both **`Today`** (using the reference file date) and **`Yesterday`** (using the reference file date minus 1 day).

3. **OS Metadata & Date Resolution Hierarchy**:
   - **Local File Paths / Server Execution**: When parsing local files or test scripts, inspect `os.stat(filepath).st_birthtime` on macOS (falling back to `st_mtime`).
   - **Web Browser Uploads**: In `index.html`, pass `file.lastModified` and `file.name` alongside each base64 image in the `/api/parse-chat` payload.
   - **Filesystem Matching**: The server checks if the uploaded filename matches an existing file in `test_chats/` or workspace to read its native OS birth date directly; otherwise, uses the client-provided `lastModified` timestamp.
   - **Fallback**: System current date (`datetime.now()`) if no timestamp or file is available.

4. **Scope Exclusions**:
   - Does not include popcorn emoji (`🍿`) detection in this update; focus is strictly on date resolution.

---

## Proposed Changes

### 1. Backend Parser: [`server.py`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/server.py)

#### Add Timestamp Normalization Function
```python
def resolve_relative_timestamp(text: str, reference_datetime: Optional[datetime.datetime] = None) -> str:
    """
    Replace relative prefixes 'Today' and 'Yesterday' with formatted date string
    e.g. 'Today 7:10 PM' -> 'Tue, Sep 29 7:10 PM'
    """
    if reference_datetime is None:
        reference_datetime = datetime.datetime.now()
    
    # Check if text starts with Today or Yesterday (case-insensitive)
    m = re.match(r"^(Today|Yesterday)(?:,?\s+(.*))?$", text.strip(), re.IGNORECASE)
    if not m:
        return text
    
    rel_word, time_part = m.group(1).lower(), m.group(2)
    target_dt = reference_datetime if rel_word == "today" else reference_datetime - datetime.timedelta(days=1)
    
    # Format: "Tue, Sep 29"
    # %a (Day abbreviation, e.g. Tue), %b (Month abbreviation, e.g. Sep), %-d (Day of month without leading zero)
    date_str = target_dt.strftime("%a, %b ") + str(target_dt.day)
    
    if time_part:
        return f"{date_str} {time_part.strip()}"
    return date_str
```

#### Update `parse_chat_images`
- Accept an optional `image_metadata: Optional[List[Dict[str, Any]]] = None` parameter (or `file_dates: Optional[List[datetime.datetime]] = None`).
- Extract the earliest/applicable creation date for the chat frames.
- When classifying `timestamp` items, pass through `resolve_relative_timestamp(text, reference_dt)`.

#### Update `/api/parse-chat` Handler
- Parse `files` metadata array from JSON / multipart payload (`name`, `lastModified`).
- Check if file exists locally in `test_chats/` to read `os.stat().st_birthtime`.
- Pass resolved reference datetime into `parse_chat_images()`.

### 2. Frontend Upload: [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)

- In `chatFileInput.addEventListener('change', async (e) => { ... })`:
  Pass file metadata in the `/api/parse-chat` JSON payload:
  ```javascript
  body: JSON.stringify({
    matchName: currentActiveMatch ? currentActiveMatch.name : '',
    images: base64Images,
    metadata: files.map(f => ({
      name: f.name,
      lastModified: f.lastModified
    }))
  })
  ```

---

## Implementation Checklist

- [x] **Step 1: Timestamp Resolution Logic in `server.py`**
  - [x] Implement `resolve_relative_timestamp()` with format `%a, %b %-d <Time>`.
  - [x] Support helper to extract file birth time from macOS (`st_birthtime` -> fallback `st_mtime`).
  - [x] Integrate into `parse_chat_images()`.

- [x] **Step 2: API Handler & Frontend Payload Integration**
  - [x] Update `index.html` to send file metadata (`name`, `lastModified`) during chat upload.
  - [x] Update `/api/parse-chat` in `server.py` to extract metadata and resolve file dates.

- [x] **Step 3: Verification**
  - [x] Test directly on `test_chats/Sakshi_Test/Sakshi_chat.jpg`: verify `Today 7:10 PM` resolves to `Tue, Sep 29 7:10 PM`.
  - [x] Test `Yesterday 4:15 PM` edge case: verify resolves to `Mon, Sep 28 4:15 PM`.
  - [x] Test via `/api/parse-chat` endpoint.
  - [x] Regression check on other test chats (`Sydney`, `Tess`, `Priya`).
