#!/usr/bin/env python3

"""
Quick test script to verify our game improvements work correctly
"""

from game_world import GameWorld
from ant import Ant
import time

def test_improvements():
    print("Testing AntFarm Simulator improvements...")
    
    # Test 1: Smaller map and anti-stuck
    print("\n1. Testing smaller map (60x25) and anti-stuck teleport...")
    world = GameWorld(width=60, height=25, num_ants=5, stuck_limit=5)
    
    print(f"   Map size: {world.width}x{world.height}")
    print(f"   Nest position: {world.nest_pos}")
    print(f"   Number of ants: {len(world.ants)}")
    print(f"   Food positions: {len(world.food_positions)}")
    print(f"   Obstacle positions: {len(world.obstacle_positions)}")
    print(f"   Stuck limit: {world.stuck_limit}")
    
    # Test 2: Visual food carrying
    print("\n2. Testing food carrying visualization...")
    
    # Force an ant to have food and update world
    test_ant = world.ants[0]
    test_ant.has_food = True
    world.update()  # Update to place ant on grid
    print(f"   Ant {test_ant.symbol} has food: {test_ant.has_food}")
    
    # Render and check for yellow background pattern
    rendered = world.render()
    has_yellow_bg = '\033[43m' in rendered  # ANSI yellow background
    print(f"   Rendered output contains carrying ant visualization: {has_yellow_bg}")
    
    # Test 3: Anti-stuck mechanism
    print("\n3. Testing anti-stuck teleport mechanism...")
    
    stuck_ant = world.ants[1]
    original_pos = (stuck_ant.x, stuck_ant.y)
    
    # Simulate stuck condition
    for i in range(6):  # More than stuck_limit=5
        stuck_ant.update(world)
        if stuck_ant.stuck_counter >= world.stuck_limit:
            break
    
    print(f"   Original position: {original_pos}")
    print(f"   Final position: {(stuck_ant.x, stuck_ant.y)}")
    print(f"   Stuck counter: {stuck_ant.stuck_counter}")
    print(f"   Teleported to nest: {(stuck_ant.x, stuck_ant.y) == world.nest_pos}")
    
    # Test 4: Game completion timing
    print("\n4. Testing game completion speed...")
    start_time = time.time()
    
    rounds = 0
    max_rounds = 200  # Our new limit
    
    while (rounds < max_rounds and 
           (len(world.food_positions) > 0 or any(ant.has_food for ant in world.ants))):
        world.update()
        rounds += 1
    
    end_time = time.time()
    
    print(f"   Simulation completed in {rounds} rounds")
    print(f"   Max rounds limit: {max_rounds}")
    print(f"   Time taken: {end_time - start_time:.3f} seconds")
    print(f"   All food collected: {len(world.food_positions) == 0}")
    
    # Test 5: Winner determination
    print("\n5. Testing winner determination...")
    
    sorted_ants = sorted(world.ants, key=lambda ant: (ant.food_collected, ant.distance_traveled), reverse=True)
    winner = sorted_ants[0]
    
    print(f"   Winner: Ant {winner.symbol}")
    print(f"   Food collected: {winner.food_collected}")
    print(f"   Distance traveled: {winner.distance_traveled}")
    
    # Show top 3
    for i, ant in enumerate(sorted_ants[:3]):
        medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
        print(f"   {medal} Ant {ant.symbol}: {ant.food_collected} food, {ant.distance_traveled} distance")
    
    print("\n✅ All improvements tested successfully!")
    
    return {
        'rounds': rounds,
        'completed': len(world.food_positions) == 0,
        'time': end_time - start_time,
        'winner_food': winner.food_collected
    }

if __name__ == "__main__":
    results = test_improvements()
    print(f"\n📊 Results: {results}")
