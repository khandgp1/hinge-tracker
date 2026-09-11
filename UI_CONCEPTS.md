# Expert & Client Chat Dialogue UI Concepts

This document presents design concepts for integrating an **Expert & Client** dialogue stream alongside the **Aubrey Chat View** in Hinge Tracker.

---

## Visual Mockups

````carousel
![Concept A: Docked Bottom Pane](assets/concept_a_floating_sheet.jpg)
### Concept A: Docked Bottom Pane
- **Description**: A collapsible bottom pane that docks below the main chat screen. When expanded (~40% height), the main chat view dynamically resizes and auto-scrolls so recent messages remain fully visible without overlap.
- **Key Advantage**: Unobscured view of both the active Aubrey chat stream and the real-time Expert & Client dialogue.
- **Best For**: Simultaneous coaching oversight with zero chat overlap.

<!-- slide -->
![Concept B: In-Line Callout Cards](assets/concept_b_inline_callouts.jpg)
### Concept B: In-Line Callout Cards
- **Description**: Distinctly styled coaching cards (e.g., "Coach's Corner" / "Design Advice") inserted chronologically into the main chat body directly beneath the message being discussed.
- **Key Advantage**: Precise contextual association right next to each specific chat bubble.
- **Best For**: Detailed message-by-message teardowns and post-analysis review.

<!-- slide -->
![Concept C: Split-Screen Dual Pane](assets/concept_c_split_screen.jpg)
### Concept C: Split-Screen Dual Pane
- **Description**: A 50/50 vertically divided view featuring Aubrey's chat in the top pane and the dedicated Expert & Client chat channel in the bottom pane.
- **Key Advantage**: Equal visual prominence for simultaneous two-way chatting.
- **Best For**: Interactive parallel conversations and side-by-side active feedback.
````

---

## Detailed Summary & Comparison

| Concept | Layout Style | Key Strengths | Considerations |
| :--- | :--- | :--- | :--- |
| **Concept A: Docked Bottom Pane** | Collapsible docked pane with dynamic viewport resize | Unobscured main chat; smooth flex-height resize; collapsible bar | Main chat height reduces to ~60% when pane is open |
| **Concept B: In-Line Cards** | Embedded cards inside message stream | Direct visual connection to specific messages | Lengthens vertical scroll area of main chat |
| **Concept C: Dual Pane** | 50/50 split screen (Top: Aubrey, Bottom: Expert) | Equal weight to both chat streams simultaneously | Reduced vertical viewing area per pane |

---

## Next Steps
Once your team selects a preferred concept:
1. We will define the data schema for Expert and Client messages.
2. Implement the chosen layout component in [`index.html`](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html).
