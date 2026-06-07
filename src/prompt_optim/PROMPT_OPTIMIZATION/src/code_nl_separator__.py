#!/usr/bin/env python3
"""
code_nl_separator__.py
--------------------------
Separates a Python source file into CODE-only and NATURAL-LANGUAGE-only parts.
Then compresses the NL part using compact_tokens__.py logic.

All paths are relative to THIS_DIR (the directory containing this script).
"""

import os
import sys
import ast
import tokenize
import io
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# THIS_DIR — all paths derived relative to this script's location
# Works correctly on both Windows and Linux
# ---------------------------------------------------------------------------
THIS_DIR = Path(__file__).resolve().parent

INPUT_FILENAME = "compress_target_file_1.py"
NL_FILENAME    = f"{Path(INPUT_FILENAME).stem}__NL_ONLY.md"  # compress_target_file_1__NL_ONLY.md

# ---------------------------------------------------------------------------
# Logger setup — uses the project's util_logger
# ---------------------------------------------------------------------------
sys.path.insert(0, str(THIS_DIR))
from util_logger import setup_logger

logger = setup_logger("code_nl_separator")


# ===========================================================================
# GLOBAL API TOGGLES — set Yes/No to control which LLM is used for compression
# ===========================================================================

CALL_CLAUDE_API = "No"   # Set to "Yes" to compress via Claude CLI
CALL_OPENAI_API = "Yes"  # Set to "Yes" to compress via OpenAI LLM


# ===========================================================================
# TASK-2 — get_code_nl_separate
# ===========================================================================

def get_code_nl_separate(input_filepath: str) -> tuple:
    """
    Reads a .py file and separates it into:
      - Code_Only_String   : well-formatted Python code (NL portions replaced with placeholders)
      - Natural_Language_Only_String : all extracted NL content with origin markers

    Handles:
      - Triple-quoted multiline strings (triple-double-quotes and triple-single-quotes)
      - Docstrings (module / class / function level)
      - Simple string assignments
      - Multiline f-strings
      - # comment lines that are prose (not structural like shebangs / coding declarations)

    Returns:
        tuple(str, str) -> (Code_Only_String, Natural_Language_Only_String)
    """
    input_filepath = str(input_filepath)
    logger.info(f"get_code_nl_separate() — START — input_filepath={input_filepath}")
    print(f"[DEBUG] get_code_nl_separate() — reading file: {input_filepath}")

    if not os.path.isfile(input_filepath):
        msg = f"File not found: {input_filepath}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    with open(input_filepath, "r", encoding="utf-8", errors="ignore") as fh:
        source_text = fh.read()

    source_lines = source_text.splitlines(keepends=True)
    total_lines = len(source_lines)
    logger.info(f"File read OK — total_lines={total_lines}, size={len(source_text)} bytes")
    print(f"[DEBUG] File read OK — {total_lines} lines, {len(source_text)} bytes")

    # ------------------------------------------------------------------
    # Phase 1 — AST-based extraction of string literals (NL candidates)
    # ------------------------------------------------------------------
    nl_spans = []  # list of (start_line, end_line, label, content)

    try:
        tree = ast.parse(source_text)
        logger.info("AST parse successful")
        print("[DEBUG] AST parse successful")
    except SyntaxError as e:
        logger.error(f"AST parse failed: {e}")
        print(f"[DEBUG] AST parse FAILED: {e} — falling back to tokenizer-only mode")
        tree = None

    if tree is not None:
        _extract_string_nodes(tree, source_lines, nl_spans)

    logger.info(f"AST extraction found {len(nl_spans)} NL spans")
    print(f"[DEBUG] AST extraction found {len(nl_spans)} NL spans")

    # ------------------------------------------------------------------
    # Phase 2 — Tokenizer-based extraction of # comment blocks
    # ------------------------------------------------------------------
    comment_spans = _extract_comment_blocks(source_text)
    logger.info(f"Tokenizer extraction found {len(comment_spans)} comment spans")
    print(f"[DEBUG] Tokenizer extraction found {len(comment_spans)} comment spans")

    # Merge comment spans into nl_spans (avoid overlaps)
    occupied = set()
    for (sl, el, _lbl, _c) in nl_spans:
        for ln in range(sl, el + 1):
            occupied.add(ln)

    for (sl, el, lbl, content) in comment_spans:
        overlap = any(ln in occupied for ln in range(sl, el + 1))
        if not overlap:
            nl_spans.append((sl, el, lbl, content))
            for ln in range(sl, el + 1):
                occupied.add(ln)

    # Sort by start line
    nl_spans.sort(key=lambda x: x[0])
    logger.info(f"Total NL spans after merge: {len(nl_spans)}")
    print(f"[DEBUG] Total NL spans after merge: {len(nl_spans)}")

    for i, (sl, el, lbl, _c) in enumerate(nl_spans):
        logger.debug(f"  NL_BLOCK_{i}: lines {sl}-{el} — {lbl}")
        print(f"[DEBUG]   NL_BLOCK_{i}: lines {sl}-{el} — {lbl}")

    # ------------------------------------------------------------------
    # Phase 3 — Build Code_Only and NL_Only strings
    # ------------------------------------------------------------------
    code_lines_out = []
    nl_parts_out = []
    nl_block_idx = 0
    skip_until = -1

    for line_num in range(1, total_lines + 1):  # 1-indexed
        # Check if this line is inside an NL span
        in_nl = False
        for (sl, el, lbl, content) in nl_spans:
            if sl <= line_num <= el:
                in_nl = True
                if line_num == sl:
                    # First line of this NL block — add placeholder to code, add content to NL
                    placeholder = f"# [NL_BLOCK_{nl_block_idx} EXTRACTED — lines {sl}-{el} — {lbl}]\n"
                    code_lines_out.append(placeholder)
                    section_header = f"\n--- NL_BLOCK_{nl_block_idx}: lines {sl}-{el}, {lbl} ---\n"
                    nl_parts_out.append(section_header)
                    nl_parts_out.append(content)
                    nl_parts_out.append("\n")
                    nl_block_idx += 1
                # Skip all lines in this span (already handled)
                break

        if not in_nl:
            code_lines_out.append(source_lines[line_num - 1])

    code_only_str = "".join(code_lines_out)
    nl_only_str = "".join(nl_parts_out)

    logger.info(f"Separation complete — code_size={len(code_only_str)}, nl_size={len(nl_only_str)}")
    print(f"[DEBUG] Separation complete — code_size={len(code_only_str)} bytes, nl_size={len(nl_only_str)} bytes")
    print(f"[DEBUG] get_code_nl_separate() — DONE")

    return (code_only_str, nl_only_str)


def _extract_string_nodes(tree, source_lines, nl_spans):
    """Walk AST and extract multiline string literals / docstrings as NL spans."""

    for node in ast.walk(tree):
        # --- Docstrings (module, class, function) ---
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if (node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                doc_node = node.body[0].value
                content = doc_node.value
                # Only extract if it's substantial NL (more than a short one-liner)
                if len(content.strip()) > 30 or "\n" in content:
                    sl = doc_node.lineno
                    el = doc_node.end_lineno if doc_node.end_lineno else sl
                    label = f"docstring in {_node_name(node)}"
                    raw = "".join(source_lines[sl - 1: el])
                    nl_spans.append((sl, el, label, raw))
                    logger.debug(f"  AST docstring: {label} lines {sl}-{el}")
                    print(f"[DEBUG]   AST docstring: {label} lines {sl}-{el}")

        # --- String assignments: variable = "..." or variable = f"..." ---
        if isinstance(node, ast.Assign):
            if (isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)):
                content = node.value.value
                if len(content.strip()) > 50 or "\n" in content:
                    val_node = node.value
                    sl = node.lineno
                    el = val_node.end_lineno if val_node.end_lineno else sl
                    target_name = _get_assign_target_name(node)
                    label = f"string assignment: {target_name}"
                    raw = "".join(source_lines[sl - 1: el])
                    nl_spans.append((sl, el, label, raw))
                    logger.debug(f"  AST string assign: {label} lines {sl}-{el}")
                    print(f"[DEBUG]   AST string assign: {label} lines {sl}-{el}")

            # Handle JoinedStr (f-strings) — Python 3.12+ may store as Constant
            elif isinstance(node.value, ast.JoinedStr):
                sl = node.lineno
                el = node.value.end_lineno if node.value.end_lineno else sl
                if el - sl >= 2:  # multiline f-string
                    target_name = _get_assign_target_name(node)
                    label = f"f-string assignment: {target_name}"
                    raw = "".join(source_lines[sl - 1: el])
                    nl_spans.append((sl, el, label, raw))
                    logger.debug(f"  AST f-string: {label} lines {sl}-{el}")
                    print(f"[DEBUG]   AST f-string: {label} lines {sl}-{el}")

        # --- Return statements with large strings ---
        if isinstance(node, ast.Return) and node.value:
            if (isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                    and (len(node.value.value.strip()) > 50 or "\n" in node.value.value)):
                val_node = node.value
                sl = node.lineno
                el = val_node.end_lineno if val_node.end_lineno else sl
                label = "return string literal"
                raw = "".join(source_lines[sl - 1: el])
                nl_spans.append((sl, el, label, raw))
                logger.debug(f"  AST return string: lines {sl}-{el}")

            elif isinstance(node.value, ast.JoinedStr):
                sl = node.lineno
                el = node.value.end_lineno if node.value.end_lineno else sl
                if el - sl >= 2:
                    label = "return f-string literal"
                    raw = "".join(source_lines[sl - 1: el])
                    nl_spans.append((sl, el, label, raw))


def _extract_comment_blocks(source_text: str) -> list:
    """Use tokenize to find # comment blocks (3+ consecutive comment lines = NL prose)."""
    comment_spans = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source_text).readline))
    except tokenize.TokenError as e:
        logger.warning(f"Tokenize error (partial parse): {e}")
        print(f"[DEBUG] Tokenize warning: {e}")
        return comment_spans

    # Collect all COMMENT tokens
    comment_tokens = [(tok.start[0], tok.string) for tok in tokens if tok.type == tokenize.COMMENT]

    if not comment_tokens:
        return comment_spans

    # Group consecutive comment lines into blocks
    block_start = comment_tokens[0][0]
    block_lines = [comment_tokens[0]]

    for i in range(1, len(comment_tokens)):
        prev_line = comment_tokens[i - 1][0]
        curr_line = comment_tokens[i][0]
        if curr_line == prev_line + 1:
            block_lines.append(comment_tokens[i])
        else:
            # End of block — save if 3+ lines (prose block, not single-line structural comments)
            if len(block_lines) >= 3:
                _save_comment_block(block_lines, comment_spans)
            block_start = curr_line
            block_lines = [comment_tokens[i]]

    # Final block
    if len(block_lines) >= 3:
        _save_comment_block(block_lines, comment_spans)

    return comment_spans


def _save_comment_block(block_lines, comment_spans):
    """Save a block of consecutive comment lines as an NL span."""
    sl = block_lines[0][0]
    el = block_lines[-1][0]
    content = "\n".join(tok_str for (_ln, tok_str) in block_lines) + "\n"
    # Skip blocks that look structural (shebangs, coding, pylint, noqa, type: ignore)
    structural_markers = ["#!/", "# -*-", "# coding", "# noqa", "# type:", "# pylint", "# flake8"]
    first_line = block_lines[0][1].strip()
    if any(first_line.startswith(m) for m in structural_markers):
        return
    label = "comment block"
    comment_spans.append((sl, el, label, content))


def _node_name(node) -> str:
    """Get a human-readable name for an AST node."""
    if isinstance(node, ast.Module):
        return "module"
    if isinstance(node, ast.ClassDef):
        return f"class {node.name}"
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return f"def {node.name}()"
    return "unknown"


def _get_assign_target_name(node) -> str:
    """Get the variable name from an ast.Assign node."""
    if node.targets and isinstance(node.targets[0], ast.Name):
        return node.targets[0].id
    return "unknown_var"


# ===========================================================================
# TASK-3 — write_to_out_dir_init
# ===========================================================================

def write_to_out_dir_init(code_only_str: str, nl_only_str: str, source_filename: str) -> str:
    """
    Creates a timestamped SUB_DIR under dir_out/ and writes:
      - FILE-1: <source_filename>__CODE_ONLY.py  (code-only content)
      - FILE-2: <source_filename>__NL_ONLY.md     (natural-language-only content)

    Args:
        code_only_str:    The code-only portion of the source file
        nl_only_str:      The natural-language-only portion
        source_filename:  Original filename (e.g. "compress_target_file_1.py")

    Returns:
        str: Full path to the created SUB_DIR
    """
    logger.info(f"write_to_out_dir_init() — START — source_filename={source_filename}")
    print(f"[DEBUG] write_to_out_dir_init() — START — source_filename={source_filename}")

    # Strip extension for prefix
    name_stem = Path(source_filename).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%Sh")

    sub_dir_name = f"SUB_DIR_{name_stem}__{timestamp}"
    out_base = THIS_DIR / "dir_out"
    sub_dir_path = out_base / sub_dir_name

    sub_dir_path = str(sub_dir_path)
    os.makedirs(sub_dir_path, exist_ok=True)
    logger.info(f"Created SUB_DIR: {sub_dir_path}")
    print(f"[DEBUG] Created SUB_DIR: {sub_dir_path}")

    # FILE-1: Code Only
    code_file = os.path.join(sub_dir_path, f"{name_stem}__CODE_ONLY.py")
    with open(code_file, "w", encoding="utf-8") as fh:
        fh.write(code_only_str)
    code_size = os.path.getsize(code_file)
    logger.info(f"Written FILE-1 (code-only): {code_file} — {code_size} bytes")
    print(f"[DEBUG] Written FILE-1: {code_file} — {code_size} bytes")

    # FILE-2: NL Only
    nl_file = os.path.join(sub_dir_path, f"{name_stem}__NL_ONLY.md")
    with open(nl_file, "w", encoding="utf-8") as fh:
        fh.write(nl_only_str)
    nl_size = os.path.getsize(nl_file)
    logger.info(f"Written FILE-2 (NL-only): {nl_file} — {nl_size} bytes")
    print(f"[DEBUG] Written FILE-2: {nl_file} — {nl_size} bytes")

    print(f"[DEBUG] write_to_out_dir_init() — DONE — sub_dir={sub_dir_path}")
    return sub_dir_path


# ===========================================================================
# TASK-8 — OpenAI LLM singleton 
# ===========================================================================

_OPENAI_COMPRESS_LLM = None


def _build_openai_compress_model():
    """Build OpenAI LLM for compression (same pattern as build_eval_model in eval_agents.py)."""
    from langchain.chat_models import init_chat_model
    return init_chat_model(
        model="gpt-4o-mini",
        temperature=0.0,
    )


def _get_openai_compress_llm():
    """Lazy singleton for OpenAI compress LLM."""
    global _OPENAI_COMPRESS_LLM
    if _OPENAI_COMPRESS_LLM is None:
        _OPENAI_COMPRESS_LLM = _build_openai_compress_model()
    return _OPENAI_COMPRESS_LLM


def _build_openai_compress_prompt(original: str) -> str:
    """
    Enhanced compression prompt for OpenAI.
    Targets better token reduction than build_compress_prompt in compact_tokens__.py
    by also collapsing redundant blank lines, merging short bullet runs, and
    abbreviating common filler phrases — while keeping all code blocks, URLs,
    headings, and file paths untouched.
    """
    return f"""You are an expert technical editor. Compress the markdown below into ULTRA-DENSE caveman style to maximise token reduction.

STRICT RULES (never break these):
- Do NOT touch anything inside ``` code blocks — reproduce them verbatim
- Do NOT touch inline backtick spans
- Preserve ALL URLs exactly as written
- Preserve ALL headings (lines starting with #) exactly
- Preserve all file paths and shell commands exactly
- Return ONLY the compressed markdown body — no outer fences, no preamble

COMPRESSION TARGETS (apply aggressively to natural-language prose only):
- Drop articles (a, an, the) everywhere they are not load-bearing
- Replace "in order to" → "to", "is able to" → "can", "due to the fact that" → "because"
- Replace "in addition" → "also", "however" → "but", "therefore" → "so"
- Collapse multi-line bullet lists into single dense lines where meaning is preserved
- Remove redundant blank lines (max 1 blank line between sections)
- Omit courtesy phrases ("please note", "it is important to", "keep in mind")
- Use numerals for numbers (three → 3)
- Abbreviate units where clear (seconds → s, milliseconds → ms)

TEXT TO COMPRESS:
{original}
"""


def call_opeanAI_compress(nl_text: str, sub_dir_path: str) -> str:
    """
    Compress *nl_text* using an OpenAI LLM (gpt-4o-mini singleton).
    Writes the compressed result to:
        <sub_dir_path>/result_compress_agent_<TIMESTAMP>.md
    Returns the path to the written file.
    """
    logger.info("call_opeanAI_compress() — START")
    print("[DEBUG] call_opeanAI_compress() — START")

    from langchain_core.messages import HumanMessage

    llm = _get_openai_compress_llm()
    prompt = _build_openai_compress_prompt(nl_text)

    logger.info("Invoking OpenAI LLM for compression...")
    print("[DEBUG] Invoking OpenAI LLM for compression...")
    response = llm.invoke([HumanMessage(content=prompt)])
    compressed_text = response.content if hasattr(response, "content") else str(response)

    input_size = len(nl_text)
    compressed_size = len(compressed_text)
    ratio = (1 - compressed_size / input_size) * 100 if input_size > 0 else 0
    logger.info(f"OpenAI compression done — {compressed_size} bytes, {ratio:.1f}% reduction")
    print(f"[DEBUG] OpenAI compression done — {compressed_size} bytes, {ratio:.1f}% reduction")

    # Write result to dir_out/SUB_DIR_* with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%Sh")
    out_filename = f"result_compress_agent_{timestamp}.md"
    out_filepath = os.path.join(sub_dir_path, out_filename)

    with open(out_filepath, "w", encoding="utf-8") as fh:
        fh.write(compressed_text)

    logger.info(f"Written OpenAI compressed file: {out_filepath}")
    print(f"[DEBUG] Written OpenAI compressed file: {out_filepath}")
    print("[DEBUG] call_opeanAI_compress() — DONE")

    return out_filepath


# ===========================================================================
# TASK-4 — compress_natural_language_only
# ===========================================================================

def compress_natural_language_only(sub_dir_path: str, nl_filename: str) -> str:
    """
    Reads the NL-only file from sub_dir_path, compresses it using the
    existing compress logic from compact_tokens__.py, and writes
    the compressed output with a timestamp.

    Args:
        sub_dir_path:  Path to the SUB_DIR containing the NL file
        nl_filename:   Name of the NL-only file (e.g. "compress_target_file_1__NL_ONLY.md")

    Returns:
        str: Path to the compressed output file
    """
    logger.info(f"compress_natural_language_only() — START")
    logger.info(f"  sub_dir_path={sub_dir_path}")
    logger.info(f"  nl_filename={nl_filename}")
    print(f"[DEBUG] compress_natural_language_only() — START")
    print(f"[DEBUG]   sub_dir_path={sub_dir_path}")
    print(f"[DEBUG]   nl_filename={nl_filename}")

    nl_filepath = os.path.join(sub_dir_path, nl_filename)

    if not os.path.isfile(nl_filepath):
        msg = f"NL file not found: {nl_filepath}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    # Read NL content
    with open(nl_filepath, "r", encoding="utf-8", errors="ignore") as fh:
        nl_text = fh.read()

    input_size = len(nl_text)
    logger.info(f"NL file read OK — size={input_size} bytes")
    print(f"[DEBUG] NL file read — {input_size} bytes")

    # Import compress functions from compact_tokens__
    try:
        from compact_tokens__ import call_claude, build_compress_prompt, strip_llm_wrapper
        logger.info("Imported compress functions from compact_tokens__")
        print("[DEBUG] Imported compress functions from compact_tokens__")
    except ImportError as e:
        msg = f"Failed to import from compact_tokens__: {e}"
        logger.error(msg)
        print(f"[DEBUG] ERROR: {msg}")
        raise

    # Route to the correct LLM based on global toggles
    if CALL_OPENAI_API == "Yes":
        logger.info("CALL_OPENAI_API=Yes — routing to call_opeanAI_compress()")
        print("[DEBUG] CALL_OPENAI_API=Yes — routing to call_opeanAI_compress()")
        compressed_text = call_opeanAI_compress(nl_text, sub_dir_path)
        # call_opeanAI_compress writes its own output file; return early
        return compressed_text
    elif CALL_CLAUDE_API == "Yes":
        logger.info("CALL_CLAUDE_API=Yes — Calling Claude for NL compression...")
        print("[DEBUG] CALL_CLAUDE_API=Yes — Calling Claude for NL compression...")
        prompt = build_compress_prompt(nl_text)
        compressed_text = call_claude(prompt)
    else:
        msg = "Both CALL_CLAUDE_API and CALL_OPENAI_API are set to 'No'. Nothing to do."
        logger.error(msg)
        raise ValueError(msg)

    compressed_size = len(compressed_text)
    ratio = (1 - compressed_size / input_size) * 100 if input_size > 0 else 0
    logger.info(f"Compression done — compressed_size={compressed_size} bytes, ratio={ratio:.1f}%")
    print(f"[DEBUG] Compression done — {compressed_size} bytes, ratio={ratio:.1f}% reduction")

    # Write compressed file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%Sh")
    name_stem = Path(nl_filename).stem  # e.g. compress_target_file_1__NL_ONLY
    compressed_filename = f"{name_stem}__COMPRESSED__{timestamp}.md"
    compressed_filepath = os.path.join(sub_dir_path, compressed_filename)

    with open(compressed_filepath, "w", encoding="utf-8") as fh:
        fh.write(compressed_text)

    logger.info(f"Written compressed file: {compressed_filepath}")
    print(f"[DEBUG] Written compressed file: {compressed_filepath}")
    print(f"[DEBUG] compress_natural_language_only() — DONE")

    return compressed_filepath


# ===========================================================================
# main() — Orchestrator
# ===========================================================================

def main():
    """
    Entry point: orchestrates TASK-2 -> TASK-3 -> TASK-4 pipeline.
    """
    print("=" * 70)
    print("code_nl_separator__.py — MAIN — START")
    print("=" * 70)
    logger.info("main() — START")

    input_dir = THIS_DIR / "dir_input"
    input_file = INPUT_FILENAME
    input_filepath = str(input_dir / input_file)

    logger.info(f"Input file: {input_filepath}")
    print(f"[DEBUG] Input file: {input_filepath}")

    # TASK-2: Separate code and NL
    print("\n" + "=" * 70)
    print("TASK-2: get_code_nl_separate()")
    print("=" * 70)
    code_str, nl_str = get_code_nl_separate(input_filepath)

    # TASK-3: Write to output SUB_DIR
    print("\n" + "=" * 70)
    print("TASK-3: write_to_out_dir_init()")
    print("=" * 70)
    sub_dir = write_to_out_dir_init(code_str, nl_str, input_file)

    # TASK-4: Compress NL only
    print("\n" + "=" * 70)
    print("TASK-4: compress_natural_language_only()")
    print("=" * 70)
    compressed_path = compress_natural_language_only(sub_dir, NL_FILENAME)

    print("\n" + "=" * 70)
    print("ALL TASKS COMPLETE")
    print(f"  Output SUB_DIR : {sub_dir}")
    print(f"  Compressed file: {compressed_path}")
    print("=" * 70)
    logger.info(f"main() — DONE — output_dir={sub_dir}")


if __name__ == "__main__":
    main()
