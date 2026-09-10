# Implementation Plan - Fix Profile Nav Avatar Alignment & Background Artifacts

This plan details the fix for the profile avatar in [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html) to eliminate the unaligned grey background and repair broken `border-radius` syntax.

## Confirmed Technical Decisions (via /grill-me)
- **Asset Fix**: Switch image source from `assets/nav_profile.jpg` to `assets/nav_profile.png` (a tight circular crop with transparent background).
- **CSS Syntax Repair**: Fix broken `border-radius: %;` syntax to `border-radius: 50%;`.
- **Dimensions**: Set `.nav-avatar` dimensions to `32px` x `32px`.

---

## Technical Architecture & CSS Modifications

```
Before Fix:
.nav-avatar { width: 50px; height: 50px; border-radius: %; } --> Invalid CSS + dark background box bleed

After Fix:
.nav-avatar { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; }
+ <img src="assets/nav_profile.png"> (Transparent PNG avatar circle)
```

---

## Implementation Checklist

- [x] **Step 1: CSS & HTML Markup Update**
  - [x] Repair CSS rule `.nav-avatar` in [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html): set `width: 32px; height: 32px; border-radius: 50%; object-fit: cover;`.
  - [x] Update `<img>` tag in [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html) to point to `assets/nav_profile.png`.

- [x] **Step 2: Verification**
  - [x] Verify profile avatar renders cleanly without grey/dark background alignment artifacts in bottom navigation bar.

---

## Verification Plan

### Manual Verification
- Open [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html) in browser.
- Confirm profile avatar renders as a perfectly aligned 32px circular icon with zero background bleed or box artifacts.
