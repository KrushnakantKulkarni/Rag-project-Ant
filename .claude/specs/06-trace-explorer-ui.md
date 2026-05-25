# 📋 Phase Spec: 06 · Trace Explorer UI

This spec details the visual dashboard layout, node color representations, multi-column diff elements, and action widgets.

---

## 🎯 1. Overview & Goal

The goal of this phase is to build the visual telemetry analyzer frontend using Streamlit. It provides developers with a clear view of step execution nodes, side-by-side payloads, low confidence warnings, and root-cause analysis triggers.

---

## 🔗 2. Depends On
* `05-backward-trace-analyzer.md`

---

## 📂 3. File & Module Map

* `ui/app.py` ➔ Streamlit main landing and routing controller.
* `ui/components/graph.py` ➔ Displays interactive execution graphs with state colors.
* `ui/components/diff_view.py` ➔ Implements the strict three-column data comparison panel.
* `ui/components/metrics.py` ➔ Render pip rows and token cost aggregates.

---

## 📝 4. Interface Contracts

### Visual Styles Configuration
* **Emerald Green (`#22c55e`)** ➔ Successful executions with high confidence scores.
* **Amber Yellow (`#eab308`)** ➔ Executions that generated data with warnings (self-score ≤ 2).
* **Coral Red (`#ef4444`)** ➔ Root cause node identified by the backward analyzer.
* **Slate Gray (`#94a3b8`)** ➔ Downstream steps aborted during execution.

### Interactive Flag Route Action
* **Endpoint Interaction**:
  ```http
  POST /api/traces/{trace_id}/flag
  Content-Type: application/json
  
  {
     "reason": "User confirmed hallucination in extraction step."
  }
  ```

---

## ⚙️ 5. Rules for Implementation

* **Responsive Columns**: Ensure the visual payload diff panel displays precisely three columns ("Step Received", "Step Produced", "Expected Output"). Never allow content to collapse to single column wraps on desktop screen viewports.
* **Progressive Loading**: Triggering a "Flag Trace" operation must show a standard Streamlit loading indicator (`st.spinner()`) and render diagnostics reports directly below the node layout without causing full page re-render.
* **Confidence Display**: Render confidence ratings strictly using Unicode filled pips (`● ● ● ○ ○` for score 3) rather than naked numerals or percentage decimals.

---

## ✅ 6. Definition of Done (DoD)

- [ ] **Visually Verified Layout**: The trace dashboard displays a clear execution node chart using the assigned hex colors.
- [ ] **Side-by-side panels**: The diff display successfully separates input, output, and ground truth data into three aligned vertical sections.
- [ ] **Actionable Flag Trigger**: Clicking the flagging element successfully performs server-side analysis and displays reports inline.
- [ ] **Stars / Pips validation**: Verify that confidence scores are rendered as unicode pip tracks.
- [ ] **No Hardcoded Assets**: Ensure visual layouts adjust dynamically to user color mode configurations (light or dark backgrounds).
