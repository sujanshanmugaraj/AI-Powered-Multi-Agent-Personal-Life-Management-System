"""
Bandit learning system for adaptive recommendations
"""

import json
import logging
from typing import Dict, List, Any
from collections import defaultdict
import random
import math

logger = logging.getLogger(__name__)

class BanditLearner:
    """Epsilon-greedy bandit learning for action optimization"""
    
    def __init__(self, epsilon: float = 0.1, decay_rate: float = 0.95):
        """
        Initialize bandit learner
        
        Args:
            epsilon: Exploration rate (0-1)
            decay_rate: Decay rate for epsilon over time
        """
        self.epsilon = epsilon
        self.decay_rate = decay_rate
        self.actions = defaultdict(lambda: {"count": 0, "total_reward": 0.0})
        self.iteration = 0
    
    def select_action(self, available_actions: List[str]) -> str:
        """
        Select action using epsilon-greedy strategy
        
        Args:
            available_actions: List of available actions
        
        Returns:
            Selected action name
        """
        
        if random.random() < self.epsilon:
            # Exploration: random action
            return random.choice(available_actions)
        else:
            # Exploitation: best known action
            action_values = {}
            for action in available_actions:
                if self.actions[action]["count"] == 0:
                    action_values[action] = 0
                else:
                    action_values[action] = (
                        self.actions[action]["total_reward"] / 
                        self.actions[action]["count"]
                    )
            
            # Return action with highest average reward
            return max(action_values, key=action_values.get)
    
    def update_reward(self, action: str, reward: float, context: Dict[str, Any] = None):
        """
        Update reward for an action
        
        Args:
            action: Action name
            reward: Reward value (-1 to +1)
            context: Optional context (mood, energy, etc.)
        """
        
        self.actions[action]["count"] += 1
        self.actions[action]["total_reward"] += reward
        
        # Decay epsilon over time (explore less as we learn more)
        self.iteration += 1
        self.epsilon = self.epsilon * self.decay_rate
        
        logger.info(f"Updated action '{action}': count={self.actions[action]['count']}, "
                   f"avg_reward={self.get_avg_reward(action):.3f}, epsilon={self.epsilon:.3f}")
    
    def get_avg_reward(self, action: str) -> float:
        """Get average reward for action"""
        if self.actions[action]["count"] == 0:
            return 0.0
        return self.actions[action]["total_reward"] / self.actions[action]["count"]
    
    def get_action_stats(self) -> Dict[str, Dict]:
        """Get statistics for all actions"""
        stats = {}
        for action, data in self.actions.items():
            stats[action] = {
                "count": data["count"],
                "total_reward": data["total_reward"],
                "avg_reward": self.get_avg_reward(action)
            }
        return stats
    
    def get_top_actions(self, n: int = 5) -> List[tuple]:
        """Get top N actions by average reward"""
        action_rewards = [
            (action, self.get_avg_reward(action))
            for action in self.actions.keys()
        ]
        return sorted(action_rewards, key=lambda x: x[1], reverse=True)[:n]


class RewardCalculator:
    """Calculate rewards from user feedback"""
    
    @staticmethod
    def calculate_reward(feedback: Dict[str, Any]) -> float:
        """
        Calculate reward from feedback
        
        Args:
            feedback: Feedback dict with rating, completion, mood change
        
        Returns:
            Reward value (-1 to +1)
        """
        
        reward = 0.0
        
        # Base reward from rating
        rating = feedback.get("rating", "neutral")
        if rating == "up":
            reward += 1.0
        elif rating == "down":
            reward -= 1.0
        # neutral = 0
        
        # Completion bonus
        completed_count = len(feedback.get("completed_tasks", []))
        total_tasks = feedback.get("total_tasks", 1)
        completion_rate = completed_count / total_tasks if total_tasks > 0 else 0
        reward += completion_rate * 0.5
        
        # Mood improvement bonus
        mood_delta = feedback.get("mood_after", 0.5) - feedback.get("mood_before", 0.5)
        reward += mood_delta * 0.5
        
        # Clamp reward to [-1, +1]
        return max(-1.0, min(1.0, reward))
    
    @staticmethod
    def calculate_action_rewards(feedback: Dict[str, Any], 
                                actions_in_plan: List[str]) -> Dict[str, float]:
        """
        Distribute reward across multiple actions in a plan
        
        Args:
            feedback: Feedback dict
            actions_in_plan: List of action names in the plan
        
        Returns:
            Dict mapping actions to individual rewards
        """
        
        base_reward = RewardCalculator.calculate_reward(feedback)
        
        # Distribute reward equally among actions
        action_rewards = {}
        reward_per_action = base_reward / len(actions_in_plan) if actions_in_plan else 0
        
        for action in actions_in_plan:
            action_rewards[action] = reward_per_action
        
        return action_rewards


class AdaptiveRecommender:
    """Use bandit learning to adapt recommendations"""
    
    def __init__(self, bandit_learner: BanditLearner):
        self.bandit = bandit_learner
    
    def get_recommended_activity(self, domain: str, mood: str, 
                                energy: str) -> str:
        """
        Get recommended activity based on learned preferences
        
        Args:
            domain: Domain (health, learning, finance)
            mood: Current mood
            energy: Current energy level
        
        Returns:
            Recommended activity
        """
        
        # Generate list of possible actions for this domain/mood/energy
        available_actions = self._get_available_actions(domain, mood, energy)
        
        if not available_actions:
            return "default_activity"
        
        # Use bandit to select best action
        return self.bandit.select_action(available_actions)
    
    def _get_available_actions(self, domain: str, mood: str, energy: str) -> List[str]:
        """Get available actions for domain/mood/energy combination"""
        
        # Health domain
        if domain == "health":
            if mood in ["stressed", "anxious"] and energy == "low":
                return ["light_walk", "yoga", "meditation", "stretching"]
            elif energy == "high":
                return ["gym", "running", "sports", "intense_workout"]
            else:
                return ["regular_workout", "walk", "yoga", "stretching"]
        
        # Learning domain
        elif domain == "learning":
            if mood == "stressed":
                return ["short_review", "flashcards", "light_reading"]
            elif energy == "high":
                return ["deep_study", "problem_solving", "project_work"]
            else:
                return ["regular_study", "video_learning", "notes_review"]
        
        # Finance domain
        elif domain == "finance":
            if mood in ["stressed", "anxious"]:
                return ["quick_check", "defer_review"]
            else:
                return ["quick_check", "detailed_review", "budget_planning"]
        
        else:
            return ["default_activity"]
    
    def record_feedback(self, plan_actions: Dict[str, str], 
                       feedback: Dict[str, Any]):
        """
        Record feedback and update bandit learning
        
        Args:
            plan_actions: Dict of domain -> selected action
            feedback: Feedback from user
        """
        
        # Calculate overall reward
        reward = RewardCalculator.calculate_reward(feedback)
        
        # Update bandit for each action in the plan
        for domain, action in plan_actions.items():
            # Weight reward slightly based on domain importance
            weighted_reward = reward
            
            # Higher weight for primary domain
            if domain == feedback.get("primary_concern"):
                weighted_reward *= 1.2
            
            self.bandit.update_reward(
                action=f"{domain}:{action}",
                reward=weighted_reward,
                context={
                    "mood": feedback.get("mood"),
                    "energy": feedback.get("energy"),
                    "timestamp": feedback.get("timestamp")
                }
            )
