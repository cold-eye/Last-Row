import argparse
import os
import requests

import numpy as np
import pandas as pd
import streamlit as st

import Metrica_PitchControl as mpc
from PlayerPitchControlAnalysis import PlayerPitchControlAnalysisPlayer

x_size, y_size = 106.0, 68.0

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', default='local')
    args = parser.parse_args()

    return args

play_list = [
    'Fulham 0 - [1] Liverpool', 
    'Genk 0 - [3] Liverpool', 
    'Bayern 0 - [1] Liverpool', 
    'Southampton 1 - [2] Liverpool', 
    'Bournemouth 0 - 3 Liverpool', 
    'Liverpool [1] - 0 Everton', 
    'Liverpool [3] - 0 Bournemouth', 
    'Liverpool [1] - 0 Wolves', 
    'Liverpool [2] - 1 Chelsea', 
    'Liverpool [3] - 0 Norwich', 
    'Liverpool [2] - 0 Porto', 
    'Liverpool [2] - 0 Everton', 
    'Liverpool [2] - 1 Newcastle', 
    'Liverpool [2] - 0 Salzburg', 
    'Liverpool [2] - 0 Man City', 
    'Liverpool [1] - 0 Watford', 
    'Leicester 0 - [3] Liverpool', 
    'Liverpool [4] - 0 Barcelona', 
    'Porto 0 - [2] Liverpool'
]

def show_movie(movie_path, args):
    if args.env == 'local':
        with open(movie_path, 'rb') as fi:
            video_bytes = fi.read()
    else:
        video_bytes = requests.get(movie_path).content

    st.video(video_bytes)

@st.cache
def read_dataset(base_dir, play):
    data_dir = os.path.join(base_dir, 'datasets', 'preprocessed', play)
    
    infile_list = [infile for infile in os.listdir(data_dir) if not infile.startswith('events.')]

    df_dict = {infile.replace('.csv','').split('_')[0]:pd.read_csv(os.path.join(data_dir, infile), index_col=[0]) for infile in infile_list}
    # rename columns
    for team, df in df_dict.items():
        df.columns = [c if c in ['Time [s]', 'ball_x', 'ball_y'] else f'{team}_{c}' for c in df.columns]
        df_dict[team] = df
    
    color_dict = {infile.replace('.csv','').split('_')[0]:infile.replace('.csv','').split('_')[1] if not infile.replace('.csv','').split('_')[1] in ['white', 'lightgray'] else 'black' for infile in infile_list}

    events_df = pd.read_csv(os.path.join(data_dir, 'events.csv'))
    events_df['Team'] = 'Liverpool'

    return df_dict, color_dict, events_df


def main_pitch_control(play, base_dir, args):
    st.subheader('Annimation Tracking Data')
    st.markdown('tracking data from [[data link](https://github.com/Friends-of-Tracking-Data-FoTD/Last-Row)].')

    movie_dir = os.path.join(base_dir, 'reports', 'movie', 'pitch_control')
    show_movie(os.path.join(movie_dir, f'{play}.mp4'), args)

    st.subheader('Simulation')
    # read dataset
    df_dict, color_dict, events_df = read_dataset(base_dir, play)
    
    # show dataframe
    st.markdown('event dataframe is ...')
    st.table(events_df)
    event_id = st.selectbox('Select a event id for analysis', events_df.index, index=events_df.index[-1])

    team = st.selectbox('Select a team for analysis', [events_df.at[event_id, 'Team']]+[k for k in list(df_dict.keys()) if k!=events_df.at[event_id, 'Team']])
    # sort player num based on end location
    end_frame = events_df.at[event_id, 'End Frame']
    ball_loc = events_df.loc[event_id, ['End X', 'End Y']].values
    player_num_list = list(set([c.split('_')[1] for c in df_dict[team].columns if c.startswith(team)]))
    sorted_index = np.argsort([np.linalg.norm(df_dict[team].loc[end_frame, [f'{team}_{player_num}_{c}' for c in ['x', 'y']]].values-ball_loc) for player_num in player_num_list])
    player_num = st.selectbox('Select a player number for analysis', np.array(player_num_list)[sorted_index])

    verification_mode = st.selectbox('Select the verification mode', ['movement:How much space created during event??', 'presense:How much space occupied during event??', 'location:if positions changed, how much space difference during event??']).split(':')[0]

    params = mpc.default_model_params(3)
    example_player_analysis_away = PlayerPitchControlAnalysisPlayer(
        df_dict=df_dict,
        params=params,
        events=events_df,
        event_id=event_id,
        team_player_to_analyze=team,
        player_to_analyze=str(player_num),
        field_dimens=(106.0, 68.0),
        n_grid_cells_x=50,
    )

    with st.spinner('wait for computing ...'):
        if verification_mode == 'movement':
            st.markdown(
                example_player_analysis_away.team_player_to_analyze
                + " Player "
                + str(example_player_analysis_away.player_to_analyze)
                + " created "
                + str(
                    int(
                        example_player_analysis_away.calculate_space_created(
                            replace_function="movement", replace_x_velocity=0, replace_y_velocity=0
                        )
                    )
                )
                + " m^2 of space with his movement during event "
                + str(example_player_analysis_away.event_id)
            )
            # Now, let's plot the space created and conceded by his run
            fig, ax = example_player_analysis_away.plot_pitch_control_difference(
                replace_function="movement", replace_x_velocity=0, replace_y_velocity=0, team_color_dict=color_dict
            )
            st.pyplot(fig, bbox_layout='tight')

        elif verification_mode == 'presense':
            st.markdown(
                example_player_analysis_away.team_player_to_analyze
                + " Player "
                + str(example_player_analysis_away.player_to_analyze)
                + " occupied "
                + str(
                    int(
                        example_player_analysis_away.calculate_space_created(
                            replace_function="presence"
                        )
                    )
                )
                + " m^2 of space during event "
                + str(example_player_analysis_away.event_id)
            )
            fig, ax = example_player_analysis_away.plot_pitch_control_difference(replace_function="presence", team_color_dict=color_dict)
            st.pyplot(fig, bbox_layout='tight')
            
        elif verification_mode == 'location':
            st_frame = events_df.at[event_id, 'Start Frame']
            x, y = df_dict[team].at[st_frame, f'{team}_{player_num}_x'], df_dict[team].at[st_frame, f'{team}_{player_num}_y']
            max_x, min_x = int(x_size/2-x), -int(x_size/2+x)
            max_y, min_y = int(y_size/2-y), -int(y_size/2+y)
            relative_x = st.slider('relative x', min_value=min_x, max_value=max_x, value=0, step=1)
            relative_y = st.slider('relative y', min_value=min_y, max_value=max_y, value=0, step=1)

            st.markdown(
                example_player_analysis_away.team_player_to_analyze
                + " Player "
                + str(example_player_analysis_away.player_to_analyze)
                + " would have occupied a difference of "
                + str(
                    int(
                        -1
                        * example_player_analysis_away.calculate_space_created(
                            replace_function="location", relative_x_change=relative_x, relative_y_change=relative_y
                        )
                    )
                )
                + " m^2 of space during event "
                + str(example_player_analysis_away.event_id)
                + " if they were changed to x, y = "
                + str(relative_x)
                + ', '
                + str(relative_y)
            )
            fig, ax = example_player_analysis_away.plot_pitch_control_difference(
                replace_function="location", relative_x_change=relative_x, relative_y_change=relative_y, team_color_dict=color_dict
            )
            st.pyplot(fig, bbox_layout='tight')
    st.success('done !!')



def main_stretch_index(play, base_dir, args):

    # show video
    st.subheader('Visualization')
    st.markdown('above is tracking data[[data link](https://github.com/Friends-of-Tracking-Data-FoTD/Last-Row)], and below is stretch index [[paper link](https://www.researchgate.net/publication/230600552_Capturing_complex_non-linear_team_behaviours_during_competitive_football_performance)].')
    movie_dir = os.path.join(base_dir, 'reports', 'movie', 'stretch_annotated')
    show_movie(os.path.join(movie_dir, f'{play}.mp4'), args)
    
def main():
    # parse argument
    args = parse_args()
    
    if args.env == 'local':
        base_dir = os.path.join('.')
    elif args.env == 'heroku':
        base_dir = os.path.join('https://raw.githubusercontent.com','saeeeeru','Last-Row','develop')
    else:
        exit(9)

    # set sidebar
    st.sidebar.title('Menu')
    mode = st.sidebar.radio('Which mode do yo want to see??', ['Annimation with Stretch Index', 'Player Pitch Control Impact'])

    md_path = os.path.join(base_dir, 'scripts', 'PROFILE.md')
    if args.env == 'local':
        with open(md_path, 'r') as fi:
            profile_md = fi.read()
    else:
        profile_md = requests.get(md_path).content

    st.sidebar.info(profile_md)

    # set title
    st.title('Liverpool Goal Scene Analyzer')

    # set header
    st.header(mode)

    # return selected play
    play = st.selectbox('Which Goal do you want to see??', play_list)

    if mode == 'Annimation with Stretch Index':
        main_stretch_index(play, base_dir, args)
    elif mode == 'Player Pitch Control Impact':
        main_pitch_control(play, base_dir, args)
    else:
        exit()

if __name__ == '__main__':
    main()