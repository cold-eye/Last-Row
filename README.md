# Liverpool Goal Scene Analyzer
## Overview
There are source code for vizualization and notebooks for analysis of Liverpool Goal Scene Dataset.

## Dataset
* [Friends-of-Tracking-Data-FoTD/Last-Row](https://github.com/Friends-of-Tracking-Data-FoTD/Last-Row)

## Referenced Source Code
* [Friends-of-Tracking-Data-FoTD/LaurieOnTracking](https://github.com/Friends-of-Tracking-Data-FoTD/LaurieOnTracking)
* [andrewsimplebet/FoT-Player-Pitch-Control-Impact](https://github.com/andrewsimplebet/FoT-Player-Pitch-Control-Impact)

## Directory Tree

    .
    ├── README.md                <- The top-level README for developers using this project.
    │
    ├── datasets                 <- Dataset Dirctory
    │   │
    │   ├── positional_data      <- The original, immutable data dump.
    │   └── preprocessed         <- The final, canonical data sets for modeling.
    │
    ├── notebook                 <- Jupyter notebooks. Naming convention is a number (for ordering).
    │   │
    │   └── {Number}-{Name}.ipynb        <- Number means processing step, Name means Processing Title 
    │               |
    │               └── {Number}-{Name}.ipynb        <- Number means processing step, Name means Processing Title 
    │                                               e.g. = 1.PreprocessingDataset.ipynb, 2-FitModel.ipynb, 
    │                                                      3-VerificatePredictPerformance.ipynb
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    └── src                <- Source code in this project.
        │
        ├── main.py                        <- main application program
        ├── Metrica_PitchControl.py        <- compute pitch control
        ├── PlayerPitchControlAnalysis.py  <- for simulation of player pitch control impact
        └── Metrica_Viz.py                 <- vizualization functions