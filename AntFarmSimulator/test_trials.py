
import sys
from game_world import GameWorld
import time

def run_trial(trial_num, width=50, height=20, num_ants=15):
    print(f"\rRunning trial {trial_num}/100...", end="", flush=True)
    
    # Initialize game
    world = GameWorld(width=width, height=height, num_ants=num_ants, stuck_limit=10)
    
    # Run simulation until completion or timeout
    round_num = 1
    max_rounds = 300
    
    while round_num <= max_rounds and (len(world.food_positions) > 0 or len(world.premium_food_positions) > 0 or any(ant.has_food for ant in world.ants)):
        world.update()
        round_num += 1
    
    # Collect results
    winner = max(world.ants, key=lambda ant: (ant.food_collected, -ant.distance_traveled))
    completed = (len(world.food_positions) == 0 and len(world.premium_food_positions) == 0 
                and not any(ant.has_food for ant in world.ants))
    
    # Check for ties
    top_food = winner.food_collected
    tied_count = sum(1 for ant in world.ants if ant.food_collected == top_food)
    
    return {
        'completed': completed,
        'rounds': round_num,
        'winner_food': winner.food_collected,
        'winner_distance': winner.distance_traveled,
        'tied_count': tied_count
    }

def main():
    num_trials = 100
    results = []
    start_time = time.time()
    
    for i in range(num_trials):
        result = run_trial(i + 1)
        results.append(result)
    
    # Calculate statistics
    completed_trials = sum(1 for r in results if r['completed'])
    avg_rounds = sum(r['rounds'] for r in results) / num_trials
    avg_winner_food = sum(r['winner_food'] for r in results) / num_trials
    tied_games = sum(1 for r in results if r['tied_count'] > 1)
    total_time = time.time() - start_time
    
    # Print results
    print("\n\nTest Results:")
    print(f"Total trials: {num_trials}")
    print(f"Completed trials: {completed_trials}")
    print(f"Games with ties: {tied_games} ({tied_games/num_trials*100:.1f}%)")
    print(f"Average rounds per trial: {avg_rounds:.2f}")
    print(f"Average winner food collected: {avg_winner_food:.2f}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per trial: {total_time/num_trials:.2f} seconds")

if __name__ == "__main__":
    main()
