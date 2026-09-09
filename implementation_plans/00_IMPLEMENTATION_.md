# Implementation Plan - Update Hinge 'H' Icon

This plan outlines the steps to replace the generic placeholder `H` icon in the bottom navigation bar with the authentic Hinge stylized `H` logo, using `h_icon.jpeg` as the visual source of truth.

## Objective
Update the `nav-item` H icon in [index.html](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/index.html) from three simple lines to an accurate SVG vector path matching the stylized Hinge "H" logo (with the curved crossbar and upward tail extension), and visually verify the result against reference images.

## User Review Required
> [!NOTE]
> No breaking changes or architectural modifications required. The change is isolated to the SVG icon definition inside `index.html`.

## Checklist & Proposed Steps

- [ ] **Step 1: Draft SVG Path Vector for H Logo**
  - Define SVG path for the stylized Hinge logo inside a `0 0 24 24` or `0 0 100 100` viewBox.
  - Ensure correct stem dimensions, inner fillets/curves, and upward tail extension.

- [ ] **Step 2: Update index.html**
  - Replace the current SVG `<line>` elements inside `.bottom-nav .nav-item:first-child` with the updated SVG path.
  - Match color `#888888` (inactive state) and sizing (`width="25" height="25"`) to conform with adjacent nav icons.

- [ ] **Step 3: Visual Verification & Comparison**
  - Capture rendered screenshot of `http://localhost:8080/`.
  - Compare rendered H icon with [h_icon.jpeg](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/h_icon.jpeg) and [hinge_view.jpeg](file:///Users/khandpv1/Desktop/.AntiGrav/hinge-tracker/hinge_view.jpeg).

- [ ] **Step 4: Iterative Refinement**
  - Adjust path coordinates, curve control points, stroke/fill styling, and scaling until visual differences are minimized.

## Verification Plan
### Manual / Visual Verification
- Use browser screenshot capture to visually audit the H icon against `h_icon.jpeg`.
- Ensure icon alignment and proportions match the original Hinge UI design.
