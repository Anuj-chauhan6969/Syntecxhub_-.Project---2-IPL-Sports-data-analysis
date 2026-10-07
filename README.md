# IPL Sports Data Analysis

A Python-based IPL data analysis project using Pandas, Matplotlib and Seaborn.

## Features

- Top 10 run scorers
- Player strike-rate analysis
- Team win-rate analysis
- Runs by season
- Player performance across seasons
- Season summary
- CSV result exports
- Automatic Markdown insights

## Project Structure

```text
IPL-Sports-Data-Analysis/
├── data/
│   ├── matches.csv
│   └── deliveries.csv
├── output/
├── analysis.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Dataset

Place these two CSV files inside the `data` folder:

- `matches.csv`
- `deliveries.csv`

The script supports common IPL datasets containing columns such as `id`, `season`, `team1`, `team2`, `winner`, `match_id`, `batter`/`batsman`, and `batsman_runs`.

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python analysis.py
```

## Output

The script generates:

- `output/top_scorers.png`
- `output/strike_rates.png`
- `output/team_win_rates.png`
- `output/season_runs.png`
- `output/player_season_comparison.png`
- `output/season_summary.png`
- CSV metric files
- `output/insights.md`

## Skills Demonstrated

- Python
- Pandas
- Data cleaning
- GroupBy and aggregation
- Exploratory Data Analysis
- Matplotlib
- Seaborn
- Sports analytics
- Data visualization
- Automated reporting

## Note

This project is for educational and portfolio purposes.
