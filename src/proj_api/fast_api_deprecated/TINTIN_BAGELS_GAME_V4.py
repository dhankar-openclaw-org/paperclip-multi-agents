import random
import os
import time
import shutil
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

# ─────────────────────────────────────────────
NUM_DIGITS = 3
MAX_GUESS  = 10
# ─────────────────────────────────────────────

HADDOCK_INSULTS = [
    "Blistering Barnacles!",
    "Thundering Typhoons!",
    "Sea Gherkin!",
    "Ostrogoth!",
    "Ectoplasm!",
    "Landlubber!",
    "Troglodyte!",
    "Nincompoop!",
    "Pockmark!",
    "Iconoclast!",
    "Billions of Bilious Blue Blistering Barnacles!",
    "Ten Thousand Thundering Typhoons!",
    "Miserable Earthworm!",
    "Bashi-bazouk!",
    "Kleptomaniac!",
    "Pickled Herrings!",
    "Vivisectionist!",
    "Carpet-seller!",
    "You Sea Cucumber!",
    "Macrocephalic Baboon!",
]

RS = Style.RESET_ALL


# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════

def _cols() -> int:
    return shutil.get_terminal_size(fallback=(100, 24)).columns


def _center_pad(raw_width: int) -> str:
    return max(0, (_cols() - raw_width) // 2) * " "


def _animated_border(frame: int) -> str:
    s = Style.BRIGHT
    star_pairs = [
        (Fore.RED     + s + "★ ", Fore.YELLOW  + s + "✦ "),
        (Fore.YELLOW  + s + "✦ ", Fore.CYAN    + s + "· "),
        (Fore.CYAN    + s + "· ", Fore.RED     + s + "★ "),
        (Fore.MAGENTA + s + "⚓ ", Fore.WHITE   + s + "· "),
    ]
    sa, sb = star_pairs[frame % len(star_pairs)]
    return "".join(sa if i % 2 == 0 else sb for i in range(_cols() // 2)) + RS


def clear():
    os.system('clear' if os.name != 'nt' else 'cls')


# ═══════════════════════════════════════════════════════════
#  BLOCK LETTER DEFINITIONS  (10 chars wide × 7 rows)
# ═══════════════════════════════════════════════════════════

_T = ["██████████","    ██    ","    ██    ","    ██    ","    ██    ","    ██    ","    ██    "]
_I = ["██████████","    ██    ","    ██    ","    ██    ","    ██    ","    ██    ","██████████"]
_N = ["██      ██","███     ██","████    ██","██ ██   ██","██  ██  ██","██   ██ ██","██    ████"]

_P = ["█████████ ","██      ██","██      ██","█████████ ","██        ","██        ","██        "]
_R = ["█████████ ","██      ██","██      ██","█████████ ","████      ","██  ██    ","██    ████"]
_A = ["    ████  ","  ██    ██"," ██      █","██        ","██████████","██      ██","██      ██"]
_E = ["██████████","██        ","██        ","████████  ","██        ","██        ","██████████"]
_S = [" █████████","██        ","██        "," ████████ ","        ██","        ██","█████████ "]

_C = [" █████████","██        ","██        ","██        ","██        ","██        "," █████████"]
_H = ["██      ██","██      ██","██      ██","██████████","██      ██","██      ██","██      ██"]
_D = ["████████  ","██      ██","██      ██","██      ██","██      ██","██      ██","████████  "]
_O = [" ████████ ","██      ██","██      ██","██      ██","██      ██","██      ██"," ████████ "]
_K = ["██     ██ ","██   ██   ","██ ██     ","████      ","██ ██     ","██   ██   ","██     ███"]


# ═══════════════════════════════════════════════════════════
#  COLOUR PALETTES
# ═══════════════════════════════════════════════════════════

_TINTIN_COLORS = [
    [Fore.RED,     Fore.YELLOW,  Fore.MAGENTA, Fore.RED,     Fore.YELLOW,  Fore.MAGENTA],
    [Fore.YELLOW,  Fore.CYAN,    Fore.RED,     Fore.YELLOW,  Fore.CYAN,    Fore.RED    ],
    [Fore.MAGENTA, Fore.RED,     Fore.YELLOW,  Fore.MAGENTA, Fore.RED,     Fore.YELLOW ],
]

_PIRATES_COLORS = [
    [Fore.RED,    Fore.WHITE,  Fore.RED,    Fore.YELLOW, Fore.RED,    Fore.WHITE,  Fore.YELLOW],
    [Fore.YELLOW, Fore.RED,    Fore.WHITE,  Fore.RED,    Fore.WHITE,  Fore.RED,    Fore.WHITE ],
    [Fore.WHITE,  Fore.YELLOW, Fore.RED,    Fore.WHITE,  Fore.RED,    Fore.YELLOW, Fore.RED   ],
]

_CAPTAIN_COLORS = [
    [Fore.CYAN,  Fore.BLUE,  Fore.CYAN,  Fore.WHITE, Fore.CYAN,  Fore.BLUE,  Fore.CYAN ],
    [Fore.WHITE, Fore.CYAN,  Fore.BLUE,  Fore.CYAN,  Fore.WHITE, Fore.CYAN,  Fore.BLUE ],
    [Fore.BLUE,  Fore.WHITE, Fore.CYAN,  Fore.BLUE,  Fore.CYAN,  Fore.WHITE, Fore.CYAN ],
]

_HADDOCK_COLORS = [
    [Fore.WHITE, Fore.CYAN,  Fore.BLUE,  Fore.CYAN,  Fore.WHITE, Fore.CYAN,  Fore.BLUE ],
    [Fore.CYAN,  Fore.WHITE, Fore.CYAN,  Fore.BLUE,  Fore.CYAN,  Fore.WHITE, Fore.CYAN ],
    [Fore.BLUE,  Fore.CYAN,  Fore.WHITE, Fore.CYAN,  Fore.BLUE,  Fore.CYAN,  Fore.WHITE],
]


# ═══════════════════════════════════════════════════════════
#  GENERIC BLOCK-WORD RENDERER
# ═══════════════════════════════════════════════════════════

def _render_word(letters: list, color_sets: list, frame: int = 0,
                 gap: str = "   ") -> str:
    n      = len(letters)
    s      = Style.BRIGHT
    raw_w  = 10 * n + len(gap) * (n - 1)
    pad    = _center_pad(raw_w)
    colors = color_sets[frame % len(color_sets)]
    lines  = []
    for row in range(7):
        parts = [colors[li] + s + letters[li][row] for li in range(n)]
        lines.append(pad + gap.join(parts) + RS + "\n")
    return "".join(lines)


# ═══════════════════════════════════════════════════════════
#  BANNER BUILDERS
# ═══════════════════════════════════════════════════════════

def build_big_title(frame: int = 0) -> str:
    letters = [_T, _I, _N, _T, _I, _N]
    s       = Style.BRIGHT
    gap     = "   "
    raw_w   = 10 * 6 + len(gap) * 5     # 75
    pad     = _center_pad(raw_w)
    border  = _animated_border(frame)
    colors  = _TINTIN_COLORS[frame % len(_TINTIN_COLORS)]

    lines = ["\n", border, "\n\n"]
    for row in range(7):
        parts = [colors[li] + s + letters[li][row] for li in range(6)]
        lines.append(pad + gap.join(parts) + RS + "\n")

    lines.append("\n")
    for col_code, text in [
        (Fore.MAGENTA, "&  THE  SECRET  COORDINATES"),
        (Fore.CYAN,    "PIRATE  BAGELS  EDITION"),
        (Fore.YELLOW,  "~~  Inspired by Tintin  --  Hergé  ~~"),
    ]:
        lines.append(pad + col_code + s + text.center(raw_w) + RS + "\n")

    lines += ["\n", border, "\n"]
    return "".join(lines)


def build_pirates_banner(frame: int = 0) -> str:
    letters = [_P, _R, _I, _A, _T, _E, _S]
    s       = Style.BRIGHT
    gap     = "  "
    raw_w   = 10 * 7 + len(gap) * 6     # 82
    pad     = _center_pad(raw_w)
    skull_p = [Fore.RED + s + "☠ ", Fore.WHITE + s + "⚔ "]
    border  = "".join(skull_p[i % 2] for i in range(_cols() // 2)) + RS

    lines = ["\n", border, "\n\n"]
    lines.append(_render_word(letters, _PIRATES_COLORS, frame, gap))
    lines.append("\n")
    for col_code, text in [
        (Fore.RED,    "RED  RACKHAM'S  CREW"),
        (Fore.YELLOW, "Dead men tell no tales …"),
        (Fore.WHITE,  "~ Beware the Black Flag ~"),
    ]:
        lines.append(pad + col_code + s + text.center(raw_w) + RS + "\n")
    lines += ["\n", border, "\n"]
    return "".join(lines)


def build_captain_haddock_banner(frame: int = 0) -> str:
    cap_letters = [_C, _A, _P, _T, _I, _A, _N]
    had_letters = [_H, _A, _D, _D, _O, _C, _K]
    s      = Style.BRIGHT
    gap    = "  "
    raw_w  = 10 * 7 + len(gap) * 6     # 82
    pad    = _center_pad(raw_w)
    anc_p  = [Fore.CYAN + s + "⚓ ", Fore.WHITE + s + "≋ "]
    border = "".join(anc_p[i % 2] for i in range(_cols() // 2)) + RS

    lines = ["\n", border, "\n\n"]
    lines.append(_render_word(cap_letters, _CAPTAIN_COLORS, frame, gap))
    lines.append("\n")
    lines.append(_render_word(had_letters, _HADDOCK_COLORS, frame, gap))
    lines.append("\n")
    for col_code, text in [
        (Fore.CYAN,   "Blistering Barnacles!"),
        (Fore.WHITE,  "Thundering Typhoons!"),
        (Fore.YELLOW, "~ Master of the Karaboudjan ~"),
    ]:
        lines.append(pad + col_code + s + text.center(raw_w) + RS + "\n")
    lines += ["\n", border, "\n"]
    return "".join(lines)


# ═══════════════════════════════════════════════════════════
#  THE GOLDEN UNICORN  —  Detailed Three-Masted Ship
# ═══════════════════════════════════════════════════════════

def build_unicorn_ship(frame: int = 0) -> str:
    s  = Style.BRIGHT
    DK = Fore.YELLOW  + s
    SA = Fore.WHITE   + s
    RO = Fore.RED     + s
    GN = Fore.GREEN   + s
    MA = Fore.MAGENTA + s
    wave_c = [Fore.CYAN + s, Fore.BLUE + s, Fore.CYAN + s]
    WV = wave_c[frame % len(wave_c)]
    flag_c = [Fore.RED + s, Fore.YELLOW + s, Fore.WHITE + s]
    FL = flag_c[frame % len(flag_c)]

    ship_lines = [
        (FL,  "                  >>              >>              >>          "),
        (RO,  "                  /\\              /\\              /\\          "),
        (DK,  "                  |       .-.     |       .-.     |           "),
        (SA,  "               [_____] /     \\  [_____] /     \\  [_____]     "),
        (SA,  "               | TOP | |     |  | TOP | |     |  | TOP |     "),
        (SA,  "               |_____| \\     /  |_____| \\     /  |_____|     "),
        (DK,  "          .------.  |   '---'      |   '---'      |          "),
        (SA,  "        /=========\\ |  /~~~~~~~~~\\ |  /~~~~~~~~~\\ |          "),
        (SA,  "       | TOPSAIL   \\|/ | TOPSAIL  \\|/ | TOPSAIL  \\|          "),
        (SA,  "        \\==========/   \\=========/    \\=========/            "),
        (DK,  "    .---+-----+--------+------+--------+------+---.          "),
        (SA,  "   / MAINSAIL          | MAIN |         MIZZEN \\  \\          "),
        (SA,  "  /  ##  ##  ##  ##    | SAIL |   ##  ##  ##    \\ \\          "),
        (SA,  " /   ##  ##  ##  ##    |      |   ##  ##  ##     \\ \\         "),
        (SA,  "|    ##  ##  ##  ##    |      |   ##  ##  ##      | |        "),
        (SA,  " \\   ##  ##  ##  ##    |      |   ##  ##  ##     / /         "),
        (SA,  "  \\  ##  ##  ##  ##    |      |   ##  ##  ##    / /          "),
        (SA,  "   \\ ##  ##  ##  ##    |      |   ##  ##  ##   / /           "),
        (SA,  "    \\==================|      |=================/            "),
        (GN,  "        |            \\|/    /|\\            |                 "),
        (GN,  "        |    .--------+----+-+-----------.  |                "),
        (GN,  "        |   /         |    |              \\ |                "),
        (DK,  "  .-----+--+----------+----+----------+--+-----.            "),
        (DK,  "  |  ::::::::::::::::::::::::::::::::::::::::: |            "),
        (MA,  "  |  [==] [==] [==] [==] [==] [==] [==] [==]  |  UNICORN   "),
        (DK,  "  |  ::::::::::::::::::::::::::::::::::::::::: |            "),
        (DK,  " /   .--. .--. .--. .--. .--. .--. .--. .--.  \\           "),
        (DK,  "/   (    )(    )(    )(    )(    )(    )(    )   \\          "),
        (MA,  "|   |PORT||PORT||PORT||PORT||PORT||PORT||PORT|   |  ════════|"),
        (DK,  "|    '--'  '--'  '--'  '--'  '--'  '--'  '--'   |           "),
        (DK,  " \\  ##################################################### / "),
        (DK,  "  \\ ##################################################### /  "),
        (DK,  "   \\###################################################/    "),
    ]

    bowsprit = [
        (DK, "               /                                               "),
        (SA, "              /====\\                                           "),
        (SA, "             / SPR  \\                                          "),
        (DK, "            /________\\__                                       "),
    ]

    wave_sets = [
        ["~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~",
         "  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~",
         "~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  ~  "],
        ["≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋",
         "  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ",
         "≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈  ≈ "],
        ["∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿",
         "  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ",
         "∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼  ∼ "],
    ]
    waves = wave_sets[frame % len(wave_sets)]
    pad   = _center_pad(65)

    out = ["\n"]
    for col_code, line in bowsprit:
        out.append(pad + col_code + line + RS + "\n")
    for col_code, line in ship_lines:
        out.append(pad + col_code + line + RS + "\n")
    for wl in waves:
        out.append(pad + WV + wl + RS + "\n")
    out.append("\n")
    return "".join(out)


# ═══════════════════════════════════════════════════════════
#  PARROT  —  CROW'S NEST
# ═══════════════════════════════════════════════════════════

def build_parrot():
    g = Fore.GREEN; y = Fore.YELLOW; m = Fore.MAGENTA
    c = Fore.CYAN;  s = Style.BRIGHT
    return (
        f"\n{y}{s}       {g}*  {m}*  {y}*  {g}*  {m}*  {y}*  {g}*  {m}*  {y}*  {g}*\n"
        f"{g}{s}            .---------.\n"
        f"{g}{s}           /   {y}o   o   {g}\\        {m}{s}SQUAWK !!  SQUAWK !!\n"
        f"{g}{s}          |   {y}/\\_/\\{g}   |        {y}{s}CROW'S NEST  !!\n"
        f"{g}{s}          |    {Fore.RED}\\__/{g}    |        {c}{s}Close but WRONG position !\n"
        f"{g}{s}           \\    {y}--{g}    /\n"
        f"{g}{s}            `----------'\n"
        f"{g}{s}            /|        |\\\n"
        f"{g}{s}           / |  POLLY | \\\n"
        f"{g}{s}          /  | {y}the {g}   |  \\\n"
        f"{g}{s}         /   | {y}Parrot{g} |   \\\n"
        f"{g}{s}        /____|________|____\\\n"
        f"{y}{s}       {g}*  {m}*  {y}*  {g}*  {m}*  {y}*  {g}*  {m}*  {y}*  {g}*\n"
    )


# ═══════════════════════════════════════════════════════════
#  SKULL  —  WALK THE PLANK
# ═══════════════════════════════════════════════════════════

def build_skull():
    w = Fore.WHITE; r = Fore.RED; y = Fore.YELLOW; s = Style.BRIGHT
    return (
        f"\n{r}{s}       {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*\n"
        f"{w}{s}             .---------.\n"
        f"{w}{s}            /  {r}{s}X{w}     {r}{s}X{w}  \\        {r}{s}WRONG !!  WRONG !!\n"
        f"{w}{s}           |             |       {r}{s}WALK THE PLANK !!\n"
        f"{w}{s}           |   {r}/\\_/\\{w}   |\n"
        f"{w}{s}           |   {r}\\___/{w}   |\n"
        f"{w}{s}            \\  {w}_____  /\n"
        f"{w}{s}             `-|{r}R.I.P{w}|-'\n"
        f"{w}{s}             __|_____|__\n"
        f"{w}{s}            /           \\\n"
        f"{w}{s}           /  {r}*{w}       {r}*{w}  \\\n"
        f"{w}{s}          /_______________\\\n"
        f"{r}{s}          ================\n"
        f"{r}{s}          SKULL & CROSSBONES\n"
        f"{y}{s}       {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*\n"
    )


# ═══════════════════════════════════════════════════════════
#  CANNON
# ═══════════════════════════════════════════════════════════

def build_cannon(shot_num, max_shots):
    c = Fore.CYAN; y = Fore.YELLOW; r = Fore.RED
    s = Style.BRIGHT; dim = Style.DIM
    bar = (y + s + "O " * shot_num) + (dim + c + "o " * (max_shots - shot_num))
    return (
        f"\n{c}{s}         _________________\n"
        f"{c}{s}        |                 |\n"
        f"{c}{s}        |   {y}{s}C A N N O N{c}   |====={r}{s}O{c}     {y}{s}BOOM !!\n"
        f"{c}{s}        |_________________|\n"
        f"{c}{s}          {dim}o{c}             {dim}o\n"
        f"{c}{s}         {dim}/ \\           / \\\n"
        f"{c}{s}        {dim}/___\\         /___\\\n"
        f"{y}{s}\n"
        f"{y}{s}   Shots fired  :  [ {bar}{y}{s} ]\n"
        f"{y}{s}   Shot #{shot_num} of {max_shots}\n"
    )


# ═══════════════════════════════════════════════════════════
#  X MARKS THE SPOT
# ═══════════════════════════════════════════════════════════

def build_x_marks(frame=0):
    y = Fore.YELLOW; r = Fore.RED; g = Fore.GREEN; s = Style.BRIGHT
    stars = [
        f"{y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*",
        f"{r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*",
    ]
    sl = stars[frame % 2]
    return (
        f"\n{y}{s}       {sl}\n"
        f"\n{y}{s}         .-------------------------.\n"
        f"{y}{s}        /   {r}X{y}                     \\\n"
        f"{y}{s}       /     {r}\\{y}    {r}X  MARKS  THE   {y}\\\n"
        f"{y}{s}      /       {r}X{y}      SPOT  !!       \\\n"
        f"{y}{s}     /       {r}/ \\{y}                     \\\n"
        f"{y}{s}    /       {r}X{y}   {r}X{y}   {g}You are getting  {y}\\\n"
        f"{y}{s}   /                  {g}W A R M E R !!   \\\n"
        f"{y}{s}  /______________________________________\\\n"
        f"\n{y}{s}       {sl}\n"
    )


# ═══════════════════════════════════════════════════════════
#  TREASURE WIN
# ═══════════════════════════════════════════════════════════

def build_treasure_win(secret):
    y = Fore.YELLOW; g = Fore.GREEN; r = Fore.RED; s = Style.BRIGHT
    return (
        f"\n{y}{s}   *    *    *    *    *    *    *    *    *    *    *\n"
        f"\n{y}{s}         .------------------------------------.\n"
        f"{y}{s}        /  {r}$  $  $  $  $  $  $  $  $  $  $  {y}\\\n"
        f"{y}{s}       |  {r}$                               $  {y}|\n"
        f"{y}{s}       |  {r}$   R E D   R A C K H A M ' S  $  {y}|\n"
        f"{y}{s}       |  {r}$                               $  {y}|\n"
        f"{y}{s}       |  {r}$   G O L D   &  T R E A S U R E  ${y}|\n"
        f"{y}{s}       |  {r}$                               $  {y}|\n"
        f"{y}{s}       |  {r}$  $  $  $  $  $  $  $  $  $  $  {y}|\n"
        f"{y}{s}        \\____________________________________/\n"
        f"{y}{s}          ||||||||||||||||||||||||||||||||||||\n"
        f"\n{g}{s}   ╔══════════════════════════════════════════════════════╗\n"
        f"{g}{s}   ║                                                      ║\n"
        f"{g}{s}   ║   BLISTERING BARNACLES !  TREASURE  FOUND !!        ║\n"
        f"{g}{s}   ║                                                      ║\n"
        f"{g}{s}   ║   Secret coordinate was  :  [ {secret} ]                 ║\n"
        f"{g}{s}   ║   Red Rackham's gold is OURS, Tintin !               ║\n"
        f"{g}{s}   ║   Thundering Typhoons -- what a cannon shot !!!      ║\n"
        f"{g}{s}   ║                                                      ║\n"
        f"{g}{s}   ╚══════════════════════════════════════════════════════╝\n"
        f"\n{y}{s}   *    *    *    *    *    *    *    *    *    *    *\n"
    )


# ═══════════════════════════════════════════════════════════
#  PLANK LOSS
# ═══════════════════════════════════════════════════════════

def build_plank_loss(secret):
    r = Fore.RED; w = Fore.WHITE; s = Style.BRIGHT
    return (
        f"\n{r}{s}   SHIP =========================================|\n"
        f"{r}{s}                                                 |\n"
        f"{w}{s}                                             .---.\n"
        f"{w}{s}                                            ( o o )\n"
        f"{w}{s}                                             | ^ |\n"
        f"{w}{s}                                             |___|\n"
        f"{w}{s}                                         ~~~~~~~~~~~~~\n"
        f"\n{r}{s}   ╔══════════════════════════════════════════════════════╗\n"
        f"{r}{s}   ║                                                      ║\n"
        f"{r}{s}   ║   Ostrogoth !   Sea Gherkin !   Landlubber !         ║\n"
        f"{r}{s}   ║                                                      ║\n"
        f"{r}{s}   ║   You wasted all {MAX_GUESS} cannon shots.                    ║\n"
        f"{r}{s}   ║   Secret coordinate was  :  [ {secret} ]                 ║\n"
        f"{r}{s}   ║   Red Rackham wins this round ...                    ║\n"
        f"{r}{s}   ║                                                      ║\n"
        f"{r}{s}   ╚══════════════════════════════════════════════════════╝\n"
    )


# ═══════════════════════════════════════════════════════════
#  RULES
# ═══════════════════════════════════════════════════════════

def build_rules():
    c = Fore.CYAN; r = Fore.RED; g = Fore.GREEN
    y = Fore.YELLOW; s = Style.BRIGHT
    return (
        f"\n{c}{s}  ┌──────────────────────────────────────────────────────────┐\n"
        f"{c}{s}  │   CAPTAIN  HADDOCK  SPEAKS  :                            │\n"
        f"{c}{s}  │                                                          │\n"
        f"{c}{s}  │   Red Rackham's treasure is at a secret 3-digit         │\n"
        f"{c}{s}  │   coordinate.  No digit repeats!                        │\n"
        f"{c}{s}  │   You have {MAX_GUESS} CANNON SHOTS to find the treasure.      │\n"
        f"{c}{s}  │                                                          │\n"
        f"{c}{s}  │   {r}{s}WALK THE PLANK !  {c}  No digit is anywhere correct.    │\n"
        f"{c}{s}  │   {g}{s}CROW'S NEST !     {c}  Digit right, WRONG position.     │\n"
        f"{c}{s}  │   {y}{s}X MARKS THE SPOT! {c}  Digit right, RIGHT position.     │\n"
        f"{c}{s}  │                                                          │\n"
        f"{c}{s}  │   Multiple clues SORTED -- you won't know WHICH digit.  │\n"
        f"{c}{s}  └──────────────────────────────────────────────────────────┘\n"
    )


# ═══════════════════════════════════════════════════════════
#  GAME LOGIC
# ═══════════════════════════════════════════════════════════

def get_secret_num():
    numbers = list(range(10))
    random.shuffle(numbers)
    return ''.join(str(numbers[i]) for i in range(NUM_DIGITS))


def get_clues(guess, secret_num):
    if guess == secret_num:
        return 'HIT'
    clues = []
    for i in range(len(guess)):
        if guess[i] == secret_num[i]:
            clues.append('X MARKS THE SPOT!')
        elif guess[i] in secret_num:
            clues.append("CROW'S NEST!")
    if not clues:
        return 'WALK THE PLANK!'
    clues.sort()
    return '  +  '.join(clues)


def is_only_digits(num):
    return bool(num) and all(c in '0123456789' for c in num)


def animate_splash(seconds=10):
    cols = _cols()
    for elapsed in range(seconds):
        clear()
        print(build_unicorn_ship(elapsed))
        print(build_big_title(elapsed))
        remaining = seconds - elapsed
        cd_color  = Fore.YELLOW if remaining > 3 else Fore.RED
        countdown = f"  Setting sail in  {remaining}  second{'s' if remaining != 1 else ''}  ..."
        print(cd_color + Style.BRIGHT + countdown.center(cols))
        time.sleep(1)


def print_clue_block(clue, frame=0):
    r = Fore.RED;  g = Fore.GREEN
    y = Fore.YELLOW; s = Style.BRIGHT

    walk  = 'WALK THE PLANK' in clue
    crows = "CROW'S NEST"    in clue
    xmark = 'X MARKS'        in clue

    if walk and not crows and not xmark:
        print(build_pirates_banner(frame))
        print(build_skull())
        insult = random.choice(HADDOCK_INSULTS)
        print(r + s + f"   Captain Haddock shouts  :  {insult}\n")

    elif crows and not xmark:
        print(build_parrot())

    elif xmark and not crows:
        print(build_x_marks(frame))

    else:
        print(build_parrot())
        print(build_x_marks(frame))

    clue_color = r if walk else (y if xmark else g)
    print(clue_color + s + f"\n   CLUE  >>  {clue}\n")
    print(Fore.WHITE + "   " + "─" * 60 + "\n")


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

def main():
    animate_splash(seconds=10)

    clear()
    print(build_captain_haddock_banner(0))
    print(build_rules())
    input(Fore.YELLOW + Style.BRIGHT +
          "   Press ENTER to set sail, sea dog !   ")

    frame = 0

    while True:
        clear()
        print(build_unicorn_ship(frame))
        frame += 1

        secret_num    = get_secret_num()
        guesses_taken = 1
        won           = False

        print(Fore.CYAN + Style.BRIGHT +
              f"\n   I have thought up the secret coordinate.  "
              f"You have {MAX_GUESS} cannon shots !\n")

        while guesses_taken <= MAX_GUESS:
            print(build_cannon(guesses_taken, MAX_GUESS))

            guess = ''
            while len(guess) != NUM_DIGITS or not is_only_digits(guess):
                print(Fore.CYAN +
                      f"   Cannon Shot #{guesses_taken} of {MAX_GUESS}  "
                      f"|  Enter {NUM_DIGITS} digits  :  ", end='')
                guess = input().strip()
                if len(guess) != NUM_DIGITS or not is_only_digits(guess):
                    print(Fore.RED + Style.BRIGHT +
                          f"   Blistering Barnacles!  "
                          f"Enter exactly {NUM_DIGITS} digits only!\n")

            clue = get_clues(guess, secret_num)
            print()

            if clue == 'HIT':
                clear()
                print(build_unicorn_ship(frame))
                print(build_treasure_win(secret_num))
                won = True
                break

            print_clue_block(clue, frame)
            frame         += 1
            guesses_taken += 1

        if not won:
            clear()
            print(build_unicorn_ship(frame))
            print(build_plank_loss(secret_num))

        print(Fore.MAGENTA + Style.BRIGHT +
              "\n   Do you want to sail again, sea dog?  (yes / no)  :  ", end='')
        if not input().strip().lower().startswith('y'):
            clear()
            print(build_captain_haddock_banner(frame))
            print(build_unicorn_ship(frame))
            print(Fore.YELLOW + Style.BRIGHT +
                  "\n   Fair winds and following seas, Captain!  Goodbye!\n")
            break

        frame += 1


if __name__ == '__main__':
    main()
