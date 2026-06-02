# ============================================================
#   FOR THE PEACE OF THE KINGDOM
#   A Game Jam - "A Better Tomorrow"
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
    for i in range(2):
        for frame in frames:
            clearTerminal()
            print(f"\n\n          {frame}\n")
            time.sleep(0.12)
    clearTerminal()

def border(char="═", width=50):
    print(char * width)

def press_enter(msg="Press ENTER to continue..."):
    input(f"\n  {msg}")

def header(title):
    border()
    print(f"  {title}")
    border()

def safe_int(prompt, lo=None, hi=None):
    while True:
        try:
            val = int(input(prompt))
            if lo is not None and val < lo:
                print(f"  Enter at least {lo}.")
                continue
            if hi is not None and val > hi:
                print(f"  Enter at most {hi}.")
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

# Classes
class Alliance:
    def __init__(self, name, requirement, trust_lvl, military_support):
        self.name = name
        self.requirement = requirement   # gold cost to form
        self.trust_lvl = trust_lvl     # 0-100
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
        self.title = title # King / Queen
        self.name = name
        self.money = 1200
        self.population = 500
        self.knights = 50 # military size
        self.reputation = 50# 0-100 (people's favour)
        self.noble_favor = 50 # 0-100 (nobles' favour)
        self.taxes = 10 # gold per citizen per turn
        self.import_tax = 5 # % on traded goods
        self.maintenance = 2 # gold per knight per turn
        self.year = 1
        self.season = 1  # 1-4 (Spring/Summer/Autumn/Winter)
        self.alliances = []
        self.trade_routes = []
        self.enemy_strength = 300 # final battle difficulty

        # Available kingdoms for alliance
        self.potential_allies = [
            Alliance("Ironhold", 500, 40, 60),
            Alliance("Mirefen", 300, 30, 30),
            Alliance("Goldspire", 800, 60, 100),
        ]

    @property
    def season_name(self):
        return ["Spring", "Summer", "Autumn", "Winter"][self.season - 1]
    
    @property
    def turn_label(self):
        return f"Year {self.year}, {self.season_name}"
    
    def tick(self):# Advance one season.
        # Income
        tax_income = self.population * self.taxes // 100
        trade_income = sum(r["income"] for r in self.trade_routes)
        total_income = tax_income + trade_income

        # Expenses
        knight_cost = self.knights * self.maintenance
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
        #Knights + allied support.
        ally_support = sum(a.military_support for a in self.alliances)
        return self.knights + ally_support

    def is_bankrupt(self):
        return self.money <= 0

    def is_collapsed(self):
        return self.population <= 0 or self.reputation <= 0

# Event system
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
    idx = choose(labels)
    _, gold, knights, noble, rep, population = event["choices"][idx]

    kingdom.money = max(0,   kingdom.money       + gold)
    kingdom.knights = max(0,   kingdom.knights     + knights)
    kingdom.noble_favor = max(0, min(100, kingdom.noble_favor + noble))
    kingdom.reputation = max(0, min(100, kingdom.reputation  + rep))
    kingdom.population = max(0,   kingdom.population  + population)

    typing("\n  Decision made. For The Peace of The Kingdom...")
    pause(1)


def intro(k):
    loadingAnimation()
    slow_typing(f"What will you be known as (King... or Queen...)?")
    k.title = input("  Title (King/Queen): ").strip().capitalize() or "Ruler"
    k.name = input("  Name: ").strip() or "Unknown"
    loadingAnimation()

    clearTerminal()
    border("Ξ")
    print("  -- PROLOGUE --")
    border("Ξ")
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
    slow_typing(f"\n  For The Peace of The Kingdom, {k.title} {k.name}.")
    press_enter()