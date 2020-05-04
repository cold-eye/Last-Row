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

    # return selected play
    play = st.selectbox('Which Goal do you want to see??', play_list)

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