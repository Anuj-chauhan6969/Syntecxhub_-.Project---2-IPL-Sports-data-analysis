
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ---------------------------------------------------------
# Setup
# ---------------------------------------------------------

os.makedirs("output", exist_ok=True)
sns.set_theme(style="whitegrid")

# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------

matches = pd.read_csv("data/matches.csv")
deliveries = pd.read_csv("data/deliveries.csv")

print("=" * 60)
print("IPL / SPORTS DATA ANALYSIS")
print("=" * 60)

# ---------------------------------------------------------
# Detect batter column
# ---------------------------------------------------------

if "batter" in deliveries.columns:
    batter_column = "batter"
elif "batsman" in deliveries.columns:
    batter_column = "batsman"
else:
    raise ValueError("Could not find batter/batsman column.")

# ---------------------------------------------------------
# Check batsman runs column
# ---------------------------------------------------------

if "batsman_runs" not in deliveries.columns:
    raise ValueError("batsman_runs column not found.")

# ---------------------------------------------------------
# Detect season column
# ---------------------------------------------------------

if "season" in matches.columns:
    season_column = "season"

elif "date" in matches.columns:
    matches["date"] = pd.to_datetime(
        matches["date"],
        errors="coerce"
    )

    matches["season"] = matches["date"].dt.year
    season_column = "season"

else:
    raise ValueError("Could not determine season.")

# ---------------------------------------------------------
# Detect match ID
# ---------------------------------------------------------

match_id_column = "id" if "id" in matches.columns else "match_id"

if "match_id" not in deliveries.columns:
    raise ValueError("deliveries.csv must contain match_id.")

# ---------------------------------------------------------
# Merge deliveries with season
# ---------------------------------------------------------

deliveries = deliveries.merge(
    matches[[match_id_column, season_column]],
    left_on="match_id",
    right_on=match_id_column,
    how="left"
)

# ---------------------------------------------------------
# 1. TOP SCORERS
# ---------------------------------------------------------

player_runs = (
    deliveries
    .groupby(batter_column)["batsman_runs"]
    .sum()
    .sort_values(ascending=False)
)

top_scorers = player_runs.head(10)

print("\nTOP 10 RUN SCORERS")
print(top_scorers)

plt.figure(figsize=(10, 6))

top_scorers.sort_values().plot(
    kind="barh"
)

plt.title("Top 10 IPL Run Scorers")
plt.xlabel("Total Runs")
plt.ylabel("Player")
plt.tight_layout()

plt.savefig(
    "output/top_scorers.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ---------------------------------------------------------
# 2. STRIKE RATES
# ---------------------------------------------------------

balls_faced = deliveries.groupby(batter_column).size()

runs = deliveries.groupby(batter_column)["batsman_runs"].sum()

strike_rate = (
    runs / balls_faced
) * 100

strike_rate_df = pd.DataFrame({
    "Runs": runs,
    "Balls": balls_faced,
    "Strike Rate": strike_rate
})

# IMPORTANT:
# Small dataset may not have players with 100 balls.
# Therefore use 20 balls as minimum qualification.

MIN_BALLS = 20

qualified_sr = (
    strike_rate_df[
        strike_rate_df["Balls"] >= MIN_BALLS
    ]
    .sort_values(
        "Strike Rate",
        ascending=False
    )
)

top_strike_rates = qualified_sr.head(10)

print("\nTOP 10 STRIKE RATES")
print(top_strike_rates)

# Only create chart if data exists

if not top_strike_rates.empty:

    plt.figure(figsize=(10, 6))

    sns.barplot(
        data=top_strike_rates.reset_index(),
        x="Strike Rate",
        y=batter_column
    )

    plt.title(
        f"Top 10 IPL Strike Rates "
        f"(Minimum {MIN_BALLS} Balls)"
    )

    plt.xlabel("Strike Rate")
    plt.ylabel("Player")

    plt.tight_layout()

    plt.savefig(
        "output/strike_rates.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

else:

    print(
        f"\nNo player has faced at least "
        f"{MIN_BALLS} balls."
    )

# ---------------------------------------------------------
# 3. TEAM WIN RATES
# ---------------------------------------------------------

team_matches = pd.concat([
    matches[["team1"]].rename(
        columns={"team1": "team"}
    ),
    matches[["team2"]].rename(
        columns={"team2": "team"}
    )
])

team_match_count = team_matches.value_counts("team")

if "winner" in matches.columns:

    team_wins = (
        matches["winner"]
        .dropna()
        .value_counts()
    )

    win_rate = (
        team_wins
        .div(team_match_count)
        .mul(100)
        .fillna(0)
        .sort_values(ascending=False)
    )

else:

    win_rate = pd.Series(dtype=float)

print("\nTEAM WIN RATES")
print(win_rate)

if not win_rate.empty:

    plt.figure(figsize=(10, 7))

    win_rate.sort_values().plot(
        kind="barh"
    )

    plt.title("IPL Team Win Rates")
    plt.xlabel("Win Rate (%)")
    plt.ylabel("Team")

    plt.tight_layout()

    plt.savefig(
        "output/team_win_rates.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# ---------------------------------------------------------
# 4. RUNS BY SEASON
# ---------------------------------------------------------

season_runs = (
    deliveries
    .groupby(season_column)["batsman_runs"]
    .sum()
    .sort_index()
)

print("\nTOTAL RUNS BY SEASON")
print(season_runs)

if not season_runs.empty:

    plt.figure(figsize=(10, 6))

    season_runs.plot(
        marker="o"
    )

    plt.title("IPL Runs by Season")
    plt.xlabel("Season")
    plt.ylabel("Total Runs")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        "output/season_runs.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# ---------------------------------------------------------
# 5. PLAYER COMPARISON ACROSS SEASONS
# ---------------------------------------------------------

player_season_runs = (
    deliveries
    .groupby(
        [season_column, batter_column]
    )["batsman_runs"]
    .sum()
    .reset_index()
)

top_players = (
    player_runs
    .head(5)
    .index
    .tolist()
)

comparison = player_season_runs[
    player_season_runs[batter_column].isin(
        top_players
    )
]

pivot_comparison = (
    comparison
    .pivot(
        index=season_column,
        columns=batter_column,
        values="batsman_runs"
    )
    .fillna(0)
)

print("\nPLAYER PERFORMANCE ACROSS SEASONS")
print(pivot_comparison)

if not pivot_comparison.empty:

    plt.figure(figsize=(12, 7))

    for player in pivot_comparison.columns:

        plt.plot(
            pivot_comparison.index,
            pivot_comparison[player],
            marker="o",
            label=player
        )

    plt.title(
        "Top Players - Runs Across IPL Seasons"
    )

    plt.xlabel("Season")
    plt.ylabel("Runs")

    plt.legend()

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        "output/player_season_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# ---------------------------------------------------------
# 6. SEASON SUMMARY
# ---------------------------------------------------------

season_matches = (
    matches
    .groupby(season_column)
    .size()
)

season_summary = pd.DataFrame({
    "Matches": season_matches,
    "Total Runs": season_runs
})

print("\nSEASON SUMMARY")
print(season_summary)

if not season_summary.empty:

    fig, ax1 = plt.subplots(
        figsize=(11, 6)
    )

    ax1.bar(
        season_summary.index.astype(str),
        season_summary["Matches"],
        alpha=0.7
    )

    ax1.set_xlabel("Season")
    ax1.set_ylabel("Number of Matches")

    ax2 = ax1.twinx()

    ax2.plot(
        season_summary.index.astype(str),
        season_summary["Total Runs"],
        marker="o",
        linewidth=2
    )

    ax2.set_ylabel("Total Runs")

    plt.title(
        "IPL Season Summary"
    )

    plt.tight_layout()

    plt.savefig(
        "output/season_summary.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# ---------------------------------------------------------
# EXPORT RESULTS
# ---------------------------------------------------------

top_scorers.to_csv(
    "output/top_scorers.csv"
)

top_strike_rates.to_csv(
    "output/top_strike_rates.csv"
)

win_rate.to_csv(
    "output/team_win_rates.csv"
)

season_summary.to_csv(
    "output/season_summary.csv"
)

# ---------------------------------------------------------
# INSIGHTS
# ---------------------------------------------------------

# Top scorer

if not top_scorers.empty:

    top_player = top_scorers.index[0]
    top_player_runs = top_scorers.iloc[0]

else:

    top_player = "N/A"
    top_player_runs = 0


# Best strike rate

if not top_strike_rates.empty:

    best_sr_player = top_strike_rates.index[0]

    best_sr = (
        top_strike_rates.iloc[0]["Strike Rate"]
    )

    strike_rate_text = (
        f"Among players with at least "
        f"{MIN_BALLS} balls faced, "
        f"**{best_sr_player}** has the highest "
        f"strike rate at **{best_sr:.2f}**."
    )

else:

    strike_rate_text = (
        f"No player faced at least "
        f"{MIN_BALLS} balls in the dataset, "
        f"so a qualified strike rate could not "
        f"be calculated."
    )


# Best team

if not win_rate.empty:

    best_team = win_rate.index[0]
    best_team_rate = win_rate.iloc[0]

    team_text = (
        f"**{best_team}** has the highest "
        f"calculated win rate of "
        f"**{best_team_rate:.2f}%**."
    )

else:

    team_text = (
        "Team win rate could not be calculated."
    )


# Highest scoring season

if not season_runs.empty:

    highest_run_season = season_runs.idxmax()
    highest_season_runs = season_runs.max()

    season_text = (
        f"The season with the highest total "
        f"batting runs was **{highest_run_season}**, "
        f"with **{highest_season_runs} runs**."
    )

else:

    season_text = (
        "Season run information is unavailable."
    )


# ---------------------------------------------------------
# Create insights.md
# ---------------------------------------------------------

insights = f"""# IPL Data Analysis - Key Insights

## Top Scorer

**{top_player}** is the highest run scorer
in the analyzed dataset with
**{top_player_runs} runs**.

## Best Strike Rate

{strike_rate_text}

## Best Team Win Rate

{team_text}

## Highest Scoring Season

{season_text}

## Analysis Summary

The analysis compares IPL players and teams
using batting runs, strike rate, team win
percentage, and season-level performance.

The project also compares player performance
across seasons and exports charts and CSV
summaries for further analysis.
"""

with open(
    "output/insights.md",
    "w",
    encoding="utf-8"
) as file:

    file.write(insights)

# ---------------------------------------------------------
# Completed
# ---------------------------------------------------------

print("\n" + "=" * 60)
print("ANALYSIS COMPLETED SUCCESSFULLY")
print("=" * 60)

print("\nGenerated files are available in:")
print("output/")

print("\nAdd matches.csv and deliveries.csv to data/")
print("before running the analysis.")
