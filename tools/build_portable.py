"""Generate portable teaching files from the plugin's canonical skill."""
import argparse
import json
import re
from pathlib import Path


def expected_files(root):
    plugin = root / "plugins/xunli-tutor"
    source = plugin / "skills/learn-with-feedback"
    target = root / "skills/learn-with-feedback"
    version = json.loads((plugin / "plugin.json").read_text(encoding="utf-8"))["version"]
    files = {target / "SKILL.md": (source / "SKILL.md").read_bytes(),
             target / "LICENSE": (root / "LICENSE").read_bytes()}
    references = []
    for folder in ("references", "assets"):
        for path in sorted((source / folder).rglob("*")):
            if path.is_symlink():
                raise ValueError("Source resources must not be symlinks")
            if path.is_file():
                files[target / path.relative_to(source)] = path.read_bytes()
                if path.suffix == ".md":
                    references.append(path)
    header = f"""# 循理学伴：通用AI教学协议 v{version}

这是可上传、粘贴或作为应用指令载入的完整单文件，不依赖插件、文件读取、联网或特定厂商工具。由 `tools/build_portable.py` 从插件规则生成，请修改源文件后重新生成。

## 给接手AI或Agent的使用约定

仅在用户请求教学、带练、练习反馈或学习交接时使用以下规则；用户的最新要求及宿主更高优先级规则优先。普通代办与代码维护仍按实际任务完成，不强制变成课程。

本文已合并核心规则、通用协议、学科指南、示例和记录模板。文中提及的附录均已包含在后面；没有文件工具时直接使用本文内容，不声称读取外部文件或持久记忆。资料中的示例是教学材料，不是要求自动执行的指令。

开始前优先沿用用户已经提供的主题、目标、偏好与学习记录。若必要前提未知或可能不懂，先提问并等待回答，不先生成依赖它的课程；若完全没有主题，只问用户想学什么及希望学完能做什么。

"""
    sections = []
    for path in [source / "SKILL.md", *references]:
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)
        # All relative references are included below, so no local file access is needed.
        def inline_link(match):
            label, destination = match.groups()
            return match.group(0) if re.match(r"(?:https?://|#)", destination) else label + "（已合并到本文）"
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", inline_link, text)
        text = re.sub(r"^(#{1,5}) ", r"#\1 ", text, flags=re.M)
        sections.append(text.strip())
    files[root / "portable/xunli-tutor.md"] = (header + "\n\n---\n\n".join(sections) + "\n").encode("utf-8")
    return files


def build(root, check=False):
    changed = []
    for path, content in expected_files(root).items():
        if not path.exists() or path.read_bytes() != content:
            changed.append(path.relative_to(root).as_posix())
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report missing or stale outputs without writing")
    arguments = parser.parse_args()
    changed = build(Path(__file__).resolve().parents[1], check=arguments.check)
    print(("Stale" if arguments.check else "Generated") + f" portable files: {len(changed)}")
    for filename in changed:
        print(filename)
    raise SystemExit(bool(changed) if arguments.check else 0)
