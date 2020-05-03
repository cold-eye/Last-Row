import argparse
import os
import requests

import pandas as pd
import streamlit as st

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', default='local')
    args = parser.parse_args()

    return args

def main():
    # parse argument
    args = parse_args()
    
    if args.env == 'local':
        base_dir = os.path.join('.')
    elif args.env == 'heroku':
        base_dir = os.path.join('https://raw.githubusercontent.com','saeeeeru','Last-Row','develop')
    else:
        exit(9)

    # set title
    st.title('Liverpool Goal Scene Analyzer')

    # generate select box
    df = pd.read_csv(os.path.join(base_dir, 'datasets', 'positional_data', 'liverpool_2019.csv'), index_col=['play'])
    play_list = df.index.unique().tolist()

    # return selected play
    play = st.selectbox('Which Goal do you want to see??', play_list[::-1])

    annotate_flg = st.checkbox('annotate player_idx and velocity')

    # show video
    movie_dir = os.path.join(base_dir, 'reports', 'movie', 'stretch') if not annotate_flg else os.path.join(base_dir, 'reports', 'movie', 'stretch_annotated')
    st.markdown('above is tracking data[[data link](https://github.com/Friends-of-Tracking-Data-FoTD/Last-Row)], and below is stretch index [[paper link](https://www.researchgate.net/publication/230600552_Capturing_complex_non-linear_team_behaviours_during_competitive_football_performance)].')
    if args.env == 'local':
        with open(os.path.join(movie_dir, f'{play}.mp4'), 'rb') as fi:
            video_bytes = fi.read()
    else:
        video_bytes = requests.get(os.path.join(movie_dir, f'{play}.mp4')).content

    st.video(video_bytes)
    st.markdown('my twitter account is [@saeeeeru](https://twitter.com/saeeeeru/)')

if __name__ == '__main__':
    main()