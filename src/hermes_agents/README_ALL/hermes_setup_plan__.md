####

# Technical Architecture & Deployment Blueprint: setup-hermes.sh

This documentation provides an exhaustive breakdown of the automated installation suite for the Hermes Agent Framework. This engine branches its execution patterns natively to handle configurations across standard high-performance infrastructure (Linux Desktops/Servers) and sandboxed mobile Linux runtimes (Android via Termux).

1. Directory Contexts & Lifecycle Paths
When executed, the script enforces directory tracking using deterministic subshell evaluations to ensure absolute path lock-in, completely preventing host filesystem pollution:

Bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

## Contextual Prerequisite Requirements
Target Execution Directory: The script must be executed within the root directory of the locally cloned git repository where tracking manifests (such as pyproject.toml, uv.lock, and configuration templates) reside.

- Working Isolation Layer: The parameter export UV_NO_CONFIG=1 is injected globally. This forces the system to ignore any overriding, invalid user-space setup files (like uv.toml or pyproject.toml) located further up the parent folder hierarchy. This guarantees clean installations even when deploying using sudo -u <user> wrappers.

## Filesystem Mutations
The script actively targets, modifies, and monitors the following explicit system paths:

- System Target Directory	Platform Space	Operations & Persistent State Modifications
[repo_root]/venv/	All Platforms	Isolated Python 3.11 runtimes, system entry points, and local site-packages. (Completely wiped and rebuilt on rerun).

- $HOME/.local/bin/	Desktop / Server	Global user-space binary interface lane. Recieves a symbolic link named hermes for global terminal routing.  

- $PREFIX/bin/	Android / Termux	Native Termux structural binary layout. Receives the hermes execution symlink to bypass Android workspace barriers.  

~/.hermes/skills/	All Platforms	Core behavioral tracking and skills directory. Receives synchronized operational automation blueprints.  


## 2. Line-by-Line Execution Engine Walkthrough

### Phase 1: Platform Fingerprinting
The script evaluates the system's context to dynamically split execution between cloud/workstation environments and sandboxed mobile environments:

```bash
is_termux() {
    [ -n "${TERMUX_VERSION:-}" ] || [[ "${PREFIX:-}" == *"com.termux/files/usr"* ]]
}  
```


- Desktop / Server Flow: Leverages Astral's high-speed Rust-based uv utility engine to orchestrate compiler steps, python virtual environments, and dependency resolution.  

- Android / Termux Flow: Bypasses uv compilation steps entirely, falling back to Python's native standard library venv and standard pip packages to comply with Android's system call limits.

### Phase 2: Dependency Compiler Compilation (uv)
If on a desktop system, the script checks for an existing uv engine path. If missing, it builds a safe, temporary installer script (mktemp wrapper) and installs the binary cleanly into the local environment:

```bash
curl -LsSf https://astral.sh/uv/install.sh -o "$_uv_installer"
```

- The script uses a two-stage evaluation pipeline to ensure network connectivity errors or architecture mismatches surface immediately in the stderr logs rather than failing silently.

### Phase 3: Python Runtime Verification & Injection
The engine requires a strict minimum Python version of 3.11.

- Termux: Confirms a system-wide binary matching the requirements exists. If missing, it halts and instructs the user to run pkg install python.

- Desktop/Server: If Python 3.11 cannot be resolved locally, the script leverages uv's internal toolchain manager to download and unpack an isolated, portable production build of Python 3.11 directly into the application folder—completely avoiding the need to add third-party PPA repositories to your system package manager.

Phase 4: Virtual Environment Isolation
To guarantee a clean environment, any legacy ./venv folder is deleted from the root workspace directory. The fresh environment is initialized using your system's specific execution engine path:

Termux: python -m venv venv

Desktop: uv venv venv --python "3.11"

Phase 5: Smart Dependency Tree Resolution
The script uses a clever multi-tier fallback architecture to handle package installation safely and securely:

Plaintext
[uv.lock discovered] ──> Cryptographically Signed SHA-256 Hash Verification
                                 │
                                 └── (On Error / Missing Lock)
                                           │
                                           └──> Resilient PyPI Fallback Core Resolve
Hash-Verified Lock Synchronizations (Primary Choice): If uv.lock is detected, the script runs uv sync --extra all --locked. This cross-checks the SHA-256 hash of every single sub-dependency downloaded from PyPI against the lockfile signature. This step blocks supply-chain injection attacks and prevents unauthorized package updates.

Resilient PyPI Resolution (Secondary Choice): If the lockfile fails to resolve due to environment variances, it automatically triggers a fallback cascade loop (_try_install). If a non-essential optional package is broken upstream, the loop isolates it, ensuring core engine modules (like task orchestration, cron jobs, and database drivers) install successfully without halting the entire setup.

Android Target Optimization: If running in Termux, the script updates development headers (pip setuptools wheel) and installs explicit dependencies mapped within constraints-termux.txt to align with the platform's constraints.

Phase 6: High-Velocity File Search Optimization (ripgrep)
The script verifies if the Rust-accelerated ripgrep (rg) file indexing utility is present. If missing, the user is prompted to authorize an automatic installation. The script intelligently detects the host platform's package manager and installs the tool using apt, dnf, brew, or native Rust cargo compile paths.

Phase 7: Environment Scaffolding & CLI Mapping
Secure Environment Configuration: If a local .env file doesn't exist, it is generated directly from the .env.example template. The script immediately restricts file access permissions via chmod 600 .env so that only the file owner can read or write to it, safeguarding downstream API keys from other local system users.

Path Expansion: The executable is symlinked directly into user space (~/.local/bin/hermes). The script automatically scans active user shell profiles (.zshrc, .bashrc, or .bash_profile), detects if the binary directory is missing from your system paths, and appends the path variables automatically:

Bash
export PATH="$HOME/.local/bin:$PATH"
Blueprint Assembly: Runs the internal Python script tools/skills_sync.py to copy and map core agent logic and tools straight into the global configuration directory at ~/.hermes/skills/.

3. User Requirements & Preparation Blueprint
Before running the installation script, ensure your system configuration satisfies the following parameters:

1. Network Routing Permissions
The installer requires outbound internet connections to download external files and libraries from the following domains:

astral.sh (Compiler updates)

pypi.org & files.pythonhosted.org (Package repositories)

github.com (Repository updates and tools synchronization)

2. Termux Environmental Preparation (Android Only)
To guarantee successful package builds under Termux, run this update and installation command sequence to provision your environment before running the setup script:

Bash
pkg update && pkg upgrade -y
pkg install python python-pip clang make termux-api ripgrep -y
3. Execution Authorization
You do not need root/sudo access to run this script—the installation runs completely inside your user space. However, if ripgrep is missing, the script will request temporary sudo permissions to install it via your native package manager.

Grant the file executable permissions before running it:

Bash
chmod +x setup-hermes.sh
./setup-hermes.sh
4. System Output Benchmarks & Expected Results
When setup-hermes.sh finishes execution, verify the installation succeeded by checking for the following system assets:

1. Hardened Configuration Files
A secure environment file (.env) will be generated in your project root, restricted to owner-only read/write access:

Plaintext
-rw------- 1 dhankar dhankar 1240 Jun  7 15:30 .env
2. Global Shell Binary Routing
The hermes CLI tool will be linked directly to your local user binary path:

Bash
$ which hermes
/home/dhankar/.local/bin/hermes

$ ls -la /home/dhankar/.local/bin/hermes
lrwxrwxrwx 1 dhankar dhankar 48 Jun  7 15:30 /home/dhankar/.local/bin/hermes -> /home/dhankar/temp/repo/venv/bin/hermes
3. Comprehensive Terminal Control API
Once you refresh your active shell layout (source ~/.bashrc or source ~/.zshrc), you can manage your entire Hermes Agent workspace using the global terminal commands:

Executable Terminal Command	Target Objective & Operational Output
hermes setup	Launches the interactive wizard to securely input model tokens, select default LLMs, and configure system connections.
hermes	Initializes the core interactive terminal interface to communicate directly with the AI Agent wrapper.
hermes status	Queries active memory layers, checks database connection pools, and verifies tool access.
hermes doctor	Runs health checks on communication ports, environment profiles, and path variables.
hermes gateway install	Configures background tracking daemons (systemd) to run background scheduling and cron pipelines.






#!/bin/bash
# ============================================================================
# Hermes Agent Setup Script
# ============================================================================
# Quick setup for developers who cloned the repo manually.
# Uses uv for desktop/server setup and Python's stdlib venv + pip on Termux.
#
# Usage:
#   ./setup-hermes.sh
#
# This script:
# 1. Detects desktop/server vs Android/Termux setup path
# 2. Creates a Python 3.11 virtual environment
# 3. Installs the appropriate dependency set for the platform
# 4. Creates .env from template (if not exists)
# 5. Symlinks the 'hermes' CLI command into a user-facing bin dir
# 6. Runs the setup wizard (optional)
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Prevent uv from discovering config files (uv.toml, pyproject.toml) from the
# wrong user's home directory when running under sudo -u <user>.  See #21269.
export UV_NO_CONFIG=1

PYTHON_VERSION="3.11"

is_termux() {
    [ -n "${TERMUX_VERSION:-}" ] || [[ "${PREFIX:-}" == *"com.termux/files/usr"* ]]
}

get_command_link_dir() {
    if is_termux && [ -n "${PREFIX:-}" ]; then
        echo "$PREFIX/bin"
    else
        echo "$HOME/.local/bin"
    fi
}

get_command_link_display_dir() {
    if is_termux && [ -n "${PREFIX:-}" ]; then
        echo '$PREFIX/bin'
    else
        echo '~/.local/bin'
    fi
}

echo ""
echo -e "${CYAN}⚕ Hermes Agent Setup${NC}"
echo ""

# ============================================================================
# Install / locate uv
# ============================================================================

echo -e "${CYAN}→${NC} Checking for uv..."

UV_CMD=""
if is_termux; then
    echo -e "${CYAN}→${NC} Termux detected — using Python's stdlib venv + pip instead of uv"
else
    if command -v uv &> /dev/null; then
        UV_CMD="uv"
    elif [ -x "$HOME/.local/bin/uv" ]; then
        UV_CMD="$HOME/.local/bin/uv"
    elif [ -x "$HOME/.cargo/bin/uv" ]; then
        UV_CMD="$HOME/.cargo/bin/uv"
    fi

    if [ -n "$UV_CMD" ]; then
        UV_VERSION=$($UV_CMD --version 2>/dev/null)
        echo -e "${GREEN}✓${NC} uv found ($UV_VERSION)"
    else
        echo -e "${CYAN}→${NC} Installing uv..."
        # Capture installer output so a failure shows the user WHY
        # (network, glibc mismatch on old distros, missing curl, disk
        # full, etc.) instead of "✗ Failed to install uv" with zero
        # diagnostic.  Two-stage to avoid `curl | sh` masking curl
        # failures (sh exits 0 on empty stdin under no pipefail).
        _uv_log="$(mktemp 2>/dev/null || echo "/tmp/hermes-uv-install.$$.log")"
        _uv_installer="$(mktemp 2>/dev/null || echo "/tmp/hermes-uv-installer.$$.sh")"
        if ! curl -LsSf https://astral.sh/uv/install.sh -o "$_uv_installer" 2>"$_uv_log"; then
            echo -e "${RED}✗${NC} Failed to download uv installer."
            sed 's/^/    /' "$_uv_log" >&2
            echo -e "${CYAN}→${NC} Install manually: https://docs.astral.sh/uv/"
            rm -f "$_uv_log" "$_uv_installer"
            exit 1
        fi
        if sh "$_uv_installer" >>"$_uv_log" 2>&1; then
            rm -f "$_uv_installer"
            if [ -x "$HOME/.local/bin/uv" ]; then
                UV_CMD="$HOME/.local/bin/uv"
            elif [ -x "$HOME/.cargo/bin/uv" ]; then
                UV_CMD="$HOME/.cargo/bin/uv"
            fi

            if [ -n "$UV_CMD" ]; then
                rm -f "$_uv_log"
                UV_VERSION=$($UV_CMD --version 2>/dev/null)
                echo -e "${GREEN}✓${NC} uv installed ($UV_VERSION)"
            else
                echo -e "${RED}✗${NC} uv installer reported success but binary not found. Add ~/.local/bin to PATH and retry."
                echo -e "${CYAN}→${NC} Installer output:"
                sed 's/^/    /' "$_uv_log" >&2
                rm -f "$_uv_log"
                exit 1
            fi
        else
            echo -e "${RED}✗${NC} Failed to install uv."
            echo -e "${CYAN}→${NC} Installer output:"
            sed 's/^/    /' "$_uv_log" >&2
            echo -e "${CYAN}→${NC} Install manually: https://docs.astral.sh/uv/"
            rm -f "$_uv_log" "$_uv_installer"
            exit 1
        fi
    fi
fi

# ============================================================================
# Python check (uv can provision it automatically)
# ============================================================================

echo -e "${CYAN}→${NC} Checking Python $PYTHON_VERSION..."

if is_termux; then
    if command -v python >/dev/null 2>&1; then
        PYTHON_PATH="$(command -v python)"
        if "$PYTHON_PATH" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
            PYTHON_FOUND_VERSION=$($PYTHON_PATH --version 2>/dev/null)
            echo -e "${GREEN}✓${NC} $PYTHON_FOUND_VERSION found"
        else
            echo -e "${RED}✗${NC} Termux Python must be 3.11+"
            echo "    Run: pkg install python"
            exit 1
        fi
    else
        echo -e "${RED}✗${NC} Python not found in Termux"
        echo "    Run: pkg install python"
        exit 1
    fi
else
    if $UV_CMD python find "$PYTHON_VERSION" &> /dev/null; then
        PYTHON_PATH=$($UV_CMD python find "$PYTHON_VERSION")
        PYTHON_FOUND_VERSION=$($PYTHON_PATH --version 2>/dev/null)
        echo -e "${GREEN}✓${NC} $PYTHON_FOUND_VERSION found"
    else
        echo -e "${CYAN}→${NC} Python $PYTHON_VERSION not found, installing via uv..."
        $UV_CMD python install "$PYTHON_VERSION"
        PYTHON_PATH=$($UV_CMD python find "$PYTHON_VERSION")
        PYTHON_FOUND_VERSION=$($PYTHON_PATH --version 2>/dev/null)
        echo -e "${GREEN}✓${NC} $PYTHON_FOUND_VERSION installed"
    fi
fi

# ============================================================================
# Virtual environment
# ============================================================================

echo -e "${CYAN}→${NC} Setting up virtual environment..."

if [ -d "venv" ]; then
    echo -e "${CYAN}→${NC} Removing old venv..."
    rm -rf venv
fi

if is_termux; then
    "$PYTHON_PATH" -m venv venv
    echo -e "${GREEN}✓${NC} venv created with stdlib venv"
else
    $UV_CMD venv venv --python "$PYTHON_VERSION"
    echo -e "${GREEN}✓${NC} venv created (Python $PYTHON_VERSION)"
fi

export VIRTUAL_ENV="$SCRIPT_DIR/venv"
SETUP_PYTHON="$SCRIPT_DIR/venv/bin/python"

# ============================================================================
# Dependencies
# ============================================================================

echo -e "${CYAN}→${NC} Installing dependencies..."

if is_termux; then
    export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk 2>/dev/null || printf '%s' "${ANDROID_API_LEVEL:-}")"
    echo -e "${CYAN}→${NC} Termux detected — installing the tested Android bundle"
    "$SETUP_PYTHON" -m pip install --upgrade pip setuptools wheel
    if [ -f "constraints-termux.txt" ]; then
        "$SETUP_PYTHON" -m pip install -e ".[termux]" -c constraints-termux.txt || {
            echo -e "${YELLOW}⚠${NC} Termux bundle install failed, falling back to base install..."
            "$SETUP_PYTHON" -m pip install -e "." -c constraints-termux.txt
        }
    else
        "$SETUP_PYTHON" -m pip install -e ".[termux]" || "$SETUP_PYTHON" -m pip install -e "."
    fi
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    # Prefer uv sync with lockfile (hash-verified installs) when available,
    # fall back to pip install for compatibility or when lockfile is stale.
    #
    # Multi-tier pip fallback. Goal: ONE compromised PyPI package
    # (mistralai 2.4.6 in May 2026 → quarantined) shouldn't silently demote
    # a fresh setup to "core only". Edit _BROKEN_EXTRAS when a transitive
    # breaks; users keep voice / honcho / google / slack / matrix etc. even
    # if mistral can't resolve.
    _BROKEN_EXTRAS=()  # populate when an extra becomes unresolvable
    _ALL_EXTRAS=(
        modal daytona messaging matrix cron cli dev tts-premium slack
        pty honcho mcp homeassistant sms acp voice dingtalk feishu google
        bedrock web youtube
    )
    _SAFE_EXTRAS=()
    for _e in "${_ALL_EXTRAS[@]}"; do
        _skip=false
        for _b in "${_BROKEN_EXTRAS[@]}"; do
            [ "$_e" = "$_b" ] && _skip=true && break
        done
        [ "$_skip" = false ] && _SAFE_EXTRAS+=("$_e")
    done
    _SAFE_SPEC=".[$(IFS=,; echo "${_SAFE_EXTRAS[*]}")]"
    _try_install() {
        $UV_CMD pip install -e ".[all]" \
            || $UV_CMD pip install -e "$_SAFE_SPEC" \
            || $UV_CMD pip install -e "."
    }

    if [ -f "uv.lock" ]; then
        # Hash-verified install (preferred). The lockfile records SHA256
        # hashes for every transitive — a compromised transitive would have
        # a different hash and be REJECTED by uv. This is the only path
        # that protects against transitive-package supply-chain attacks
        # (the direct deps in pyproject.toml are exact-pinned, but
        # `uv pip install` re-resolves transitives fresh from PyPI).
        echo -e "${CYAN}→${NC} Using uv.lock for hash-verified installation..."
        echo -e "${CYAN}→${NC} (first run on a fresh venv can take 1-5 minutes; uv prints progress below)"
        # Critical flag choice: `--extra all`, NOT `--all-extras`. The
        # latter installs every [project.optional-dependencies] key,
        # bypassing the curated [all] extra and pulling backends like
        # [matrix] (python-olm needs make on Windows) and [rl] (git+https
        # deps that fail offline). See pyproject.toml's [all] for the
        # curated set, and tools/lazy_deps.py for backends that install
        # at first use.
        # Also: stream stderr through directly so the user sees uv's
        # progress UI instead of staring at a frozen prompt.
        if UV_PROJECT_ENVIRONMENT="$SCRIPT_DIR/venv" $UV_CMD sync --extra all --locked; then
            echo -e "${GREEN}✓${NC} Dependencies installed (hash-verified via uv.lock)"
        else
            echo -e "${YELLOW}⚠${NC} Lockfile sync failed (see uv output above)."
            echo -e "${YELLOW}⚠${NC} Falling back to PyPI resolve — transitives will NOT be hash-verified."
            _try_install
            echo -e "${GREEN}✓${NC} Dependencies installed (transitives re-resolved, not hash-verified)"
        fi
    else
        echo -e "${YELLOW}⚠${NC} uv.lock not found — installing without hash verification of transitives."
        _try_install
        echo -e "${GREEN}✓${NC} Dependencies installed (transitives re-resolved, not hash-verified)"
    fi
fi

# ============================================================================
# ============================================================================
# Optional: ripgrep (for faster file search)
# ============================================================================

echo -e "${CYAN}→${NC} Checking ripgrep (optional, for faster search)..."

if command -v rg &> /dev/null; then
    echo -e "${GREEN}✓${NC} ripgrep found"
else
    echo -e "${YELLOW}⚠${NC} ripgrep not found (file search will use grep fallback)"
    read -p "Install ripgrep for faster search? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        INSTALLED=false

        if is_termux; then
            pkg install -y ripgrep && INSTALLED=true
        else
            # Check if sudo is available
            if command -v sudo &> /dev/null && sudo -n true 2>/dev/null; then
                if command -v apt &> /dev/null; then
                    sudo apt install -y ripgrep && INSTALLED=true
                elif command -v dnf &> /dev/null; then
                    sudo dnf install -y ripgrep && INSTALLED=true
                fi
            fi

            # Try brew (no sudo needed)
            if [ "$INSTALLED" = false ] && command -v brew &> /dev/null; then
                brew install ripgrep && INSTALLED=true
            fi

            # Try cargo (no sudo needed)
            if [ "$INSTALLED" = false ] && command -v cargo &> /dev/null; then
                echo -e "${CYAN}→${NC} Trying cargo install (no sudo required)..."
                cargo install ripgrep && INSTALLED=true
            fi
        fi

        if [ "$INSTALLED" = true ]; then
            echo -e "${GREEN}✓${NC} ripgrep installed"
        else
            echo -e "${YELLOW}⚠${NC} Auto-install failed. Install options:"
            if is_termux; then
                echo "    pkg install ripgrep          # Termux / Android"
            else
                echo "    sudo apt install ripgrep     # Debian/Ubuntu"
                echo "    brew install ripgrep         # macOS"
                echo "    cargo install ripgrep        # With Rust (no sudo)"
            fi
            echo "    https://github.com/BurntSushi/ripgrep#installation"
        fi
    fi
fi

# ============================================================================
# Environment file
# ============================================================================

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        # .env holds API keys — restrict to owner-only access (matches
        # scripts/install.sh which already chmods 600 after creation).
        chmod 600 .env 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Created .env from template"
    fi
else
    # Tighten an existing .env's perms in case it was created elsewhere
    # under a permissive umask.
    chmod 600 .env 2>/dev/null || true
    echo -e "${GREEN}✓${NC} .env exists"
fi

# ============================================================================
# PATH setup — symlink hermes into a user-facing bin dir
# ============================================================================

echo -e "${CYAN}→${NC} Setting up hermes command..."

HERMES_BIN="$SCRIPT_DIR/venv/bin/hermes"
COMMAND_LINK_DIR="$(get_command_link_dir)"
COMMAND_LINK_DISPLAY_DIR="$(get_command_link_display_dir)"
mkdir -p "$COMMAND_LINK_DIR"
ln -sf "$HERMES_BIN" "$COMMAND_LINK_DIR/hermes"
echo -e "${GREEN}✓${NC} Symlinked hermes → $COMMAND_LINK_DISPLAY_DIR/hermes"

if is_termux; then
    export PATH="$COMMAND_LINK_DIR:$PATH"
    echo -e "${GREEN}✓${NC} $COMMAND_LINK_DISPLAY_DIR is already on PATH in Termux"
else
    # Determine the appropriate shell config file
    SHELL_CONFIG=""
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        SHELL_CONFIG="$HOME/.bashrc"
        [ ! -f "$SHELL_CONFIG" ] && SHELL_CONFIG="$HOME/.bash_profile"
    else
        # Fallback to checking existing files
        if [ -f "$HOME/.zshrc" ]; then
            SHELL_CONFIG="$HOME/.zshrc"
        elif [ -f "$HOME/.bashrc" ]; then
            SHELL_CONFIG="$HOME/.bashrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            SHELL_CONFIG="$HOME/.bash_profile"
        fi
    fi

    if [ -n "$SHELL_CONFIG" ]; then
        # Touch the file just in case it doesn't exist yet but was selected
        touch "$SHELL_CONFIG" 2>/dev/null || true

        if ! echo "$PATH" | tr ':' '\n' | grep -q "^$HOME/.local/bin$"; then
            if ! grep -q '\.local/bin' "$SHELL_CONFIG" 2>/dev/null; then
                echo "" >> "$SHELL_CONFIG"
                echo "# Hermes Agent — ensure ~/.local/bin is on PATH" >> "$SHELL_CONFIG"
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_CONFIG"
                echo -e "${GREEN}✓${NC} Added ~/.local/bin to PATH in $SHELL_CONFIG"
            else
                echo -e "${GREEN}✓${NC} ~/.local/bin already in $SHELL_CONFIG"
            fi
        else
            echo -e "${GREEN}✓${NC} ~/.local/bin already on PATH"
        fi
    fi
fi

# ============================================================================
# Seed bundled skills into ~/.hermes/skills/
# ============================================================================

HERMES_SKILLS_DIR="${HERMES_HOME:-$HOME/.hermes}/skills"
mkdir -p "$HERMES_SKILLS_DIR"

echo ""
echo "Syncing bundled skills to ~/.hermes/skills/ ..."
if "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/tools/skills_sync.py" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Skills synced"
else
    # Fallback: copy if sync script fails (missing deps, etc.)
    if [ -d "$SCRIPT_DIR/skills" ]; then
        cp -rn "$SCRIPT_DIR/skills/"* "$HERMES_SKILLS_DIR/" 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Skills copied"
    fi
fi

# ============================================================================
# Done
# ============================================================================

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo ""
if is_termux; then
    echo "  1. Run the setup wizard to configure API keys:"
    echo "     hermes setup"
    echo ""
    echo "  2. Start chatting:"
    echo "     hermes"
    echo ""
else
    echo "  1. Reload your shell:"
    echo "     source $SHELL_CONFIG"
    echo ""
    echo "  2. Run the setup wizard to configure API keys:"
    echo "     hermes setup"
    echo ""
    echo "  3. Start chatting:"
    echo "     hermes"
    echo ""
fi
echo "Other commands:"
echo "  hermes status        # Check configuration"
if is_termux; then
    echo "  hermes gateway       # Run gateway in foreground"
else
    echo "  hermes gateway install # Install gateway service (messaging + cron)"
fi
echo "  hermes cron list     # View scheduled jobs"
echo "  hermes doctor        # Diagnose issues"
echo ""

# Ask if they want to run setup wizard now
read -p "Would you like to run the setup wizard now? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo ""
    # Run directly with venv Python (no activation needed)
    "$SCRIPT_DIR/venv/bin/python" -m hermes_cli.main setup
fi


#####

# ============================================================================

# Hermes Agent Setup Script

# ============================================================================

# Quick setup for developers who cloned the repo manually.

# Uses uv for desktop/server setup and Python's stdlib venv + pip on Termux.

#

# Usage:

# ./setup-hermes.sh

#

# This script:

# 1. Detects desktop/server vs Android/Termux setup path

# 2. Creates a Python 3.11 virtual environment

# 3. Installs the appropriate dependency set for the platform

# 4. Creates .env from template (if not exists)

# 5. Symlinks the 'hermes' CLI command into a user-facing bin dir

# 6. Runs the setup wizard (optional)

# ============================================================================



set -e



# Colors

GREEN='\033[0;32m'

YELLOW='\033[0;33m'

CYAN='\033[0;36m'

RED='\033[0;31m'

NC='\033[0m'



SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"



# Prevent uv from discovering config files (uv.toml, pyproject.toml) from the

# wrong user's home directory when running under sudo -u <user>. See #21269.

export UV_NO_CONFIG=1



PYTHON_VERSION="3.11"



is_termux() {

[ -n "${TERMUX_VERSION:-}" ] || [[ "${PREFIX:-}" == *"com.termux/files/usr"* ]]

}



get_command_link_dir() {

if is_termux && [ -n "${PREFIX:-}" ]; then

echo "$PREFIX/bin"

else

echo "$HOME/.local/bin"

fi

}



get_command_link_display_dir() {

if is_termux && [ -n "${PREFIX:-}" ]; then

echo '$PREFIX/bin'

else

echo '~/.local/bin'

fi

}



echo ""

echo -e "${CYAN}⚕ Hermes Agent Setup${NC}"

echo ""



# ============================================================================

# Install / locate uv

# ============================================================================



echo -e "${CYAN}→${NC} Checking for uv..."



UV_CMD=""

if is_termux; then

echo -e "${CYAN}→${NC} Termux detected — using Python's stdlib venv + pip instead of uv"

else

if command -v uv &> /dev/null; then

UV_CMD="uv"

elif [ -x "$HOME/.local/bin/uv" ]; then

UV_CMD="$HOME/.local/bin/uv"

elif [ -x "$HOME/.cargo/bin/uv" ]; then

UV_CMD="$HOME/.cargo/bin/uv"

fi



if [ -n "$UV_CMD" ]; then

UV_VERSION=$($UV_CMD --version 2>/dev/null)

echo -e "${GREEN}✓${NC} uv found ($UV_VERSION)"

else

echo -e "${CYAN}→${NC} Installing uv..."

# Capture installer output so a failure shows the user WHY

# (network, glibc mismatch on old distros, missing curl, disk

# full, etc.) instead of "✗ Failed to install uv" with zero

# diagnostic. Two-stage to avoid `curl | sh` masking curl

# failures (sh exits 0 on empty stdin under no pipefail).

_uv_log="$(mktemp 2>/dev/null || echo "/tmp/hermes-uv-install.$$.log")"

_uv_installer="$(mktemp 2>/dev/null || echo "/tmp/hermes-uv-installer.$$.sh")"

if ! curl -LsSf https://astral.sh/uv/install.sh -o "$_uv_installer" 2>"$_uv_log"; then

echo -e "${RED}✗${NC} Failed to download uv installer."

sed 's/^/ /' "$_uv_log" >&2

echo -e "${CYAN}→${NC} Install manually: https://docs.astral.sh/uv/"

rm -f "$_uv_log" "$_uv_installer"

exit 1

fi

if sh "$_uv_installer" >>"$_uv_log" 2>&1; then

rm -f "$_uv_installer"

if [ -x "$HOME/.local/bin/uv" ]; then

UV_CMD="$HOME/.local/bin/uv"

elif [ -x "$HOME/.cargo/bin/uv" ]; then

UV_CMD="$HOME/.cargo/bin/uv"

fi



if [ -n "$UV_CMD" ]; then

rm -f "$_uv_log"

UV_VERSION=$($UV_CMD --version 2>/dev/null)

echo -e "${GREEN}✓${NC} uv installed ($UV_VERSION)"

else

echo -e "${RED}✗${NC} uv installer reported success but binary not found. Add ~/.local/bin to PATH and retry."

echo -e "${CYAN}→${NC} Installer output:"

sed 's/^/ /' "$_uv_log" >&2

rm -f "$_uv_log"

exit 1

fi

else

echo -e "${RED}✗${NC} Failed to install uv."

echo -e "${CYAN}→${NC} Installer output:"

sed 's/^/ /' "$_uv_log" >&2

echo -e "${CYAN}→${NC} Install manually: https://docs.astral.sh/uv/"

rm -f "$_uv_log" "$_uv_installer"

exit 1

fi

fi

fi



# ============================================================================

# Python check (uv can provision it automatically)

# ============================================================================



echo -e "${CYAN}→${NC} Checking Python $PYTHON_VERSION..."



if is_termux; then

if command -v python >/dev/null 2>&1; then

PYTHON_PATH="$(command -v python)"

if "$PYTHON_PATH" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then

PYTHON_FOUND_VERSION=$($PYTHON_PATH --version 2>/dev/null)

echo -e "${GREEN}✓${NC} $PYTHON_FOUND_VERSION found"

else

echo -e "${RED}✗${NC} Termux Python must be 3.11+"

echo " Run: pkg install python"

exit 1

fi

else

echo -e "${RED}✗${NC} Python not found in Termux"

echo " Run: pkg install python"

exit 1

fi

else

if $UV_CMD python find "$PYTHON_VERSION" &> /dev/null; then

PYTHON_PATH=$($UV_CMD python find "$PYTHON_VERSION")

PYTHON_FOUND_VERSION=$($PYTHON_PATH --version 2>/dev/null)

echo -e "${GREEN}✓${NC} $PYTHON_FOUND_VERSION found"

else

echo -e "${CYAN}→${NC} Python $PYTHON_VERSION not found, installing via uv..."

$UV_CMD python install "$PYTHON_VERSION"

PYTHON_PATH=$($UV_CMD python find "$PYTHON_VERSION")

PYTHON_FOUND_VERSION=$($PYTHON_PATH --version 2>/dev/null)

echo -e "${GREEN}✓${NC} $PYTHON_FOUND_VERSION installed"

fi

fi



# ============================================================================

# Virtual environment

# ============================================================================



echo -e "${CYAN}→${NC} Setting up virtual environment..."



if [ -d "venv" ]; then

echo -e "${CYAN}→${NC} Removing old venv..."

rm -rf venv

fi



if is_termux; then

"$PYTHON_PATH" -m venv venv

echo -e "${GREEN}✓${NC} venv created with stdlib venv"

else

$UV_CMD venv venv --python "$PYTHON_VERSION"

echo -e "${GREEN}✓${NC} venv created (Python $PYTHON_VERSION)"

fi



export VIRTUAL_ENV="$SCRIPT_DIR/venv"

SETUP_PYTHON="$SCRIPT_DIR/venv/bin/python"



# ============================================================================

# Dependencies

# ============================================================================



echo -e "${CYAN}→${NC} Installing dependencies..."



if is_termux; then

export ANDROID_API_LEVEL="$(getprop ro.build.version.sdk 2>/dev/null || printf '%s' "${ANDROID_API_LEVEL:-}")"

echo -e "${CYAN}→${NC} Termux detected — installing the tested Android bundle"

"$SETUP_PYTHON" -m pip install --upgrade pip setuptools wheel

if [ -f "constraints-termux.txt" ]; then

"$SETUP_PYTHON" -m pip install -e ".[termux]" -c constraints-termux.txt || {

echo -e "${YELLOW}⚠${NC} Termux bundle install failed, falling back to base install..."

"$SETUP_PYTHON" -m pip install -e "." -c constraints-termux.txt

}

else

"$SETUP_PYTHON" -m pip install -e ".[termux]" || "$SETUP_PYTHON" -m pip install -e "."

fi

echo -e "${GREEN}✓${NC} Dependencies installed"

else

# Prefer uv sync with lockfile (hash-verified installs) when available,

# fall back to pip install for compatibility or when lockfile is stale.

#

# Multi-tier pip fallback. Goal: ONE compromised PyPI package

# (mistralai 2.4.6 in May 2026 → quarantined) shouldn't silently demote

# a fresh setup to "core only". Edit _BROKEN_EXTRAS when a transitive

# breaks; users keep voice / honcho / google / slack / matrix etc. even

# if mistral can't resolve.

_BROKEN_EXTRAS=() # populate when an extra becomes unresolvable

_ALL_EXTRAS=(

modal daytona messaging matrix cron cli dev tts-premium slack

pty honcho mcp homeassistant sms acp voice dingtalk feishu google

bedrock web youtube

)

_SAFE_EXTRAS=()

for _e in "${_ALL_EXTRAS[@]}"; do

_skip=false

for _b in "${_BROKEN_EXTRAS[@]}"; do

[ "$_e" = "$_b" ] && _skip=true && break

done

[ "$_skip" = false ] && _SAFE_EXTRAS+=("$_e")

done

_SAFE_SPEC=".[$(IFS=,; echo "${_SAFE_EXTRAS[*]}")]"

_try_install() {

$UV_CMD pip install -e ".[all]" \

|| $UV_CMD pip install -e "$_SAFE_SPEC" \

|| $UV_CMD pip install -e "."

}



if [ -f "uv.lock" ]; then

# Hash-verified install (preferred). The lockfile records SHA256

# hashes for every transitive — a compromised transitive would have

# a different hash and be REJECTED by uv. This is the only path

# that protects against transitive-package supply-chain attacks

# (the direct deps in pyproject.toml are exact-pinned, but

# `uv pip install` re-resolves transitives fresh from PyPI).

echo -e "${CYAN}→${NC} Using uv.lock for hash-verified installation..."

echo -e "${CYAN}→${NC} (first run on a fresh venv can take 1-5 minutes; uv prints progress below)"

# Critical flag choice: `--extra all`, NOT `--all-extras`. The

# latter installs every [project.optional-dependencies] key,

# bypassing the curated [all] extra and pulling backends like

# [matrix] (python-olm needs make on Windows) and [rl] (git+https

# deps that fail offline). See pyproject.toml's [all] for the

# curated set, and tools/lazy_deps.py for backends that install

# at first use.

# Also: stream stderr through directly so the user sees uv's

# progress UI instead of staring at a frozen prompt.

if UV_PROJECT_ENVIRONMENT="$SCRIPT_DIR/venv" $UV_CMD sync --extra all --locked; then

echo -e "${GREEN}✓${NC} Dependencies installed (hash-verified via uv.lock)"

else

echo -e "${YELLOW}⚠${NC} Lockfile sync failed (see uv output above)."

echo -e "${YELLOW}⚠${NC} Falling back to PyPI resolve — transitives will NOT be hash-verified."

_try_install

echo -e "${GREEN}✓${NC} Dependencies installed (transitives re-resolved, not hash-verified)"

fi

else

echo -e "${YELLOW}⚠${NC} uv.lock not found — installing without hash verification of transitives."

_try_install

echo -e "${GREEN}✓${NC} Dependencies installed (transitives re-resolved, not hash-verified)"

fi

fi



# ============================================================================

# ============================================================================

# Optional: ripgrep (for faster file search)

# ============================================================================



echo -e "${CYAN}→${NC} Checking ripgrep (optional, for faster search)..."



if command -v rg &> /dev/null; then

echo -e "${GREEN}✓${NC} ripgrep found"

else

echo -e "${YELLOW}⚠${NC} ripgrep not found (file search will use grep fallback)"

read -p "Install ripgrep for faster search? [Y/n] " -n 1 -r

echo

if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then

INSTALLED=false



if is_termux; then

pkg install -y ripgrep && INSTALLED=true

else

# Check if sudo is available

if command -v sudo &> /dev/null && sudo -n true 2>/dev/null; then

if command -v apt &> /dev/null; then

sudo apt install -y ripgrep && INSTALLED=true

elif command -v dnf &> /dev/null; then

sudo dnf install -y ripgrep && INSTALLED=true

fi

fi



# Try brew (no sudo needed)

if [ "$INSTALLED" = false ] && command -v brew &> /dev/null; then

brew install ripgrep && INSTALLED=true

fi



# Try cargo (no sudo needed)

if [ "$INSTALLED" = false ] && command -v cargo &> /dev/null; then

echo -e "${CYAN}→${NC} Trying cargo install (no sudo required)..."

cargo install ripgrep && INSTALLED=true

fi

fi



if [ "$INSTALLED" = true ]; then

echo -e "${GREEN}✓${NC} ripgrep installed"

else

echo -e "${YELLOW}⚠${NC} Auto-install failed. Install options:"

if is_termux; then

echo " pkg install ripgrep # Termux / Android"

else

echo " sudo apt install ripgrep # Debian/Ubuntu"

echo " brew install ripgrep # macOS"

echo " cargo install ripgrep # With Rust (no sudo)"

fi

echo " https://github.com/BurntSushi/ripgrep#installation"

fi

fi

fi



# ============================================================================

# Environment file

# ============================================================================



if [ ! -f ".env" ]; then

if [ -f ".env.example" ]; then

cp .env.example .env

# .env holds API keys — restrict to owner-only access (matches

# scripts/install.sh which already chmods 600 after creation).

chmod 600 .env 2>/dev/null || true

echo -e "${GREEN}✓${NC} Created .env from template"

fi

else

# Tighten an existing .env's perms in case it was created elsewhere

# under a permissive umask.

chmod 600 .env 2>/dev/null || true

echo -e "${GREEN}✓${NC} .env exists"

fi



# ============================================================================

# PATH setup — symlink hermes into a user-facing bin dir

# ============================================================================



echo -e "${CYAN}→${NC} Setting up hermes command..."



HERMES_BIN="$SCRIPT_DIR/venv/bin/hermes"

COMMAND_LINK_DIR="$(get_command_link_dir)"

COMMAND_LINK_DISPLAY_DIR="$(get_command_link_display_dir)"

mkdir -p "$COMMAND_LINK_DIR"

ln -sf "$HERMES_BIN" "$COMMAND_LINK_DIR/hermes"

echo -e "${GREEN}✓${NC} Symlinked hermes → $COMMAND_LINK_DISPLAY_DIR/hermes"



if is_termux; then

export PATH="$COMMAND_LINK_DIR:$PATH"

echo -e "${GREEN}✓${NC} $COMMAND_LINK_DISPLAY_DIR is already on PATH in Termux"

else

# Determine the appropriate shell config file

SHELL_CONFIG=""

if [[ "$SHELL" == *"zsh"* ]]; then

SHELL_CONFIG="$HOME/.zshrc"

elif [[ "$SHELL" == *"bash"* ]]; then

SHELL_CONFIG="$HOME/.bashrc"

[ ! -f "$SHELL_CONFIG" ] && SHELL_CONFIG="$HOME/.bash_profile"

else

# Fallback to checking existing files

if [ -f "$HOME/.zshrc" ]; then

SHELL_CONFIG="$HOME/.zshrc"

elif [ -f "$HOME/.bashrc" ]; then

SHELL_CONFIG="$HOME/.bashrc"

elif [ -f "$HOME/.bash_profile" ]; then

SHELL_CONFIG="$HOME/.bash_profile"

fi

fi



if [ -n "$SHELL_CONFIG" ]; then

# Touch the file just in case it doesn't exist yet but was selected

touch "$SHELL_CONFIG" 2>/dev/null || true



if ! echo "$PATH" | tr ':' '\n' | grep -q "^$HOME/.local/bin$"; then

if ! grep -q '\.local/bin' "$SHELL_CONFIG" 2>/dev/null; then

echo "" >> "$SHELL_CONFIG"

echo "# Hermes Agent — ensure ~/.local/bin is on PATH" >> "$SHELL_CONFIG"

echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_CONFIG"

echo -e "${GREEN}✓${NC} Added ~/.local/bin to PATH in $SHELL_CONFIG"

else

echo -e "${GREEN}✓${NC} ~/.local/bin already in $SHELL_CONFIG"

fi

else

echo -e "${GREEN}✓${NC} ~/.local/bin already on PATH"

fi

fi

fi



# ============================================================================

# Seed bundled skills into ~/.hermes/skills/

# ============================================================================



HERMES_SKILLS_DIR="${HERMES_HOME:-$HOME/.hermes}/skills"

mkdir -p "$HERMES_SKILLS_DIR"



echo ""

echo "Syncing bundled skills to ~/.hermes/skills/ ..."

if "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/tools/skills_sync.py" 2>/dev/null; then

echo -e "${GREEN}✓${NC} Skills synced"

else

# Fallback: copy if sync script fails (missing deps, etc.)

if [ -d "$SCRIPT_DIR/skills" ]; then

cp -rn "$SCRIPT_DIR/skills/"* "$HERMES_SKILLS_DIR/" 2>/dev/null || true

echo -e "${GREEN}✓${NC} Skills copied"

fi

fi



# ============================================================================

# Done

# ============================================================================



echo ""

echo -e "${GREEN}✓ Setup complete!${NC}"

echo ""

echo "Next steps:"

echo ""

if is_termux; then

echo " 1. Run the setup wizard to configure API keys:"

echo " hermes setup"

echo ""

echo " 2. Start chatting:"

echo " hermes"

echo ""

else

echo " 1. Reload your shell:"

echo " source $SHELL_CONFIG"

echo ""

echo " 2. Run the setup wizard to configure API keys:"

echo " hermes setup"

echo ""

echo " 3. Start chatting:"

echo " hermes"

echo ""

fi

echo "Other commands:"

echo " hermes status # Check configuration"

if is_termux; then

echo " hermes gateway # Run gateway in foreground"

else

echo " hermes gateway install # Install gateway service (messaging + cron)"

fi

echo " hermes cron list # View scheduled jobs"

echo " hermes doctor # Diagnose issues"

echo ""



# Ask if they want to run setup wizard now

read -p "Would you like to run the setup wizard now? [Y/n] " -n 1 -r

echo

if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then

echo ""

# Run directly with venv Python (no activation needed)

"$SCRIPT_DIR/venv/bin/python" -m hermes_cli.main setup

fi













#### Termux 

Termux is an open-source, high-performance terminal emulator and Linux environment application designed specifically for Android devices.

Unlike most mobile terminal apps that simply let you connect to an external server via SSH, Termux transforms your phone or tablet into a standalone, local development machine. It installs a minimal, sandboxed Linux filesystem structure inside Android’s internal storage space without requiring you to "root" or modify your mobile operating system.

What is Happening under the Hood?
Normally, an operating system like Linux or Android isolation keeps applications locked inside their own sandboxed containers.

Termux works by leveraging Android's native Linux kernel. It creates a localized Linux environment under a custom internal directory tree (/data/data/com.termux/files/usr/). Because Android prevents traditional Linux binary file paths (like /bin, /usr/bin, or /lib) from being altered by non-root programs, Termux re-maps its entire package compiler stack to point toward this custom path prefix.

Technical Breakdown of the Bash Script Layer
The shell script snippet you provided is an environment detection guard clause. It mathematically calculates whether your current runtime session is running on a standard mobile Android CPU space or a typical desktop x86 workstation:

Bash
is_termux() {
    [ -n "${TERMUX_VERSION:-}" ] || [[ "${PREFIX:-}" == *"com.termux/files/usr"* ]]
}
This function evaluates true or false based on two strict environmental checks:

1. The TERMUX_VERSION Check
Bash
[ -n "${TERMUX_VERSION:-}" ]
The Mechanism: When the Termux application opens a shell session on Android, it automatically registers a global environment variable called TERMUX_VERSION (holding a value like 0.118.0).

The Logic: The -n flag checks if this variable is not empty. If it contains a value, it instantly confirms that the script is executing directly inside the native Termux mobile app environment.

2. The PREFIX Fallback Scan
Bash
[[ "${PREFIX:-}" == *"com.termux/files/usr"* ]]
The Mechanism: If the script is executed inside a subshell or an external background service wrapper where global variables might be missing, it triggers an evaluation of the system PREFIX environment path.

The Logic: Termux defines the environment variable $PREFIX to point directly to its localized binary storage folder (/data/data/com.termux/files/usr). This string match checks if the path contains the signature app identifier string com.termux. If it matches, it confirms that the runtime context is bounded by Android's filesystem rules.

Why the Hermes Setup Script Cares About It
The script checks for Termux to adjust its installation steps because a mobile device handles software compilation differently than a computer workstation:

Resource Limits: Standard desktops run Astral's uv tool to compile packages concurrently across multiple CPU threads. Termux environments running on mobile architectures can freeze or trigger Android's "Out of Memory" (OOM) task killer if pushed too hard by multi-threaded compilers.

Pre-compiled Binary Compatibility: Many packages on the Python Package Index (PyPI) distribute pre-compiled binary modules designed specifically for standard glibc (GNU C Library) environments found on Ubuntu or macOS. Android, however, uses a specialized C library called Bionic. By identifying Termux upfront, the script skips incompatible binary syncs and falls back to clean, native pip source builds optimized directly for mobile setups.