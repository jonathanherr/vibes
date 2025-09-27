#!/usr/bin/env python3
"""
Player History and Handicap System for AntFarm Simulator
Tracks win/loss records and calculates fair handicaps for balanced competition
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class PlayerHistory:
    """Manages player win/loss history and handicap calculations"""
    
    def __init__(self, data_file="player_history.json"):
        self.data_file = data_file
        self.players = self._load_data()
        
    def _load_data(self) -> Dict:
        """Load player history from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def _save_data(self):
        """Save player history to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.players, f, indent=2, default=str)
        except IOError:
            print(f"Warning: Could not save player history to {self.data_file}")
    
    def add_player(self, player_name: str):
        """Initialize a new player's history"""
        if player_name not in self.players:
            self.players[player_name] = {
                "total_wins": 0,
                "total_games": 0,
                "last_won_date": None,
                "created_date": datetime.now().isoformat(),
                "recent_scores": []  # Track last 10 scores for analysis
            }
            self._save_data()
    
    def record_game(self, player_name: str, won: bool, score: int):
        """Record the result of a game for a player"""
        self.add_player(player_name)
        
        player = self.players[player_name]
        player["total_games"] += 1
        
        if won:
            player["total_wins"] += 1
            player["last_won_date"] = datetime.now().isoformat()
        
        # Track recent scores (keep last 10)
        player["recent_scores"].append({
            "score": score,
            "won": won,
            "date": datetime.now().isoformat()
        })
        if len(player["recent_scores"]) > 10:
            player["recent_scores"] = player["recent_scores"][-10:]
        
        self._save_data()
    
    def get_player_stats(self, player_name: str) -> Dict:
        """Get comprehensive stats for a player"""
        self.add_player(player_name)
        player = self.players[player_name]
        
        # Calculate days since last win
        days_since_win = 0
        if player["last_won_date"]:
            last_win = datetime.fromisoformat(player["last_won_date"])
            days_since_win = (datetime.now() - last_win).days
        else:
            # Never won - use days since creation
            created = datetime.fromisoformat(player["created_date"])
            days_since_win = (datetime.now() - created).days
        
        # Calculate win rate
        win_rate = player["total_wins"] / max(player["total_games"], 1)
        
        return {
            "total_wins": player["total_wins"],
            "total_games": player["total_games"],
            "win_rate": win_rate,
            "days_since_last_win": days_since_win,
            "last_won_date": player["last_won_date"],
            "recent_scores": player["recent_scores"]
        }
    
    def calculate_handicap(self, player_name: str) -> float:
        """Calculate handicap value (0.0 = no handicap, 1.0 = maximum)"""
        stats = self.get_player_stats(player_name)
        
        # Win ratio factor (0.0 = no wins, 1.0 = always wins)
        win_ratio = stats["win_rate"]
        win_disadvantage = 1.0 - win_ratio  # Higher for fewer wins
        
        # Time factor (more days = more handicap)
        max_days = 365  # Cap at 1 year
        time_factor = min(stats["days_since_last_win"], max_days) / max_days
        
        # Combined handicap (60% win history, 40% time since win)
        handicap = (win_disadvantage * 0.6) + (time_factor * 0.4)
        
        # Cap at 95% to prevent overpowering
        return min(handicap, 0.95)
    
    def get_handicap_tier(self, handicap: float) -> Dict:
        """Get display tier information for handicap level"""
        tiers = [
            (0.0, 0.2, {"name": "Champion", "icon": "👑", "color": "gold"}),
            (0.2, 0.4, {"name": "Veteran", "icon": "⭐", "color": "silver"}), 
            (0.4, 0.6, {"name": "Contender", "icon": "🔥", "color": "orange"}),
            (0.6, 0.8, {"name": "Underdog", "icon": "🎯", "color": "green"}),
            (0.8, 1.0, {"name": "Rookie", "icon": "🌟", "color": "blue"})
        ]
        
        for min_h, max_h, tier_info in tiers:
            if min_h <= handicap < max_h:
                return tier_info
        
        # Fallback for exactly 1.0
        return tiers[-1][2]
    
    def format_player_display(self, player_name: str) -> str:
        """Format player name with handicap tier for display"""
        handicap = self.calculate_handicap(player_name)
        tier = self.get_handicap_tier(handicap)
        return f"{tier['icon']} {player_name} {tier['name']}"
    
    def get_all_players_summary(self) -> Dict:
        """Get summary of all players for leaderboard display"""
        summary = {}
        for player_name in self.players:
            stats = self.get_player_stats(player_name)
            handicap = self.calculate_handicap(player_name)
            tier = self.get_handicap_tier(handicap)
            
            summary[player_name] = {
                "stats": stats,
                "handicap": handicap,
                "tier": tier,
                "display_name": self.format_player_display(player_name)
            }
        
        return summary


class HandicapScoring:
    """Applies handicap-based scoring bonuses"""
    
    @staticmethod
    def apply_food_bonus(base_points: int, handicap: float) -> int:
        """Apply scoring bonus based on handicap (0-50% bonus)"""
        bonus_multiplier = 1.0 + (handicap * 0.5)
        return max(int(base_points * bonus_multiplier + 0.5), base_points)  # Round up, ensure at least base
    
    @staticmethod  
    def apply_distance_tiebreaker_bonus(distance: int, handicap: float) -> int:
        """Apply distance bonus for tiebreaker advantage (0-30% bonus)"""
        return int(distance * (1.0 + handicap * 0.3))
    
    @staticmethod
    def apply_premium_food_attraction(handicap: float) -> float:
        """Calculate premium food attraction bonus (0-100% better chance)"""
        return handicap  # 0-100% bonus chance to target premium food
    
    @staticmethod
    def get_handicap_summary(player_name: str, handicap: float) -> str:
        """Get human-readable summary of active handicaps"""
        if handicap < 0.1:
            return "No handicap bonuses"
        
        bonuses = []
        if handicap > 0.2:
            food_bonus = int(handicap * 50)
            bonuses.append(f"+{food_bonus}% food scoring")
        
        if handicap > 0.3:
            distance_bonus = int(handicap * 30)
            bonuses.append(f"+{distance_bonus}% tiebreaker")
            
        if handicap > 0.4:
            premium_bonus = int(handicap * 100)
            bonuses.append(f"+{premium_bonus}% premium attraction")
        
        return ", ".join(bonuses)


# Example usage and testing
if __name__ == "__main__":
    # Create test history
    history = PlayerHistory("test_history.json")
    
    # Add some test players with different win patterns
    test_players = [
        ("Alice", 0, 5),      # New player, no wins
        ("Bob", 8, 10),       # Veteran, high win rate
        ("Charlie", 2, 8),    # Struggling player
        ("Diana", 4, 6),      # Moderate player
    ]
    
    print("🎯 HANDICAP SYSTEM TEST")
    print("=" * 50)
    
    for name, wins, games in test_players:
        # Simulate game history
        for i in range(games):
            won = i < wins
            score = 3 + (2 if won else 0)  # Winners get better scores
            history.record_game(name, won, score)
        
        # Show handicap calculation
        stats = history.get_player_stats(name)
        handicap = history.calculate_handicap(name)
        display_name = history.format_player_display(name)
        bonus_summary = HandicapScoring.get_handicap_summary(name, handicap)
        
        print(f"\n{display_name}")
        print(f"  Record: {stats['total_wins']}/{stats['total_games']} ({stats['win_rate']:.1%})")
        print(f"  Handicap: {handicap:.1%}")
        print(f"  Bonuses: {bonus_summary}")
        
        # Show scoring examples
        base_score = 3
        handicap_score = HandicapScoring.apply_food_bonus(base_score, handicap)
        print(f"  Score boost: {base_score} → {handicap_score} points")
    
    print(f"\n✅ Test complete! Data saved to test_history.json")
