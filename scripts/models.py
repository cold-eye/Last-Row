import os

import numpy as np
import pandas as pd
import streamlit as st

import Metrica_PitchControl as mpc
from PlayerPitchControlAnalysis import PlayerPitchControlAnalysisPlayer
from utils import parse_url
from views import show_movie

x_size, y_size = 106.0, 68.0


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


class LiverpoolAnalyzer:
    def __init__(self, mode, play, base_dir, args):
        self.mode = mode
        self.play = play
        self.base_dir = base_dir
        self.args = args

        self.set_title()

    def set_title(self):
        # set title
        st.title(f"{self.mode}, {self.play}")

    def show_analysis_report(self):
        summary_df = read_analysis_report(self.base_dir)
        stretch_index_text, pitch_control_text = summary_df.loc[self.play].values
        if stretch_index_text:
            st.header("Stretch Index")
            st.markdown("*" + stretch_index_text + "*")
            self.plot_stretch_index()
        if pitch_control_text:
            st.header("Pitch Control")
            st.markdown("*" + pitch_control_text + "*")
            self.plot_pitch_control()

    def player_pitch_control_impact(self):
        st.subheader("Simulation")
        # read dataset
        df_dict, color_dict, events_df = read_dataset(
            self.base_dir, self.play, self.args
        )

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
            "Select a player number for analysis",
            np.array(player_num_list)[sorted_index],
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

    def plot_pitch_control(self):
        # show video
        st.subheader("Annimation Tracking Data")
        st.markdown(
            "tracking data from [[Friends-of-Tracking-Data-FoTD/Last-Row]\
            (https://github.com/Friends-of-Tracking-Data-FoTD/Last-Row)],\
            and referenced source code [[andrewsimplebet/FoT-Player-Pitch-Control-Impact]\
            (https://github.com/andrewsimplebet/FoT-Player-Pitch-Control-Impact)]"
        )

        movie_dir = os.path.join(self.base_dir, "reports", "movie", "pitch_control")
        show_movie(os.path.join(movie_dir, f"{self.play}.mp4"), self.args)

    def plot_stretch_index(self):
        # show video
        st.subheader("Visualization")
        st.markdown(
            "above is tracking data[[Friends-of-Tracking-Data-FoTD/Last-Row]\
            (https://github.com/Friends-of-Tracking-Data-FoTD/Last-Row)],\
            and below is stretch index [[paper link]\
            (https://www.researchgate.net/publication/230600552_Capturing_complex_non-linear_team_behaviours_during_competitive_football_performance)]."
        )
        movie_dir = os.path.join(self.base_dir, "reports", "movie", "stretch_annotated")
        show_movie(os.path.join(movie_dir, f"{self.play}.mp4"), self.args)
