from typing import List, Dict, Optional
from dataclasses import dataclass
from statistics import median
from espn_api.football import League

@dataclass
class PowerRankingTeam:
    name: str
    team_id: int
    ranking: float
    weekly_records: List[Dict[str, int]]
    scores: List[float]
    actual_record: Dict[str, int]
    total_points: float
    total_wins: int
    total_losses: int
    median_wins: int
    median_losses: int
    combined_wins: int
    combined_losses: int

def get_weekly_records(all_teams: List, week: int) -> List[Dict]:
    """Calculate weekly records for each team based on scoring rank"""
    weekly_records = []
    
    for week_idx in range(week):
        week_scores = []
        for team in all_teams:
            if week_idx < len(team.scores):
                week_scores.append((team.team_id, team.scores[week_idx]))
                
        week_scores.sort(key=lambda x: x[1], reverse=True)
        
        week_records = {}
        for rank, (team_id, score) in enumerate(week_scores):
            wins = len(week_scores) - (rank + 1)
            losses = rank
            week_records[team_id] = {
                'wins': wins,
                'losses': losses,
                'score': score
            }
            
        weekly_records.append(week_records)
        
    return weekly_records

def calculate_power_rankings(league, week: Optional[int] = None) -> List[PowerRankingTeam]:
    """Calculate power rankings through week 14"""
    max_week = 14
    if not week:
        week = min(league.current_week, max_week)
    else:
        week = min(week, max_week)

    teams = sorted(league.teams, key=lambda x: x.team_id)
    
    weekly_records = get_weekly_records(teams, week)
    
    power_rankings = []
    for team in teams:
        total_wins = 0
        total_losses = 0
        median_wins = 0
        
        team_weekly_records = []
        regular_season_scores = team.scores[:week]
        
        for week_idx, week_record in enumerate(weekly_records):
            if week_idx >= len(regular_season_scores):
                continue
                
            if team.team_id in week_record:
                record = week_record[team.team_id]
                team_weekly_records.append(record)
                total_wins += record['wins']
                total_losses += record['losses']
                
                scores = [r['score'] for r in week_record.values()]
                if record['score'] > median(scores):
                    median_wins += 1

        median_losses = week - median_wins
        actual_records = team.outcomes[:week]
        actual_wins = sum(1 for outcome in actual_records if outcome == 'W')
        actual_losses = sum(1 for outcome in actual_records if outcome == 'L')
        actual_ties = sum(1 for outcome in actual_records if outcome == 'T')
        
        power_rankings.append(PowerRankingTeam(
            name=team.team_name,
            team_id=team.team_id,
            ranking=total_wins / (total_wins + total_losses) if (total_wins + total_losses) > 0 else 0,
            weekly_records=team_weekly_records,
            scores=regular_season_scores,
            actual_record={
                'wins': actual_wins,
                'losses': actual_losses,
                'ties': actual_ties
            },
            total_points=sum(regular_season_scores),
            total_wins=total_wins,
            total_losses=total_losses,
            median_wins=median_wins,
            median_losses=median_losses,
            combined_wins=actual_wins + median_wins,
            combined_losses=actual_losses + median_losses
        ))

    return sorted(power_rankings, key=lambda x: x.ranking, reverse=True)

def print_power_rankings_table(rankings: List[PowerRankingTeam], week: int):
    """Print formatted power rankings tables"""
    print(f"\nRegular Season Power Rankings through Week {week}\n")
    
    header = "{:<4} {:<25} {:<10} {:<15} {:<15} {:<15} {:<15}".format(
        "Rank", "Team", "Rating", "True Record", "vs Median", "Combined", "Actual Record"
    )
    print(header)
    print("-" * 100)
    
    for i, team in enumerate(rankings, 1):
        print("{:<4} {:<25} {:<10.3f} {:<15} {:<15} {:<15} {:<15}".format(
            i,
            team.name[:24],
            team.ranking,
            f"{team.total_wins}-{team.total_losses}",
            f"{team.median_wins}-{team.median_losses}",
            f"{team.combined_wins}-{team.combined_losses}",
            f"{team.actual_record['wins']}-{team.actual_record['losses']}" +
            (f"-{team.actual_record['ties']}" if team.actual_record['ties'] > 0 else "")
        ))
    
    print("\nPoints Per Game Rankings:\n")
    ppg_rankings = sorted(rankings, key=lambda x: x.total_points / len(x.scores), reverse=True)
    
    header = "{:<4} {:<25} {:<15} {:<15} {:<15}".format(
        "Rank", "Team", "PPG", "Total Points", "Games Played"
    )
    print(header)
    print("-" * 75)
    
    for i, team in enumerate(ppg_rankings, 1):
        ppg = team.total_points / len(team.scores)
        print("{:<4} {:<25} {:<15.2f} {:<15.2f} {:<15}".format(
            i,
            team.name[:24],
            ppg,
            team.total_points,
            len(team.scores)
        ))
    
    print("\nWeekly Scoring Records:\n")
    print("{:<25}".format("Team"), end="")
    for w in range(min(week, 14)):
        print("{:<10}".format(f"Week {w+1}"), end="")
    print()
    print("-" * (25 + 10 * min(week, 14)))
    
    for team in rankings:
        print("{:<25}".format(team.name[:24]), end="")
        for record in team.weekly_records:
            print("{:<10}".format(f"{record['wins']}-{record['losses']}"), end="")
        print()
    
    print("\nDetailed Breakdown:\n")
    
    for i, team in enumerate(rankings, 1):
        print(f"{i}. {team.name}")
        print(f"   Points Per Game: {team.total_points / len(team.scores):.2f}")
        print(f"   True Record (vs Everyone): {team.total_wins}-{team.total_losses}")
        print(f"   Median Record: {team.median_wins}-{team.median_losses}")
        print(f"   Combined Record: {team.combined_wins}-{team.combined_losses}")
        print(f"   Actual Record: {team.actual_record['wins']}-{team.actual_record['losses']}" +
              (f"-{team.actual_record['ties']}" if team.actual_record['ties'] > 0 else ""))
        
        true_win_pct = team.total_wins / (team.total_wins + team.total_losses)
        median_win_pct = team.median_wins / (team.median_wins + team.median_losses)
        actual_games = team.actual_record['wins'] + team.actual_record['losses']
        actual_win_pct = team.actual_record['wins'] / actual_games if actual_games > 0 else 0
        
        print(f"   Win Percentages:")
        print(f"      True: {true_win_pct:.3f}")
        print(f"      Median: {median_win_pct:.3f}")
        print(f"      Actual: {actual_win_pct:.3f}")
        print()

def main():
    league = League(
        league_id=123456,
        year=2021,
        espn_s2="your_espn_s2",
        swid="your_swid"
    )

    rankings = calculate_power_rankings(league)
    print_power_rankings_table(rankings, min(league.current_week, 14))

if __name__ == "__main__":
    main()
