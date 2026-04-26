"""Prediction engine for MCGG opponent prediction."""

from dataclasses import dataclass
from typing import Optional
from mcgg.models import Session, Player, RoundRecord, Prediction, RoundNumber

# Total players in MCGG
TOTAL_PLAYERS = 8


@dataclass
class PredictionEngine:
    """Engine for predicting opponents based on MCGG matchmaking rules.
    
    The MCGG matchmaking system uses a chain-based prediction where:
    - Rounds i-2, i-3, ii-1 are RANDOM (cannot predict)
    - Round i-4: opponent = opponent of your "first ex" at round i-3
    - Round ii-2: opponent = opponent of your "first ex" at round ii-1  
    - Round ii-4: opponent = opponent of your ii-2 opponent at round i-4
    - Round ii-5: opponent = opponent of your ii-4 opponent at round ii-2
    - Round ii-6: opponent = opponent of your ii-5 opponent at round ii-3
    
    "First ex" (mantan pertama) = opponent at the first random player round:
    - Phase 1: round i-2
    - Phase 2+: round ii-1
    """
    
    session: Session
    max_players: int = TOTAL_PLAYERS
    
    def predict(self) -> Prediction:
        """Predict opponent for current round."""
        current = self.session.current_round_number
        
        if not current.is_predictable:
            return Prediction(
                predicted_opponent=None,
                confidence=0.0,
                prediction_method="random_round",
                is_valid=False,
                warnings=["This is a random round - cannot predict"]
            )
        
        phase = self.session.current_phase
        round_num = self.session.current_round
        
        # Determine prediction based on round
        if phase == 1 and round_num == 4:
            return self._predict_i4()
        if phase >= 2 and round_num == 2:
            return self._predict_ii2()
        if phase >= 2 and round_num == 4:
            return self._predict_ii4()
        if phase >= 2 and round_num == 5:
            return self._predict_ii5()
        if phase >= 2 and round_num == 6:
            return self._predict_ii6()
        
        return Prediction(
            predicted_opponent=None,
            confidence=0.0,
            prediction_method="no_rule",
            is_valid=False,
            warnings=["No prediction rule defined for this round"]
        )
    
    def _predict_i4(self) -> Prediction:
        """Predict round i-4.
        
        Rule: Your opponent at i-4 is the opponent that your "first ex" 
        (opponent at i-2) faced at round i-3.
        
        Chain: You → first_ex (i-2) → first_ex's_i3_opponent
        """
        first_ex = self._get_first_ex()
        if not first_ex:
            return Prediction(
                predicted_opponent=None, confidence=0.0,
                prediction_method="i4_no_first_ex", is_valid=False,
                warnings=["No 'first ex' found - need round i-2 data"]
            )
        
        i3_record = self.session.get_round_record(phase=1, round_num=3)
        if not i3_record or not i3_record.opponent:
            return Prediction(
                predicted_opponent=None, confidence=0.0,
                prediction_method="i4_no_i3_history", is_valid=False,
                warnings=["No data for round i-3 - cannot chain predict"]
            )
        
        predicted = i3_record.opponent
        confidence = self._calculate_confidence()
        chain = f"You → {first_ex.name} (i-2) → {predicted.name} (i-3)"
        
        return Prediction(
            predicted_opponent=predicted,
            confidence=confidence,
            based_on_round=i3_record,
            prediction_method="i4_rule",
            chain_description=chain,
            warnings=self._get_warnings()
        )
    
    def _predict_ii2(self) -> Prediction:
        """Predict round ii-2.
        
        Rule: Your opponent at ii-2 is the opponent that your "first ex" 
        (opponent at ii-1) faced at round ii-1.
        
        Chain: You → first_ex (ii-1) → first_ex's_ii1_opponent
        """
        first_ex = self._get_first_ex_phase2()
        if not first_ex:
            return Prediction(
                predicted_opponent=None, confidence=0.0,
                prediction_method="ii2_no_first_ex", is_valid=False,
                warnings=["No 'first ex' for phase 2 found - need round ii-1 data"]
            )
        
        ii1_record = self.session.get_round_record(
            phase=self.session.current_phase, round_num=1
        )
        if not ii1_record or not ii1_record.opponent:
            return Prediction(
                predicted_opponent=None, confidence=0.0,
                prediction_method="ii2_no_ii1_history", is_valid=False,
                warnings=["No data for round ii-1 - cannot chain predict"]
            )
        
        predicted = ii1_record.opponent
        confidence = self._calculate_confidence()
        chain = f"You → {first_ex.name} (ii-1) → {predicted.name} (ii-1)"
        
        return Prediction(
            predicted_opponent=predicted,
            confidence=confidence,
            based_on_round=ii1_record,
            prediction_method="ii2_rule",
            chain_description=chain,
            warnings=self._get_warnings()
        )
    
    def _predict_ii4(self) -> Prediction:
        """Predict round ii-4.
        
        Rule: Your opponent at ii-4 is the opponent of your ii-2 opponent 
        at round i-4.
        
        Chain: You → ii2_opponent → ii2_opponent's_i4_opponent
        """
        ii2_record = self.session.get_round_record(
            phase=self.session.current_phase, round_num=2
        )
        if not ii2_record or not ii2_record.opponent:
            return Prediction(
                predicted_opponent=None, confidence=0.0,
                prediction_method="ii4_no_ii2", is_valid=False,
                warnings=["No data for round ii-2 - need ii-2 to predict ii-4"]
            )
        
        ii2_opponent = ii2_record.opponent
        
        # Now find what ii2_opponent faced at round i-4
        i4_record = self.session.get_round_record(phase=1, round_num=4)
        if not i4_record or not i4_record.opponent:
            return Prediction(
                predicted_opponent=None, confidence=0.0,
                prediction_method="ii4_no_i4", is_valid=False,
                warnings=["No data for round i-4 - cannot chain predict"]
            )
        
        predicted = i4_record.opponent
        confidence = self._calculate_confidence() * 0.95  # Slightly lower
        chain = f"You → {ii2_opponent.name} (ii-2) → {predicted.name} (i-4)"
        
        return Prediction(
            predicted_opponent=predicted,
            confidence=confidence,
            based_on_round=i4_record,
            prediction_method="ii4_rule",
            chain_description=chain,
            warnings=self._get_warnings()
        )
    
    def _predict_ii5(self) -> Prediction:
        """Predict round ii-5.
        
        Rule: Your opponent at ii-5 is the opponent of your ii-4 opponent 
        at round ii-2.
        
        Chain: You → ii4_opponent → ii4_opponent's_ii2_opponent
        """
        ii4_record = self.session.get_round_record(
            phase=self.session.current_phase, round_num=4
        )
        if not ii4_record or not ii4_record.opponent:
            return Prediction(
                predicted_opponent=None, confidence=0.0,
                prediction_method="ii5_no_ii4", is_valid=False,
                warnings=["No data for round ii-4 - need ii-4 to predict ii-5"]
            )
        
        ii4_opponent = ii4_record.opponent
        
        ii2_record = self.session.get_round_record(
            phase=self.session.current_phase, round_num=2
        )
        if not ii2_record or not ii2_record.opponent:
            return Prediction(
                predicted_opponent=None, confidence=0.0,
                prediction_method="ii5_no_ii2", is_valid=False,
                warnings=["No data for round ii-2 - cannot chain predict"]
            )
        
        predicted = ii2_record.opponent
        confidence = self._calculate_confidence() * 0.90
        chain = f"You → {ii4_opponent.name} (ii-4) → {predicted.name} (ii-2)"
        
        return Prediction(
            predicted_opponent=predicted,
            confidence=confidence,
            based_on_round=ii2_record,
            prediction_method="ii5_rule",
            chain_description=chain,
            warnings=self._get_warnings()
        )
    
    def _predict_ii6(self) -> Prediction:
        """Predict round ii-6.
        
        Rule: Your opponent at ii-6 is the opponent of your ii-5 opponent 
        at round ii-3.
        
        Chain: You → ii5_opponent → ii5_opponent's_ii3_opponent
        """
        ii5_record = self.session.get_round_record(
            phase=self.session.current_phase, round_num=5
        )
        if not ii5_record or not ii5_record.opponent:
            return Prediction(
                predicted_opponent=None, confidence=0.0,
                prediction_method="ii6_no_ii5", is_valid=False,
                warnings=["No data for round ii-5 - need ii-5 to predict ii-6"]
            )
        
        ii5_opponent = ii5_record.opponent
        
        ii3_record = self.session.get_round_record(
            phase=self.session.current_phase, round_num=3
        )
        if not ii3_record or not ii3_record.opponent:
            return Prediction(
                predicted_opponent=None, confidence=0.0,
                prediction_method="ii6_no_ii3", is_valid=False,
                warnings=["No data for round ii-3 - cannot chain predict"]
            )
        
        predicted = ii3_record.opponent
        confidence = self._calculate_confidence() * 0.85
        chain = f"You → {ii5_opponent.name} (ii-5) → {predicted.name} (ii-3)"
        
        return Prediction(
            predicted_opponent=predicted,
            confidence=confidence,
            based_on_round=ii3_record,
            prediction_method="ii6_rule",
            chain_description=chain,
            warnings=self._get_warnings()
        )
    
    def _get_first_ex(self) -> Optional[Player]:
        """Get the 'first ex' (mantan pertama) - opponent at round i-2."""
        i2_record = self.session.get_round_record(phase=1, round_num=2)
        if i2_record:
            return i2_record.opponent
        return None
    
    def _get_first_ex_phase2(self) -> Optional[Player]:
        """Get the 'first ex' for phase 2+ - opponent at round ii-1."""
        ii1_record = self.session.get_round_record(
            phase=self.session.current_phase, round_num=1
        )
        if ii1_record:
            return ii1_record.opponent
        return None
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence score based on conditions.
        
        Confidence decreases when:
        - Not all 8 players are active (players eliminated)
        - Less history data available
        """
        active_players = len(self.session.active_players)
        
        if active_players == self.max_players:
            base_confidence = 0.95
        else:
            # Every elimination reduces confidence by 10%
            eliminated = self.max_players - active_players
            base_confidence = max(0.30, 0.95 - (eliminated * 0.10))
        
        return base_confidence
    
    def _get_warnings(self) -> list[str]:
        """Generate warnings based on current session state."""
        warnings = []
        
        active = len(self.session.active_players)
        if active < self.max_players:
            warnings.append(
                f"Only {active}/{self.max_players} players active - "
                "prediction accuracy may be reduced"
            )
        
        return warnings
