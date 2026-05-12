"""
Unit tests for Mood Agent
"""

import pytest
from app.agents.mood_agent import MoodAgent

@pytest.fixture
def mood_agent():
    """Create mood agent instance"""
    return MoodAgent()

@pytest.mark.asyncio
async def test_mood_detection_stressed(mood_agent):
    """Test mood detection for stressed state"""
    state = {
        "user_id": 1,
        "user_text": "I feel very stressed and overwhelmed",
    }
    
    proposal = await mood_agent.generate_proposal(state)
    
    assert proposal["agent"] == "mood"
    assert proposal["mood"] == "stressed"
    assert proposal["stress_score"] > 0.7
    assert proposal["energy_score"] < 0.6
    assert proposal["confidence"] > 0.5

@pytest.mark.asyncio
async def test_mood_detection_energetic(mood_agent):
    """Test mood detection for energetic state"""
    state = {
        "user_id": 1,
        "user_text": "I feel energized and excited today",
    }
    
    proposal = await mood_agent.generate_proposal(state)
    
    assert proposal["agent"] == "mood"
    assert proposal["mood"] == "energetic"
    assert proposal["stress_score"] < 0.4
    assert proposal["energy_score"] > 0.7

@pytest.mark.asyncio
async def test_mood_detection_tired(mood_agent):
    """Test mood detection for tired state"""
    state = {
        "user_id": 1,
        "user_text": "I'm very tired and exhausted",
    }
    
    proposal = await mood_agent.generate_proposal(state)
    
    assert proposal["agent"] == "mood"
    assert proposal["mood"] == "tired"
    assert proposal["energy_score"] < 0.4

@pytest.mark.asyncio
async def test_mood_neutral_fallback(mood_agent):
    """Test neutral mood as fallback"""
    state = {
        "user_id": 1,
        "user_text": "Just regular day",
    }
    
    proposal = await mood_agent.generate_proposal(state)
    
    assert proposal["agent"] == "mood"
    assert "stress_score" in proposal
    assert "energy_score" in proposal
    assert proposal["confidence"] > 0

@pytest.mark.asyncio
async def test_proposal_format(mood_agent):
    """Test proposal format correctness"""
    state = {
        "user_id": 1,
        "user_text": "Test text",
    }
    
    proposal = await mood_agent.generate_proposal(state)
    
    required_fields = ["agent", "proposal", "priority", "confidence", "reasoning"]
    for field in required_fields:
        assert field in proposal
    
    assert 0 <= proposal["priority"] <= 1
    assert 0 <= proposal["confidence"] <= 1
    assert 0 <= proposal["stress_score"] <= 1
    assert 0 <= proposal["energy_score"] <= 1
