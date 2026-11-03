"""Offline package checks using only Python's standard library (Python >= 3.10)."""

import json
import importlib.util
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def validate(root):
    errors = []
    checks = 0

    def check(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(message)

    def read_json(path):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            return {}

    def inside(path, boundary):
        return path.resolve().is_relative_to(boundary.resolve())

    plugin = root / "plugins/xunli-tutor"
    portable = read_json(plugin / "plugin.json")
    legacy = read_json(plugin / ".codex-plugin/plugin.json")
    market = read_json(root / ".agents/plugins/marketplace.json")
    scenarios = read_json(root / "evals/scenarios.json")
    extension = portable.get("extensions", {}).get("com.openai", {})
    check(portable.get("name") == "xunli-tutor", "Unexpected plugin name")
    check(bool(re.fullmatch(r"\d+\.\d+\.\d+", portable.get("version", ""))), "Invalid version")
    check(portable.get("license") == "MIT", "Missing MIT declaration")
    for field in ("name", "version", "description", "author", "license"):
        check(portable.get(field) == legacy.get(field), f"Manifest mismatch: {field}")
    check(extension.get("interface") == legacy.get("interface"), "Interface metadata differs")
    check(extension.get("onboardingSkill") == legacy.get("extensions", {}).get("com.openai", {}).get("onboardingSkill"), "Onboarding differs")
    onboarding = extension.get("onboardingSkill", "")
    check(onboarding.startswith("./"), "Onboarding must use a relative plugin path")
    check(inside(plugin / onboarding, plugin) and (plugin / onboarding).is_file(), "Onboarding target missing or outside plugin")
    check(legacy.get("skills") == "./skills/", "Legacy skills path invalid")
    check(market.get("name") == "xunli-tutor-local", "Unexpected marketplace name")
    for item in market.get("plugins", []):
        source = item.get("source", {})
        source_path = source.get("path", "")
        check(source.get("source") == "local", "Unexpected marketplace source")
        check(source_path.startswith("./") and inside(root / source_path, root), "Unsafe marketplace path")
        check((root / source_path / "plugin.json").is_file(), "Marketplace plugin missing")
        check(item.get("policy", {}).get("installation") == "AVAILABLE", "Unexpected install policy")
        check("authentication" in item.get("policy", {}), "Missing auth policy")
    check(len(market.get("plugins", [])) == 1, "Expected one marketplace entry")
    skills = sorted((plugin / "skills").glob("*/SKILL.md"))
    check(len(skills) == 1, "Expected one teaching skill")
    for path in skills:
        content = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", content, re.S)
        check(match is not None, "Missing skill frontmatter")
        if match:
            # This package deliberately uses only plain single-line scalar fields.
            fields = dict(line.split(": ", 1) for line in match[1].splitlines() if ": " in line)
            check(fields.get("name") == path.parent.name, "Skill folder/name mismatch")
            check(0 < len(fields.get("description", "")) <= 1024, "Invalid skill description")
            check(set(fields) == {"name", "description"}, "Unexpected frontmatter keys")
    for path in root.rglob("*"):
        if ".git" in path.relative_to(root).parts or "__pycache__" in path.parts:
            continue
        check(not path.is_symlink(), f"Symlink in package: {path.relative_to(root)}")
        if not path.is_file():
            continue
        if path.suffix in {".md", ".json", ".yaml", ".py"}:
            content = path.read_text(encoding="utf-8")
            check("\ufffd" not in content, f"Encoding damage: {path.relative_to(root)}")
            if path.suffix != ".py":
                check(not re.search(r"(?:[A-Z]:[/\\]Users[/\\]|/Users/|/home/)[^\s]+", content), f"Personal absolute path: {path.relative_to(root)}")
        if path.suffix == ".md":
            content = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
            for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", content):
                url = urlsplit(target)
                if url.scheme or not url.path:
                    continue
                linked = path.parent / unquote(url.path)
                check(inside(linked, root) and linked.exists(), f"Broken local link in {path.relative_to(root)}: {target}")
    if isinstance(scenarios, list):
        check(len(scenarios) >= 8, "Missing behavior scenarios")
        ids = [s.get("id") for s in scenarios]
        check(len(ids) == len(set(ids)), "Duplicate scenario IDs")
        for scenario in scenarios:
            check(bool(scenario.get("messages")) and bool(scenario.get("pass")) and bool(scenario.get("critical_fail")), f"Incomplete scenario: {scenario.get('id')}")
    else:
        check(False, "Scenarios must be an array")
    for required in ("LICENSE", "README.md", "CONTRIBUTING.md", "evals/results.md"):
        check((root / required).is_file(), f"Missing {required}")
    check((plugin / "LICENSE").is_file(), "Plugin archive needs a license")
    spec = importlib.util.spec_from_file_location("portable_builder", Path(__file__).with_name("build_portable.py"))
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    check(not builder.build(root, check=True), "Portable files are missing or stale; run python tools/build_portable.py")
    return checks, errors


if __name__ == "__main__":
    repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    count, failures = validate(repo)
    for failure in failures:
        print(f"FAIL: {failure}")
    print(f"{count} checks; {len(failures)} failures")
    raise SystemExit(bool(failures))
