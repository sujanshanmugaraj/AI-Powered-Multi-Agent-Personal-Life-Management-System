"""
Unit tests for Health Agent
"""

import pytest
from app.agents.health_agent import HealthAgent

@pytest.fixture
def health_agent():
    """Create health agent instance"""
    return HealthAgent()

@pytest.mark.asyncio
async def test_health_recommendation_stressed_low_energy(health_agent):
    """Test health recommendation for stressed, low energy state"""
    state = {
        "user_id": 1,
        "mood_data": {
            "mood": "stressed",
            "stress_score": 0.8,
            "energy_score": 0.3
        }
    }
    
    proposal = await health_agent.generate_proposal(state)
    
    assert proposal["agent"] == "health"
    assert proposal["intensity"] == "low"
    assert proposal["duration"] <= 20
    assert proposal["priority"] > 0.6

@pytest.mark.asyncio
async def test_health_recommendation_energetic_high_energy(health_agent):
    """Test health recommendation for energetic, high energy state"""
    state = {
        "user_id": 1,
        "mood_data": {
            "mood": "energetic",
            "stress_score": 0.2,
            "energy_score": 0.9
        }
    }
    
    proposal = await health_agent.generate_proposal(state)
    
    assert proposal["agent"] == "health"
    assert proposal["intensity"] == "high"
    assert proposal["duration"] >= 45
    assert proposal["priority"] > 0.8

@pytest.mark.asyncio
async def test_health_recommendation_neutral(health_agent):
    """Test health recommendation for neutral state"""
    state = {
        "user_id": 1,
        "mood_data": {
            "mood": "neutral",
            "stress_score": 0.5,
            "energy_score": 0.5
        }
    }
    
    proposal = await health_agent.generate_proposal(state)
    
    assert proposal["agent"] == "health"
    assert "proposal" in proposal
    assert proposal["priority"] > 0
    assert proposal["duration"] > 0

@pytest.mark.asyncio
async def test_health_proposal_format(health_agent):
    """Test proposal format correctness"""
    state = {
        "user_id": 1,
        "mood_data": {"mood": "neutral", "stress_score": 0.5, "energy_score": 0.5}
    }
    
    proposal = await health_agent.generate_proposal(state)
    
    required_fields = ["agent", "proposal", "priority", "confidence", "intensity", "duration"]
    for field in required_fields:
        assert field in proposal
    
    assert proposal["agent"] == "health"
    assert proposal["intensity"] in ["very_low", "low", "medium", "high"]
