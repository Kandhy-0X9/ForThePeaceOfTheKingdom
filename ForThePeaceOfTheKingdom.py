# ============================================================
#   FOR THE PEACE OF THE KINGDOM - prototype with minimum lore
#   A Game Jam Entry - "A Better Tomorrow"
# ============================================================

import os
import sys
import time
import random

# Helpers

def clearTerminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def typing(text, speed=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def slow_typing(text):
    typing(text, speed=0.07)

def pause(seconds=1.5):
    time.sleep(seconds)

def loadingAnimation():
    frames = ["_ _ _ _ _", "▌ _ _ _ _", "▌ ▌ _ _ _", "▌ ▌ ▌ _ _", "▌ ▌ ▌ ▌ _", "▌ ▌ ▌ ▌ ▌"]
    for _ in range(2):
        for frame in frames:
            clearTerminal()
            print(f"\n\n          {frame}\n")
            time.sleep(0.12)
    clearTerminal()

def border(char="═", width=50):
    print(char * width)

def header(title):
    border()
    print(f"  {title}")
    border()

def press_enter(msg="Press ENTER to continue..."):
    input(f"\n  {msg}")

def safe_int(prompt, lowest=None, highest=None):
    while True:
        try:
            val = int(input(prompt))
            if lowest is not None and val < lowest:
                print(f"  Enter at least {lowest}.")
                continue
            if highest is not None and val > highest:
                print(f"  Enter at most {highest}.")
                continue
            return val
        except ValueError:
            print("  Please enter a number.")

def choose(options):
    # Display numbered menu, return chosen index (0-based).
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    while True:
        try:
            choice = int(input("\n  Your choice: "))
            if 1 <= choice <= len(options):
                return choice - 1
        except ValueError:
            pass
        print("  Invalid choice.")

#  Classes

class Alliance:
    def __init__(self, name, requirement, trust_lvl, military_support):
        self.name          = name
        self.requirement   = requirement   # gold cost to form
        self.trust_lvl     = trust_lvl     # 0-100
        self.military_support = military_support  # soldiers they'll send in war

    def status(self):
        if self.trust_lvl >= 80:
            return "Strong Ally"
        elif self.trust_lvl >= 50:
            return "Friendly"
        elif self.trust_lvl >= 20:
            return "Neutral"
        else:
            return "Strained"

class Kingdom:
    def __init__(self, name, title):
        self.name        = name
        self.title       = title          # King / Queen
        self.money       = 1200
        self.population  = 500
        self.knights     = 50             # military size
        self.reputation  = 50            # 0-100 (people's favour)
        self.noble_favor = 50            # 0-100 (nobles' favour)
        self.taxes       = 10            # gold per citizen per turn
        self.import_tax  = 5             # % on traded goods
        self.maintenance = 2             # gold per knight per turn
        self.year        = 1
        self.season      = 1             # 1-4 (Spring/Summer/Autumn/Winter)
        self.alliances   = []
        self.trade_routes = []
        self.enemy_strength = 300        # final battle difficulty

        # Available kingdoms for alliance
        self.potential_allies = [
            Alliance("Ironhold",   500,  40, 60),
            Alliance("Mirefen",    300,  30, 30),
            Alliance("Goldspire",  800,  60, 100),
        ]

    @property
    def season_name(self):
        return ["Spring", "Summer", "Autumn", "Winter"][self.season - 1]

    @property
    def turn_label(self):
        return f"{self.season_name} of Year {self.year}"

    def tick(self):# Advance one season.
        # Income
        tax_income    = self.population * self.taxes // 100
        trade_income  = sum(r["income"] for r in self.trade_routes)
        total_income  = tax_income + trade_income

        # Expenses
        knight_cost   = self.knights * self.maintenance
        total_expenses = knight_cost

        net = total_income - total_expenses
        self.money += net

        # Population growth / decline based on reputation
        if self.reputation >= 70:
            growth = random.randint(5, 20)
        elif self.reputation >= 40:
            growth = random.randint(-5, 10)
        else:
            growth = random.randint(-20, -2)
        self.population = max(0, self.population + growth)

        # Military = 10 % of population (but player can train more; floor at natural draft)
        natural_army = self.population // 10
        if natural_army < self.knights:
            lost = self.knights - natural_army
            self.knights = natural_army
            print(f"\n  ⚠  Population drop — you lost {lost} soldiers.")

        # Advance season/year
        self.season += 1
        if self.season > 4:
            self.season = 1
            self.year  += 1

        return net, tax_income, trade_income, knight_cost

    def total_military(self):
        # Knights + allied support.
        ally_support = sum(a.military_support for a in self.alliances)
        return self.knights + ally_support

    def is_bankrupt(self):
        return self.money <= 0

    def is_collapsed(self):
        return self.population <= 0 or self.reputation <= 0

# Event System

RANDOM_EVENTS = [
    {
        "name": "Noble's Grand Feast",
        "desc": "A powerful noble requests you fund a lavish feast to celebrate his son's wedding.",
        "choices": [
            ("Fund the feast (-300 gold, +15 noble favour, -10 reputation)", -300, 0,  15, -10, 0),
            ("Decline politely (no cost, -10 noble favour)",                   0,  0, -10,   0, 0),
        ]
    },
    {
        "name": "Bandit Raid",
        "desc": "Bandits have attacked merchant caravans on the eastern road!",
        "choices": [
            ("Send knights to clear them (-5 knights, +10 reputation)",          0, -5,  0,  10, 0),
            ("Offer gold bounty (-200 gold, +5 reputation)",                  -200,  0,  0,   5, 0),
            ("Ignore it (-15 reputation, -100 from lost trade)",              -100,  0,  0, -15, 0),
        ]
    },
    {
        "name": "Monster Attack",
        "desc": "A creature from the deep forest terrorises outlying villages!",
        "choices": [
            ("Send elite knights (-8 knights, +20 reputation)",                 0, -8,  0,  20, 0),
            ("Hire mercenaries (-400 gold, +10 reputation)",                 -400,  0,  0,  10, 0),
            ("Evacuate villagers (-50 gold, -5 reputation, saves lives)",     -50,  0,  0,  -5, 0),
        ]
    },
    {
        "name": "Plague Scare",
        "desc": "Rumours of sickness spread through the lower districts.",
        "choices": [
            ("Fund healers (-350 gold, prevents population loss, +10 rep)",  -350,  0,  0,  10, 0),
            ("Quarantine district (-10 population, +5 reputation)",           0,  0,  0,   5, -10),
            ("Do nothing (-50 population, -20 reputation)",                     0,  0,  0, -20, 0),
        ]
    },
    {
        "name": "Harvest Festival",
        "desc": "Your people request a harvest festival to lift spirits.",
        "choices": [
            ("Sponsor the festival (-200 gold, +20 reputation)",             -200,  0,  0,  20, 0),
            ("Allow it, no funds (free, +5 reputation)",                        0,  0,  0,   5, 0),
            ("Cancel it (saves gold, -15 reputation)",                          0,  0,  0, -15, 0),
        ]
    },
    {
        "name": "Drought",
        "desc": "A dry summer threatens the food supply.",
        "choices": [
            ("Import grain (-300 gold, no population loss)",                 -300,  0,  0,   0, 0),
            ("Ration food (-10 reputation, saves gold)",                        0,  0,  0, -10, 0),
            ("Do nothing (-30 population, -10 reputation)",                   0,  0,  0, -10, -30),
        ]
    },
]

def trigger_random_event(kingdom):
    event = random.choice(RANDOM_EVENTS)
    clearTerminal()
    header(f"⚡  RANDOM EVENT: {event['name']}")
    typing(f"\n  {event['desc']}\n")
    pause(0.5)
    print("  What will you do?\n")

    labels = [c[0] for c in event["choices"]]
    idx    = choose(labels)
    _, gold, knights, noble, rep, population = event["choices"][idx]

    kingdom.money       = max(0,   kingdom.money       + gold)
    kingdom.knights     = max(0,   kingdom.knights     + knights)
    kingdom.noble_favor = max(0, min(100, kingdom.noble_favor + noble))
    kingdom.reputation  = max(0, min(100, kingdom.reputation  + rep))
    kingdom.population  = max(0,   kingdom.population  + population)

    typing("\n  Decision made. For The Peace of The Kingdom...")
    pause(1)

# Screens

def show_status(k):
    clearTerminal()
    header(f"  ♚  {k.turn_label} of {k.title} {k.name}")
    print(f"  💰  Treasury  :  {k.money:,} gold")
    print(f"  👥  Population:  {k.population:,}")
    print(f"  ⚔   Military  :  {k.knights} knights  (+{sum(a.military_support for a in k.alliances)} allied)")
    print(f"  ❤   Reputation:  {k.reputation}/100")
    print(f"  👑  Nobles     :  {k.noble_favor}/100")
    print(f"  📦  Trade routes: {len(k.trade_routes)}")
    if k.alliances:
        allies = ", ".join(a.name for a in k.alliances)
        print(f"  🤝  Allies     :  {allies}")
    else:
        print(f"  🤝  Allies     :  None")
    border()

def action_menu(k):
    # Main turn menu. Returns True if player wants to end turn.
    show_status(k)
    print("\n  What would you like to do?\n")
    options = [
        "Adjust Taxes",
        "Train Military",
        "Seek Alliance",
        "Open Trade Route",
        "Hold Court (reputation boost)",
        "End Turn",
    ]
    idx = choose(options)

    if idx == 0:  # Taxes
        clearTerminal()
        header("TAX POLICY")
        typing(f"  Current tax rate: {k.taxes} gold per 100 citizens.")
        typing(f"  Low taxes → happy people. High taxes → fat treasury.\n")
        new = safe_int("  New tax rate (1-30): ", 1, 30)
        old = k.taxes
        k.taxes = new
        if new > old:
            k.reputation = max(0, k.reputation - (new - old))
            typing(f"  Taxes raised. The people are... less than thrilled. (-{new-old} reputation)")
        elif new < old:
            k.reputation = min(100, k.reputation + (old - new) // 2)
            typing(f"  Taxes cut. The people cheer! (+{(old-new)//2} reputation)")
        else:
            typing("  No change.")
        pause()

    elif idx == 1:  # Military
        clearTerminal()
        header("TRAIN KNIGHTS")
        cost_per = 50
        typing(f"  Each knight costs {cost_per} gold to recruit and equip.")
        typing(f"  You have {k.money} gold and {k.knights} knights.\n")
        max_affordable = k.money // cost_per
        n = safe_int(f"  How many to recruit (0-{max_affordable})? ", 0, max_affordable)
        k.money   -= n * cost_per
        k.knights += n
        if n:
            typing(f"  {n} new knights join your ranks! Total: {k.knights}")
        pause()

    elif idx == 2:  # Alliance
        clearTerminal()
        header("SEEK ALLIANCE")
        available = [a for a in k.potential_allies if a not in k.alliances]
        if not available:
            typing("  You have forged all possible alliances!")
            pause()
            return False
        for i, a in enumerate(available, 1):
            print(f"  [{i}] {a.name}  —  costs {a.requirement} gold  |  trust {a.trust_lvl}/100  |  +{a.military_support} soldiers in war")
        print(f"  [{len(available)+1}] Cancel")
        choice = safe_int("  Choose: ", 1, len(available)+1) - 1
        if choice < len(available):
            a = available[choice]
            if k.money >= a.requirement:
                k.money -= a.requirement
                k.alliances.append(a)
                typing(f"\n  {a.name} agrees to stand with you! (-{a.requirement} gold)")
            else:
                typing(f"\n  You cannot afford the {a.requirement} gold gift.")
        pause()

    elif idx == 3:  # Trade
        clearTerminal()
        header("OPEN TRADE ROUTE")
        if len(k.trade_routes) >= 3:
            typing("  Your merchants are stretched thin. Max 3 routes.")
            pause()
            return False
        routes = [
            {"name": "Ironhold Ore",    "cost": 200, "income": 80},
            {"name": "Mirefen Spices",  "cost": 150, "income": 60},
            {"name": "Goldspire Silk",  "cost": 400, "income": 150},
            {"name": "Southern Lumber", "cost": 100, "income": 40},
        ]
        existing = [r["name"] for r in k.trade_routes]
        options  = [r for r in routes if r["name"] not in existing]
        if not options:
            typing("  All trade routes already established!")
            pause()
            return False
        print()
        for i, r in enumerate(options, 1):
            print(f"  [{i}] {r['name']}  —  costs {r['cost']} gold  |  earns {r['income']} gold/season")
        print(f"  [{len(options)+1}] Cancel")
        choice = safe_int("  Choose: ", 1, len(options)+1) - 1
        if choice < len(options):
            r = options[choice]
            if k.money >= r["cost"]:
                k.money -= r["cost"]
                k.trade_routes.append(r)
                typing(f"\n  Trade route with {r['name']} opened! Earns {r['income']} gold/season.")
            else:
                typing(f"\n  Not enough gold for the {r['cost']} startup investment.")
        pause()

    elif idx == 4:  # Hold court
        clearTerminal()
        header("HOLD COURT")
        typing("  You open the throne room to your people.")
        typing("  You listen to petitions, settle disputes, and share bread.\n")
        cost = 100
        if k.money >= cost:
            k.money      -= cost
            k.reputation  = min(100, k.reputation + 10)
            k.noble_favor = min(100, k.noble_favor + 5)
            typing(f"  The people adore you. (-{cost} gold, +10 reputation, +5 noble favour)")
        else:
            typing("  Your coffers are bare — you cannot afford the feast.")
        pause()

    elif idx == 5:  # End turn
        return True

    return False

def end_of_season_report(k, net, tax_income, trade_income, knight_cost):
    clearTerminal()
    header(f"END OF {k.season_name.upper()} REPORT")
    print(f"\n  Income")
    print(f"    Tax revenue  : +{tax_income} gold")
    print(f"    Trade income : +{trade_income} gold")
    print(f"  Expenses")
    print(f"    Army upkeep  : -{knight_cost} gold")
    print(f"  ─────────────────────────")
    sign = "+" if net >= 0 else ""
    print(f"    Net          : {sign}{net} gold")
    print(f"\n  Treasury now  : {k.money} gold")
    press_enter()

# Final Battle

def final_battle(k):
    clearTerminal()
    header("⚔   THE RECKONING")
    slow_typing(f"\n  Three years have passed, {k.title} {k.name}.")
    slow_typing("  The enemy kingdom — Vorreth — marches at last.\n")
    pause(1)

    player_power = k.total_military() + (k.reputation // 5) + (k.noble_favor // 10)
    enemy_power  = k.enemy_strength

    print(f"  Your forces : {player_power}  (knights + allies + morale)")
    print(f"  Enemy forces: {enemy_power}\n")
    pause(1.5)

    typing("  The battle begins...\n")
    pause(2)

    # Resolve
    margin = player_power - enemy_power

    if margin >= 50:
        outcome = "DECISIVE VICTORY"
        msg = [
            f"  Your armies crush Vorreth's forces!",
            f"  {k.name} is hailed as the greatest ruler in a generation.",
            f"  The kingdom prospers. Peace reigns.",
        ]
    elif margin >= 0:
        outcome = "NARROW VICTORY"
        msg = [
            f"  After brutal fighting, Vorreth retreats.",
            f"  The cost was heavy, but {k.name} holds the realm.",
            f"  A hard-won peace settles over the land.",
        ]
    elif margin >= -50:
        outcome = "DEFEAT — BUT SURVIVED"
        msg = [
            f"  Vorreth breaches the walls, but stops short of conquest.",
            f"  {k.name} signs a humiliating peace treaty.",
            f"  The kingdom survives, but its glory dims.",
        ]
    else:
        outcome = "THE KINGDOM FALLS"
        msg = [
            f"  Vorreth's armies overrun your defences.",
            f"  {k.name} is executed and his head is hang on a battlement.",
            f"  The realm you knew is no more.",
        ]

    border("═")
    print(f"\n  ★  {outcome}  ★\n")
    for line in msg:
        slow_typing(line)
        pause(0.5)
    print()
    border("═")

    # Score
    score = k.money // 10 + k.population // 2 + player_power * 3 + k.reputation * 2
    print(f"\n  Final Score: {score:,}")
    print(f"  Treasury: {k.money:,} gold  |  Population: {k.population:,}  |  Reputation: {k.reputation}/100")
    press_enter("Press ENTER to exit.")

# Main Game Loop

def intro(k):
    loadingAnimation()
    slow_typing(f"What will you be known as (King... or Queen...)?")
    k.title = input("  Title (King/Queen/Other title): ").strip().capitalize() or "Ruler"
    k.name  = input("  Name: ").strip() or "Unknown"
    loadingAnimation()

    clearTerminal()
    border("‡")
    print("  -- PROLOGUE --")
    border("‡")
    pause(0.5)

    slow_typing(f"\n  There once was a kingdom ruled by a fairly new sovereign — {k.title} {k.name}.")
    slow_typing("  Young, untested, and still learning the weight of the crown.")
    pause(0.8)
    slow_typing("\n  Your father left you a modest realm: a few hundred souls,")
    slow_typing("  a thinning treasury, and a handful of loyal knights.")
    pause(0.8)
    slow_typing("\n  But to the east, the warlords of Vorreth grow bold.")
    slow_typing("  Their spies whisper of your weakness. Their armies prepare.")
    pause(0.8)
    slow_typing("\n  You have three years.")
    slow_typing("  Grow your kingdom. Win alliances. Fill your coffers.")
    slow_typing("  Win the hearts of your people — and pray your knights hold fast.")
    pause(1)
    slow_typing(f"\n  The realm awaits, {k.title} {k.name}.")
    press_enter()

def run_game():
    k = Kingdom("", "Ruler")
    intro(k)

    max_turns = 12  # 3 years × 4 seasons
    turns_done = 0

    while turns_done < max_turns:
        # Player actions loop for this season
        while True:
            end_turn = action_menu(k)
            if end_turn:
                break

        # Advance season
        net, tax_income, trade_income, knight_cost = k.tick()
        end_of_season_report(k, net, tax_income, trade_income, knight_cost)
        turns_done += 1

        # Random event every 2 seasons
        if turns_done % 2 == 0 and turns_done < max_turns:
            trigger_random_event(k)

        # Check for early loss
        if k.is_bankrupt():
            clearTerminal()
            typing("\n  Your treasury is empty. Riots break out. The throne is lost.\n")
            press_enter()
            return

        if k.is_collapsed():
            clearTerminal()
            typing("\n  Your people have abandoned the kingdom. It crumbles into dust.\n")
            press_enter()
            return

    # Final battle
    final_battle(k)

# Entry Point

if __name__ == "__main__":
    run_game()