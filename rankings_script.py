from typing import List, Dict, Optional
from dataclasses import dataclass
import math
from espn_api.football import League

@dataclass
class PowerRankingTeam:
    name: str
    team_id: int
    ranking: float
    weekly_records: List[Dict[str, int]]  # List of weekly win-loss records
    scores: List[float]
    actual_record: Dict[str, int]
    total_points: float
    total_wins: int
    total_losses: int

def calculate_weekly_records(teams, week: int) -> List[List[Dict[str, int]]]:
    """Calculate win-loss records for each team based on weekly scoring"""
    weekly_records = []
    
    # For each week
    for week_idx in range(week):
        week_scores = []
        # Get all scores for the week
        for team in teams:
            if week_idx < len(team.scores):
                week_scores.append((team.team_id, team.scores[week_idx]))
        
        # Sort scores from highest to lowest
        week_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate records for each team
        week_records = {}
        for rank, (team_id, score) in enumerate(week_scores):
            wins = len(week_scores) - (rank + 1)  # Teams you outscored
            losses = rank  # Teams that outscored you
            week_records[team_id] = {'wins': wins, 'losses': losses}
            
        weekly_records.append(week_records)
    
    return weekly_records

def calculate_power_rankings(league, week: Optional[int] = None) -> List[PowerRankingTeam]:
    """Calculate power rankings based on weekly scoring performance"""
    if not week:
        week = league.current_week

    teams = sorted(league.teams, key=lambda x: x.team_id)
    weekly_records = calculate_weekly_records(teams, week)
    
    power_rankings = []
    for team in teams:
        team_weekly_records = []
        total_wins = 0
        total_losses = 0
        
        # Compile weekly records for this team
        for week_record in weekly_records:
            if team.team_id in week_record:
                record = week_record[team.team_id]
                team_weekly_records.append(record)
                total_wins += record['wins']
                total_losses += record['losses']
            
        # Calculate power score based on total scoring performance
        power_score = total_wins / (total_wins + total_losses) if (total_wins + total_losses) > 0 else 0
        
        power_rankings.append(PowerRankingTeam(
            name=team.team_name,
            team_id=team.team_id,
            ranking=power_score,
            weekly_records=team_weekly_records,
            scores=team.scores[:week],
            actual_record={
                'wins': team.wins,
                'losses': team.losses,
                'ties': team.ties
            },
            total_points=sum(team.scores[:week]),
            total_wins=total_wins,
            total_losses=total_losses
        ))

    return sorted(power_rankings, key=lambda x: x.ranking, reverse=True)

def print_power_rankings_table(rankings: List[PowerRankingTeam], week: int):
    """Print formatted power rankings table"""
    print("\nPower Rankings through Week {}\n".format(week))
    
    # Print header
    header = "{:<4} {:<25} {:<10} {:<15} {:<15} {:<10}".format(
        "Rank", "Team", "Rating", "True Record", "Actual Record", "Points"
    )
    print(header)
    print("-" * 85)
    
    # Print team data
    for i, team in enumerate(rankings, 1):
        print("{:<4} {:<25} {:<10.3f} {:<15} {:<15} {:<10.2f}".format(
            i,
            team.name[:24],
            team.ranking,
            f"{team.total_wins}-{team.total_losses}",
            f"{team.actual_record['wins']}-{team.actual_record['losses']}-{team.actual_record['ties']}",
            team.total_points
        ))
    
    print("\nWeekly Breakdown:\n")
    
    # Print weekly records
    print("{:<25}".format("Team"), end="")
    for w in range(len(rankings[0].weekly_records)):
        print("{:<12}".format(f"Week {w+1}"), end="")
    print()
    print("-" * (25 + 12 * len(rankings[0].weekly_records)))
    
    for team in rankings:
        print("{:<25}".format(team.name[:24]), end="")
        for record in team.weekly_records:
            print("{:<12}".format(f"{record['wins']}-{record['losses']}"), end="")
        print()
    
    print("\nDetailed Breakdown:\n")
    
    # Print detailed stats for each team
    for i, team in enumerate(rankings, 1):
        print(f"{i}. {team.name}")
        print(f"   Power Rating: {team.ranking:.3f}")
        print(f"   Total Points: {team.total_points:.2f}")
        print(f"   Points Per Game: {team.total_points / len(team.scores):.2f}")
        print(f"   True Record: {team.total_wins}-{team.total_losses}")z
        print()

def add_power_rankings_method(League):
    def extended_power_rankings(self, week: Optional[int] = None) -> List[PowerRankingTeam]:
        return calculate_power_rankings(self, week)
    setattr(League, 'extended_power_rankings', extended_power_rankings)

def main():
    # Add extended power rankings to League class
    add_power_rankings_method(League)

    # Create league instance
    league = League(
        league_id=123456,
        year=2021,
    )

    # Get and print power rankings
    rankings = league.extended_power_rankings()
    print_power_rankings_table(rankings, league.current_week)

if __name__ == "__main__":
    main()
