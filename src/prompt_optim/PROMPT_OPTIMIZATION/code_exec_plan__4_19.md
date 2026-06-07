# CODE EXECUTION PLAN — Session 2026-04-19
## CODE_AGENT_LEAD 🧠

---

## OVERVIEW
Create a new module `code_nl_separator__4_19.py` in ROOT_DIR `/home/dhankar/temp/26_07__1/26_07__v2/proj_root_/` that:
1. Reads a `.py` file from `dir_input/`
2. Separates CODE vs NATURAL LANGUAGE portions
3. Writes both to separate files in a timestamped SUB_DIR under `dir_out/`
4. Compresses only the natural language file using existing `compress_file()` logic

---

## TARGET INPUT FILE ANALYSIS
`dir_input/compress_target_file_1.py` contains:
- **CODE**: `import` statements, `def` signatures, `return` statements, function logic, `logger = ...`
- **NATURAL LANGUAGE inside Python**:
  - Triple-quoted multiline strings (`"""..."""`) — e.g., `prompt_static = """...large NL text..."""`
  - Docstrings (triple-quoted under `def`)
  - `#` comments that are prose (not code-structural)
  - f-string multiline blocks with NL content

---

## NEW MODULE: `code_nl_separator__4_19.py`
**Location:** `/home/dhankar/temp/26_07__1/26_07__v2/proj_root_/code_nl_separator__4_19.py`

### METHOD 1: `get_code_nl_separate(input_filepath: str) -> tuple[str, str]`
**Assigned to:** SUB_AGENT_1

**Logic:**
1. Read the input `.py` file as raw text
2. Use Python `ast` module to parse the file into an AST
3. Walk the AST to identify all string nodes:
   - `ast.Constant` nodes where value is `str` (covers triple-quoted strings, docstrings, f-strings resolved at parse time)
   - Multiline strings assigned to variables (e.g., `prompt_static = """..."""`)
   - Docstrings (first `ast.Expr` in function/class/module body)
4. Also extract `#` comment lines using `tokenize` module (AST doesn't capture comments)
5. For each identified NL region, record its `(start_line, end_line)` span
6. Split the original file:
   - **Code_Only_String**: All lines NOT in NL spans (imports, defs, logic, assignments minus the string literal content). Replace NL spans with placeholder markers like `# [NL_BLOCK_<n> EXTRACTED]`
   - **Natural_Language_Only_String**: All extracted NL content, concatenated with section markers showing origin (e.g., `--- FROM: line 25-325, variable: prompt_static ---`)
7. Return `(Code_Only_String, Natural_Language_Only_String)`

**Handles these NL formats:**
- Triple-quoted strings: `"""..."""` and `'''...'''`
- Simple string assignments: `x = "some NL text"`
- Python multiline f-strings: `f"...{var}..."` (extract the template text)
- `#` comment blocks that are prose

**Logging:** Every step logged via `util_logger.setup_logger("code_nl_separator")` + `print()` debug statements.

---

### METHOD 2: `write_to_out_dir_init(code_only_str: str, nl_only_str: str, source_filename: str) -> str`
**Assigned to:** SUB_AGENT_2

**Logic:**
1. Generate SUB_DIR name: `SUB_DIR_<source_filename>_<YYYYMMDD_HHMMSSh>/`
   - e.g., `SUB_DIR_compress_target_file_1__20260419_192500h/`
2. Create the SUB_DIR at: `/home/dhankar/temp/26_07__1/26_07__v2/proj_root_/dir_out/SUB_DIR_.../`
3. Write FILE-1: `<source_filename>__CODE_ONLY.py` — contains `Code_Only_String`
4. Write FILE-2: `<source_filename>__NL_ONLY.md` — contains `Natural_Language_Only_String`
5. Return the SUB_DIR path as string

**Logging:** Log SUB_DIR creation, both file writes with sizes, full paths.

---

### METHOD 3: `compress_natural_language_only(sub_dir_path: str, nl_filename: str) -> str`
**Assigned to:** SUB_AGENT_3

**Logic:**
1. Read the NL-only file from `sub_dir_path/nl_filename`
2. Call existing `compress_file()` from `compact_tokens__4_19.py` (line 161)
   - NOTE: `compress_file()` currently uses relative imports (`from .detect`). We will import `call_claude`, `build_compress_prompt`, `strip_llm_wrapper`, and the validation logic directly rather than calling `compress_file()` as a package method.
   - Alternative: refactor the imports in `compact_tokens__4_19.py` to use absolute imports so it can be called standalone.
3. Write the compressed output as: `<source_filename>__NL_COMPRESSED__<timestamp>.md`
4. Save to the same SUB_DIR
5. Return the compressed file path

**Logging:** Log input file size, compressed file size, compression ratio, timestamp.

---

### METHOD 4: `main()` — Orchestrator
**Assigned to:** SUB_AGENT_1 (as entry point)

```python
def main():
    input_dir = "/home/dhankar/temp/26_07__1/26_07__v2/proj_root_/dir_input/"
    input_file = "compress_target_file_1.py"

    # TASK-2: Separate code and NL
    code_str, nl_str = get_code_nl_separate(os.path.join(input_dir, input_file))

    # TASK-3: Write to output SUB_DIR
    sub_dir = write_to_out_dir_init(code_str, nl_str, input_file)

    # TASK-4: Compress NL only
    compressed_path = compress_natural_language_only(sub_dir, f"{input_file}__NL_ONLY.md")

    print(f"DONE. Output in: {sub_dir}")
```

---

## SUB-AGENT ASSIGNMENTS

| Agent | Task | Method |
|---|---|---|
| SUB_AGENT_1 | TASK-2 + main() | `get_code_nl_separate()` + `main()` |
| SUB_AGENT_2 | TASK-3 | `write_to_out_dir_init()` |
| SUB_AGENT_3 | TASK-4 | `compress_natural_language_only()` |

---
