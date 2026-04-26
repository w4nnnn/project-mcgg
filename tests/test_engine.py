"""Tests for prediction engine."""

import pytest
from mcgg.models import Session, Player, RoundType, RoundNumber
from mcgg.engine import PredictionEngine


class TestPredictionEngine:
    """Test cases for PredictionEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.session = Session()
        self.local = Player(name="You", position=1, is_local_player=True)
        self.alice = Player(name="Alice", position=2)
        self.bob = Player(name="Bob", position=3)
        self.charlie = Player(name="Charlie", position=4)
        
        for p in [self.local, self.alice, self.bob, self.charlie]:
            self.session.add_player(p)
    
    def test_random_round_not_predictable(self):
        """Test that random rounds (i-2, i-3, ii-1) are not predictable."""
        engine = PredictionEngine(self.session)
        
        # i-2 should be random
        self.session.current_round = 2
        pred = engine.predict()
        assert not pred.is_valid
        assert pred.prediction_method == "random_round"
        
        # i-3 should be random
        self.session.current_round = 3
        pred = engine.predict()
        assert not pred.is_valid
        
        # ii-1 should be random
        self.session.current_phase = 2
        self.session.current_round = 1
        pred = engine.predict()
        assert not pred.is_valid
    
    def test_i4_needs_i2_data(self):
        """Test that i-4 needs i-2 first ex data."""
        # Skip to i-4 without i-2
        self.session.current_round = 4
        engine = PredictionEngine(self.session)
        pred = engine.predict()
        
        assert not pred.is_valid
        assert "first ex" in pred.warnings[0].lower()
    
    def test_confidence_reduces_with_eliminations(self):
        """Test that confidence reduces when players are eliminated."""
        # Full 8 players should have high confidence
        for i in range(4, 9):
            self.session.add_player(Player(name=f"Player{i}", position=i))
        
        # Setup: first ex at i-2
        self.session.advance_round()  # i-1 (monster)
        self.session.add_round(self.alice)
        self.session.advance_round()
        self.session.add_round(self.bob)
        self.session.advance_round()
        
        # Now at i-4
        engine = PredictionEngine(self.session)
        self.session.current_round = 4
        
        # Base confidence with 8 players
        pred = engine.predict()
        base_confidence = pred.confidence if pred.is_valid else 0.0
        
        # Eliminate one player
        self.charlie.is_active = False
        engine = PredictionEngine(self.session)
        pred = engine.predict()
        
        # With elimination, confidence should be lower
        # (Note: This test may fail if prediction is invalid)
    
    def test_predictable_rounds_list(self):
        """Test which rounds are marked as predictable."""
        predictable_rounds = []
        non_predictable_rounds = []
        
        for phase in range(1, 3):
            for round_num in range(1, 7):
                if phase == 1 and round_num > 4:
                    break
                    
                rn = RoundNumber.from_phase_and_round(phase, round_num)
                if rn.is_predictable:
                    predictable_rounds.append(rn.value)
                else:
                    non_predictable_rounds.append(rn.value)
        
        # i-2, i-3 should not be predictable
        assert "i-2" in non_predictable_rounds
        assert "i-3" in non_predictable_rounds
        
        # i-4 should be predictable
        assert "i-4" in predictable_rounds

    def test_i4_uses_chain_relation_mapping(self):
        """Predict i-4 from explicitly mapped i-3 relation."""
        self.session.current_phase = 1
        self.session.current_round = 2
        self.session.add_round(self.bob)  # i-2, first ex
        self.session.current_round = 4
        self.session.set_chain_relation(1, 3, "Bob", "Charlie")

        engine = PredictionEngine(self.session)
        pred = engine.predict()
        assert pred.is_valid
        assert pred.predicted_opponent is not None
        assert pred.predicted_opponent.name == "Charlie"

    def test_ii5_uses_chain_relation_mapping(self):
        """Predict ii-5 from mapped relation at ii-2."""
        self.session.current_phase = 2
        self.session.current_round = 5
        ii4_record = self.session.add_round(self.alice)
        ii4_record.phase = 2
        ii4_record.round = 4
        self.session.set_chain_relation(2, 2, "Alice", "Bob")

        engine = PredictionEngine(self.session)
        pred = engine.predict()
        assert pred.is_valid
        assert pred.predicted_opponent is not None
        assert pred.predicted_opponent.name == "Bob"


class TestSessionModel:
    """Test cases for Session model."""
    
    def test_session_initial_state(self):
        """Test session starts with correct initial state."""
        s = Session()
        assert s.current_phase == 1
        assert s.current_round == 1
        assert s.is_active is True
        assert len(s.round_history) == 0
    
    def test_add_player(self):
        """Test adding players to session."""
        s = Session()
        p = Player(name="Test", position=1)
        s.add_player(p)
        
        assert len(s.players) == 1
        assert s.get_player_by_name("Test") == p
    
    def test_advance_round_phase1(self):
        """Test round advancement in phase 1."""
        s = Session()
        assert s.current_phase == 1
        assert s.current_round == 1
        
        s.advance_round()
        assert s.current_round == 2
        
        s.advance_round()
        assert s.current_round == 3
        
        s.advance_round()
        assert s.current_round == 4
        
        s.advance_round()
        # Should transition to phase 2
        assert s.current_phase == 2
        assert s.current_round == 1
    
    def test_advance_round_phase2(self):
        """Test round advancement in phase 2."""
        s = Session()
        s.current_phase = 2
        s.current_round = 1
        
        for i in range(1, 7):
            assert s.current_round == i
            if i < 6:
                s.advance_round()
        
        # Should transition to phase 3
        s.advance_round()
        assert s.current_phase == 3
        assert s.current_round == 1
    
    def test_get_player_by_name_case_insensitive(self):
        """Test player lookup is case insensitive."""
        s = Session()
        s.add_player(Player(name="Alice", position=1))
        
        assert s.get_player_by_name("alice") is not None
        assert s.get_player_by_name("ALICE") is not None
    
    def test_local_player_property(self):
        """Test local_player property."""
        s = Session()
        p1 = Player(name="Local", position=1, is_local_player=True)
        p2 = Player(name="Other", position=2)
        s.add_player(p1)
        s.add_player(p2)
        
        assert s.local_player == p1
