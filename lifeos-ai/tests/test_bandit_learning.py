"""
Unit tests for Bandit Learning
"""

import pytest
from app.learning.bandit_learning import BanditLearner, RewardCalculator

@pytest.fixture
def bandit():
    """Create bandit learner instance"""
    return BanditLearner(epsilon=0.2, decay_rate=0.95)

def test_bandit_initialization():
    """Test bandit learner initialization"""
    bandit = BanditLearner(epsilon=0.1, decay_rate=0.95)
    
    assert bandit.epsilon == 0.1
    assert bandit.decay_rate == 0.95
    assert len(bandit.actions) == 0

def test_select_action_exploration(bandit):
    """Test action selection with exploration"""
    actions = ["walk", "gym", "yoga"]
    
    # With epsilon=0.2, some selections should be random
    selections = [bandit.select_action(actions) for _ in range(100)]
    
    # Should have diversity in selections
    assert len(set(selections)) > 1

def test_update_reward(bandit):
    """Test reward update"""
    action = "walk"
    reward = 0.5
    
    bandit.update_reward(action, reward)
    
    assert bandit.actions[action]["count"] == 1
    assert bandit.actions[action]["total_reward"] == 0.5

def test_get_avg_reward(bandit):
    """Test average reward calculation"""
    action = "gym"
    
    bandit.update_reward(action, 0.8)
    bandit.update_reward(action, 0.6)
    bandit.update_reward(action, 0.4)
    
    avg_reward = bandit.get_avg_reward(action)
    
    assert abs(avg_reward - 0.6) < 0.01

def test_epsilon_decay(bandit):
    """Test epsilon decay over time"""
    initial_epsilon = bandit.epsilon
    
    for _ in range(10):
        bandit.update_reward("action", 0.5)
    
    assert bandit.epsilon < initial_epsilon

def test_get_action_stats(bandit):
    """Test action statistics"""
    bandit.update_reward("walk", 0.8)
    bandit.update_reward("walk", 0.6)
    bandit.update_reward("gym", 0.9)
    
    stats = bandit.get_action_stats()
    
    assert "walk" in stats
    assert "gym" in stats
    assert stats["walk"]["count"] == 2
    assert stats["gym"]["count"] == 1

def test_get_top_actions(bandit):
    """Test getting top actions"""
    bandit.update_reward("walk", 0.5)
    bandit.update_reward("gym", 0.9)
    bandit.update_reward("yoga", 0.7)
    
    top_actions = bandit.get_top_actions(n=2)
    
    assert len(top_actions) == 2
    assert top_actions[0][0] == "gym"  # Highest reward
    assert top_actions[1][0] == "yoga"

def test_reward_calculator_positive_feedback():
    """Test reward calculation for positive feedback"""
    feedback = {
        "rating": "up",
        "completed_tasks": ["task1", "task2"],
        "total_tasks": 2,
        "mood_before": 0.4,
        "mood_after": 0.7
    }
    
    reward = RewardCalculator.calculate_reward(feedback)
    
    # Should be positive due to up rating + completion + mood improvement
    assert reward > 0

def test_reward_calculator_negative_feedback():
    """Test reward calculation for negative feedback"""
    feedback = {
        "rating": "down",
        "completed_tasks": [],
        "total_tasks": 2,
        "mood_before": 0.6,
        "mood_after": 0.3
    }
    
    reward = RewardCalculator.calculate_reward(feedback)
    
    # Should be negative
    assert reward < 0

def test_reward_calculator_neutral_feedback():
    """Test reward calculation for neutral feedback"""
    feedback = {
        "rating": "neutral",
        "completed_tasks": ["task1"],
        "total_tasks": 2,
        "mood_before": 0.5,
        "mood_after": 0.5
    }
    
    reward = RewardCalculator.calculate_reward(feedback)
    
    # Should be near 0.25 (partial completion, neutral mood)
    assert -1 <= reward <= 1

def test_calculate_action_rewards():
    """Test reward distribution across actions"""
    feedback = {
        "rating": "up",
        "completed_tasks": ["all"],
        "total_tasks": 1,
        "mood_before": 0.4,
        "mood_after": 0.7
    }
    
    actions = ["action1", "action2", "action3"]
    action_rewards = RewardCalculator.calculate_action_rewards(feedback, actions)
    
    assert len(action_rewards) == 3
    # Each action should get 1/3 of the total reward
    for action in actions:
        assert action in action_rewards
        assert action_rewards[action] > 0
