# 67 — Far-Right Pulsing Beacon Unread Indicator on Match List

## Goal

Upgrade the unread coach message indicator on the match list from the avatar overlay to an eye-catching **Pulsing Beacon** located at the **far right edge** of the match row:
- Leaves the match avatar 100% clean and unobstructed.
- Positions a prominent, vertically-centered indicator at the trailing edge of `.match-row`.
- Employs a continuous, rhythmic **radar pulse / ripple animation** (core berry dot + expanding translucent halo ring) that draws peripheral vision immediately.
- Retains the existing Firestore bidirectional tracking (`hasUnreadCoachMessage()`) and sheet-open dismissal behavior.

---

## Design Decisions

1. **Indicator Placement & Alignment**:
   - Move the unread indicator out of `.avatar-wrap` and place it at the far right of `.match-row` after `.match-info`.
   - Wrap in `.beacon-indicator-wrap` with `margin-left: auto;` to anchor it to the trailing edge with consistent alignment across all screen widths.
   - Fixed bounding container (`width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;`) to house the expanding ripple without expanding row dimensions or causing layout shift.

2. **Pulsing Beacon Aesthetics & Motion**:
   - **Core Dot**:
     - Dimensions: 11px × 11px solid circular dot.
     - Color: Hinge signature berry/plum (`#701A51`).
     - Core animation: Smooth breathing scale (`scale(1)` to `scale(1.12)` back to `scale(1)` over 1.8s).
   - **Concentric Radar Ripple (`::after`)**:
     - Starts at 11px and ripples outward to ~30px.
     - Background: `rgba(112, 26, 81, 0.45)`.
     - Fades smoothly to `rgba(112, 26, 81, 0)` over a 1.8s infinite loop with cubic-bezier easing.
   - **Contrast**: Because it renders on the pure white row background (`#ffffff`), the rich plum ripple has maximum visual contrast without needing an artificial white border.

3. **Avatar Restoration**:
   - Restore `.avatar` to standard inline rendering without overlay badges so profile photos remain pristine.

---

## Proposed Changes

### 1. UI Styling: [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Replace `.coach-unread-dot` avatar overlay styles with `.beacon-indicator-wrap` and `.beacon-dot`:
  ```css
  .beacon-indicator-wrap {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: auto;
    flex-shrink: 0;
    pointer-events: none;
  }

  .beacon-dot {
    position: relative;
    width: 11px;
    height: 11px;
    border-radius: 50%;
    background-color: #701A51;
    animation: beaconCorePulse 1.8s ease-in-out infinite;
  }

  .beacon-dot::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 11px;
    height: 11px;
    border-radius: 50%;
    background-color: rgba(112, 26, 81, 0.45);
    animation: beaconRippleWave 1.8s cubic-bezier(0.22, 0.61, 0.36, 1) infinite;
  }

  @keyframes beaconCorePulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.12); }
  }

  @keyframes beaconRippleWave {
    0% {
      width: 11px;
      height: 11px;
      opacity: 0.85;
    }
    100% {
      width: 32px;
      height: 32px;
      opacity: 0;
    }
  }
  ```

### 2. Match Row Markup: [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html)
- Update `renderMatchesList()`:
  ```javascript
  container.innerHTML = matchesData.map((item) => {
    const hasUnread = hasUnreadCoachMessage(item);
    return `
      <div class="match-row" data-name="${item.name}">
        <img class="avatar" src="${item.image}" alt="${item.name}">
        <div class="match-info">
          <div class="name-row">
            <span class="name">${item.name}</span>
          </div>
        </div>
        ${hasUnread ? `
          <div class="beacon-indicator-wrap" title="New coach advice">
            <div class="beacon-dot"></div>
          </div>
        ` : ''}
      </div>
      <div class="divider-line"></div>
    `;
  }).join('');
  ```

---

## Implementation Checklist

- [x] **Step 1: Update CSS in `index.html`**
  - [x] Add `.beacon-indicator-wrap` and `.beacon-dot` styling with `@keyframes beaconCorePulse` and `@keyframes beaconRippleWave`.
  - [x] Remove obsolete avatar badge CSS overlay positioning.

- [x] **Step 2: Update `renderMatchesList()` in `index.html`**
  - [x] Place `.beacon-indicator-wrap` on the trailing right edge of `.match-row`.
  - [x] Clean up avatar rendering so profile photos are unobstructed.

- [x] **Step 3: Verification & Visual Polish**
  - [x] Inspect match list in browser: verify beacon pulse animation is smooth, high-contrast, and eye-catching.
  - [x] Verify dismissal flow: opening and expanding Coach dialogue sheet clears the beacon in real-time.
  - [x] Test cross-role views (`client` vs `?role=coach`).
