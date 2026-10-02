# Coach Splash Screen Lock Controls (Firestore Guide)

This document provides ready-to-run commands for controlling the Coach View splash screen lock in the Hinge Tracker application.

When the lock flag is `true`, the coach view (`?role=coach`) immediately overlays the animated [`splash.mp4`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/splash.mp4) video and intercepts all interactions to indicate the coach should not use the app. When set to `false`, the overlay is removed and coach access is restored. The client view is never locked by this flag.

---

## Firestore Configuration
- **Project ID**: `hinge-tracker-coach`
- **Document Path**: `settings/coach_lock`
- **Field**: `locked` (Boolean: `true` or `false`)

---

## 1. Lock Coach View (Activate Splash Screen)

Run this command in the terminal to activate the splash screen overlay on the coach's device:

```bash
curl -s -X PATCH "https://firestore.googleapis.com/v1/projects/hinge-tracker-coach/databases/(default)/documents/settings/coach_lock?updateMask.fieldPaths=locked&key=AIzaSyBMojXGVQzWFrj7zQ6i28btmljMSj7e6Iw" \
  -H "Content-Type: application/json" \
  -d '{"fields": {"locked": {"booleanValue": true}}}'
```

---

## 2. Unlock Coach View (Deactivate Splash Screen)

Run this command in the terminal to dismiss the splash screen and restore the coach's full access:

```bash
curl -s -X PATCH "https://firestore.googleapis.com/v1/projects/hinge-tracker-coach/databases/(default)/documents/settings/coach_lock?updateMask.fieldPaths=locked&key=AIzaSyBMojXGVQzWFrj7zQ6i28btmljMSj7e6Iw" \
  -H "Content-Type: application/json" \
  -d '{"fields": {"locked": {"booleanValue": false}}}'
```

---

## 3. Query Current Lock Status

Run this command to check whether the coach view is currently locked:

```bash
curl -s "https://firestore.googleapis.com/v1/projects/hinge-tracker-coach/databases/(default)/documents/settings/coach_lock?key=AIzaSyBMojXGVQzWFrj7zQ6i28btmljMSj7e6Iw"
```

Expected JSON response:
- **Locked**: `"locked": { "booleanValue": true }`
- **Unlocked**: `"locked": { "booleanValue": false }`
