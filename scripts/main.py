import argparse
import os
import requests
import urllib

import numpy as np
import pandas as pd
import streamlit as st

from PIL import Image

import Metrica_PitchControl as mpc
from PlayerPitchControlAnalysis import PlayerPitchControlAnalysisPlayer

x_size, y_size = 106.0, 68.0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="local")
    args = parser.parse_args()

    return args


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


def parse_url(path):
    return urllib.parse.quote(path, safe=":/")


def show_movie(movie_path, args):
    if args.env == "local":
        with open(movie_path, "rb") as fi:
            video_bytes = fi.read()
    else:
        video_bytes = requests.get(movie_path).content

    st.video(video_bytes)


@st.cache
def read_dataset(base_dir, play, args):
    data_dir = os.path.join(base_dir, "datasets", "preprocessed", play)
    if args.env == "heroku":
        data_dir = parse_url(data_dir)

    infile_list = pd.read_csv(
        os.path.join(data_dir, "infile_list.txt"), header=None, names=["infile"]
    ).infile.tolist()

    df_dict = {
        infile.replace(".csv", "").split("_")[0]: pd.read_csv(
            os.path.join(data_dir, infile), index_col=[0]
        )
        for infile in infile_list
    }
    # rename columns
    for team, df in df_dict.items():
        df.columns = [
            c if c in ["Time [s]", "ball_x", "ball_y"] else f"{team}_{c}"
            for c in df.columns
        ]
        df_dict[team] = df

    color_dict = {
        infile.replace(".csv", "")
        .split("_")[0]: infile.replace(".csv", "")
        .split("_")[1]
        if not infile.replace(".csv", "").split("_")[1] in ["white", "lightgray"]
        else "black"
        for infile in infile_list
    }

    events_df = pd.read_csv(os.path.join(data_dir, "events.csv"))
    events_df["Team"] = "Liverpool"

    return df_dict, color_dict, events_df


@st.cache
def read_analysis_report(base_dir):
    infile = os.path.join(base_dir, "datasets", "analysis_report", "liverpool2019.csv")
    summary_df = pd.read_csv(infile, index_col=[0], dtype=object).fillna("")

    return summary_df


def main_analysis_report(play, base_dir, args):
    summary_df = read_analysis_report(base_dir)
    stretch_index_text, pitch_control_text = summary_df.loc[play].values
    if stretch_index_text:
        st.header("Stretch Index")
        st.markdown("*" + stretch_index_text + "*")
        main_stretch_index(play, base_dir, args)
    if pitch_control_text:
        st.header("Pitch Control")
        st.markdown("*" + pitch_control_text + "*")
        main_pitch_control(play, base_dir, args)


def player_pitch_control_impact(play, base_dir, args):
    st.subheader("Simulation")
    # read dataset
    df_dict, color_dict, events_df = read_dataset(base_dir, play, args)

    # show dataframe
    st.markdown("event dataframe is ...")
    st.table(events_df)
    event_id = st.selectbox(
        "Select a event id for analysis", events_df.index, index=events_df.index[-1]
    )

    team = st.selectbox(
        "Select a team for analysis",
        [events_df.at[event_id, "Team"]]
        + [k for k in list(df_dict.keys()) if k != events_df.at[event_id, "Team"]],
    )
    # sort player num based on end location
    end_frame = events_df.at[event_id, "End Frame"]
    ball_loc = events_df.loc[event_id, ["End X", "End Y"]].values
    player_num_list = list(
        set([c.split("_")[1] for c in df_dict[team].columns if c.startswith(team)])
    )
    sorted_index = np.argsort(
        [
            np.linalg.norm(
                df_dict[team]
                .loc[end_frame, [f"{team}_{player_num}_{c}" for c in ["x", "y"]]]
                .values
                - ball_loc
            )
            for player_num in player_num_list
        ]
    )
    player_num = st.selectbox(
        "Select a player number for analysis", np.array(player_num_list)[sorted_index]
    )

    verification_mode = st.selectbox(
        "Select the verification mode",
        [
            "movement:How much space created during event??",
            "presense:How much space occupied during event??",
            "location:if positions changed, how much space difference during event??",
        ],
    ).split(":")[0]

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

    with st.spinner("wait for computing ..."):
        if verification_mode == "movement":
            st.markdown(
                example_player_analysis_away.team_player_to_analyze
                + " Player "
                + str(example_player_analysis_away.player_to_analyze)
                + " created "
                + str(
                    int(
                        example_player_analysis_away.calculate_space_created(
                            replace_function="movement",
                            replace_x_velocity=0,
                            replace_y_velocity=0,
                        )
                    )
                )
                + " m^2 of space with his movement during event "
                + str(example_player_analysis_away.event_id)
            )
            # Now, let's plot the space created and conceded by his run
            fig, ax = example_player_analysis_away.plot_pitch_control_difference(
                replace_function="movement",
                replace_x_velocity=0,
                replace_y_velocity=0,
                team_color_dict=color_dict,
            )
            st.pyplot(fig, bbox_layout="tight")

        elif verification_mode == "presense":
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
            fig, ax = example_player_analysis_away.plot_pitch_control_difference(
                replace_function="presence", team_color_dict=color_dict
            )
            st.pyplot(fig, bbox_layout="tight")

        elif verification_mode == "location":
            st_frame = events_df.at[event_id, "Start Frame"]
            x, y = (
                df_dict[team].at[st_frame, f"{team}_{player_num}_x"],
                df_dict[team].at[st_frame, f"{team}_{player_num}_y"],
            )
            max_x, min_x = int(x_size / 2 - x), -int(x_size / 2 + x)
            max_y, min_y = int(y_size / 2 - y), -int(y_size / 2 + y)
            relative_x = st.slider(
                "relative x", min_value=min_x, max_value=max_x, value=0, step=1
            )
            relative_y = st.slider(
                "relative y", min_value=min_y, max_value=max_y, value=0, step=1
            )

            st.markdown(
                example_player_analysis_away.team_player_to_analyze
                + " Player "
                + str(example_player_analysis_away.player_to_analyze)
                + " would have occupied a difference of "
                + str(
                    int(
                        -1
                        * example_player_analysis_away.calculate_space_created(
                            replace_function="location",
                            relative_x_change=relative_x,
                            relative_y_change=relative_y,
                        )
                    )
                )
                + " m^2 of space during event "
                + str(example_player_analysis_away.event_id)
                + " if they were changed to x, y = "
                + str(relative_x)
                + ", "
                + str(relative_y)
            )
            fig, ax = example_player_analysis_away.plot_pitch_control_difference(
                replace_function="location",
                relative_x_change=relative_x,
                relative_y_change=relative_y,
                team_color_dict=color_dict,
            )
            st.pyplot(fig, bbox_layout="tight")
    st.success("done !!")


def main_pitch_control(play, base_dir, args):
    # show video
    st.subheader("Annimation Tracking Data")
    st.markdown(
        "tracking data from [[Friends-of-Tracking-Data-FoTD/Last-Row]\
        (https://github.com/Friends-of-Tracking-Data-FoTD/Last-Row)],\
        and referenced source code [[andrewsimplebet/FoT-Player-Pitch-Control-Impact]\
        (https://github.com/andrewsimplebet/FoT-Player-Pitch-Control-Impact)]"
    )

    movie_dir = os.path.join(base_dir, "reports", "movie", "pitch_control")
    show_movie(os.path.join(movie_dir, f"{play}.mp4"), args)


def main_stretch_index(play, base_dir, args):

    # show video
    st.subheader("Visualization")
    st.markdown(
        "above is tracking data[[Friends-of-Tracking-Data-FoTD/Last-Row]\
        (https://github.com/Friends-of-Tracking-Data-FoTD/Last-Row)],\
        and below is stretch index [[paper link]\
        (https://www.researchgate.net/publication/230600552_Capturing_complex_non-linear_team_behaviours_during_competitive_football_performance)]."
    )
    movie_dir = os.path.join(base_dir, "reports", "movie", "stretch_annotated")
    show_movie(os.path.join(movie_dir, f"{play}.mp4"), args)


def main():
    # parse argument
    args = parse_args()

    if args.env == "local":
        base_dir = os.path.join(".")
    elif args.env == "heroku":
        base_dir = os.path.join(
            "https://raw.githubusercontent.com", "saeeeeru", "Last-Row", "master"
        )
    else:
        exit(9)

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

    # set title
    st.title(f"{mode}, {play}")

    if mode == "Annimation with Stretch Index":
        main_stretch_index(play, base_dir, args)
    elif mode == "Player Pitch Control Impact":
        main_pitch_control(play, base_dir, args)
        player_pitch_control_impact(play, base_dir, args)
    elif mode == "Analysis Report":
        main_analysis_report(play, base_dir, args)
    else:
        exit()


if __name__ == "__main__":
    main()
