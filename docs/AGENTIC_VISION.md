# Agentic Vision Note

OpenCV 5 visual perception informs subsequent agent actions. Flow: screenshot → `detect_regions` / `change_percent` → fallback to "Continue" control if selectors break → click. Sensitive/costly actions pause for human approval.

## Measurement

`tests/test_vision_change_and_dom_recovery_are_measured` specifies a controlled test set: 10 identical cards unchanged, 10 shifted cards changed, 20 bounding boxes of "Continue" buttons with identifiers stripped. The test asserts that detection matches the ground-truth set completely and passes. This reflects performance on this controlled benchmark; rates on other cameras or live external sites remain unmeasured.

Third-party live page HTML was not deliberately mutated. The local REC scenario in `tests/test_realweb.py` recovers via text heuristics after selector disappearance and records vision model invocations.

## Jury Evidence

Diagram in `docs/ARCHITECTURE.md`. Artifacts: `*_regions.png` and `blast_radius.json` in the run directory. AWS deployment steps documented in `docs/OPENCV_AWS.md`. Live cloud deployment unmeasured.
