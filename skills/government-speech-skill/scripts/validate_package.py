#!/usr/bin/env python3
"""Validate the government-speech-skill package without third-party modules."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


EXPECTED_NAME = "government-speech-skill"
ALLOWED_TOP_LEVEL = {"SKILL.md", "references", "examples", "scripts"}
ALLOWED_SCRIPTS = {"validate_package.py"}
REFERENCE_FILES = (
    "document-type-rules.md",
    "scene-structure-rules.md",
    "role-audience-rules.md",
    "material-processing-rules.md",
    "language-style-rules.md",
    "ai-style-rules.md",
    "length-format-rules.md",
    "proofreading-rules.md",
    "fallback-output-templates.md",
)
REQUIRED_FILES = (
    "SKILL.md",
    *(f"references/{name}" for name in REFERENCE_FILES),
    "examples/task-examples.md",
    "examples/boundary-cases.md",
    "scripts/validate_package.py",
)
SEMANTIC_VERSION = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
YAML_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$")


class FrontmatterError(ValueError):
    """Raised when SKILL.md frontmatter is absent or malformed."""


def _strip_yaml_comment(value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
            continue
        if quote == '"' and character == "\\":
            escaped = True
            continue
        if character in {"'", '"'}:
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
            continue
        if character == "#" and quote is None and (
            index == 0 or value[index - 1].isspace()
        ):
            return value[:index].rstrip()
    if quote is not None:
        raise FrontmatterError("YAML 字符串引号未闭合")
    return value.rstrip()


def _parse_yaml_scalar(value: str) -> Any:
    value = _strip_yaml_comment(value).strip()
    if not value:
        return ""
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError) as error:
            raise FrontmatterError(f"YAML 双引号字符串无效：{error.msg}") from error
        if not isinstance(parsed, str):
            raise FrontmatterError("YAML 双引号值必须是字符串")
        return parsed
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise FrontmatterError("YAML 单引号字符串未闭合")
        return value[1:-1].replace("''", "'")
    lowered = value.lower()
    if lowered in {"null", "~"}:
        return None
    if lowered in {"true", "false"}:
        return lowered == "true"
    return value


def _parse_yaml_mapping(frontmatter: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, result)]
    mapping_indentation = {id(result): 0}
    lines = frontmatter.splitlines()
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        index += 1
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            raise FrontmatterError(f"第 {index} 行使用了制表符缩进")

        indentation = len(raw_line) - len(raw_line.lstrip(" "))
        while len(stack) > 1 and indentation <= stack[-1][0]:
            stack.pop()
        if len(stack) == 1 and indentation != 0:
            raise FrontmatterError(f"第 {index} 行存在意外缩进")

        match = YAML_KEY.fullmatch(raw_line.strip())
        if match is None:
            raise FrontmatterError(f"第 {index} 行不是有效的 YAML 键值映射")
        key, raw_value = match.groups()
        current = stack[-1][1]
        expected_indentation = mapping_indentation.setdefault(id(current), indentation)
        if indentation != expected_indentation:
            raise FrontmatterError(f"第 {index} 行的同级映射缩进不一致")
        if key in current:
            raise FrontmatterError(f"第 {index} 行包含重复键：{key}")

        if raw_value in {"|", ">", "|-", ">-", "|+", ">+"}:
            block_lines: list[str] = []
            while index < len(lines):
                candidate = lines[index]
                candidate_indent = len(candidate) - len(candidate.lstrip(" "))
                if candidate.strip() and candidate_indent <= indentation:
                    break
                block_lines.append(candidate[indentation + 1 :].lstrip(" "))
                index += 1
            separator = "\n" if raw_value.startswith("|") else " "
            current[key] = separator.join(block_lines).strip()
        elif raw_value == "":
            nested: dict[str, Any] = {}
            current[key] = nested
            stack.append((indentation, nested))
        else:
            current[key] = _parse_yaml_scalar(raw_value)

    return result


def extract_frontmatter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("SKILL.md 缺少起始 YAML frontmatter 分隔符")
    try:
        closing_index = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration as error:
        raise FrontmatterError("SKILL.md 缺少结束 YAML frontmatter 分隔符") from error
    frontmatter = "\n".join(lines[1:closing_index])
    if not frontmatter.strip():
        raise FrontmatterError("SKILL.md 的 YAML frontmatter 为空")
    return _parse_yaml_mapping(frontmatter)


def _read_utf8(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        errors.append(f"文件不是有效的 UTF-8：{path}（字节 {error.start}）")
    except OSError as error:
        errors.append(f"无法读取文件：{path}（{error}）")
    return None


def validate_package(package_path: Path) -> list[str]:
    errors: list[str] = []
    package_path = package_path.resolve()
    if not package_path.is_dir():
        return [f"包目录不存在或不是目录：{package_path}"]
    if package_path.name != EXPECTED_NAME:
        errors.append(
            f"包目录名应为 {EXPECTED_NAME}，实际为 {package_path.name}"
        )

    try:
        top_level_names = {entry.name for entry in package_path.iterdir()}
    except OSError as error:
        return [f"无法读取包目录：{package_path}（{error}）"]
    for unexpected in sorted(top_level_names - ALLOWED_TOP_LEVEL):
        errors.append(f"顶层包含不允许的条目：{unexpected}")

    scripts_path = package_path / "scripts"
    if scripts_path.is_dir():
        try:
            script_names = {entry.name for entry in scripts_path.iterdir()}
        except OSError as error:
            errors.append(f"无法读取 scripts 目录：{scripts_path}（{error}）")
        else:
            for unexpected in sorted(script_names - ALLOWED_SCRIPTS):
                errors.append(f"scripts 包含不允许的条目：scripts/{unexpected}")

    missing_files: list[str] = []
    for relative_path in REQUIRED_FILES:
        candidate = package_path / relative_path
        if not candidate.is_file():
            missing_files.append(relative_path)
    errors.extend(f"缺少必需文件：{relative_path}" for relative_path in missing_files)

    for candidate in sorted(package_path.rglob("*")):
        if candidate.is_file() and candidate.suffix.lower() in {".md", ".py"}:
            _read_utf8(candidate, errors)

    skill_path = package_path / "SKILL.md"
    if not skill_path.is_file():
        return errors
    skill_text = _read_utf8(skill_path, errors)
    if skill_text is None:
        return errors

    try:
        frontmatter = extract_frontmatter(skill_text)
    except FrontmatterError as error:
        errors.append(f"YAML frontmatter 无效：{error}")
    else:
        if frontmatter.get("name") != EXPECTED_NAME:
            errors.append(f"frontmatter 的 name 必须为 {EXPECTED_NAME}")
        description = frontmatter.get("description")
        if not isinstance(description, str) or not description.strip():
            errors.append("frontmatter 的 description 必须是非空字符串")
        metadata = frontmatter.get("metadata")
        if not isinstance(metadata, dict) or not metadata:
            errors.append("frontmatter 的 metadata 必须是非空映射")
        else:
            version = metadata.get("version")
            if not isinstance(version, str) or SEMANTIC_VERSION.fullmatch(version) is None:
                errors.append("frontmatter 的 metadata.version 必须是语义化版本号")

    for reference_name in REFERENCE_FILES:
        reference_path = f"references/{reference_name}"
        if reference_path not in skill_text:
            errors.append(f"SKILL.md 未引用规则文件：{reference_path}")
    for tool_name in ("knowledge_search", "read_uploaded_file"):
        if tool_name not in skill_text:
            errors.append(f"SKILL.md 未包含工具名：{tool_name}")
    for mapping_term in ("files", "file_id"):
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(mapping_term)}(?![A-Za-z0-9_])", skill_text) is None:
            errors.append(f"SKILL.md 未明确包含映射术语：{mapping_term}")

    # Core routing and output-contract invariants.
    required_skill_terms = (
        "用户直接提供", "素材来源", "真实性 > 任务正确性",
        "〔待补充〕", "〔待核实〕", "只输出目标文本",
        "最多 4 次", "禁止在素材获取完成前起草",
    )
    for term in required_skill_terms:
        if term not in skill_text:
            errors.append(f"SKILL.md 缺少核心约束：{term}")

    # All 16 supported document types must be present in the external rule file.
    document_path = package_path / "references/document-type-rules.md"
    document_text = _read_utf8(document_path, errors) if document_path.is_file() else None
    document_types = (
        "讲话稿", "演讲稿", "发言稿", "表态发言", "主持词", "致辞",
        "动员讲话", "总结讲话", "会议讲话", "专题讲话", "工作部署讲话",
        "交流发言", "典型经验发言", "宣传稿", "公开信", "感谢信",
    )
    if document_text is not None:
        for doc_type in document_types:
            if re.search(rf"^## {re.escape(doc_type)}$", document_text, re.MULTILINE) is None:
                errors.append(f"文种规则缺少二级标题：{doc_type}")

    # Rule files should contain meaningful headings instead of placeholders.
    for reference_name in REFERENCE_FILES:
        path = package_path / "references" / reference_name
        if not path.is_file():
            continue
        text = _read_utf8(path, errors)
        if text is None:
            continue
        if len(text.strip()) < 300:
            errors.append(f"规则文件内容过短，疑似占位：references/{reference_name}")
        if not re.search(r"^# \S", text, re.MULTILINE):
            errors.append(f"规则文件缺少一级标题：references/{reference_name}")

    # Examples must cover both positive flows and boundaries.
    task_examples = package_path / "examples/task-examples.md"
    boundary_examples = package_path / "examples/boundary-cases.md"
    if task_examples.is_file():
        text = _read_utf8(task_examples, errors)
        if text is not None and len(re.findall(r"^## 示例 \d+", text, re.MULTILINE)) < 8:
            errors.append("examples/task-examples.md 至少应包含 8 个任务示例")
    if boundary_examples.is_file():
        text = _read_utf8(boundary_examples, errors)
        if text is not None and len(re.findall(r"^## 边界 \d+", text, re.MULTILINE)) < 10:
            errors.append("examples/boundary-cases.md 至少应包含 10 个边界案例")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("验证失败：请提供一个待验证的包目录。")
        print(f"用法：python3 {Path(argv[0]).name} <{EXPECTED_NAME}目录>")
        return 1

    errors = validate_package(Path(argv[1]))
    if errors:
        print("验证失败：发现以下问题：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("验证通过：government-speech-skill 包结构和核心规则符合要求。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
