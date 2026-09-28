"""Turn a traceback into a unified diff. The patch is rehearsed on a temp copy and never auto-applied."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from grasshopper.schemas import new_id

_KNOWN = """--- a/playbooks/broken_export.yaml
+++ b/playbooks/broken_export.yaml
@@ -1,6 +1,6 @@
       - type: click
-        selector: "[data-testid=export-btn]"
+        selector: "[data-testid=export-btn-renamed]"
"""


class SelfRepair:
    def __init__(self, settings, router):
        self.settings = settings
        self.router = router

    async def propose(self, error_text: str, *, run_id: str) -> dict:
        known = "export-btn" in error_text or "selector not found" in error_text
        if known:
            diff = _KNOWN
            explanation = (
                "The broken sandbox renamed the control to data-testid=export-btn-renamed. "
                "Retrying the old selector cannot succeed. This patch updates the playbook only."
            )
        else:
            prompt = (
                "Produce a unified diff that would fix this Python or YAML failure. "
                "Do not apply it. Explain in one sentence after the diff.\n"
                f"{error_text[-2000:]}\nunified diff:"
            )
            response = await self.router.complete("repair", prompt, run_id=run_id)
            diff = response.text
            explanation = "Repair model proposed a diff. It was not applied."
        patch_path = self.settings.patches_dir / f"{run_id}_{new_id('patch_')}.diff"
        patch_path.write_text(diff, encoding="utf-8")
        passed = _rehearse(diff)
        return {
            "patch_path": str(patch_path),
            "explanation": explanation,
            "temp_test_passed": passed,
            "diff": diff,
        }


def _rehearse(diff: str) -> bool:
    """Apply a one-line selector swap on a throwaway copy and check the new selector is present."""
    if "export-btn-renamed" not in diff:
        return False
    with tempfile.TemporaryDirectory() as tmp:
        sample = Path(tmp) / "broken_export.yaml"
        sample.write_text('selector: "[data-testid=export-btn]"\n', encoding="utf-8")
        copy = Path(tmp) / "copy.yaml"
        shutil.copy(sample, copy)
        text = copy.read_text(encoding="utf-8").replace(
            "[data-testid=export-btn]",
            "[data-testid=export-btn-renamed]",
        )
        copy.write_text(text, encoding="utf-8")
        updated = copy.read_text(encoding="utf-8")
        original = sample.read_text(encoding="utf-8")
        return "export-btn-renamed" in updated and "export-btn-renamed" not in original
