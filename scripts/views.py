import os
import requests

import streamlit as st

from PIL import Image

play_list = [
    "Liverpool [2] - 0 Porto",
    "Liverpool [2] - 0 Man City",
    "Liverpool [1] - 0 Watford",
    "Liverpool [1] - 0 Wolves",
    "Leicester 0 - [3] Liverpool",
    "Liverpool [2] - 0 Salzburg",
    "Liverpool [2] - 1 Newcastle",
    "Bournemouth 0 - 3 Liverpool",
    "Liverpool [3] - 0 Bournemouth",
    "Fulham 0 - [1] Liverpool",
    "Southampton 1 - [2] Liverpool",
    "Liverpool [2] - 1 Chelsea",
    "Porto 0 - [2] Liverpool",
    "Liverpool [3] - 0 Norwich",
    "Liverpool [2] - 0 Everton",
    "Bayern 0 - [1] Liverpool",
    "Liverpool [4] - 0 Barcelona",
    "Liverpool [1] - 0 Everton",
    "Genk 0 - [3] Liverpool",
]


def set_sidebar(base_dir, args):
    # set sidebar
    st.sidebar.title("Liverpool Goal Scene Analyzer")
    st.sidebar.markdown(
        "for [Friends of Tracking](https://www.youtube.com/channel/UCUBFJYcag8j2rm_9HkrrA7w)"
    )
    st.sidebar.markdown("")

    st.sidebar.header("Navigation")
    st.sidebar.subheader("Play")

    # return selected play
    play = st.sidebar.selectbox("Which Goal do you want to see??", play_list)

    # mode
    st.sidebar.subheader("Mode")
    mode = st.sidebar.radio(
        "Which mode do yo want to see??",
        [
            "Analysis Report",
            "Annimation with Stretch Index",
            "Player Pitch Control Impact",
        ],
    )
    st.sidebar.markdown("")
    st.sidebar.markdown("")

    # about
    st.sidebar.header("About")
    image_path = os.path.join(base_dir, "reports", "figure", "profile.JPG")
    md_path = os.path.join(base_dir, "scripts", "PROFILE.md")
    if args.env == "local":
        image = Image.open(image_path)
        with open(md_path, "r") as fi:
            profile_md = fi.read()
    else:
        profile_md = requests.get(md_path).content.decode(encoding="utf-8")
        image = requests.get(image_path).content
    st.sidebar.image(image, caption="@saeeeeru", use_column_width=True)
    st.sidebar.info(profile_md)
    st.sidebar.markdown("")
    st.sidebar.markdown("")

    return mode, play


def show_movie(movie_path, args):
    if args.env == "local":
        with open(movie_path, "rb") as fi:
            video_bytes = fi.read()
    else:
        video_bytes = requests.get(movie_path).content

    st.video(video_bytes)


def set_title(mode, play):
    # set title
    st.title(f"{mode}, {play}")
