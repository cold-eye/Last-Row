import os
import requests

import streamlit as st

from PIL import Image

from utils import parse_args
from views import set_sidebar
from models import LiverpoolAnalyzer

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

    # get image
    image_path = os.path.join(base_dir, "reports", "figure", "profile.JPG")
    md_path = os.path.join(base_dir, "scripts", "PROFILE.md")
    if args.env == "local":
        image = Image.open(image_path)
        with open(md_path, "r") as fi:
            profile_md = fi.read()
    else:
        profile_md = requests.get(md_path).content.decode(encoding="utf-8")
        image = requests.get(image_path).content

    # set layout
    st.beta_set_page_config(
        page_title="LiverpoolAnalyzer",
        page_icon=image,
        # layout="wide",
        initial_sidebar_state="expanded"
    )

    # set sidebar
    mode, play = set_sidebar(base_dir, args)

    # instance class
    liverpool_analyzer = LiverpoolAnalyzer(mode, play, base_dir, args)

    if mode == "Annimation with Stretch Index":
        liverpool_analyzer.plot_pitch_control()
    elif mode == "Player Pitch Control Impact":
        liverpool_analyzer.plot_pitch_control()
        liverpool_analyzer.player_pitch_control_impact()
    elif mode == "Analysis Report":
        liverpool_analyzer.show_analysis_report()
    else:
        exit()


if __name__ == "__main__":
    main()
