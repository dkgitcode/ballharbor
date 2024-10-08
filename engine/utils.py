import json
import spacy
from spacy.matcher import PhraseMatcher
from nba_api.stats.static import players

def load_team_id_dict(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def create_player_dictionaries():
    active_players = {player['full_name'].lower(): player['id'] for player in players.get_active_players()}
    first_name_to_full_names = {}
    last_name_to_full_names = {}

    for player in players.get_active_players():
        full_name = player['full_name'].lower()
        first_name = full_name.split()[0].lower()
        last_name = full_name.split()[-1].lower()

        if first_name in first_name_to_full_names:
            first_name_to_full_names[first_name].append(full_name)
        else:
            first_name_to_full_names[first_name] = [full_name]

        if last_name in last_name_to_full_names:
            last_name_to_full_names[last_name].append(full_name)
        else:
            last_name_to_full_names[last_name] = [full_name]

    return active_players, first_name_to_full_names, last_name_to_full_names

def create_matchers(nlp, team_id_dict, active_players, first_name_to_full_names, last_name_to_full_names):
    team_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    player_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    team_patterns = [nlp.make_doc(name) for name in team_id_dict.keys()]
    team_matcher.add("TEAM_NAMES", team_patterns)

    full_name_patterns = [nlp.make_doc(name) for name in active_players.keys()]
    player_matcher.add("FULL_PLAYER_NAMES", full_name_patterns)

    # We'll handle first and last names separately in the entity extractor

    return team_matcher, player_matcher

def preprocess_query(query):
    stopwords = {"the", "a", "an"}
    query_tokens = query.split()
    filtered_tokens = [word for word in query_tokens if word.lower() not in stopwords]
    return " ".join(filtered_tokens)


def process_videos(df):
    """
    Reformat NBA video DataFrame rows into more readable columns and extract video URLs and thumbnails.

    Parameters:
        df (pd.DataFrame): Input DataFrame with NBA video data.

    Returns:
        pd.DataFrame: Reformatted DataFrame.
    """
    # Create a new DataFrame with clearer column names
    formatted_df = df.rename(columns={
        'gi': 'Game_ID',
        'ei': 'Event_Index',
        'y': 'Year',
        'm': 'Month',
        'd': 'Day',
        'gc': 'Game_Code',
        'p': 'Period',
        'dsc': 'Description',
        'ha': 'Home_Team',
        'hid': 'Home_Team_ID',
        'va': 'Visitor_Team',
        'vid': 'Visitor_Team_ID',
        'hpb': 'Home_Points_Before',
        'hpa': 'Home_Points_After',
        'vpb': 'Visitor_Points_Before',
        'vpa': 'Visitor_Points_After',
        'pta': 'Points_This_Action',
        'video_url': 'Video_URL',
        'date': 'Game_Date'
    })

    # Use hpb, hpa, vpb, and vpa to calculate the Points_This_Action (pta is showing zero due to a bug in the API)
    formatted_df['Point_Change'] = (
        (formatted_df['Home_Points_After'] - formatted_df['Home_Points_Before']) + 
        (formatted_df['Visitor_Points_After'] - formatted_df['Visitor_Points_Before'])
    )
    
    formatted_df['Score_Diff'] = (formatted_df['Home_Points_Before'] - formatted_df['Visitor_Points_Before']).abs()
    

    # Unpack the `video_url` dictionary to extract the video link and thumbnail link
    formatted_df['Video_Link'] = formatted_df['Video_URL'].apply(lambda x: x.get('lurl') if isinstance(x, dict) else None)
    formatted_df['Thumbnail_Link'] = formatted_df['Video_URL'].apply(lambda x: x.get('lth') if isinstance(x, dict) else None)

    # Reorder columns to a more logical structure for readability
    formatted_df = formatted_df[[
        'Game_ID', 'Game_Date', 'Year', 'Month', 'Day', 'Game_Code', 'Period', 
        'Home_Team', 'Visitor_Team', 'Description', 'Home_Points_Before', 'Home_Points_After',
        'Visitor_Points_Before', 'Visitor_Points_After', 'Point_Change', 'Score_Diff',
        'Home_Team_ID', 'Visitor_Team_ID', 'Video_Link', 'Thumbnail_Link'
    ]]

    return formatted_df