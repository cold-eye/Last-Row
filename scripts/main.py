import os

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
