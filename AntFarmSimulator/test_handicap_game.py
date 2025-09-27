#!/usr/bin/env python3
"""
Test the complete handicap system with a simulated game
"""

from game_world import GameWorld
from player_history import PlayerHistory, HandicapScoring
from ant import Ant
import json

def simulate_handicap_game():
    """Simulate a game with players having different handicap levels"""
    
    print("🎯 HANDICAP SYSTEM FULL GAME TEST")
    print("=" * 60)
    
    # Create player history and set up different player types
    history = PlayerHistory("handicap_test_history.json")
    
    # Define test players with different win histories
    test_players = [
        {"name": "Champion_Bob", "wins": 15, "games": 20, "handicap_tier": "Champion"},
        {"name": "Veteran_Sue", "wins": 12, "games": 20, "handicap_tier": "Veteran"}, 
        {"name": "Contender_Max", "wins": 8, "games": 20, "handicap_tier": "Contender"},
        {"name": "Underdog_Amy", "wins": 4, "games": 20, "handicap_tier": "Underdog"},
        {"name": "Rookie_Tim", "wins": 1, "games": 20, "handicap_tier": "Rookie"}
    ]
    
    # Set up player histories
    for player in test_players:
        # Clear any existing history
        if player["name"] in history.players:
            del history.players[player["name"]]
        
        # Simulate game history
        for i in range(player["games"]):
            won = i < player["wins"]
            score = 4 + (2 if won else -1)  # Winners get better scores
            history.record_game(player["name"], won, score)
        
        # Calculate handicap
        player["handicap"] = history.calculate_handicap(player["name"])
        player["display_name"] = history.format_player_display(player["name"])
    
    print("Player Setup:")
    print("-" * 40)
    for player in test_players:
        stats = history.get_player_stats(player["name"])
        bonuses = HandicapScoring.get_handicap_summary(player["name"], player["handicap"])
        print(f"{player['display_name']}")
        print(f"  Record: {stats['total_wins']}/{stats['total_games']} ({stats['win_rate']:.0%})")
        print(f"  Handicap: {player['handicap']:.0%}")
        print(f"  Bonuses: {bonuses}")
        print()
    
    # Create a game world
    world = GameWorld(width=70, height=25, num_ants=len(test_players), stuck_limit=5)
    
    # Replace default ants with handicapped ants
    world.ants = []
    for i, player in enumerate(test_players):
        start_pos = world.starting_positions[i % len(world.starting_positions)]
        handicapped_ant = Ant(chr(65 + i), start_pos[0], start_pos[1], player["handicap"])
        handicapped_ant.player_name = player["name"]  # Track player name
        world.ants.append(handicapped_ant)
    
    print("🎮 SIMULATED GAME RESULTS")
    print("-" * 40)
    
    # Run a quick simulation
    rounds = 0
    max_rounds = 150
    
    while rounds < max_rounds and (len(world.food_positions) > 0 or len(world.premium_food_positions) > 0 or any(ant.has_food for ant in world.ants)):
        rounds += 1
        world.update()
        
        # Show progress every 30 rounds
        if rounds % 30 == 0:
            food_left = len(world.food_positions) + len(world.premium_food_positions)
            print(f"Round {rounds}: {food_left} food remaining")
    
    print(f"\nGame completed in {rounds} rounds")
    
    # Sort ants by final score (with handicap bonuses applied)
    sorted_ants = sorted(world.ants, key=lambda ant: (ant.food_collected, ant.distance_traveled), reverse=True)
    
    print("\n🏆 FINAL RESULTS (With Handicap Bonuses):")
    print("-" * 50)
    
    for i, ant in enumerate(sorted_ants):
        player_name = getattr(ant, 'player_name', f'Player_{ant.symbol}')
        player_info = next(p for p in test_players if p['name'] == player_name)
        
        # Show both base score and handicapped score
        base_score = getattr(ant, 'base_food_collected', ant.food_collected)
        handicap_score = ant.food_collected
        bonus = handicap_score - base_score
        
        medal = ["🥇", "🥈", "🥉", "4th", "5th"][i]
        
        print(f"{medal} {player_info['display_name']}")
        print(f"     Score: {handicap_score} points (base: {base_score}, bonus: +{bonus})")
        print(f"     Distance: {ant.distance_traveled}")
        print()
    
    # Analyze results
    print("📊 HANDICAP SYSTEM ANALYSIS:")
    print("-" * 40)
    
    # Check if underdogs performed better
    champion_score = next(ant.food_collected for ant in sorted_ants if getattr(ant, 'player_name', '') == 'Champion_Bob')
    rookie_score = next(ant.food_collected for ant in sorted_ants if getattr(ant, 'player_name', '') == 'Rookie_Tim')
    underdog_score = next(ant.food_collected for ant in sorted_ants if getattr(ant, 'player_name', '') == 'Underdog_Amy')
    
    print(f"Champion final score: {champion_score}")
    print(f"Rookie final score: {rookie_score}")  
    print(f"Underdog final score: {underdog_score}")
    
    score_gap = max(ant.food_collected for ant in sorted_ants) - min(ant.food_collected for ant in sorted_ants)
    print(f"Score gap: {score_gap} points (lower = more balanced)")
    
    # Count how many underdogs (handicap > 0.4) placed in top 3
    top3_underdogs = sum(1 for ant in sorted_ants[:3] 
                        if next(p for p in test_players if p['name'] == getattr(ant, 'player_name', ''))['handicap'] > 0.4)
    
    print(f"Underdogs in top 3: {top3_underdogs}/3")
    
    if top3_underdogs > 0:
        print("✅ Handicap system helping underdogs compete!")
    else:
        print("⚖️  Veterans still dominating - may need stronger handicaps")
    
    print(f"\n✅ Handicap system test complete!")
    
    return sorted_ants, test_players

if __name__ == "__main__":
    simulate_handicap_game()
