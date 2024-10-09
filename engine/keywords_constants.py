SHOT_SPECIFIER_MAP = {
    # Variations for "fadeaway"
    "fade": "Fadeaway", "fades": "Fadeaway", "fadeaway": "Fadeaway", "fadeaways": "Fadeaway",
    # Variations for "bank"
    "bank": "Bank", "banks": "Bank", "bankshot": "Bank",
    # Variations for "hook"
    "hook": "Hook", "hooks": "Hook",
    # Variations for "floater"
    "floater": "Floating", "floaters": "Floating", "floating": "Floating",
    # Variations for "layup"
    "layup": "Layup", "layups": "Layup", "putback": "Putback", "reverse": "Reverse Layup",
    # Variations for "finger roll"
    "finger": "Finger Roll", "roll": "Finger Roll",
    # Variations for "jump"
    "jumper": "Jump Shot", "jumpers": "Jump Shot", "jump": "Jump Shot",
    # Variations for "putback"
    "putback": "Putback", "putbacks": "Putback",
    # Variations for "step back"
    "step": "Step Back", "back": "Step Back",
    # Variations for "alley oop"
    "alley": "Alley Oop", "oop": "Alley Oop",
    # pullup
    "pullup": "Pullup", "pull-up": "Pullup", "pullups": "Pullup", "pull-ups": "Pullup", "pulls": "Pullup", "pull": "Pullup", "hang-pulls": "Pullup", "hang pulls": "Pullup", "hang-pull": "Pullup", "hang pull": "Pullup",
    # Variations for "tip"
    "tip": "Tip", "tips": "Tip",
    # Variations for "running"
    "running": "Running", "runner": "Running", "runners": "Running",
    # Variations for "turnaround"
    "turnaround": "Turnaround", "turnarounds": "Turnaround",
    # Variations for "dunk"
    "dunk": "Dunk", "dunks": "Dunk", "driving": "Driving", "drive": "Driving", "slams": "Dunk", "slam": "Dunk", "jam": "Dunk", "jams": "Dunk",
    # Variations for "cutting"
    "cutting": "Cutting", "cut": "Cutting",
    # Additional common variations
    "bank": "Bank", "hookshot": "Hook", "runner": "Running",
    # tip-in
    "tip-in": "Tip", "tip-ins": "Tip", "tip in": "Tip", "tip ins": "Tip",
    # 3-pointers
    "three": '3PT', "three-pointer": '3PT', "three-point": '3PT', "three-pointers": '3PT', "3-pointer": '3PT', "3-point": '3PT', "3-pointers": '3PT', "3pt": '3PT', "3pts": '3PT', "3-point shot": '3PT', "3-point shots": '3PT', "3pt shot": '3PT', "3pt shots": '3PT', "trey-ball": '3PT', 'three ball': '3PT', 'trey balls': '3PT', 'three balls': '3PT', 'trey-ball': '3PT', 'trey-balls': '3PT', 'three-ball': '3PT', 'three-balls': '3PT', 'treyball': '3PT', 'threeball': '3PT', 'treyballs': '3PT', 'threeballs': '3PT', 'treys': '3PT'
    # range finder
}

SCORE_SPECIFIER_MAP = {
    'game-tying': 'GT', 'game tying': 'GT', 'tying': 'GT', 
    'lead-taking': 'LT', 'lead taking': 'LT', 'lead-taker': 'LT', 'lead taker': 'LT', 'lead-takers': 'LT', 'lead takers': 'LT', 'go ahead': 'LT', 'go-ahead': 'LT', 'go-aheads': 'LT', 'go aheads': 'LT', 'go-ahead': 'LT',
}

CONTEXT_MEASURE_MAP = {
    "PTS": ["point", "score", "pts", "points", "scoring", "buckets", "bucket", "layups", "makes", "lays",
            "step back", "alley oop", "dunk", "fadeaway", "fadeaways", "jumper", "jump shot", "midrange", "middy", "layup", "layups", "dunks", "dunk", "flush", "flushes", "alley oops", "oops", "slams", "slam dunk", "slam dunks", "slam",  "jam", "jams"] + list(SHOT_SPECIFIER_MAP.keys()),
    "BLK": ["block", "swat", "blocks", "swats", "reject", "rejections", "rejection", "swatted"],
    "STL": ["steal", "steals", "thief", "thieves", "cookies", "cookie", "stolen"],
    "AST": ["assist", "apple", "dime", "assists", "passing", "apples"],
    "REB": ["board", "rebound", "rebounds", "boards", "grab"],
    "TOV": ["turnover", "giveaway", "turnovers", "lose", "losing possession", "lost possesion", "giveaways"],
    "MISS": ["brick", "bricks", "miss", "misses", "airball", "missed shot", "failed shot", "missed shots", "clank", "clanks"],
    "FGA": ["all shots", "shot attempts", "attempts", "shots", "field goal attempts", "fga", "fgas", "field goal attempt"],
}

MONTH_MAP = {
    "january": "04", "jan": "04",
    "february": "05", "feb": "05",
    "march": "06", "mar": "06",
    "april": "07", "apr": "07",
    "may": "08",
    "june": "09", "jun": "09",
    "july": "10", "jul": "10",
    "august": "11", "aug": "11",
    "september": "12", "sep": "12",
    "october": "01", "oct": "01",
    "november": "02", "nov": "02",
    "december": "03", "dec": "03"
}

CLUTCH_KEYWORDS = ["clutch", "last minute", "final minute", "end of the game", "last second", "final seconds", "last 10 seconds", "last-second", 'last seconds', 'last 5 seconds']
SEASON_KEYWORDS = ["playoffs", "postseason", "regular season", "preseason", "all-star", "all star", 'play-offs', 'play-off', 'post-season', ]

CLUTCH_TIME_MAP = {
    "clutch": "Last 5 Minutes",
    "last minute": "Last 1 Minute",
    "final minute": "Last 1 Minute",
    "end of the game": "Last 5 Minutes",
    "last second": "Last 10 Seconds",
    "final seconds": "Last 10 Seconds",
    "last 10 seconds": "Last 10 Seconds",
}