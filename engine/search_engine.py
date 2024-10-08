import spacy
from nba_api.stats.endpoints import commonplayerinfo, videodetailsasset
import pandas as pd
from engine.utils import load_team_id_dict, create_player_dictionaries, create_matchers, process_videos
from engine.entity_extractor import EntityExtractor
import re
class SearchEngine:
    def __init__(self, season='2023-24', season_type='Regular Season', last_n_games=200):
        self.nlp = spacy.load("en_core_web_sm")
        self.team_id_dict = load_team_id_dict("engine/team_id_dict.json")
        self.active_players, first_name_to_full_name, last_name_to_full_name = create_player_dictionaries()
        team_matcher, player_matcher = create_matchers(self.nlp, self.team_id_dict, self.active_players, first_name_to_full_name, last_name_to_full_name)


        self.entity_extractor = EntityExtractor(self.nlp, team_matcher, player_matcher, self.active_players, first_name_to_full_name, last_name_to_full_name)

        self.params = {
            "context_measure_detailed": [],
            "season": season,
            "season_type_all_star": season_type,
            "last_n_games": last_n_games,
            "period": 0,
            "month": 0,
        }

    def set_parameter(self, param_name, value):
        self.params[param_name] = value

    def build_params(self):
        required_params = ["context_measure_detailed", "season", "season_type_all_star", "team_id", "player_id"]
        missing_params = [param for param in required_params if self.params.get(param) is None]
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
        return self.params
    
    def filter_play_descriptions(self, df, keywords):
        """
        Filter plays based on all specified keywords in the description.

        Parameters:
            df (pd.DataFrame): DataFrame with play descriptions.
            keywords (list): List of keywords to search for.

        Returns:
            pd.DataFrame: Filtered DataFrame with only the desired plays that include all keywords.
        """
        if not keywords:
            return df  

        filtered_df = df
        for keyword in keywords:
            pattern = rf'\b{re.escape(keyword)}\b' 
            filtered_df = filtered_df[filtered_df['Description'].str.contains(pattern, case=False, na=False, regex=True)]

        return filtered_df
    
    def build_interpretation_message(self, params, play_type_keywords):
        message_parts = []

        if params.get('player_id'):
            player_name = next((name for name, id in self.active_players.items() if id == params['player_id']), None)
            if player_name:
                message_parts.append(player_name.title())  # Capitalize the name

        context_measure = params.get('context_measure_detailed')
        
        if play_type_keywords:
            play_type_str = ' '.join(play_type_keywords).lower()
        else:
            play_type_str = ""

        if context_measure:
            action = self.get_action(context_measure)
            if play_type_str:
                message_parts.append(f"{play_type_str} {action}")
            else:
                message_parts.append(action)
        elif play_type_str:
            message_parts.append(play_type_str)

        season_type = params.get('season_type_all_star')
        if season_type and season_type != "Regular Season":
            message_parts.append(f"in the {season_type}")

        month = params.get('month')
        if month and month != "0":
            months = ["", "October", "November", "December", "January", "February", "March", "April", "May", "June", "July", "August", "September"]
            message_parts.append(f"in {months[int(month)]}")

        season = params.get('season')
        if season:
            message_parts.append(f"during the {season} season")


        opponent_team_id = params.get('opponent_team_id')
        if opponent_team_id:
            team_name = next((name for name, id in self.team_id_dict.items() if id == opponent_team_id), None)
            if team_name:
                message_parts.append(f"against the {team_name.title()}")

        clutch_time = params.get('clutch_time_nullable')
        if clutch_time:
            message_parts.append(f"in {clutch_time}")

        # Combine all parts
        if message_parts:
            return "Interpreted as: " + " ".join(message_parts)
        else:
            return "No specific interpretation available"

    def get_action(self, context_measure):
        """ Helper function to determine the action based on context_measure """
        if context_measure == 'PTS':
            return 'field goals made'
        elif context_measure == 'AST':
            return 'assists'
        elif context_measure == 'REB':
            return 'rebounds'
        elif context_measure == 'STL':
            return 'steals'
        elif context_measure == 'BLK':
            return 'blocks'
        elif context_measure == 'TOV':
            return 'turnovers'
        elif context_measure == 'FGA':
            return 'shot attempts'
        elif context_measure == 'MISS':
            return 'misses'
        else:
            return context_measure.lower()
        
    def filter_with_score_specifiers(self, df, score_specifiers):
        df['Score_Diff_Before'] = df['Home_Points_Before'] - df['Visitor_Points_Before']
        df['Score_Diff_After'] = df['Home_Points_After'] - df['Visitor_Points_After']

        # GT: Check if the shot tied the game
        if score_specifiers == 'GT':
            df = df[df['Score_Diff_After'] == 0]
        
        # LT: Check if the shot was a lead-taking shot
        elif score_specifiers == 'LT':
            df = df[((df['Score_Diff_Before'] <= 0) & (df['Score_Diff_After'] > 0)) |
                    ((df['Score_Diff_Before'] >= 0) & (df['Score_Diff_After'] < 0))]

        return df
    def fetch_videos(self, context_measure, shot_specifiers=None, score_specifiers=None):
        try:
            self.set_parameter("context_measure_detailed", context_measure)
            params = self.build_params()
            intepretation = self.build_interpretation_message(params, shot_specifiers)
            print(intepretation)
            if params['context_measure_detailed'] == 'MISS':
                params['context_measure_detailed'] = 'FGA'
            
            response = videodetailsasset.VideoDetailsAsset(**params)
            video_dict = response.get_dict()
            videos = video_dict['resultSets']
            video_urls = videos['Meta']['videoUrls']
            plays = videos['playlist']
            df = pd.DataFrame(plays)
            df['video_url'] = video_urls


            df['date'] = pd.to_datetime(df['y'].astype(str) + '-' + 
                                        df['m'].astype(str).str.zfill(2) + '-' + 
                                        df['d'].astype(str).str.zfill(2))

            df = df.sort_values(by='date', ascending=False)

            df = process_videos(df)  # Processing layer

            if shot_specifiers:
                df = self.filter_play_descriptions(df, shot_specifiers)
            
            if score_specifiers:
                df = self.filter_with_score_specifiers(df, score_specifiers)
            
            if params['clutch_time_nullable']:
                # Clutch is defined as the last 5 minutes of a game with a score differential of 5 or fewer points
                df = df[df['Score_Diff'] <= 5]
            
            if context_measure == 'MISS':
                df = df[df['Point_Change'] == 0]

            return df
        except Exception as e:
            print("Query returned no results")
            print(e)
            return pd.DataFrame()

    def map_player_team_ids(self, player_name, team_name=None):
        try:
            player_id = self.active_players.get(player_name.lower())
            if not player_id:
                raise ValueError(f"No player found for the name: {player_name}")

            player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id).get_dict()
            team_id = player_info['resultSets'][0]['rowSet'][0][18]

            opponent_team_id = None
            if team_name:
                opponent_team_id = self.team_id_dict.get(team_name.upper(), None)
                if opponent_team_id is None:
                    raise ValueError(f"Could not find opponent team with name: {team_name}")

            return player_id, team_id, opponent_team_id

        except Exception as e:
            print(f"Error mapping player and team IDs: {e}")
            return None, None, None

    def query(self, query):
        player_name, team_name, season_type, context_measures, month, clutch_time, shot_specifiers, score_specifiers = self.entity_extractor.extract_entities(query)
        print(f"EXTRACTED: Player Name={player_name}, Team Name={team_name}, Season Type={season_type}, Context Measures={context_measures}, Month={month}, Clutch Time={clutch_time}, Shot Specifiers={shot_specifiers}, Score Specifier={score_specifiers}") 
        
        if "MISS" in context_measures and "PTS" in context_measures:
            context_measures.remove("PTS")

        self.set_parameter("season_type_all_star", season_type)
        self.set_parameter("month", month)
        self.set_parameter("clutch_time_nullable", clutch_time)

        player_id, team_id, opponent_team_id = self.map_player_team_ids(player_name, team_name)
        if player_id is None or team_id is None:
            print(f"Could not retrieve valid player or team ID for query: {query}")
            return pd.DataFrame()

        self.set_parameter("player_id", player_id)
        self.set_parameter("team_id", team_id)
        if opponent_team_id:
            self.set_parameter("opponent_team_id", opponent_team_id)

        videos = pd.DataFrame()
        
        # If no specific context measures are extracted, default to PTS
        if not context_measures:
            context_measures = ["PTS"]
            
        print(context_measures)

        for measure in context_measures:
            vids = None
            if measure == "PTS" or measure == "FGA" or measure == "MISS":
                vids = self.fetch_videos(measure, shot_specifiers, score_specifiers)
            else: 
                vids = self.fetch_videos(measure)
            videos = pd.concat([videos, vids])

        return videos