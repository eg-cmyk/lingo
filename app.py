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
        unlock = stage['unlocks']
        # Normalize: single-tile stages use 'color', multi use 'colors'
        normalized_unlock = {
            "colors": unlock.get('colors', [unlock['color']]),
            "height": unlock['height'],
        }
        for puzz_idx, p in enumerate(stage['puzzles']):
            ordered.append({
                **p,
                "colors": [p['color']],
                "is_multi": False,
                "stage_index": stage_idx,
                "stage_name": stage['name'],
                "is_first_in_stage": puzz_idx == 0,
                "unlocks": normalized_unlock if puzz_idx == 0 else None,
                "stage_intro": stage['intro'] if puzz_idx == 0 else None,
            })
    return ordered

ALL_PUZZLES = build_ordered_puzzles()  # will be extended after build_multi_puzzles is defined below
TOTAL_STAGES = 18  # 12 single-tile + 6 multi-tile stages

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
    unlock = first['unlocks']
    return jsonify({
        "total": len(ALL_PUZZLES),
        "total_stages": TOTAL_STAGES,
        "puzzle": _safe_puzzle(first, 0),
        "score": 0,
        "stage_unlock": {
            "colors": unlock.get('colors', [unlock.get('color', first['color'])]),
            "height": unlock.get('height', first['height']),
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
            unlock = next_p['unlocks']
            response["stage_unlock"] = {
                "colors": unlock.get('colors', [unlock.get('color', next_p['color'])]),
                "height": unlock.get('height', next_p['height']),
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

# ─── MULTI-TILE PUZZLE BANK ─────────────────────────────────────────────────
# Each puzzle has TWO colors + one height. Both rules must be applied together.
# color2 is the second tile. Points = both colors + height bonus.

MULTI_BANK = {
    # RED + BLACK = subtract to find the opposite
    ("red","black","mid"): [
        {"clue":"ANCIENT",    "answer":"MODERN",  "hint":"First find the opposite, then simplify it — contemporary works too", "alternates":["CONTEMPORARY","NEW","RECENT"]},
        {"clue":"ENORMOUS",   "answer":"TINY",    "hint":"Subtract the scale AND flip it", "alternates":["SMALL","LITTLE","MINI"]},
        {"clue":"BLAZING",    "answer":"COOL",    "hint":"Less intense AND the opposite temperature", "alternates":["COLD","CHILLY"]},
        {"clue":"VICTORY",    "answer":"LOSS",    "hint":"Reduce the outcome AND flip it", "alternates":["DEFEAT","FAIL"]},
        {"clue":"THUNDERSTORM","answer":"CALM",   "hint":"Reduce the weather AND find its opposite", "alternates":["STILL","QUIET","PEACE"]},
    ],
    # BLUE + BLACK = amplify to find the opposite
    ("blue","black","mid"): [
        {"clue":"WARM",       "answer":"FREEZING","hint":"Amplify AND flip the temperature", "alternates":["FROZEN","ICY","FRIGID"]},
        {"clue":"DISLIKE",    "answer":"ADORE",   "hint":"Find the opposite AND intensify it", "alternates":["LOVE","WORSHIP"]},
        {"clue":"WHISPER",    "answer":"ROAR",    "hint":"Amplify AND flip the sound", "alternates":["SCREAM","SHOUT","BELLOW"]},
        {"clue":"DRIZZLE",    "answer":"BLIZZARD","hint":"Add intensity AND flip the warmth"},
        {"clue":"JOY",        "answer":"AGONY",   "hint":"Amplify AND reverse the emotion", "alternates":["MISERY","DESPAIR","GRIEF"]},
    ],
    # RED + BROWN = subtract to find what came before
    ("red","brown","mid"): [
        {"clue":"SUMMER",     "answer":"SPRING",  "hint":"Go back one season AND reduce the warmth"},
        {"clue":"ADULTHOOD",  "answer":"BIRTH",   "hint":"Go back to the very beginning", "alternates":["INFANCY","BABY"]},
        {"clue":"MILLENNIUM", "answer":"DECADE",  "hint":"Go back in time AND reduce the scale"},
        {"clue":"EVENING",    "answer":"DAWN",    "hint":"Earlier in the day AND a simpler word", "alternates":["MORNING","SUNRISE"]},
        {"clue":"RIVER",      "answer":"SPRING",  "hint":"Reduce the water AND go to its source", "alternates":["SOURCE","CREEK"]},
    ],
    # BLUE + BROWN = amplify AND move forward in time
    ("blue","brown","mid"): [
        {"clue":"MORNING",    "answer":"TOMORROW","hint":"Later in time AND expand beyond today"},
        {"clue":"SEED",       "answer":"FOREST",  "hint":"Grow it AND let time pass", "alternates":["TREE","WOODLAND"]},
        {"clue":"CHILD",      "answer":"ELDER",   "hint":"Age forward AND amplify", "alternates":["ADULT","SENIOR","OLD"]},
        {"clue":"SPARK",      "answer":"INFERNO", "hint":"Let time and fuel amplify the fire", "alternates":["FIRE","BLAZE"]},
        {"clue":"CREEK",      "answer":"OCEAN",   "hint":"Amplify the water AND let it flow over time"},
    ],
    # RED + YELLOW = subtract with a twist / anagram of a lesser form
    ("red","yellow","mid"): [
        {"clue":"ANAGRAM OF 'SPARE' → LESSER FORM", "answer":"REAP",   "hint":"Unscramble then reduce — harvesting less", "alternates":["REAPS"]},
        {"clue":"ANAGRAM OF 'NIGHT' → SIMPLER",     "answer":"THIN",   "hint":"Rearrange, then strip it down", "alternates":["HINT"]},
        {"clue":"ANAGRAM OF 'EARTH' → LESSER ORGAN","answer":"EAR",    "hint":"Unscramble heart, then find a smaller part"},
        {"clue":"ANAGRAM OF 'STARE' → LESS WATER",  "answer":"TEAR",   "hint":"Rearrange tears, then reduce to one drop", "alternates":["TEARS"]},
        {"clue":"ANAGRAM OF 'BELOW' → SIMPLER JOINT","answer":"ELBOW", "hint":"Unscramble, then it's already the answer"},
    ],
    # BLUE + YELLOW = amplify with a twist / anagram of a greater form
    ("blue","yellow","mid"): [
        {"clue":"ANAGRAM OF 'LEMON' → BIGGER FRUIT", "answer":"MELON",  "hint":"Rearrange to find the larger fruit"},
        {"clue":"ANAGRAM OF 'EARTH' → BIGGER ORGAN", "answer":"HEART",  "hint":"Rearrange to the organ that powers everything"},
        {"clue":"ANAGRAM OF 'DUSTY' → BIGGER EFFORT","answer":"STUDY",  "hint":"Rearrange to a greater mental exercise"},
        {"clue":"ANAGRAM OF 'LISTEN' → AMPLIFIED",   "answer":"ENLIST", "hint":"Rearrange listen — a bigger commitment", "alternates":["SILENT","TINSEL"]},
        {"clue":"ANAGRAM OF 'BELOW' → AMPLIFIED",    "answer":"ELBOW",  "hint":"Rearrange to the joint that lets you reach further"},
    ],
    # BLACK + BROWN = opposite + time shift
    ("black","brown","mid"): [
        {"clue":"WINTER",     "answer":"AUTUMN",  "hint":"Go back one season AND find its warmer opposite", "alternates":["FALL"]},
        {"clue":"ENEMY",      "answer":"ALLY",    "hint":"Flip it AND think of who stood with you in the past", "alternates":["FRIEND","COMPANION"]},
        {"clue":"END",        "answer":"GENESIS", "hint":"The opposite of the end, at the beginning of time", "alternates":["BEGINNING","START","ORIGIN"]},
        {"clue":"DUSK",       "answer":"DAWN",    "hint":"The opposite moment — when it all begins"},
        {"clue":"FUTURE",     "answer":"PAST",    "hint":"Flip the direction of time"},
    ],
    # RED + GREEN = subtract using context clues
    ("red","green","low"): [
        {"clue":"WHAT A FOREST BECOMES WHEN STRIPPED", "answer":"STUMP",  "hint":"Remove the trees — what's left?", "alternates":["LOG","WOOD"]},
        {"clue":"WHAT AN OCEAN BECOMES WITHOUT WATER",  "answer":"DESERT", "hint":"Remove the water — what remains?", "alternates":["SAND","BASIN"]},
        {"clue":"WHAT A FIRE BECOMES WITHOUT FUEL",     "answer":"ASH",    "hint":"Subtract the flame", "alternates":["EMBER","SMOKE"]},
        {"clue":"WHAT A STORM BECOMES AT ITS END",      "answer":"CALM",   "hint":"After the weather passes", "alternates":["STILL","PEACE","QUIET"]},
        {"clue":"WHAT A RIVER BECOMES IN DROUGHT",      "answer":"BED",    "hint":"The channel without water", "alternates":["DITCH","CHANNEL"]},
    ],
    # BLUE + GREEN = amplify using context
    ("blue","green","low"): [
        {"clue":"WHAT A SPARK BECOMES IN A DRY FOREST",  "answer":"WILDFIRE","hint":"Context amplifies the danger", "alternates":["INFERNO","BLAZE"]},
        {"clue":"WHAT A PUDDLE BECOMES AFTER A FLOOD",   "answer":"LAKE",    "hint":"Amplify the water in context", "alternates":["POND","RIVER"]},
        {"clue":"WHAT A WHISPER BECOMES IN AN EMPTY HALL","answer":"ECHO",   "hint":"The space amplifies the sound"},
        {"clue":"WHAT A SEED BECOMES IN RICH SOIL",      "answer":"TREE",    "hint":"Growth amplified by context", "alternates":["PLANT","FOREST"]},
        {"clue":"WHAT A CRACK BECOMES IN AN EARTHQUAKE", "answer":"CHASM",   "hint":"Amplified by seismic force", "alternates":["CANYON","FAULT","RIFT"]},
    ],
    # BLACK + YELLOW = opposite + wordplay
    ("black","yellow","mid"): [
        {"clue":"ANAGRAM OF 'NIGHT' → ITS OPPOSITE",    "answer":"DAY",    "hint":"Unscramble THING, then find the opposite of dark"},
        {"clue":"ANAGRAM OF 'EARTH' → ITS OPPOSITE",    "answer":"SKY",    "hint":"Unscramble HEART, then look up", "alternates":["SPACE","HEAVEN"]},
        {"clue":"ANAGRAM OF 'BELOW' → ITS OPPOSITE",    "answer":"ABOVE",  "hint":"Unscramble ELBOW — then flip the direction"},
        {"clue":"ANAGRAM OF 'STARE' → EMOTION OPPOSITE","answer":"CALM",   "hint":"Unscramble TEARS — then find its opposite", "alternates":["PEACE","JOY"]},
        {"clue":"ANAGRAM OF 'SPARE' → OPPOSITE OF SAVE","answer":"SPEND",  "hint":"Unscramble REAPS — then flip the economy", "alternates":["WASTE","LOSE"]},
    ],
    # RED + BLACK + HIGH = phonetic subtraction of an opposite
    ("red","black","high"): [
        {"clue":"SOUNDS LIKE THE OPPOSITE OF 'NIGHT' BUT SMALLER", "answer":"DAY",   "hint":"The opposite of darkness — one syllable"},
        {"clue":"SOUNDS LIKE THE OPPOSITE OF 'WAR' — SHORTER",     "answer":"PEACE", "hint":"Sounds like 'piece' — the simpler form of harmony"},
        {"clue":"SOUNDS LIKE THE OPPOSITE OF 'LOVE' — ONE SOUND",  "answer":"HATE",  "hint":"Four letters, rhymes with 'late'"},
        {"clue":"SOUNDS LIKE A LESSER FORM OF 'ANCIENT'",          "answer":"OLD",   "hint":"Simpler word for the opposite of new"},
        {"clue":"SOUNDS LIKE THE OPPOSITE OF 'FULL' — SHORT",      "answer":"EMPTY", "hint":"Two syllables, sounds like 'em-tee'"},
    ],
    # BLUE + BROWN + HIGH = phonetic amplification over time
    ("blue","brown","high"): [
        {"clue":"SOUNDS LIKE WHAT A BOY BECOMES — AMPLIFIED",        "answer":"MAN",      "hint":"Grow up — sounds simple but means everything", "alternates":["ADULT"]},
        {"clue":"SOUNDS LIKE WHAT 'NOW' BECOMES — SOUNDS LIKE 'FUTURE'","answer":"LATER",  "hint":"Time moves forward — sounds like 'lay-ter'"},
        {"clue":"SOUNDS LIKE WHAT AN 'EMBER' GROWS INTO OVER TIME",  "answer":"INFERNO",  "hint":"Fire amplified — sounds like 'in-FER-no'", "alternates":["BLAZE","FIRE"]},
        {"clue":"SOUNDS LIKE WHAT 'ATE' BECOMES WHEN TIME PASSES",   "answer":"EIGHT",    "hint":"The number that sounds like the past tense of eat"},
        {"clue":"SOUNDS LIKE A GROWN VERSION OF 'CREEK'",            "answer":"RIVER",    "hint":"Larger waterway — sounds like 'RIV-er'"},
    ],
}

# Descriptions for multi-tile combos
MULTI_DESCRIPTIONS = {
    ("red","black","mid"):   "Subtract AND reverse — find a lesser opposite",
    ("blue","black","mid"):  "Amplify AND reverse — find a greater opposite",
    ("red","brown","mid"):   "Subtract AND go back in time",
    ("blue","brown","mid"):  "Amplify AND move forward in time",
    ("red","yellow","mid"):  "Subtract AND unscramble — anagram of a lesser form",
    ("blue","yellow","mid"): "Amplify AND unscramble — anagram of a greater form",
    ("black","brown","mid"): "Reverse AND shift through time",
    ("red","green","low"):   "Subtract using context clues",
    ("blue","green","low"):  "Amplify using context clues",
    ("black","yellow","mid"):"Reverse AND apply wordplay",
    ("red","black","high"):  "Phonetic subtraction of an opposite",
    ("blue","brown","high"): "Phonetic amplification over time",
}

# Tutorial multi-tile stages (13-18)
MULTI_STAGES = [
    {
        "name": "Stage 13 — Subtract the Opposite",
        "unlocks": {"colors": ["red","black"], "height": "mid"},
        "intro": "🔴⬛ Red + Black: first find the OPPOSITE, then reduce it to a simpler or lesser form. Two rules, one answer.",
        "puzzles": [
            {"clue":"ANCIENT",     "answer":"MODERN",   "alternates":["CONTEMPORARY","NEW","RECENT"], "colors":["red","black"], "height":"mid","hint":"Opposite in time, then simplify"},
            {"clue":"ENORMOUS",    "answer":"TINY",     "alternates":["SMALL","LITTLE"],              "colors":["red","black"], "height":"mid","hint":"Subtract the scale AND flip it"},
            {"clue":"BLAZING",     "answer":"COOL",     "alternates":["COLD","CHILLY"],               "colors":["red","black"], "height":"mid","hint":"Less intense AND the opposite temperature"},
            {"clue":"VICTORY",     "answer":"LOSS",     "alternates":["DEFEAT","FAIL"],               "colors":["red","black"], "height":"mid","hint":"Reduce the outcome AND flip it"},
            {"clue":"THUNDERSTORM","answer":"CALM",     "alternates":["STILL","QUIET","PEACE"],       "colors":["red","black"], "height":"mid","hint":"Reduce the weather AND find its opposite"},
        ],
    },
    {
        "name": "Stage 14 — Amplify the Opposite",
        "unlocks": {"colors": ["blue","black"], "height": "mid"},
        "intro": "🔵⬛ Blue + Black: find the OPPOSITE and then INTENSIFY it. Push it further in the other direction.",
        "puzzles": [
            {"clue":"WARM",    "answer":"FREEZING","alternates":["FROZEN","ICY","FRIGID"],     "colors":["blue","black"],"height":"mid","hint":"Amplify AND flip the temperature"},
            {"clue":"DISLIKE", "answer":"ADORE",   "alternates":["LOVE","WORSHIP"],            "colors":["blue","black"],"height":"mid","hint":"Find the opposite AND intensify it"},
            {"clue":"WHISPER", "answer":"ROAR",    "alternates":["SCREAM","SHOUT","BELLOW"],   "colors":["blue","black"],"height":"mid","hint":"Amplify AND flip the sound"},
            {"clue":"DRIZZLE", "answer":"BLIZZARD","alternates":[],                            "colors":["blue","black"],"height":"mid","hint":"Add intensity AND flip the warmth"},
            {"clue":"JOY",     "answer":"AGONY",   "alternates":["MISERY","DESPAIR","GRIEF"],  "colors":["blue","black"],"height":"mid","hint":"Amplify AND reverse the emotion"},
        ],
    },
    {
        "name": "Stage 15 — Turn Back Time",
        "unlocks": {"colors": ["red","brown"], "height": "mid"},
        "intro": "🔴🟫 Red + Brown: go BACKWARDS in time and find a simpler or earlier form. Subtract through the timeline.",
        "puzzles": [
            {"clue":"SUMMER",     "answer":"SPRING",  "alternates":[],                    "colors":["red","brown"],"height":"mid","hint":"Go back one season AND reduce the warmth"},
            {"clue":"ADULTHOOD",  "answer":"BIRTH",   "alternates":["INFANCY","BABY"],     "colors":["red","brown"],"height":"mid","hint":"Go back to the very beginning"},
            {"clue":"MILLENNIUM", "answer":"DECADE",  "alternates":[],                    "colors":["red","brown"],"height":"mid","hint":"Go back in time AND reduce the scale"},
            {"clue":"EVENING",    "answer":"DAWN",    "alternates":["MORNING","SUNRISE"],  "colors":["red","brown"],"height":"mid","hint":"Earlier in the day AND a simpler word"},
            {"clue":"RIVER",      "answer":"SPRING",  "alternates":["SOURCE","CREEK"],     "colors":["red","brown"],"height":"mid","hint":"Reduce the water AND go to its source"},
        ],
    },
    {
        "name": "Stage 16 — Future Amplified",
        "unlocks": {"colors": ["blue","brown"], "height": "mid"},
        "intro": "🔵🟫 Blue + Brown: move FORWARD in time AND amplify. What does this become when it grows and time passes?",
        "puzzles": [
            {"clue":"MORNING",  "answer":"TOMORROW","alternates":[],                       "colors":["blue","brown"],"height":"mid","hint":"Later in time AND expand beyond today"},
            {"clue":"SEED",     "answer":"FOREST",  "alternates":["TREE","WOODLAND"],      "colors":["blue","brown"],"height":"mid","hint":"Grow it AND let time pass"},
            {"clue":"CHILD",    "answer":"ELDER",   "alternates":["ADULT","SENIOR","OLD"], "colors":["blue","brown"],"height":"mid","hint":"Age forward AND amplify"},
            {"clue":"SPARK",    "answer":"INFERNO", "alternates":["FIRE","BLAZE"],         "colors":["blue","brown"],"height":"mid","hint":"Let time and fuel amplify the fire"},
            {"clue":"CREEK",    "answer":"OCEAN",   "alternates":[],                       "colors":["blue","brown"],"height":"mid","hint":"Amplify the water AND let it flow over time"},
        ],
    },
    {
        "name": "Stage 17 — Context Subtracted",
        "unlocks": {"colors": ["red","green"], "height": "low"},
        "intro": "🔴🟢 Red + Green: use CONTEXT to understand the clue, then SUBTRACT — find what remains when something is taken away.",
        "puzzles": [
            {"clue":"WHAT A FOREST BECOMES WHEN STRIPPED",  "answer":"STUMP",  "alternates":["LOG","WOOD"],         "colors":["red","green"],"height":"low","hint":"Remove the trees — what's left?"},
            {"clue":"WHAT AN OCEAN BECOMES WITHOUT WATER",  "answer":"DESERT", "alternates":["SAND","BASIN"],       "colors":["red","green"],"height":"low","hint":"Remove the water — what remains?"},
            {"clue":"WHAT A FIRE BECOMES WITHOUT FUEL",     "answer":"ASH",    "alternates":["EMBER","SMOKE"],      "colors":["red","green"],"height":"low","hint":"Subtract the flame"},
            {"clue":"WHAT A STORM BECOMES AT ITS END",      "answer":"CALM",   "alternates":["STILL","PEACE"],      "colors":["red","green"],"height":"low","hint":"After the weather passes"},
            {"clue":"WHAT A RIVER BECOMES IN DROUGHT",      "answer":"BED",    "alternates":["DITCH","CHANNEL"],    "colors":["red","green"],"height":"low","hint":"The channel without water"},
        ],
    },
    {
        "name": "Stage 18 — Context Amplified",
        "unlocks": {"colors": ["blue","green"], "height": "low"},
        "intro": "🔵🟢 Blue + Green: use CONTEXT to understand the situation, then AMPLIFY — what does this become when it grows?",
        "puzzles": [
            {"clue":"WHAT A SPARK BECOMES IN A DRY FOREST",   "answer":"WILDFIRE","alternates":["INFERNO","BLAZE"],   "colors":["blue","green"],"height":"low","hint":"Context amplifies the danger"},
            {"clue":"WHAT A PUDDLE BECOMES AFTER A FLOOD",    "answer":"LAKE",    "alternates":["POND","RIVER"],       "colors":["blue","green"],"height":"low","hint":"Amplify the water in context"},
            {"clue":"WHAT A WHISPER BECOMES IN AN EMPTY HALL","answer":"ECHO",    "alternates":[],                    "colors":["blue","green"],"height":"low","hint":"The space amplifies the sound"},
            {"clue":"WHAT A SEED BECOMES IN RICH SOIL",       "answer":"TREE",    "alternates":["PLANT","FOREST"],    "colors":["blue","green"],"height":"low","hint":"Growth amplified by context"},
            {"clue":"WHAT A CRACK BECOMES IN AN EARTHQUAKE",  "answer":"CHASM",   "alternates":["CANYON","FAULT"],    "colors":["blue","green"],"height":"low","hint":"Amplified by seismic force"},
        ],
    },
]

def build_multi_puzzles():
    ordered = []
    base_stage = len(STAGES)
    for stage_idx, stage in enumerate(MULTI_STAGES):
        unlock = stage['unlocks']
        normalized_unlock = {
            "colors": unlock.get('colors', [unlock.get('color', 'red')]),
            "height": unlock['height'],
        }
        for puzz_idx, p in enumerate(stage['puzzles']):
            ordered.append({
                **p,
                "color": p['colors'][0],
                "stage_index": base_stage + stage_idx,
                "stage_name": stage['name'],
                "is_first_in_stage": puzz_idx == 0,
                "unlocks": normalized_unlock if puzz_idx == 0 else None,
                "stage_intro": stage['intro'] if puzz_idx == 0 else None,
                "is_multi": True,
            })
    return ordered

ALL_MULTI_PUZZLES = build_multi_puzzles()
ALL_PUZZLES = ALL_PUZZLES + ALL_MULTI_PUZZLES
TOTAL_MULTI_STAGES = len(MULTI_STAGES)

def _safe_puzzle(puzzle, index):
    is_multi = puzzle.get('is_multi', False)
    colors = puzzle.get('colors', [puzzle['color']])
    if is_multi:
        pts = sum(COLOR_POINTS.get(c, 100) for c in colors) + HEIGHT_BONUS.get(puzzle['height'], 0)
    else:
        pts = COLOR_POINTS.get(puzzle['color'], 100) + HEIGHT_BONUS.get(puzzle['height'], 0)
    return {
        "index": index,
        "clue": puzzle['clue'],
        "height": puzzle['height'],
        "color": puzzle['color'],
        "colors": colors,
        "is_multi": is_multi,
        "answer_length": len(puzzle['answer']),
        "points_possible": pts,
        "stage_index": puzzle['stage_index'],
        "stage_name": puzzle['stage_name'],
    }

# ─── MULTI-TILE TUTORIAL ROUTES ─────────────────────────────────────────────

@app.route('/api/new_multi_game', methods=['POST'])
def new_multi_game():
    session['multi_current'] = 0
    session['multi_score'] = 0
    session['multi_results'] = []
    first = ALL_MULTI_PUZZLES[0]
    return jsonify({
        "total": len(ALL_MULTI_PUZZLES),
        "total_stages": TOTAL_MULTI_STAGES,
        "puzzle": _safe_puzzle(first, 0),
        "score": 0,
        "stage_unlock": {
            "colors": first['unlocks']['colors'],
            "height": first['unlocks']['height'],
            "stage_name": first['stage_name'],
            "intro": first['stage_intro'],
        }
    })

@app.route('/api/submit_multi', methods=['POST'])
def submit_multi():
    data = request.get_json()
    answer = data.get('answer', '').strip().upper()
    current = session.get('multi_current', 0)
    score = session.get('multi_score', 0)
    if current >= len(ALL_MULTI_PUZZLES):
        return jsonify({"error": "Game over"}), 400
    puzzle = ALL_MULTI_PUZZLES[current]
    accepted = [puzzle['answer'].upper()] + [a.upper() for a in puzzle.get('alternates', [])]
    is_correct = answer in accepted
    correct_answer = puzzle['answer'].upper()
    points_earned = 0
    if is_correct:
        points_earned = sum(COLOR_POINTS.get(c, 100) for c in puzzle.get('colors', [puzzle['color']])) + HEIGHT_BONUS.get(puzzle['height'], 0)
        score += points_earned
    session['multi_score'] = score
    session['multi_results'] = session.get('multi_results', []) + [{"c": int(is_correct), "p": points_earned}]
    result = {
        "correct": is_correct,
        "your_answer": answer,
        "correct_answer": correct_answer,
        "points_earned": points_earned,
        "score": score,
        "puzzle_index": current,
    }
    next_index = current + 1
    session['multi_current'] = next_index
    game_over = next_index >= len(ALL_MULTI_PUZZLES)
    response = {**result, "game_over": game_over}
    if not game_over:
        next_p = ALL_MULTI_PUZZLES[next_index]
        response["next_puzzle"] = _safe_puzzle(next_p, next_index)
        response["puzzle_number"] = next_index + 1
        response["total"] = len(ALL_MULTI_PUZZLES)
        if next_p['is_first_in_stage']:
            response["stage_unlock"] = {
                "colors": next_p['unlocks']['colors'],
                "height": next_p['unlocks']['height'],
                "stage_name": next_p['stage_name'],
                "intro": next_p['stage_intro'],
            }
    return jsonify(response)

@app.route('/api/hint_multi', methods=['POST'])
def get_hint_multi():
    current = session.get('multi_current', 0)
    if current < len(ALL_MULTI_PUZZLES):
        return jsonify({"hint": ALL_MULTI_PUZZLES[current].get('hint', 'No hint available.')})
    return jsonify({"hint": "No hint available."})

# ─── MULTI-TILE SANDBOX ROUTES ───────────────────────────────────────────────

@app.route('/api/sandbox/multi_combos', methods=['GET'])
def sandbox_multi_combos():
    combos = {}
    for (c1, c2, h), puzzles in MULTI_BANK.items():
        key = f"{c1}_{c2}_{h}"
        combos[key] = {
            "color1": c1, "color2": c2, "height": h,
            "count": len(puzzles),
            "description": MULTI_DESCRIPTIONS.get((c1, c2, h), ""),
        }
    return jsonify(combos)

@app.route('/api/sandbox/multi_puzzle', methods=['POST'])
def sandbox_multi_puzzle():
    data = request.get_json()
    c1 = data.get('color1','').lower()
    c2 = data.get('color2','').lower()
    h  = data.get('height','').lower()
    key = (c1, c2, h)
    pool = MULTI_BANK.get(key)
    if not pool:
        return jsonify({"error": f"No puzzles for {c1}/{c2}/{h}"}), 404
    puzzle = random.choice(pool)
    points = COLOR_POINTS.get(c1,100) + COLOR_POINTS.get(c2,100) + HEIGHT_BONUS.get(h,0)
    return jsonify({
        "clue": puzzle['clue'],
        "color1": c1, "color2": c2, "height": h,
        "answer_length": len(puzzle['answer']),
        "points_possible": points,
        "description": MULTI_DESCRIPTIONS.get(key, ""),
        "hint": puzzle.get('hint',''),
        "_answer": puzzle['answer'],
        "_alternates": puzzle.get('alternates', []),
    })

@app.route('/api/sandbox/multi_submit', methods=['POST'])
def sandbox_multi_submit():
    data = request.get_json()
    answer = data.get('answer','').strip().upper()
    correct_answer = data.get('correct_answer','').upper()
    alternates = [a.upper() for a in data.get('alternates',[])]
    is_correct = answer in ([correct_answer] + alternates)
    points_earned = 0
    if is_correct:
        c1 = data.get('color1','white')
        c2 = data.get('color2','black')
        h  = data.get('height','mid')
        points_earned = COLOR_POINTS.get(c1,100) + COLOR_POINTS.get(c2,100) + HEIGHT_BONUS.get(h,0)
    return jsonify({"correct": is_correct, "correct_answer": correct_answer, "points_earned": points_earned})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
