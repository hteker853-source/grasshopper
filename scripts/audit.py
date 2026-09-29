#!/usr/bin/env python3
"""Check competition readiness and write docs/AUDIT.md.

Missing real API keys are "⏳ anahtar bekliyor", not failures. The script never
prints a secret value.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PASS = "✅"
WAIT = "⏳ waiting for key"
FAIL = "❌"

_TOKEN = re.compile(
    r"(\b\d{8,12}:[A-Za-z0-9_-]{30,}\b|sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|\b[0-9a-fA-F]{64,}\b)"
)
_KEY_FLAGS = {
    "bedrock": ["AWS_REGION", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "BEDROCK_MODEL_ID"],
    "nebius": ["NEBIUS_API_KEY", "NEBIUS_BASE_URL", "NEBIUS_FAST_MODEL"],
    "tavily": ["TAVILY_API_KEY"],
    "assemblyai": ["ASSEMBLYAI_API_KEY"],
    "solana-devnet": ["WALLET_KEYPAIR_PATH"],
    "gemma": ["GEMMA_MODEL"],
    "azure": ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION"],
    "meta": ["META_API_KEY", "META_BASE_URL", "WHATSAPP_TOKEN"],
}


@dataclass
class Row:
    name: str
    status: str
    missing: str


def missing_keys(names: list[str], env: dict[str, str]) -> list[str]:
    return [name for name in names if not (env.get(name) or "").strip()]


def wants_form(required: str) -> bool:
    return bool(re.search(r"\bform\b", required.lower()))


def wants_pr(required: str) -> bool:
    text = required.lower()
    return "pull request" in text or bool(re.search(r"\bpr\b", text))


def flag_code_ready(flag: str, root: Path = ROOT) -> bool:
    checks = {
        "mcp": root / "grasshopper" / "mcp_server" / "server.py",
        "mit": root / "LICENSE",
        "explainer": root / "grasshopper" / "core" / "explainer.py",
        "opencv": root / "grasshopper" / "browser" / "vision.py",
        "prototype": root / "grasshopper" / "ui" / "templates" / "dashboard.html",
        "agent": root / "grasshopper" / "core" / "orchestrator.py",
        "founder": root / "playbooks" / "shop_old_listings.yaml",
        "vultr": root / "grasshopper" / "sandbox_runner" / "vultr.py",
        "climate": root / "grasshopper" / "realweb" / "climate.py",
        "ing": root / "grasshopper" / "realweb" / "bank.py",
        "asus": root / "submissions" / "asus" / "PRESENTATION.md",
        "human": root / "docs" / "INSAN_ISLERI.md",
    }
    path = checks.get(flag)
    if path is None:
        return flag in _KEY_FLAGS and _key_flag_code(flag, root)
    if flag == "mit":
        return path.is_file() and "MIT License" in path.read_text(encoding="utf-8")
    if flag == "opencv":
        req = (root / "requirements.txt").read_text(encoding="utf-8")
        text = path.read_text(encoding="utf-8")
        return "import cv2" in text and "opencv-python-headless==5" in req
    if flag == "mcp":
        text = path.read_text(encoding="utf-8")
        return "def run_task" in text and "MCPServer" in text
    return path.is_file()


def _key_flag_code(flag: str, root: Path) -> bool:
    files = {
        "bedrock": root / "grasshopper" / "providers" / "llm_bedrock.py",
        "nebius": root / "grasshopper" / "providers" / "factory.py",
        "tavily": root / "grasshopper" / "providers" / "search_tavily.py",
        "solana-devnet": root / "grasshopper" / "providers" / "wallet_solana_devnet.py",
        "gemma": root / "grasshopper" / "providers" / "llm_ollama.py",
        "azure": root / "grasshopper" / "providers" / "stt_azure.py",
        "meta": root / "grasshopper" / "providers" / "notify_whatsapp.py",
        "assemblyai": root / "grasshopper" / "providers" / "stt_assemblyai.py",
    }
    path = files.get(flag)
    return path is not None and path.is_file()


def competition_row(
    row: dict,
    env: dict[str, str],
    *,
    video_ok: bool,
    mcp_ok: bool,
    has_form: bool,
    has_pr: bool,
    root: Path = ROOT,
) -> Row:
    flag = str(row.get("flag") or "")
    required = str(row.get("required") or "")
    name = f"{row.get('name', row.get('slug', flag))} (`{flag}`)"
    gaps: list[str] = []
    keys = _KEY_FLAGS.get(flag, [])
    absent = missing_keys(keys, env) if keys else []
    if absent:
        gaps.append("key: " + ", ".join(absent))
    if "video" in required.lower() and not video_ok:
        gaps.append("video")
    if wants_form(required) and not has_form:
        gaps.append("form")
    if wants_pr(required) and not has_pr:
        gaps.append("PR")
    code_ok = flag_code_ready(flag, root) and (flag != "mcp" or mcp_ok)
    if flag == "mcp" and not mcp_ok:
        gaps.append("MCP tool list")
    if absent:
        return Row(name, WAIT, "; ".join(gaps))
    if not code_ok or any(item in {"video", "form", "PR"} for item in gaps) or (flag == "mcp" and not mcp_ok):
        return Row(name, FAIL, "; ".join(gaps) or "flag not satisfied")
    note = str(row.get("audit_note") or "")
    if row.get("eligible") is False:
        note = "eligible=false in competitions.json"
    return Row(name, PASS, note)


def readme_gaps(text: str) -> list[str]:
    gaps = []
    lower = text.lower()
    if "scripts/setup.sh" not in text and "setup" not in lower and "kurulum" not in lower and "## run it" not in lower:
        gaps.append("setup")
    if "| competition |" not in lower and "| yar\u0131\u015fma |" not in lower:
        gaps.append("competition table")
    return gaps


def _trivial_assert(node: ast.Assert) -> bool:
    test = node.test
    if isinstance(test, ast.Constant):
        return True
    if isinstance(test, ast.Compare) and _constant(test.left) and all(_constant(item) for item in test.comparators):
        return True
    return False


def _constant(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.Constant):
        return True
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return all(_constant(item) for item in node.elts)
    return False


def _uses_raises(fn: ast.AST) -> bool:
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "raises":
            return True
    return False


def fake_tests(paths: list[Path]) -> list[str]:
    """Test functions with no assert/pytest.raises, or with a constant assertion."""
    found = []
    for path in paths:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            found.append(f"{path}: unreadable")
            continue
        for node in tree.body:
            funcs = []
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs = [node]
            elif isinstance(node, ast.ClassDef):
                funcs = [item for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))]
            for fn in funcs:
                if not fn.name.startswith("test_"):
                    continue
                asserts = [item for item in ast.walk(fn) if isinstance(item, ast.Assert)]
                if any(_trivial_assert(item) for item in asserts) or (not asserts and not _uses_raises(fn)):
                    found.append(f"{path.name}:{fn.name}")
    return found


def secret_hits(files: list[Path]) -> list[str]:
    """Filenames whose contents match a token pattern. The value is not returned."""
    hits = []
    for path in files:
        if path.name == ".env" or not path.is_file():
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".db", ".pyc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if _TOKEN.search(text):
            hits.append(str(path))
    return hits


def env_is_tracked(tracked: list[str]) -> bool:
    return any(name == ".env" or name.endswith("/.env") for name in tracked)


def video_ok(path: Path) -> tuple[bool, str]:
    if not path.is_file():
        return False, "missing"
    from grasshopper.publish.demo_edit import probe_duration

    try:
        duration = probe_duration(path)
    except (OSError, subprocess.CalledProcessError, ValueError):
        return False, "unreadable"
    if duration > 180:
        return False, f"{duration:.0f}s"
    return True, f"{duration:.0f}s"


def mcp_tools_ok(names: set[str]) -> bool:
    return {"run_task", "get_task_status", "approve"}.issubset(names)


def _tracked_names() -> list[str]:
    if not (ROOT / ".git").exists():
        return []
    proc = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    return [line for line in proc.stdout.splitlines() if line]


def _live_mcp_tools() -> set[str]:
    import httpx

    port = 18771
    work = Path(tempfile.mkdtemp(prefix="grasshopper-audit-"))
    env = os.environ.copy()
    for key in (
        "TELEGRAM_BOT_TOKEN", "TELEGRAM_ALLOWED_USER_ID", "WHATSAPP_TOKEN",
        "NEBIUS_API_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
        "AZURE_OPENAI_API_KEY", "AZURE_SPEECH_KEY", "META_API_KEY",
        "OPENAI_COMPAT_API_KEY", "ASSEMBLYAI_API_KEY", "TAVILY_API_KEY", "WALLET_KEYPAIR_PATH",
    ):
        env[key] = ""
    env.update({
        "MODE": "mock",
        "BROWSER_DRIVER": "http",
        "GRASSHOPPER_EMBED_SANDBOX": "0",
        "API_TOKEN": "audit-token",
        "GRASSHOPPER_DATA_DIR": str(work),
        "GRASSHOPPER_DB": str(work / "gh.db"),
        "GRASSHOPPER_RUNS_DIR": str(work / "runs"),
        "SANDBOX_BASE_URL": "http://127.0.0.1:9",
    })
    log = (work / "audit-server.log").open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "grasshopper.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.time() + 30
        url = f"http://127.0.0.1:{port}/health"
        while time.time() < deadline:
            if proc.poll() is not None:
                return set()
            try:
                httpx.get(url, timeout=0.4)
                break
            except Exception:
                time.sleep(0.2)
        else:
            return set()
        from mcp import Client

        async def listed() -> set[str]:
            async with Client(f"http://127.0.0.1:{port}/mcp/") as client:
                tools = await client.list_tools()
                return {tool.name for tool in tools.tools}

        import asyncio
        return asyncio.run(listed())
    except Exception:
        return set()
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        log.close()


def build_rows(*, env: dict[str, str] | None = None, mcp_names: set[str] | None = None) -> list[Row]:
    from grasshopper.config import load_dotenv

    load_dotenv()
    env = os.environ if env is None else env
    rows_json = json.loads((ROOT / "data" / "competitions.json").read_text(encoding="utf-8"))
    demo = ROOT / "videos" / "demo.mp4"
    ok_video, video_detail = video_ok(demo)
    names = mcp_names if mcp_names is not None else _live_mcp_tools()
    mcp_ok = mcp_tools_ok(names)
    rows: list[Row] = []
    for item in rows_json:
        slug = item.get("slug", "")
        form = (ROOT / "submissions" / slug / "CHECKLIST.md").is_file()
        pr = (ROOT / "submissions" / slug / "PR_URL").is_file()
        rows.append(competition_row(item, env, video_ok=ok_video, mcp_ok=mcp_ok, has_form=form, has_pr=pr))
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    rows.append(Row("LICENSE is MIT", PASS if license_text.startswith("MIT License") else FAIL, "" if license_text.startswith("MIT License") else "LICENSE"))
    tracked = _tracked_names()
    if not (ROOT / ".git").exists():
        rows.append(Row("Secrets stay out of git", FAIL, "git repo is not initialized"))
    else:
        hits = secret_hits([ROOT / name for name in tracked])
        tracked_env = env_is_tracked(tracked)
        gaps = []
        if tracked_env:
            gaps.append(".env is tracked")
        if hits:
            gaps.append("token pattern in " + ", ".join(Path(hit).name for hit in hits))
        rows.append(Row("Secrets stay out of git", PASS if not gaps else FAIL, "; ".join(gaps)))
    fakes = fake_tests(sorted((ROOT / "tests").glob("test_*.py")))
    rows.append(Row("Tests assert something real", PASS if not fakes else FAIL, ", ".join(fakes)))
    rows.append(Row("videos/demo.mp4 ≤ 180s", PASS if ok_video else FAIL, video_detail))
    tool_note = ", ".join(sorted(names)) if names else "no tools"
    rows.append(Row("MCP /mcp tool list", PASS if mcp_ok else FAIL, tool_note))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    gaps = readme_gaps(readme)
    rows.append(Row("README setup and competition table", PASS if not gaps else FAIL, ", ".join(gaps)))
    return rows


def render(rows: list[Row]) -> str:
    lines = [
        "# Audit",
        "",
        "Real keys that are still empty are waiting, not failed. Nothing here is submitted.",
        "",
        "| Check | Status | Missing |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        missing = row.missing.replace("|", "\\|")
        lines.append(f"| {row.name} | {row.status} | {missing} |")
    ok = sum(row.status == PASS for row in rows)
    wait = sum(row.status.startswith("⏳") for row in rows)
    bad = sum(row.status == FAIL for row in rows)
    lines.extend(["", f"{ok} ✅ / {wait} ⏳ / {bad} ❌", ""])
    return "\n".join(lines)


def counts(rows: list[Row]) -> tuple[int, int, int]:
    return (
        sum(row.status == PASS for row in rows),
        sum(row.status.startswith("⏳") for row in rows),
        sum(row.status == FAIL for row in rows),
    )


def main() -> int:
    rows = build_rows()
    text = render(rows)
    dest = ROOT / "docs" / "AUDIT.md"
    dest.write_text(text, encoding="utf-8")
    ok, wait, bad = counts(rows)
    print(f"Audit: {ok} ✅ / {wait} ⏳ / {bad} ❌")
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
