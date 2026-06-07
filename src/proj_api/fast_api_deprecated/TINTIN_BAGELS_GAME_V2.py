import random
import os
import time
import shutil
import colorama
from colorama import Fore, Back, Style

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

# ═══════════════════════════════════════════════════════════
#  ANIMATED SHIP  (wave animation via frame counter)
# ═══════════════════════════════════════════════════════════

def build_ship(frame=0):
    y      = Fore.YELLOW
    b      = Fore.BLUE
    w      = Fore.WHITE
    c      = Fore.CYAN
    r      = Fore.RED
    m      = Fore.MAGENTA
    dim    = Style.DIM
    bright = Style.BRIGHT

    wave_patterns = [
        f"{b}~    ~  ~~   ~~~~   ~~  ~    ~~   ~~~~   ~~  ~    ~~   ~~~~",
        f"{b}  ~~   ~~~~   ~~  ~   ~~     ~  ~~   ~~~~   ~~  ~   ~~   ~~ ",
        f"{b}~   ~~~~   ~~  ~   ~~   ~  ~~~~   ~~  ~   ~~   ~  ~~~~   ~~ ",
    ]
    wave1 = wave_patterns[frame % 3]
    wave2 = wave_patterns[(frame + 1) % 3]
    wave3 = wave_patterns[(frame + 2) % 3]

    return f"""
{c}{dim}                          .      *      .       *       .
{y}{bright}                                |\\
{y}{bright}                                | \\         {r}{bright}^
{y}{bright}                                |  \\       {r}{bright}/|\\
{y}{bright}                                |   \\      {r}{bright}/_\\
{y}{bright}                               /|    \\
{y}{bright}                              / |     \\          {w}{bright}___
{y}{bright}                             /  |      \\        {w}{bright}/___\\
{y}{bright}                            /   |       \\       {w}{bright}\\___/
{y}{bright}                           /    |        \\
{y}{bright}                          /     |         \\
{y}{bright}                _________/______|__________\\_________
{y}{bright}               /\\                                     /\\
{y}{bright}              /  \\                                   /  \\
{y}             /++++\\        {w}{bright}  THE  UNICORN  {y}       /++++\\
{y}            /++++++\\   {w}{bright}Red Rackham's Treasure Ship{y}  /++++++\\
{y}           /++++++++\\                               /++++++++\\
{y}          /++++++++++\\_____________________________/++++++++++\\
{y}{bright}         /___________________________________________________\\
{y}{bright}         |  {dim}██{bright}   {dim}██{bright}   {dim}██{bright}   {dim}██{bright}   {dim}██{bright}   {dim}██{bright}   {dim}██{bright}   {dim}██{bright}   {dim}██{bright}  |
{y}{bright}         |                                               |
{y}{bright}         |   {w}o       o       o       o       o       {y}|
{y}{bright}         |_______________________________________________|
{y}{bright}          \\                                             /
{y}{bright}           \\_____________________________________________/
{wave1}
{wave2}
{wave3}
"""

# ═══════════════════════════════════════════════════════════
#  BIG BLOCK-LETTER TITLE  (10 chars wide × 7 rows per letter)
# ═══════════════════════════════════════════════════════════

_T = [
    "██████████",
    "    ██    ",
    "    ██    ",
    "    ██    ",
    "    ██    ",
    "    ██    ",
    "    ██    ",
]
_I = [
    "██████████",
    "    ██    ",
    "    ██    ",
    "    ██    ",
    "    ██    ",
    "    ██    ",
    "██████████",
]
_N = [
    "██      ██",
    "███     ██",
    "████    ██",
    "██ ██   ██",
    "██  ██  ██",
    "██   ██ ██",
    "██    ████",
]

_TINTIN_LETTERS = [_T, _I, _N, _T, _I, _N]

_COLOR_SETS = [
    [Fore.RED,     Fore.YELLOW,  Fore.MAGENTA, Fore.RED,     Fore.YELLOW,  Fore.MAGENTA],
    [Fore.YELLOW,  Fore.CYAN,    Fore.RED,     Fore.YELLOW,  Fore.CYAN,    Fore.RED    ],
    [Fore.MAGENTA, Fore.RED,     Fore.YELLOW,  Fore.MAGENTA, Fore.RED,     Fore.YELLOW ],
]

def build_big_title(frame=0):
    cols   = shutil.get_terminal_size(fallback=(100, 24)).columns
    s      = Style.BRIGHT
    gap    = "   "
    raw_w  = 10 * 6 + 3 * 5        # 75 chars
    pad    = max(0, (cols - raw_w) // 2) * " "
    colors = _COLOR_SETS[frame % len(_COLOR_SETS)]

    star_pairs = [
        (Fore.RED    + s + "★ ", Fore.YELLOW + s + "✦ "),
        (Fore.YELLOW + s + "✦ ", Fore.CYAN   + s + "· "),
        (Fore.CYAN   + s + "· ", Fore.RED    + s + "★ "),
    ]
    sa, sb = star_pairs[frame % 3]
    border = "".join(sa if i % 2 == 0 else sb for i in range(cols // 2))

    lines = ["\n", border, "\n\n"]
    for row in range(7):
        row_parts = [colors[li] + s + _TINTIN_LETTERS[li][row] for li in range(6)]
        lines.append(pad + gap.join(row_parts) + "\n")

    subtitle_data = [
        (Fore.MAGENTA, "&  THE  SECRET  COORDINATES"),
        (Fore.CYAN,    "PIRATE  BAGELS  EDITION"),
        (Fore.YELLOW,  "~~  Inspired by Tintin  --  Herge  ~~"),
    ]
    lines.append("\n")
    for col_code, text in subtitle_data:
        lines.append(pad + col_code + s + text.center(raw_w) + "\n")

    lines += ["\n", border, "\n"]
    return "".join(lines)

# ═══════════════════════════════════════════════════════════
#  PIRATE  --  Red Rackham
# ═══════════════════════════════════════════════════════════

def build_pirate():
    r  = Fore.RED
    y  = Fore.YELLOW
    w  = Fore.WHITE
    c  = Fore.CYAN
    m  = Fore.MAGENTA
    s  = Style.BRIGHT
    dim = Style.DIM
    return f"""
{y}{s}     {r}*{y}   {r}*{y}   {r}*{y}   {r}*{y}   {r}*{y}   {r}*{y}   {r}*{y}   {r}*{y}   {r}*
{w}{s}            .-""""""-.
{w}{s}           /  {r}°{w}    {r}°{w}  \\         {r}{s}RED  RACKHAM
{w}{s}          |  {y}/\\ /\\{w}   |         {y}{s}The Dreaded Pirate!
{w}{s}          |   {r}\\--/{w}    |
{w}{s}           \\  {w}____  /
{w}{s}            `------'
{r}{s}          .--| {y}/\\{r} |--.
{r}{s}         / .-|_||_|-. \\
{r}{s}        |  |  {y}SKULL{r}  |  |      {y}Blistering Barnacles!
{r}{s}        |  |_{y}& BONES{r}_|  |
{r}{s}         \\ '----------' /
{r}{s}          '------------'
{r}{s}            |    |
{r}{s}           _|_  _|_
{r}{s}          /   \/   \\
{r}{s}         / RACKHAM  \\
{c}{s}        /___________\\
{y}{s}     {r}*{y}   {r}*{y}   {r}*{y}   {r}*{y}   {r}*{y}   {r}*{y}   {r}*{y}   {r}*{y}   {r}*
"""

# ═══════════════════════════════════════════════════════════
#  PARROT  --  CROW'S NEST
# ═══════════════════════════════════════════════════════════

def build_parrot():
    g  = Fore.GREEN
    y  = Fore.YELLOW
    m  = Fore.MAGENTA
    r  = Fore.RED
    c  = Fore.CYAN
    w  = Fore.WHITE
    s  = Style.BRIGHT
    return f"""
{y}{s}       {g}*  {m}*  {y}*  {g}*  {m}*  {y}*  {g}*  {m}*  {y}*  {g}*
{g}{s}            .---------.
{g}{s}           /   {y}o   o   {g}\\        {m}{s}SQUAWK !!  SQUAWK !!
{g}{s}          |   {y}/\\_/\\{g}   |        {y}{s}CROW'S NEST  !!
{g}{s}          |    {r}\\__/{g}    |        {c}{s}Close but WRONG position !
{g}{s}           \\    {y}--{g}    /
{g}{s}            `----------'
{g}{s}            /|        |\\
{g}{s}           / |  POLLY | \\
{g}{s}          /  | {y}the {g}   |  \\
{g}{s}         /   | {y}Parrot{g} |   \\
{g}{s}        /____|________|____\\
{y}{s}       {g}*  {m}*  {y}*  {g}*  {m}*  {y}*  {g}*  {m}*  {y}*  {g}*
"""

# ═══════════════════════════════════════════════════════════
#  SKULL  --  WALK THE PLANK
# ═══════════════════════════════════════════════════════════

def build_skull():
    w  = Fore.WHITE
    r  = Fore.RED
    y  = Fore.YELLOW
    s  = Style.BRIGHT
    dim = Style.DIM
    return f"""
{r}{s}       {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*
{w}{s}             .---------.
{w}{s}            /  {r}{s}X{w}     {r}{s}X{w}  \\        {r}{s}WRONG !!  WRONG !!
{w}{s}           |             |       {r}{s}WALK THE PLANK !!
{w}{s}           |   {r}/\\_/\\{w}   |
{w}{s}           |   {r}\\___/{w}   |
{w}{s}            \\  {w}_____  /
{w}{s}             `-|{r}R.I.P{w}|-'
{w}{s}             __|_____|__
{w}{s}            /           \\
{w}{s}           /  {r}*{w}       {r}*{w}  \\
{w}{s}          /_______________\\
{r}{s}          ================
{r}{s}          SKULL & CROSSBONES
{y}{s}       {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*
"""

# ═══════════════════════════════════════════════════════════
#  CANNON
# ═══════════════════════════════════════════════════════════

def build_cannon(shot_num, max_shots):
    c  = Fore.CYAN
    y  = Fore.YELLOW
    r  = Fore.RED
    w  = Fore.WHITE
    s  = Style.BRIGHT
    dim = Style.DIM
    shots_bar = (y + s + "O " * shot_num) + (dim + c + "o " * (max_shots - shot_num))
    return f"""
{c}{s}         _________________
{c}{s}        |                 |
{c}{s}        |   {y}{s}C A N N O N{c}   |====={r}{s}O{c}     {y}{s}BOOM !!
{c}{s}        |_________________|
{c}{s}          {dim}o{c}             {dim}o
{c}{s}         {dim}/ \\           / \\
{c}{s}        {dim}/___\\         /___\\
{c}{s}       {dim}/////////   /////////
{y}{s}
{y}{s}   Shots fired:  [ {shots_bar}{y}{s} ]
{y}{s}   Shot #{shot_num} of {max_shots}
"""

# ═══════════════════════════════════════════════════════════
#  X MARKS THE SPOT
# ═══════════════════════════════════════════════════════════

def build_x_marks(frame=0):
    y  = Fore.YELLOW
    r  = Fore.RED
    g  = Fore.GREEN
    s  = Style.BRIGHT
    stars = [
        f"{y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*",
        f"{r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*  {r}*  {y}*",
    ]
    star_line = stars[frame % 2]
    return f"""
{y}{s}       {star_line}
{y}{s}
{y}{s}         .-------------------------.
{y}{s}        /   {r}X{y}                     \\
{y}{s}       /     {r}\\{y}    {r}X  MARKS  THE   {y}\\
{y}{s}      /       {r}X{y}      SPOT  !!       \\
{y}{s}     /       {r}/ \\{y}                     \\
{y}{s}    /       {r}X{y}   {r}X{y}   {g}You are getting  {y}\\
{y}{s}   /                  {g}W A R M E R !!   \\
{y}{s}  /_____________________________ __________\\
{y}{s}
{y}{s}       {star_line}
"""

# ═══════════════════════════════════════════════════════════
#  TREASURE WIN
# ═══════════════════════════════════════════════════════════

def build_treasure_win(secret):
    y  = Fore.YELLOW
    g  = Fore.GREEN
    r  = Fore.RED
    w  = Fore.WHITE
    s  = Style.BRIGHT
    return f"""
{y}{s}   *    *    *    *    *    *    *    *    *    *    *
{y}{s}
{y}{s}         .------------------------------------.
{y}{s}        /  {r}$  $  $  $  $  $  $  $  $  $  $  {y}\\
{y}{s}       |  {r}$                               $  {y}|
{y}{s}       |  {r}$   R E D   R A C K H A M ' S  $  {y}|
{y}{s}       |  {r}$                               $  {y}|
{y}{s}       |  {r}$   G O L D   &   T R E A S U R E  ${y}|
{y}{s}       |  {r}$                               $  {y}|
{y}{s}       |  {r}$  $  $  $  $  $  $  $  $  $  $  {y}|
{y}{s}        \\____________________________________/
{y}{s}          ||||||||||||||||||||||||||||||||||||
{g}{s}
{g}{s}   ╔══════════════════════════════════════════════════════╗
{g}{s}   ║                                                      ║
{g}{s}   ║   BLISTERING BARNACLES !  TREASURE  FOUND !!        ║
{g}{s}   ║                                                      ║
{g}{s}   ║   Secret coordinate was  :  [ {secret} ]                 ║
{g}{s}   ║   Red Rackham's gold is OURS, Tintin !               ║
{g}{s}   ║   Thundering Typhoons -- what a cannon shot !!!      ║
{g}{s}   ║                                                      ║
{g}{s}   ╚══════════════════════════════════════════════════════╝
{y}{s}
{y}{s}   *    *    *    *    *    *    *    *    *    *    *
"""

# ═══════════════════════════════════════════════════════════
#  PLANK LOSS
# ═══════════════════════════════════════════════════════════

def build_plank_loss(secret):
    r  = Fore.RED
    y  = Fore.YELLOW
    w  = Fore.WHITE
    s  = Style.BRIGHT
    return f"""
{r}{s}   SHIP =========================================|
{r}{s}                                                 |
{r}{s}                                                 |
{w}{s}                                             .---.
{w}{s}                                            ( o o )
{w}{s}                                             | ^ |
{w}{s}                                             |___|
{w}{s}                                         ~~~~~~~~~~~~~
{r}{s}
{r}{s}   ╔══════════════════════════════════════════════════════╗
{r}{s}   ║                                                      ║
{r}{s}   ║   Ostrogoth !   Sea Gherkin !   Landlubber !         ║
{r}{s}   ║                                                      ║
{r}{s}   ║   You wasted all {MAX_GUESS} cannon shots.                    ║
{r}{s}   ║   Secret coordinate was  :  [ {secret} ]                 ║
{r}{s}   ║   Red Rackham wins this round ...                    ║
{r}{s}   ║                                                      ║
{r}{s}   ╚══════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════
#  RULES
# ═══════════════════════════════════════════════════════════

def build_rules():
    c  = Fore.CYAN
    r  = Fore.RED
    g  = Fore.GREEN
    y  = Fore.YELLOW
    w  = Fore.WHITE
    m  = Fore.MAGENTA
    s  = Style.BRIGHT
    return f"""
{c}{s}  ┌──────────────────────────────────────────────────────────┐
{c}{s}  │                                                          │
{c}{s}  │   CAPTAIN  HADDOCK  SPEAKS  :                           │
{c}{s}  │                                                          │
{c}{s}  │   Thundering Typhoons!  I have found the map!           │
{c}{s}  │   Red Rackham's treasure is at a secret 3-digit        │
{c}{s}  │   coordinate.  No digit repeats -- that scurvy         │
{c}{s}  │   pirate was too clever for that!                       │
{c}{s}  │                                                          │
{c}{s}  │   You have {MAX_GUESS} CANNON SHOTS to find the treasure.      │
{c}{s}  │                                                          │
{c}{s}  │   CLUES  AFTER  EACH  CANNON  SHOT  :                   │
{c}{s}  │                                                          │
{c}  │   {r}{s}WALK THE PLANK !  {c}  No digit is anywhere correct.    │
{c}  │   {g}{s}CROW'S NEST !     {c}  Digit right, WRONG position.     │
{c}  │   {y}{s}X MARKS THE SPOT! {c}  Digit right, RIGHT position.     │
{c}{s}  │                                                          │
{c}{s}  │   Multiple clues SORTED -- you won't know WHICH        │
{c}{s}  │   digit matched.  Think carefully, sea dog!             │
{c}{s}  │                                                          │
{c}{s}  └──────────────────────────────────────────────────────────┘
"""

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


def clear():
    os.system('clear' if os.name != 'nt' else 'cls')


def animate_splash(seconds=10):
    cols = shutil.get_terminal_size(fallback=(100, 24)).columns
    for elapsed in range(seconds):
        clear()
        print(build_ship(elapsed))
        print(build_big_title(elapsed))
        remaining = seconds - elapsed
        if remaining > 3:
            cd_color = Fore.YELLOW
        else:
            cd_color = Fore.RED
        countdown = f"  Setting sail in  {remaining}  second{'s' if remaining != 1 else ''} ..."
        print(cd_color + Style.BRIGHT + countdown.center(cols))
        time.sleep(1)


def print_clue_block(clue, frame=0):
    r = Fore.RED
    g = Fore.GREEN
    y = Fore.YELLOW
    w = Fore.WHITE
    s = Style.BRIGHT

    walk  = 'WALK THE PLANK' in clue
    crows = "CROW'S NEST"    in clue
    xmark = 'X MARKS'        in clue

    if walk and not crows and not xmark:
        print(build_skull())
        insult = random.choice(HADDOCK_INSULTS)
        print(r + s + f"   Captain Haddock shouts  :  {insult}\n")

    elif crows and not xmark:
        print(build_parrot())

    elif xmark and not crows:
        print(build_x_marks(frame))

    else:
        # mixed: both parrot and X
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
    print(build_ship(0))
    print(build_pirate())
    print(build_rules())
    input(Fore.YELLOW + Style.BRIGHT +
          "   Press ENTER to set sail, sea dog !   ")

    frame = 0

    while True:
        clear()
        print(build_ship(frame))
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
                print(build_ship(frame))
                print(build_treasure_win(secret_num))
                won = True
                break

            print_clue_block(clue, frame)
            frame        += 1
            guesses_taken += 1

        if not won:
            clear()
            print(build_ship(frame))
            print(build_plank_loss(secret_num))

        print(Fore.MAGENTA + Style.BRIGHT +
              "\n   Do you want to sail again, sea dog?  (yes / no)  :  ", end='')
        if not input().strip().lower().startswith('y'):
            clear()
            print(build_ship(frame))
            print(Fore.YELLOW + Style.BRIGHT +
                  "\n   Fair winds and following seas, Captain!  Goodbye!\n")
            print(build_pirate())
            break

        frame += 1


if __name__ == '__main__':
    main()
