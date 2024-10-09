import re
import spacy
from engine.keywords_constants import SHOT_SPECIFIER_MAP, SCORE_SPECIFIER_MAP
from rapidfuzz import process, fuzz


class EntityExtractor:
    def __init__(self, nlp, team_matcher, player_matcher, active_players, first_name_to_full_names, last_name_to_full_names):
        self.nlp = nlp
        self.team_matcher = team_matcher
        self.player_matcher = player_matcher
        self.active_players = active_players
        self.first_name_to_full_names = first_name_to_full_names
        self.last_name_to_full_names = last_name_to_full_names

        # Context Measure mapping dictionary
        self.context_measure_map = {
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
        # Month mapping for user queries
        self.month_map = {
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
        
    def reformulate_query(self, user_query):
        """
        Reformulates the user query by matching it to the nearest player names, context keywords, or month names.
        
        Parameters:
        - user_query: The original user input string.
        
        Returns:
        - A reformulated query string with corrected player names and keywords.
        """
        # Step 1: Separate the keyword categories
        player_names = list(self.active_players.keys())
        context_keywords = [word for measure in self.context_measure_map for word in self.context_measure_map[measure]]
        month_keywords = list(self.month_map.keys())
        specifier_keywords = list(SHOT_SPECIFIER_MAP.keys())
        score_keywords = list(SCORE_SPECIFIER_MAP.keys())
        clutch_keywords = ["clutch", "last minute", "final minute", "end of the game", "last second", "final seconds", "last 10 seconds", "last-second"]
        season_keywords = ["playoffs", "postseason", "regular season", "preseason", "all-star", "all star", 'play-offs', 'play-off', 'post-season', ]
        non_player_keywords = context_keywords + month_keywords + specifier_keywords + clutch_keywords + season_keywords + score_keywords

        # Step 2: Perform fuzzy matching on the entire query using player names
        matched_fragment, score, _ = process.extractOne(user_query.lower(), [p.lower() for p in player_names], scorer=fuzz.partial_ratio)

        # Step 3: Remove the matched fragment (typo version) from the query if the score is high enough
        if score > 70:
            matched_player_name = player_names[[p.lower() for p in player_names].index(matched_fragment)]
            remaining_query = self.remove_fragment(user_query, matched_player_name)
        else:
            matched_player_name = None
            remaining_query = user_query

        # Step 4: Apply word-level fuzzy matching on the remaining query
        reformulated_words = []
        query_words = remaining_query.split()
        for word in query_words:
            # Perform word-level matching using non-player keywords
            match, score, _ = process.extractOne(word.lower(), [kw.lower() for kw in non_player_keywords], scorer=fuzz.ratio)

            # Replace the word if a close match is found in context or month keywords
            if score > 85:
                matched_keyword = non_player_keywords[[kw.lower() for kw in non_player_keywords].index(match)]
                reformulated_words.append(matched_keyword)
            else:
                reformulated_words.append(word)

        # Step 5: Reconstruct the query with the correctly matched player name
        if matched_player_name:
            reformulated_query = f"{matched_player_name} " + " ".join(reformulated_words)
        else:
            reformulated_query = " ".join(reformulated_words)
        return reformulated_query

    def remove_fragment(self, query, fragment):
        """
        Removes a fragment from the query, allowing for misspellings and partial matches.
        
        Parameters:
        - query: The original user query.
        - fragment: The correctly spelled fragment to be removed.
        
        Returns:
        - The query string with the fragment removed.
        """
        query_words = query.lower().split()
        fragment_words = fragment.lower().split()
        
        # Find the best matching sequence in the query
        best_start = 0
        best_length = 0
        best_score = 0
        
        for i in range(len(query_words)):
            for j in range(i + 1, min(len(query_words) + 1, i + len(fragment_words) + 2)):  # Allow for +1 word
                sequence = ' '.join(query_words[i:j])
                score = fuzz.ratio(sequence, fragment.lower())
                if score > best_score:
                    best_score = score
                    best_start = i
                    best_length = j - i
        
        # Remove the best matching sequence if the score is high enough
        if best_score > 70:  # Adjust this threshold as needed
            del query_words[best_start:best_start + best_length]
        
        return ' '.join(query_words)
        
        
    def extract_entities(self, query):
        from engine.utils import preprocess_query  # Import here to avoid circular dependency
        cleaned_query = preprocess_query(query)
        cleaned_query = self.reformulate_query(cleaned_query)
        doc = self.nlp(cleaned_query)

        player_name = self._extract_player_name(doc)
        team_name = self._extract_team_name(doc)
        season_type = self._extract_season_type(cleaned_query)
        context_measures, shot_specifiers = self.get_context_measures(cleaned_query)
        score_specifers = self._extract_score_specifiers(cleaned_query)
        month = self._extract_month(cleaned_query)
        clutch_time = self._extract_clutch_time(cleaned_query)

        return player_name, team_name, season_type, context_measures, month, clutch_time, shot_specifiers, score_specifers

    def get_context_measures(self, user_input):
        """
        Determine all relevant Context_Measures and specific shot specifiers based on the keywords in the user input.
        
        :param user_input: String input from the user.
        :return: A tuple (list of context measures, list of specific play type keywords).
        """
        doc = self.nlp(user_input.lower())
        raw_split = user_input.lower().split()
        found_measures = set()
        shot_specifiers = []

        # Convert the user input to a set of canonical shot specifiers
        canonical_specifiers = set()
        canonical_score_specifiers = []

        # Check for individual keywords against context measure map and shot specifier map
        for token in doc:

            normalized_text =token.text
            
            # Check if the token matches a context measure keyword
            for measure, keywords in self.context_measure_map.items():
                if normalized_text in keywords:
                    found_measures.add(measure)
                    if measure == "PTS" and normalized_text not in shot_specifiers:
                        shot_specifiers.append(normalized_text)
            
            # Check if the token matches a shot specifier and capture its canonical form
            if normalized_text in SHOT_SPECIFIER_MAP:
                canonical_form = SHOT_SPECIFIER_MAP[normalized_text]
                if canonical_form not in canonical_specifiers:
                    canonical_specifiers.add(canonical_form)
        
        # If no context measures are found, default to PTS
        if not found_measures:
            found_measures.add("PTS")

        # Add the canonical shot specifiers to the shot_specifiers list
        shot_specifiers = canonical_specifiers
        return list(found_measures), shot_specifiers, 

    def _extract_score_specifiers(self, query):
        score_specifiers = []
        for spec in SCORE_SPECIFIER_MAP:
            if re.search(rf"\b{re.escape(spec)}\b", query):
                score_specifiers.append(SCORE_SPECIFIER_MAP[spec])
        if not score_specifiers:
            return None
        
        return score_specifiers[0]
    
    def _extract_clutch_time(self, query):
        clutch_time_map = {
            "clutch": "Last 5 Minutes",
            "last minute": "Last 1 Minute",
            "final minute": "Last 1 Minute",
            "end of the game": "Last 5 Minutes",
            "last second": "Last 10 Seconds",
            "final seconds": "Last 10 Seconds",
            "last 10 seconds": "Last 10 Seconds",
        }
        
        # Define priority order (from most specific to least specific)
        priority_order = ["Last 10 Seconds", "Last 1 Minute", "Last 5 Minutes"]
        
        lower_query = query.lower()
        matches = []
        
        for phrase, clutch_value in clutch_time_map.items():
            if re.search(rf"\b{re.escape(phrase)}\b", lower_query):
                matches.append(clutch_value)
        
        if not matches:
            return None
        
        # Sort matches based on priority
        sorted_matches = sorted(set(matches), key=lambda x: priority_order.index(x))
        
        # Return the highest priority match
        return sorted_matches[0]
    
    def _extract_player_name(self, doc):
        player_matches = self.player_matcher(doc)
        if player_matches:
            match_id, start, end = player_matches[0]
            matched_text = doc[start:end].text.lower()

            if matched_text in self.active_players:
                return matched_text
            
        # If no full name match, try to match first and last names
        tokens = [token.text.lower() for token in doc]
        for i, token in enumerate(tokens):
            if token in self.first_name_to_full_names:
                if i + 1 < len(tokens) and ' '.join([token, tokens[i+1]]) in self.active_players:
                    return ' '.join([token, tokens[i+1]])
            if token in self.last_name_to_full_names:
                if len(self.last_name_to_full_names[token]) == 1:
                    return self.last_name_to_full_names[token][0]
                elif i > 0 and ' '.join([tokens[i-1], token]) in self.active_players:
                    return ' '.join([tokens[i-1], token])
        
        return None

    def _extract_team_name(self, doc):
        team_matches = self.team_matcher(doc)
        if team_matches:
            match_id, start, end = team_matches[0]
            return doc[start:end].text.lower()
        return None

    def _extract_season_type(self, query):
        season_type_patterns = {
            "Playoffs": r"\b(play[-\s]?offs?|postseason)\b",
            "Regular Season": r"\bregular season\b",
            "Pre Season": r"\b(pre[-\s]?season)\b",
            "All Star": r"\ball[-\s]?star\b"
        }

        for season, pattern in season_type_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return season
        return "Regular Season"

    def _extract_month(self, query):
        """
        Extract the month mentioned in the user query.
        
        :param query: User input query as a string.
        :return: The month as a string if found, else "0".
        """
        doc = self.nlp(query.lower())

        for token in doc:
            if token.text in self.month_map:
                return self.month_map[token.text]

        return "0"  # Default to "0" if no month is found