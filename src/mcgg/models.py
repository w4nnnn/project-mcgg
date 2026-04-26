"""Domain models for Magic Chess Go Go (MCGG) opponent prediction system."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class RoundType(Enum):
    """Types of opponents in a round."""

    MONSTER = "monster"
    USER = "user"


class MatchResult(Enum):
    """Match outcome."""

    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"


class RoundPhase(Enum):
    """Phase classification within a round."""

    RANDOM = "random"  # Cannot be predicted
    PREDICTABLE = "predictable"  # Can be predicted based on history


class RoundNumber(Enum):
    """Round numbers within a phase."""

    # Phase 1 (index phase i)
    P1_R1 = "i-1"  # Monster (random)
    P1_R2 = "i-2"  # User (random)
    P1_R3 = "i-3"  # User (random)
    P1_R4 = "i-4"  # User (predictable)

    # Phase 2+ (index phase ii, iii, iv, ...)
    P2_R1 = "ii-1"  # User (random)
    P2_R2 = "ii-2"  # User (predictable)
    P2_R3 = "ii-3"  # Monster (random)
    P2_R4 = "ii-4"  # User (predictable)
    P2_R5 = "ii-5"  # User (predictable)
    P2_R6 = "ii-6"  # User (predictable)

    # Phase 3+ follows same pattern as Phase 2
    P3_R1 = "iii-1"
    P3_R2 = "iii-2"
    P3_R3 = "iii-3"
    P3_R4 = "iii-4"
    P3_R5 = "iii-5"
    P3_R6 = "iii-6"

    @property
    def phase(self) -> int:
        """Get the phase number (1, 2, 3, ...)."""
        mapping = {
            "i": 1, "ii": 2, "iii": 3, "iv": 4,
            "v": 5, "vi": 6, "vii": 7, "viii": 8,
        }
        roman = self.value.split("-")[0]
        return mapping.get(roman, 0)

    @property
    def round_within_phase(self) -> int:
        """Get round number within the phase (1-6)."""
        return int(self.value.split("-")[1])

    @property
    def is_predictable(self) -> bool:
        """Check if this round is predictable."""
        predictable_rounds = {
            RoundNumber.P1_R4,
            RoundNumber.P2_R2, RoundNumber.P2_R4, RoundNumber.P2_R5, RoundNumber.P2_R6,
            RoundNumber.P3_R2, RoundNumber.P3_R4, RoundNumber.P3_R5, RoundNumber.P3_R6,
        }
        return self in predictable_rounds

    @property
    def is_monster_round(self) -> bool:
        """Check if this round involves a monster."""
        monster_rounds = {
            RoundNumber.P1_R1,
            RoundNumber.P2_R3,
            RoundNumber.P3_R3,
        }
        return self in monster_rounds

    @classmethod
    def from_phase_and_round(cls, phase: int, round_num: int) -> RoundNumber:
        """Create RoundNumber from phase number and round number."""
        if phase == 1 and round_num == 1:
            return cls.P1_R1
        if phase == 1 and round_num == 2:
            return cls.P1_R2
        if phase == 1 and round_num == 3:
            return cls.P1_R3
        if phase == 1 and round_num == 4:
            return cls.P1_R4

        roman_phase = {2: "ii", 3: "iii", 4: "iv", 5: "v", 6: "vi"}
        roman = roman_phase.get(phase, f"phase_{phase}")
        return cls(f"{roman}-{round_num}")


@dataclass
class Player:
    """Represents a player in the game session."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = "Unknown"
    position: int = 0  # Player position (e.g., P1, P2, ... P8)
    is_active: bool = True  # False if eliminated
    is_local_player: bool = False  # True if this is the user running the prediction

    def __str__(self) -> str:
        return f"P{self.position}" if self.position else self.name

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return False
        return self.id == other.id


@dataclass
class RoundRecord:
    """Records the opponent faced in a specific round."""

    round_number: RoundNumber
    phase: int
    round: int
    opponent: Optional[Player] = None
    opponent_type: RoundType = RoundType.USER
    result: Optional[MatchResult] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if isinstance(self.round_number, str):
            self.round_number = RoundNumber(self.round_number)

    @property
    def is_predictable_round(self) -> bool:
        """Whether this round's opponent could be predicted."""
        return self.round_number.is_predictable

    @property
    def description(self) -> str:
        """Human-readable description of this round."""
        return f"{self.round_number.value} ({self.opponent})"


@dataclass
class Session:
    """A game session containing multiple rounds of play."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    started_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    players: list[Player] = field(default_factory=list)
    round_history: list[RoundRecord] = field(default_factory=list)
    current_phase: int = 1
    current_round: int = 1
    is_active: bool = True
    winner: Optional[str] = None
    chain_relations: dict[str, str] = field(default_factory=dict)

    @property
    def local_player(self) -> Optional[Player]:
        """Get the local player (the user running this app)."""
        for player in self.players:
            if player.is_local_player:
                return player
        return None

    @property
    def active_players(self) -> list[Player]:
        """Get all players who haven't been eliminated."""
        return [p for p in self.players if p.is_active]

    @property
    def current_round_number(self) -> RoundNumber:
        """Get the current RoundNumber enum value."""
        return RoundNumber.from_phase_and_round(self.current_phase, self.current_round)

    @property
    def total_rounds_played(self) -> int:
        """Total number of rounds completed in this session."""
        return len(self.round_history)

    def add_player(self, player: Player) -> None:
        """Add a player to the session."""
        if player not in self.players:
            self.players.append(player)

    def get_player_by_name(self, name: str) -> Optional[Player]:
        """Find player by name (case-insensitive)."""
        name_lower = name.lower()
        for p in self.players:
            if p.name.lower() == name_lower:
                return p
        return None

    def add_round(self, opponent: Player, opponent_type: RoundType = RoundType.USER) -> RoundRecord:
        """Record a completed round."""
        record = RoundRecord(
            round_number=self.current_round_number,
            phase=self.current_phase,
            round=self.current_round,
            opponent=opponent,
            opponent_type=opponent_type,
        )
        self.round_history.append(record)
        return record

    def advance_round(self) -> None:
        """Move to the next round.
        
        Phase 1: rounds 1-4
        Phase 2+: rounds 1-6
        """
        if self.current_phase == 1:
            max_round = 4
        else:
            max_round = 6
        
        self.current_round += 1
        if self.current_round > max_round:
            self.current_round = 1
            self.current_phase += 1

    def get_previous_opponent(self) -> Optional[Player]:
        """Get the opponent from the most recent round."""
        if self.round_history:
            return self.round_history[-1].opponent
        return None

    def get_first_ex(self) -> Optional[Player]:
        """Get the 'first ex' (mantan pertama) - opponent from round i-2.

        Per the prediction rules, the first ex is the opponent faced in
        the first random user round (round i-2 for phase 1, ii-1 for phase 2+).
        """
        for record in self.round_history:
            # Round i-2 or ii-1 or iii-1, etc.
            if record.phase == 1 and record.round == 2:
                return record.opponent
            if record.phase > 1 and record.round == 1:
                return record.opponent
        return None

    def get_round_record(self, phase: int, round_num: int) -> Optional[RoundRecord]:
        """Get a specific round record by phase and round number."""
        for record in self.round_history:
            if record.phase == phase and record.round == round_num:
                return record
        return None

    def set_chain_relation(self, phase: int, round_num: int, source_player: str, opponent_player: str) -> None:
        """Store extra chain data: who a player faced in a round."""
        source = source_player.strip().lower()
        target = opponent_player.strip()
        if not source or not target:
            return
        self.chain_relations[f"{phase}-{round_num}:{source}"] = target

    def get_chain_opponent(self, phase: int, round_num: int, source_player: str) -> Optional[str]:
        """Fetch stored chain relation for a player in specific round."""
        source = source_player.strip().lower()
        if not source:
            return None
        return self.chain_relations.get(f"{phase}-{round_num}:{source}")

    def end_session(self) -> None:
        """Mark the session as ended."""
        self.ended_at = datetime.now()


@dataclass
class Prediction:
    """Represents a prediction for the next opponent."""

    predicted_opponent: Optional[Player]
    confidence: float  # 0.0 to 1.0
    based_on_round: Optional[RoundRecord] = None
    prediction_method: str = ""
    is_valid: bool = True
    chain_description: Optional[str] = None
    warnings: list = field(default_factory=list)  # e.g. ["Player eliminated", "Insufficient data"]

    @property
    def description(self) -> str:
        """Human-readable prediction description."""
        if not self.is_valid:
            return "No prediction available"
        if self.predicted_opponent:
            return f"Predicted: {self.predicted_opponent} (confidence: {self.confidence:.0%})"
        return "No prediction possible for this round"


class PredictionEngine:
    """Engine for predicting opponents based on the MCGG rules."""

    def __init__(self, session: Session):
        self.session = session

    def predict(self) -> Prediction:
        """Predict the opponent for the current round.

        Rules based on MCGG opponent prediction system:
        - Ronde i-2, i-3, ii-1: Random (cannot predict)
        - Ronde i-4: Opponent = opponent of "first ex" in round i-3
        - Ronde ii-2: Opponent = opponent of "first ex" in round ii-1
        - Ronde ii-4: Opponent = opponent of your round ii-2 opponent in round i-4
        """
        current = self.session.current_round_number

        if not current.is_predictable:
            return Prediction(
                predicted_opponent=None,
                confidence=0.0,
                prediction_method="random_round",
                is_valid=False,
            )

        phase = self.session.current_phase
        round_num = self.session.current_round

        # Ronde i-4: opponent of your first ex's opponent at round i-3
        if phase == 1 and round_num == 4:
            return self._predict_i4()

        # Ronde ii-2: opponent of your first ex at round ii-1
        if phase >= 2 and round_num == 2:
            return self._predict_ii2()

        # Ronde ii-4: opponent of your ii-2 opponent at round ii-2's i-4
        if phase >= 2 and round_num == 4:
            return self._predict_ii4()

        # Ronde ii-5, ii-6, etc.
        if phase >= 2 and round_num in (5, 6):
            return self._predict_ii5_6(round_num)

        return Prediction(
            predicted_opponent=None,
            confidence=0.0,
            prediction_method="no_rule",
            is_valid=False,
        )

    def _predict_i4(self) -> Prediction:
        """Predict round i-4.

        Your opponent at i-4 is the opponent of your "first ex" at i-3.
        """
        # Get first ex (opponent at i-2)
        first_ex = self.session.get_first_ex()
        if not first_ex:
            return Prediction(None, 0.0, prediction_method="i4_no_first_ex", is_valid=False)

        # Get what first_ex faced at i-3
        i3_record = self.session.get_round_record(phase=1, round_num=3)
        if i3_record and i3_record.opponent:
            return Prediction(
                predicted_opponent=i3_record.opponent,
                confidence=0.95,
                based_on_round=i3_record,
                prediction_method="i4_rule",
            )

        return Prediction(None, 0.0, prediction_method="i4_no_history", is_valid=False)

    def _predict_ii2(self) -> Prediction:
        """Predict round ii-2.

        Your opponent at ii-2 is the opponent of your "first ex" at ii-1.
        """
        first_ex = self.session.get_first_ex()
        if not first_ex:
            return Prediction(None, 0.0, prediction_method="ii2_no_first_ex", is_valid=False)

        # Get what first_ex faced at ii-1 (the "first ex" round for phase 2)
        ii1_record = self.session.get_round_record(phase=self.session.current_phase, round_num=1)
        if ii1_record and ii1_record.opponent:
            return Prediction(
                predicted_opponent=ii1_record.opponent,
                confidence=0.95,
                based_on_round=ii1_record,
                prediction_method="ii2_rule",
            )

        return Prediction(None, 0.0, prediction_method="ii2_no_history", is_valid=False)

    def _predict_ii4(self) -> Prediction:
        """Predict round ii-4.

        Your opponent at ii-4 is the opponent of your ii-2 opponent at round i-4.
        """
        # Get our ii-2 opponent
        ii2_record = self.session.get_round_record(phase=self.session.current_phase, round_num=2)
        if not ii2_record or not ii2_record.opponent:
            return Prediction(None, 0.0, prediction_method="ii4_no_ii2", is_valid=False)

        ii2_opponent = ii2_record.opponent

        # Get what ii2_opponent faced at round i-4
        i4_record = self.session.get_round_record(phase=1, round_num=4)
        if i4_record and i4_record.opponent:
            return Prediction(
                predicted_opponent=i4_record.opponent,
                confidence=0.90,
                based_on_round=i4_record,
                prediction_method="ii4_rule",
            )

        return Prediction(None, 0.0, prediction_method="ii4_no_history", is_valid=False)

    def _predict_ii5_6(self, target_round: int) -> Prediction:
        """Predict rounds ii-5 and ii-6.

        These follow a pattern where your opponent is the opponent of your
        previous round's opponent at a specific earlier round.
        """
        # For now, mark as not fully predictable without more history
        return Prediction(
            predicted_opponent=None,
            confidence=0.0,
            prediction_method=f"ii{target_round}_not_implemented",
            is_valid=False,
        )
