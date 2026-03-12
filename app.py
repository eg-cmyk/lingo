from flask import Flask, render_template, jsonify, request, session
import random

app = Flask(__name__)
app.secret_key = 'lingo-secret-key-2024'

COLOR_POINTS = {
    "white": 100, "red": 150, "blue": 150,
    "black": 200, "yellow": 250, "green": 200, "brown": 200,
}
HEIGHT_BONUS = {"high": 50, "mid": 0, "low": 25}

# ─── COMBO DESCRIPTIONS (used by sandbox) ───────────────────────────────────
COMBO_DESCRIPTIONS = {
    ("white","mid"):  "Basic synonym — find a word that means the same thing",
    ("white","high"): "Phonetic synonym — find a word that sounds the same or similar",
    ("white","low"):  "Meaning synonym — think about what the word represents",
    ("red","mid"):    "Spelling subtraction — remove letters or find a shorter form",
    ("red","high"):   "Phonetic subtraction — sounds like a simpler word",
    ("red","low"):    "Meaning subtraction — find a lesser, smaller, or simpler form",
    ("blue","mid"):   "Spelling addition — add letters or find a longer form",
    ("blue","high"):  "Phonetic addition — sounds like a bigger or more complex word",
    ("blue","low"):   "Meaning addition — find a greater, larger, or more intense form",
    ("black","mid"):  "Spelling opposite — find the antonym",
    ("black","high"): "Phonetic opposite — sounds like a reversal or contrast",
    ("black","low"):  "Meaning opposite — think about what contradicts this",
    ("yellow","mid"): "Spelling mix — anagram or wordplay with the letters",
    ("yellow","high"):"Phonetic mix — sounds scrambled or transformed",
    ("yellow","low"): "Meaning mix — lateral thinking, unexpected association",
    ("green","mid"):  "Contextual spelling — what word fits this situation?",
    ("green","high"): "Contextual sound — what sounds right in this context?",
    ("green","low"):  "Contextual meaning — use your surroundings and knowledge",
    ("brown","mid"):  "Time + spelling — what comes next or before?",
    ("brown","high"): "Time + sound — what sounds like the next step in time?",
    ("brown","low"):  "Time + meaning — what follows or precedes this?",
}

# ─── SANDBOX PUZZLE BANK ────────────────────────────────────────────────────
# All 21 color+height combos, multiple puzzles each
SANDBOX_BANK = {
    ("white","mid"): [
        {"clue":"HAPPY",   "answer":"JOY",      "alternates":["GLAD","JOYFUL","ELATED","CHEERFUL"],"hint":"A positive emotion"},
        {"clue":"LARGE",   "answer":"BIG",       "alternates":["HUGE","GIANT","ENORMOUS","MASSIVE"],"hint":"Not small"},
        {"clue":"FAST",    "answer":"QUICK",     "alternates":["SWIFT","RAPID","SPEEDY"],"hint":"Moving rapidly"},
        {"clue":"COLD",    "answer":"FRIGID",    "alternates":["CHILLY","FREEZING","ICY","COOL"],"hint":"Very low temperature"},
        {"clue":"BRAVE",   "answer":"BOLD",      "alternates":["COURAGEOUS","FEARLESS","DARING"],"hint":"Not afraid"},
        {"clue":"SMART",   "answer":"CLEVER",    "alternates":["INTELLIGENT","BRIGHT","WISE"],"hint":"Quick-minded"},
        {"clue":"TIRED",   "answer":"WEARY",     "alternates":["EXHAUSTED","SLEEPY","FATIGUED"],"hint":"In need of rest"},
    ],
    ("white","high"): [
        {"clue":"SEA",     "answer":"SEE",       "hint":"To perceive with your eyes"},
        {"clue":"BARE",    "answer":"BEAR",      "hint":"The forest animal"},
        {"clue":"WRITE",   "answer":"RIGHT",     "hint":"Correct, or a direction"},
        {"clue":"KNIGHT",  "answer":"NIGHT",     "hint":"Darkness — silent K"},
        {"clue":"FLOWER",  "answer":"FLOUR",     "hint":"Used for baking"},
        {"clue":"FRIGHT",  "answer":"FREIGHT",   "hint":"Cargo — sounds like frate"},
        {"clue":"HAIR",    "answer":"HARE",      "hint":"A rabbit-like animal"},
        {"clue":"MEET",    "answer":"MEAT",      "hint":"Animal flesh — sounds like meet"},
    ],
    ("white","low"): [
        {"clue":"A DOG'S HOME",      "answer":"KENNEL",  "hint":"Where dogs sleep"},
        {"clue":"WHAT TREES GIVE",   "answer":"SHADE",   "hint":"Shelter from sunlight"},
        {"clue":"A SAILOR'S TOOL",   "answer":"COMPASS", "hint":"Shows direction"},
        {"clue":"WHAT BEES MAKE",    "answer":"HONEY",   "hint":"Sweet golden liquid"},
        {"clue":"SOUND OF THUNDER",  "answer":"RUMBLE",  "alternates":["BOOM","CRASH"],"hint":"A deep rolling noise"},
    ],
    ("red","mid"): [
        {"clue":"BEAUTIFUL",  "answer":"CUTE",    "alternates":["PRETTY","NICE"],"hint":"Simpler compliment"},
        {"clue":"ENORMOUS",   "answer":"BIG",     "alternates":["LARGE","GREAT"],"hint":"Simpler size word"},
        {"clue":"FAMISHED",   "answer":"HUNGRY",  "hint":"Less intense hunger"},
        {"clue":"SPRINTING",  "answer":"RUNNING", "hint":"Less intense speed"},
        {"clue":"FREEZING",   "answer":"COLD",    "hint":"Less extreme temperature"},
        {"clue":"FURIOUS",    "answer":"ANGRY",   "alternates":["MAD","UPSET"],"hint":"Less intense emotion"},
    ],
    ("red","high"): [
        {"clue":"SCENT",   "answer":"SENT",  "hint":"Past tense of send — sounds the same"},
        {"clue":"KNOT",    "answer":"NOT",   "hint":"The negative — silent K"},
        {"clue":"WRAP",    "answer":"RAP",   "hint":"Silent W — a music genre"},
        {"clue":"THROUGH", "answer":"THREW", "hint":"Past tense of throw"},
        {"clue":"GNAW",    "answer":"NAW",   "hint":"To chew — silent G"},
        {"clue":"KNIGHT",  "answer":"NITE",  "hint":"Informal spelling of night"},
    ],
    ("red","low"): [
        {"clue":"SPRINT",  "answer":"WALK",    "hint":"Much slower movement"},
        {"clue":"OCEAN",   "answer":"LAKE",    "hint":"Smaller body of water"},
        {"clue":"STORM",   "answer":"DRIZZLE", "hint":"Lighter rain"},
        {"clue":"MANSION", "answer":"HOUSE",   "hint":"A humbler dwelling"},
        {"clue":"BEACH",   "answer":"SAND",    "hint":"Remove the water"},
        {"clue":"EXPERT",  "answer":"NOVICE",  "hint":"A beginner"},
        {"clue":"ROAR",    "answer":"WHISPER", "hint":"Much quieter"},
        {"clue":"BLIZZARD","answer":"FROST",   "hint":"Lighter cold weather"},
    ],
    ("blue","mid"): [
        {"clue":"BIG",     "answer":"ENORMOUS",  "alternates":["HUGE","MASSIVE","GIANT"],"hint":"More extreme size"},
        {"clue":"COLD",    "answer":"FREEZING",  "alternates":["FRIGID","ICY"],"hint":"More extreme chill"},
        {"clue":"ANGRY",   "answer":"FURIOUS",   "alternates":["ENRAGED","LIVID"],"hint":"More intense anger"},
        {"clue":"FAST",    "answer":"LIGHTNING",  "hint":"Superlative speed"},
        {"clue":"SMART",   "answer":"GENIUS",    "hint":"Extreme intelligence"},
    ],
    ("blue","high"): [
        {"clue":"ATE",   "answer":"EIGHT",  "hint":"The number — sounds like ate"},
        {"clue":"AIR",   "answer":"HEIR",   "hint":"One who inherits — sounds like air"},
        {"clue":"OR",    "answer":"OAR",    "hint":"Used to row — sounds like or"},
        {"clue":"EYE",   "answer":"AYE",    "hint":"A vote of yes — sounds like eye"},
        {"clue":"SO",    "answer":"SOW",    "hint":"To plant seeds — sounds like so"},
        {"clue":"BY",    "answer":"BUY",    "alternates":["BYE"],"hint":"To purchase — sounds like by"},
    ],
    ("blue","low"): [
        {"clue":"WALK",    "answer":"SPRINT",  "hint":"Much faster movement"},
        {"clue":"POND",    "answer":"OCEAN",   "hint":"The largest body of water"},
        {"clue":"CREEK",   "answer":"RIVER",   "hint":"A larger waterway"},
        {"clue":"COTTAGE", "answer":"MANSION", "hint":"A grander home"},
        {"clue":"SAND",    "answer":"BEACH",   "hint":"Add water and waves"},
        {"clue":"WHISPER", "answer":"SHOUT",   "hint":"Much louder"},
        {"clue":"DRIZZLE", "answer":"STORM",   "hint":"More intense weather"},
    ],
    ("black","mid"): [
        {"clue":"DAY",     "answer":"NIGHT",   "hint":"The other half of a cycle"},
        {"clue":"LOVE",    "answer":"HATE",    "hint":"The opposite feeling"},
        {"clue":"WAR",     "answer":"PEACE",   "hint":"The opposite of conflict"},
        {"clue":"RICH",    "answer":"POOR",    "hint":"The other end of wealth"},
        {"clue":"ANCIENT", "answer":"MODERN",  "hint":"The opposite in time"},
        {"clue":"BEGIN",   "answer":"END",     "hint":"Where things finish"},
        {"clue":"FULL",    "answer":"EMPTY",   "hint":"Nothing inside"},
        {"clue":"NORTH",   "answer":"SOUTH",   "hint":"Opposite compass direction"},
    ],
    ("black","high"): [
        {"clue":"KNOW",    "answer":"NO",    "hint":"Refusal — sounds like know"},
        {"clue":"PEACE",   "answer":"PIECE", "hint":"A fragment — sounds identical"},
        {"clue":"WHOLE",   "answer":"HOLE",  "hint":"An empty space"},
        {"clue":"MALE",    "answer":"MAIL",  "hint":"Letters — sounds like male"},
        {"clue":"WEAK",    "answer":"WEEK",  "hint":"Seven days — sounds like weak"},
        {"clue":"KNOT",    "answer":"NOT",   "hint":"Negation — sounds like knot"},
    ],
    ("black","low"): [
        {"clue":"SUNRISE",  "answer":"SUNSET",   "hint":"The opposite time of day"},
        {"clue":"PREDATOR", "answer":"PREY",     "hint":"The hunted, not the hunter"},
        {"clue":"QUESTION", "answer":"ANSWER",   "hint":"The response"},
        {"clue":"TEACHER",  "answer":"STUDENT",  "hint":"The one who learns"},
        {"clue":"VICTORY",  "answer":"DEFEAT",   "hint":"The opposite outcome"},
        {"clue":"CHAOS",    "answer":"ORDER",    "alternates":["CALM","PEACE"],"hint":"The opposite of disorder"},
    ],
    ("yellow","mid"): [
        {"clue":"ANAGRAM OF 'LEMON'",   "answer":"MELON",  "hint":"A juicy green fruit"},
        {"clue":"ANAGRAM OF 'EARTH'",   "answer":"HEART",  "hint":"Pumps blood"},
        {"clue":"ANAGRAM OF 'LISTEN'",  "answer":"SILENT", "hint":"Making no sound"},
        {"clue":"ANAGRAM OF 'DUSTY'",   "answer":"STUDY",  "hint":"What students do"},
        {"clue":"ANAGRAM OF 'NIGHT'",   "answer":"THING",  "hint":"An object or matter"},
        {"clue":"ANAGRAM OF 'SPARE'",   "answer":"REAPS",  "hint":"Harvests crops"},
        {"clue":"ANAGRAM OF 'BELOW'",   "answer":"ELBOW",  "hint":"A joint in your arm"},
        {"clue":"ANAGRAM OF 'STARE'",   "answer":"TEARS",  "hint":"From crying — or rips"},
    ],
    ("yellow","high"): [
        {"clue":"SOUNDS LIKE A NUMBER + A LETTER: 'ATE'+'ING'", "answer":"EATING", "hint":"Consuming food"},
        {"clue":"SAY 'ICE CREAM' FAST — WHAT DO YOU HEAR?",     "answer":"I SCREAM","hint":"A homophone phrase"},
        {"clue":"SOUNDS LIKE 'FOR' + 'TY'",                     "answer":"FORTY",  "hint":"The number 40"},
        {"clue":"WHAT DOES 'CELLAR' SOUND LIKE?",               "answer":"SELLER", "hint":"One who sells"},
        {"clue":"SOUNDS LIKE 'PROPHET'",                        "answer":"PROFIT", "hint":"Financial gain"},
    ],
    ("yellow","low"): [
        {"clue":"FIRE + WATER",          "answer":"STEAM",  "hint":"What you get when they meet"},
        {"clue":"DAY + NIGHT TOGETHER",  "answer":"TIME",   "alternates":["CYCLE","DAY"],"hint":"The bigger concept"},
        {"clue":"SILENCE + MUSIC",       "answer":"PAUSE",  "alternates":["REST","BREAK"],"hint":"A moment between sounds"},
        {"clue":"COLD + WET",            "answer":"SNOW",   "alternates":["SLEET","ICE","FROST"],"hint":"Winter precipitation"},
        {"clue":"SWEET + COLD",          "answer":"ICECREAM","alternates":["ICE CREAM","SORBET"],"hint":"A frozen dessert"},
    ],
    ("green","mid"): [
        {"clue":"WHAT YOU SEE WHEN YOU LOOK UP OUTSIDE",  "answer":"SKY",    "hint":"Above you"},
        {"clue":"WHAT COVERS THE GROUND IN A GARDEN",     "answer":"GRASS",  "alternates":["SOIL","EARTH","DIRT"],"hint":"Green and grows"},
        {"clue":"WHAT A DOOR HAS THAT LETS YOU IN",       "answer":"HANDLE", "alternates":["KNOB","LOCK"],"hint":"You grab it"},
        {"clue":"WHAT YOU STAND ON INSIDE A HOUSE",       "answer":"FLOOR",  "hint":"Not the ceiling"},
        {"clue":"WHAT HOLDS BOOKS IN A LIBRARY",          "answer":"SHELF",  "alternates":["SHELVES"],"hint":"A flat surface on a wall"},
    ],
    ("green","high"): [
        {"clue":"WHAT A BEE DOES — SOUNDS LIKE 'HYMN'",              "answer":"HUM",    "hint":"Buzzing sound"},
        {"clue":"WHAT YOU CALL A PATH — SOUNDS LIKE 'ROAD'",         "answer":"RODE",   "hint":"Past tense of ride"},
        {"clue":"WHAT WIND DOES — RHYMES WITH 'FLOWS'",              "answer":"BLOWS",  "hint":"Air in motion"},
        {"clue":"WHAT THE SUN DOES — RHYMES WITH 'BITES'",           "answer":"LIGHTS", "hint":"Illuminates"},
        {"clue":"WHAT WATER DOES DOWNHILL — SOUNDS LIKE 'RUNES'",    "answer":"RUNS",   "hint":"Flows quickly"},
    ],
    ("green","low"): [
        {"clue":"WHAT YOU SIT ON IN A PARK",           "answer":"BENCH",    "hint":"Found along paths"},
        {"clue":"WHAT BIRDS BUILD IN TREES",           "answer":"NEST",     "hint":"Home for eggs"},
        {"clue":"WHAT FALLS FROM TREES IN AUTUMN",     "answer":"LEAVES",   "hint":"Seasonal shedding"},
        {"clue":"WHAT YOU WALK UNDER IN THE RAIN",     "answer":"UMBRELLA", "hint":"Keeps you dry"},
        {"clue":"WHAT A CLOCK DOES EVERY SECOND",      "answer":"TICK",     "hint":"The sound it makes"},
        {"clue":"WHAT YOU SEE AFTER RAIN IN THE SKY",  "answer":"RAINBOW",  "hint":"Seven colours"},
        {"clue":"WHAT A CANDLE GIVES IN THE DARK",     "answer":"LIGHT",    "hint":"Illumination"},
    ],
    ("brown","mid"): [
        {"clue":"MORNING → ?",    "answer":"EVENING",    "hint":"Later in the day"},
        {"clue":"SPRING → ?",     "answer":"SUMMER",     "hint":"The next season"},
        {"clue":"YESTERDAY → ?",  "answer":"TOMORROW",   "hint":"Skip today"},
        {"clue":"DECADE → ?",     "answer":"CENTURY",    "hint":"10x longer"},
        {"clue":"CENTURY → ?",    "answer":"MILLENNIUM", "hint":"10x longer still"},
        {"clue":"DAWN → ?",       "answer":"DUSK",       "hint":"The other end of the day"},
        {"clue":"JANUARY → ?",    "answer":"FEBRUARY",   "hint":"The next month"},
    ],
    ("brown","high"): [
        {"clue":"SOUNDS LIKE THE DAY AFTER 'MONDAY'",       "answer":"TUESDAY",   "hint":"Second weekday"},
        {"clue":"SOUNDS LIKE 'WEAK' BUT MEANS 7 DAYS",      "answer":"WEEK",      "hint":"A unit of time"},
        {"clue":"SOUNDS LIKE 'MOURNING' BUT IT'S EARLY DAY","answer":"MORNING",   "hint":"Start of the day"},
        {"clue":"SOUNDS LIKE 'KNEEL' BUT MEANS TO DROP",    "answer":"KNEEL",     "hint":"To go down on one knee"},
        {"clue":"SOUNDS LIKE 'HOUR' — A UNIT OF TIME",      "answer":"OUR",       "hint":"Belonging to us — sounds like hour"},
    ],
    ("brown","low"): [
        {"clue":"WHAT COMES AFTER CHILDHOOD",       "answer":"ADULTHOOD",  "alternates":["YOUTH","ADOLESCENCE","TEENS"],"hint":"Growing up"},
        {"clue":"WHAT A SEED BECOMES",              "answer":"PLANT",      "alternates":["TREE","FLOWER"],"hint":"It grows"},
        {"clue":"WHAT WINTER BECOMES",              "answer":"SPRING",     "hint":"The warmer season that follows"},
        {"clue":"WHAT A TADPOLE BECOMES",           "answer":"FROG",       "hint":"An amphibian"},
        {"clue":"WHAT NIGHT BECOMES",               "answer":"DAY",        "alternates":["DAWN","MORNING"],"hint":"Light returns"},
        {"clue":"WHAT A CATERPILLAR BECOMES",       "answer":"BUTTERFLY",  "alternates":["MOTH"],"hint":"It flies"},
    ],
}

# ─── TUTORIAL STAGES ────────────────────────────────────────────────────────
STAGES = [
    {
        "name": "Stage 1 — The Basics",
        "unlocks": {"color": "white", "height": "mid"},
        "intro": "White tiles test basic vocabulary. Mid height means the clue is about spelling — read it straight and find a synonym.",
        "puzzles": [
            {"clue": "HAPPY",  "answer": "JOY",    "alternates":["GLAD","JOYFUL","ELATED"], "height": "mid", "color": "white", "hint": "A simple positive emotion"},
            {"clue": "LARGE",  "answer": "BIG",    "alternates":["HUGE","GIANT","ENORMOUS"], "height": "mid", "color": "white", "hint": "Not small"},
            {"clue": "FAST",   "answer": "QUICK",  "alternates":["SWIFT","RAPID","SPEEDY"], "height": "mid", "color": "white", "hint": "Moving rapidly"},
            {"clue": "COLD",   "answer": "FRIGID", "alternates":["CHILLY","FREEZING","ICY"], "height": "mid", "color": "white", "hint": "Extremely low temperature"},
            {"clue": "CAT",    "answer": "FELINE", "alternates":["KITTY","KITTEN"], "height": "mid", "color": "white", "hint": "The scientific family name"},
        ],
    },
    {
        "name": "Stage 2 — Sound It Out",
        "unlocks": {"color": "white", "height": "high"},
        "intro": "High tiles are above eye level — they're about SOUND. Think homophones and phonetic spellings.",
        "puzzles": [
            {"clue": "SEA",    "answer": "SEE",     "height": "high", "color": "white", "hint": "To perceive with your eyes"},
            {"clue": "BARE",   "answer": "BEAR",    "height": "high", "color": "white", "hint": "The forest animal"},
            {"clue": "WRITE",  "answer": "RIGHT",   "height": "high", "color": "white", "hint": "Correct — or a direction"},
            {"clue": "KNIGHT", "answer": "NIGHT",   "height": "high", "color": "white", "hint": "Silent K — darkness"},
            {"clue": "FLOWER", "answer": "FLOUR",   "height": "high", "color": "white", "hint": "Used for baking bread"},
            {"clue": "FRIGHT", "answer": "FREIGHT", "height": "high", "color": "white", "hint": "Cargo shipped by truck or train"},
        ],
    },
    {
        "name": "Stage 3 — Opposites",
        "unlocks": {"color": "black", "height": "mid"},
        "intro": "Black tiles mean REVERSAL — find the opposite, antonym, or direct contrast of the clue word.",
        "puzzles": [
            {"clue": "DAY",     "answer": "NIGHT",   "height": "mid", "color": "black", "hint": "The other half of a cycle"},
            {"clue": "LOVE",    "answer": "HATE",    "height": "mid", "color": "black", "hint": "The opposite feeling"},
            {"clue": "WAR",     "answer": "PEACE",   "height": "mid", "color": "black", "hint": "The opposite of conflict"},
            {"clue": "RICH",    "answer": "POOR",    "height": "mid", "color": "black", "hint": "The other end of wealth"},
            {"clue": "ANCIENT", "answer": "MODERN",  "height": "mid", "color": "black", "hint": "The opposite in time"},
            {"clue": "BEGIN",   "answer": "END",     "height": "mid", "color": "black", "hint": "Where things finish"},
        ],
    },
    {
        "name": "Stage 4 — Take It Down",
        "unlocks": {"color": "red", "height": "low"},
        "intro": "Red means SUBTRACTION — find a lesser, smaller, or simpler form. Low height means meaning matters, not spelling.",
        "puzzles": [
            {"clue": "SPRINT",  "answer": "WALK",    "height": "low", "color": "red", "hint": "Much slower movement"},
            {"clue": "OCEAN",   "answer": "LAKE",    "height": "low", "color": "red", "hint": "Smaller body of water"},
            {"clue": "STORM",   "answer": "DRIZZLE", "height": "low", "color": "red", "hint": "Lighter rain"},
            {"clue": "MANSION", "answer": "HOUSE",   "height": "low", "color": "red", "hint": "A humbler dwelling"},
            {"clue": "BEACH",   "answer": "SAND",    "height": "low", "color": "red", "hint": "Remove the water and waves"},
            {"clue": "EXPERT",  "answer": "NOVICE",  "height": "low", "color": "red", "hint": "A beginner"},
        ],
    },
    {
        "name": "Stage 5 — Build It Up",
        "unlocks": {"color": "blue", "height": "low"},
        "intro": "Blue means ADDITION — find a greater, bigger, or more intense form of the clue word.",
        "puzzles": [
            {"clue": "WALK",    "answer": "SPRINT",  "height": "low", "color": "blue", "hint": "Much faster movement"},
            {"clue": "POND",    "answer": "OCEAN",   "height": "low", "color": "blue", "hint": "The largest body of water"},
            {"clue": "CREEK",   "answer": "RIVER",   "height": "low", "color": "blue", "hint": "A larger waterway"},
            {"clue": "COTTAGE", "answer": "MANSION", "height": "low", "color": "blue", "hint": "A grander home"},
            {"clue": "SAND",    "answer": "BEACH",   "height": "low", "color": "blue", "hint": "Add water and waves"},
            {"clue": "WHISPER", "answer": "SHOUT",   "height": "low", "color": "blue", "hint": "Much louder"},
        ],
    },
    {
        "name": "Stage 6 — Through Time",
        "unlocks": {"color": "brown", "height": "mid"},
        "intro": "Brown tiles deal with TIME — what comes next, what comes before, or how time scales up or down.",
        "puzzles": [
            {"clue": "MORNING → ?",   "answer": "EVENING",    "height": "mid", "color": "brown", "hint": "Later the same day"},
            {"clue": "SPRING → ?",    "answer": "SUMMER",     "height": "mid", "color": "brown", "hint": "The next season"},
            {"clue": "YESTERDAY → ?", "answer": "TOMORROW",   "height": "mid", "color": "brown", "hint": "Skip today"},
            {"clue": "DECADE → ?",    "answer": "CENTURY",    "height": "mid", "color": "brown", "hint": "10x longer than a decade"},
            {"clue": "CENTURY → ?",   "answer": "MILLENNIUM", "height": "mid", "color": "brown", "hint": "10x longer than a century"},
            {"clue": "DAWN → ?",      "answer": "DUSK",       "height": "mid", "color": "brown", "hint": "The opposite end of the day"},
        ],
    },
    {
        "name": "Stage 7 — Read the Room",
        "unlocks": {"color": "green", "height": "low"},
        "intro": "Green tiles use CONTEXT — the answer comes from your surroundings or situational knowledge.",
        "puzzles": [
            {"clue": "WHAT YOU SIT ON IN A PARK",          "answer": "BENCH",   "height": "low", "color": "green", "hint": "Found along pathways"},
            {"clue": "WHAT BIRDS BUILD IN TREES",          "answer": "NEST",    "height": "low", "color": "green", "hint": "Home for eggs"},
            {"clue": "WHAT FALLS FROM TREES IN AUTUMN",    "answer": "LEAVES",  "height": "low", "color": "green", "hint": "Seasonal shedding"},
            {"clue": "WHAT YOU WALK UNDER IN THE RAIN",    "answer": "UMBRELLA","height": "low", "color": "green", "hint": "Keeps you dry"},
            {"clue": "WHAT A CLOCK DOES EVERY SECOND",     "answer": "TICK",    "height": "low", "color": "green", "hint": "The sound it makes"},
            {"clue": "WHAT YOU SEE AFTER RAIN IN THE SKY", "answer": "RAINBOW", "height": "low", "color": "green", "hint": "Seven colours"},
        ],
    },
    {
        "name": "Stage 8 — Mixed Signals",
        "unlocks": {"color": "yellow", "height": "mid"},
        "intro": "Yellow tiles mix it all up — anagrams, wordplay, and lateral thinking. No single rule applies.",
        "puzzles": [
            {"clue": "ANAGRAM OF 'LEMON'",  "answer": "MELON",  "height": "mid", "color": "yellow", "hint": "A green or yellow fruit"},
            {"clue": "ANAGRAM OF 'EARTH'",  "answer": "HEART",  "height": "mid", "color": "yellow", "hint": "Pumps blood"},
            {"clue": "ANAGRAM OF 'LISTEN'", "answer": "SILENT", "height": "mid", "color": "yellow", "hint": "Making no sound"},
            {"clue": "ANAGRAM OF 'DUSTY'",  "answer": "STUDY",  "height": "mid", "color": "yellow", "hint": "What students do"},
            {"clue": "ANAGRAM OF 'NIGHT'",  "answer": "THING",  "height": "mid", "color": "yellow", "hint": "An object or matter"},
            {"clue": "ANAGRAM OF 'SPARE'",  "answer": "REAPS",  "height": "mid", "color": "yellow", "hint": "Harvests crops"},
        ],
    },
    {
        "name": "Stage 9 — Flip the Sound",
        "unlocks": {"color": "black", "height": "high"},
        "intro": "Black + High: find a word that SOUNDS like an opposite or phonetic reversal. Toughest combination so far.",
        "puzzles": [
            {"clue": "KNOW",   "answer": "NO",     "height": "high", "color": "black", "hint": "The word of refusal — sounds like know"},
            {"clue": "PEACE",  "answer": "PIECE",  "height": "high", "color": "black", "hint": "A fragment — sounds identical"},
            {"clue": "WHOLE",  "answer": "HOLE",   "height": "high", "color": "black", "hint": "An empty space — sounds like whole"},
            {"clue": "MALE",   "answer": "MAIL",   "height": "high", "color": "black", "hint": "Letters delivered — sounds like male"},
            {"clue": "WEAK",   "answer": "WEEK",   "height": "high", "color": "black", "hint": "Seven days — sounds like weak"},
        ],
    },
    {
        "name": "Stage 10 — Echo & Reduce",
        "unlocks": {"color": "red", "height": "high"},
        "intro": "Red + High: find a SIMPLER word that sounds related. Strip away complexity phonetically.",
        "puzzles": [
            {"clue": "SCENT",   "answer": "SENT",  "height": "high", "color": "red", "hint": "Past tense of send — sounds the same"},
            {"clue": "KNOT",    "answer": "NOT",   "height": "high", "color": "red", "hint": "The negative — silent K"},
            {"clue": "WRAP",    "answer": "RAP",   "height": "high", "color": "red", "hint": "Silent W — a style of music"},
            {"clue": "THROUGH", "answer": "THREW", "height": "high", "color": "red", "hint": "Past tense of throw — near homophone"},
            {"clue": "KNIGHT",  "answer": "NITE",  "height": "high", "color": "red", "hint": "Informal spelling of night"},
        ],
    },
    {
        "name": "Stage 11 — Amplify the Sound",
        "unlocks": {"color": "blue", "height": "high"},
        "intro": "Blue + High: find a LARGER or more complex word that sounds like the clue phonetically.",
        "puzzles": [
            {"clue": "ATE",  "answer": "EIGHT", "height": "high", "color": "blue", "hint": "The number — sounds like ate"},
            {"clue": "AIR",  "answer": "HEIR",  "height": "high", "color": "blue", "hint": "One who inherits — sounds like air"},
            {"clue": "OR",   "answer": "OAR",   "height": "high", "color": "blue", "hint": "Used to row a boat — sounds like or"},
            {"clue": "EYE",  "answer": "AYE",   "height": "high", "color": "blue", "hint": "A vote of yes — sounds like eye"},
            {"clue": "SO",   "answer": "SOW",   "height": "high", "color": "blue", "hint": "To plant seeds — sounds like so"},
        ],
    },
    {
        "name": "Stage 12 — Master Level",
        "unlocks": {"color": "green", "height": "high"},
        "intro": "Green + High: the hardest combo — use both CONTEXT and SOUND together to find the answer.",
        "puzzles": [
            {"clue": "WHAT A BEE DOES — SOUNDS LIKE 'HYMN'",             "answer": "HUM",    "height": "high", "color": "green", "hint": "Buzzing sound"},
            {"clue": "WHAT THE SEA DOES TO SHORE — SOUNDS LIKE 'BEECH'", "answer": "REACH",  "height": "high", "color": "green", "hint": "To extend toward"},
            {"clue": "WHAT YOU CALL A PATH — SOUNDS LIKE 'ROAD'",        "answer": "RODE",   "height": "high", "color": "green", "hint": "Past tense of ride"},
            {"clue": "WHAT WIND DOES — RHYMES WITH 'FLOWS'",             "answer": "BLOWS",  "height": "high", "color": "green", "hint": "Air in motion"},
            {"clue": "WHAT THE SUN DOES — RHYMES WITH 'BITES'",          "answer": "LIGHTS", "height": "high", "color": "green", "hint": "Illuminates"},
        ],
    },
]

def build_ordered_puzzles():
    ordered = []
    for stage_idx, stage in enumerate(STAGES):
        for puzz_idx, p in enumerate(stage['puzzles']):
            ordered.append({
                **p,
                "stage_index": stage_idx,
                "stage_name": stage['name'],
                "is_first_in_stage": puzz_idx == 0,
                "unlocks": stage['unlocks'] if puzz_idx == 0 else None,
                "stage_intro": stage['intro'] if puzz_idx == 0 else None,
            })
    return ordered

ALL_PUZZLES = build_ordered_puzzles()
TOTAL_STAGES = len(STAGES)

# ─── ROUTES — PAGES ─────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sandbox')
def sandbox():
    return render_template('sandbox.html')

# ─── ROUTES — TUTORIAL API ──────────────────────────────────────────────────

@app.route('/api/new_game', methods=['POST'])
def new_game():
    session['current'] = 0
    session['score'] = 0
    session['results'] = []
    first = ALL_PUZZLES[0]
    return jsonify({
        "total": len(ALL_PUZZLES),
        "total_stages": TOTAL_STAGES,
        "puzzle": _safe_puzzle(first, 0),
        "score": 0,
        "stage_unlock": {
            "color": first['unlocks']['color'],
            "height": first['unlocks']['height'],
            "stage_name": first['stage_name'],
            "intro": first['stage_intro'],
        }
    })

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.get_json()
    answer = data.get('answer', '').strip().upper()
    current = session.get('current', 0)
    score = session.get('score', 0)
    if current >= len(ALL_PUZZLES):
        return jsonify({"error": "Game over"}), 400
    puzzle = ALL_PUZZLES[current]
    accepted = [puzzle['answer'].upper()] + [a.upper() for a in puzzle.get('alternates', [])]
    is_correct = answer in accepted
    correct_answer = puzzle['answer'].upper()
    points_earned = 0
    if is_correct:
        base = COLOR_POINTS.get(puzzle['color'], 100)
        bonus = HEIGHT_BONUS.get(puzzle['height'], 0)
        points_earned = base + bonus
        score += points_earned
    session['score'] = score
    session['results'] = session.get('results', []) + [{"c": int(is_correct), "p": points_earned}]
    result = {
        "correct": is_correct,
        "your_answer": answer,
        "correct_answer": correct_answer,
        "points_earned": points_earned,
        "score": score,
        "puzzle_index": current,
        "stage_index": puzzle['stage_index'],
    }
    next_index = current + 1
    session['current'] = next_index
    game_over = next_index >= len(ALL_PUZZLES)
    response = {**result, "game_over": game_over}
    if not game_over:
        next_p = ALL_PUZZLES[next_index]
        response["next_puzzle"] = _safe_puzzle(next_p, next_index)
        response["puzzle_number"] = next_index + 1
        response["total"] = len(ALL_PUZZLES)
        if next_p['is_first_in_stage']:
            response["stage_unlock"] = {
                "color": next_p['unlocks']['color'],
                "height": next_p['unlocks']['height'],
                "stage_name": next_p['stage_name'],
                "intro": next_p['stage_intro'],
            }
    return jsonify(response)

@app.route('/api/hint', methods=['POST'])
def get_hint():
    current = session.get('current', 0)
    if current < len(ALL_PUZZLES):
        return jsonify({"hint": ALL_PUZZLES[current].get('hint', 'No hint available.')})
    return jsonify({"hint": "No hint available."})

# ─── ROUTES — SANDBOX API ───────────────────────────────────────────────────

@app.route('/api/sandbox/combos', methods=['GET'])
def sandbox_combos():
    """Return all available combos and how many puzzles each has."""
    combos = {}
    for (color, height), puzzles in SANDBOX_BANK.items():
        combos[f"{color}_{height}"] = {
            "color": color,
            "height": height,
            "count": len(puzzles),
            "description": COMBO_DESCRIPTIONS.get((color, height), ""),
        }
    return jsonify(combos)

@app.route('/api/sandbox/puzzle', methods=['POST'])
def sandbox_puzzle():
    """Return a random puzzle for the requested color+height combo."""
    data = request.get_json()
    color = data.get('color', '').lower()
    height = data.get('height', '').lower()
    key = (color, height)
    pool = SANDBOX_BANK.get(key)
    if not pool:
        return jsonify({"error": f"No puzzles for {color}/{height}"}), 404
    puzzle = random.choice(pool)
    return jsonify({
        "clue": puzzle['clue'],
        "color": color,
        "height": height,
        "answer_length": len(puzzle['answer']),
        "points_possible": COLOR_POINTS.get(color, 100) + HEIGHT_BONUS.get(height, 0),
        "description": COMBO_DESCRIPTIONS.get(key, ""),
        "hint": puzzle.get('hint', ''),
        "_answer": puzzle['answer'],
        "_alternates": puzzle.get('alternates', []),
    })

@app.route('/api/sandbox/submit', methods=['POST'])
def sandbox_submit():
    """Check a sandbox answer."""
    data = request.get_json()
    answer = data.get('answer', '').strip().upper()
    correct_answer = data.get('correct_answer', '').upper()
    alternates = [a.upper() for a in data.get('alternates', [])]
    accepted = [correct_answer] + alternates
    is_correct = answer in accepted
    points_earned = 0
    if is_correct:
        color = data.get('color', 'white')
        height = data.get('height', 'mid')
        points_earned = COLOR_POINTS.get(color, 100) + HEIGHT_BONUS.get(height, 0)
    return jsonify({
        "correct": is_correct,
        "correct_answer": correct_answer,
        "points_earned": points_earned,
    })

def _safe_puzzle(puzzle, index):
    return {
        "index": index,
        "clue": puzzle['clue'],
        "height": puzzle['height'],
        "color": puzzle['color'],
        "answer_length": len(puzzle['answer']),
        "points_possible": COLOR_POINTS.get(puzzle['color'], 100) + HEIGHT_BONUS.get(puzzle['height'], 0),
        "stage_index": puzzle['stage_index'],
        "stage_name": puzzle['stage_name'],
    }

if __name__ == '__main__':
    app.run(debug=False)
