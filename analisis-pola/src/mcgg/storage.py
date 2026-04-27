"""Storage layer for MCGG session persistence.

Handles saving/loading sessions to JSON files, and export/import to CSV.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Optional

from mcgg.models import Session, Player, RoundRecord, RoundType, RoundNumber


# Default data directory
DEFAULT_DATA_DIR = Path.home() / ".mcgg" / "data"
DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)


class StorageError(Exception):
    """Custom exception for storage operations."""
    pass


class SessionStorage:
    """Manages session persistence to JSON files."""
    
    def __init__(self, data_dir: Path | str = DEFAULT_DATA_DIR):
        if isinstance(data_dir, str):
            data_dir = Path(data_dir)
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_session_path(self, session_id: str) -> Path:
        """Get the file path for a session."""
        return self.data_dir / f"session_{session_id}.json"
    
    def save_session(self, session: Session) -> str:
        """Save a session to JSON file.
        
        Returns the path where the session was saved.
        """
        try:
            path = self._get_session_path(session.id)
            session.updated_at = datetime.now()
            
            data = self._session_to_dict(session)
            
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            
            return str(path)
        except Exception as e:
            raise StorageError(f"Failed to save session: {e}")
    
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session from JSON file."""
        try:
            path = self._get_session_path(session_id)
            if not path.exists():
                return None
            
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return self._dict_to_session(data)
        except Exception as e:
            raise StorageError(f"Failed to load session: {e}")
    
    def list_sessions(self) -> list[dict]:
        """List all saved sessions (summary info only)."""
        sessions = []
        for path in sorted(self.data_dir.glob("session_*.json")):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                sessions.append({
                    "id": data.get("id"),
                    "started_at": data.get("started_at"),
                    "ended_at": data.get("ended_at"),
                    "current_phase": data.get("current_phase"),
                    "current_round": data.get("current_round"),
                    "total_rounds": len(data.get("round_history", [])),
                    "is_active": data.get("is_active", False),
                })
            except Exception:
                continue
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session file. Returns True if deleted."""
        path = self._get_session_path(session_id)
        if path.exists():
            path.unlink()
            return True
        return False
    
    def _session_to_dict(self, session: Session) -> dict:
        """Convert Session to dictionary for JSON serialization."""
        return {
            "id": session.id,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "updated_at": session.updated_at.isoformat() if session.updated_at else None,
            "current_phase": session.current_phase,
            "current_round": session.current_round,
            "is_active": session.is_active,
            "winner": session.winner,
            "chain_relations": session.chain_relations,
            "players": [
                {
                    "id": p.id,
                    "name": p.name,
                    "position": p.position,
                    "is_active": p.is_active,
                    "is_local_player": p.is_local_player,
                }
                for p in session.players
            ],
            "round_history": [
                {
                    "round_number": r.round_number.value if isinstance(r.round_number, RoundNumber) else r.round_number,
                    "phase": r.phase,
                    "round": r.round,
                    "opponent_id": r.opponent.id if r.opponent else None,
                    "opponent_name": r.opponent.name if r.opponent else None,
                    "opponent_type": r.opponent_type.value if isinstance(r.opponent_type, RoundType) else r.opponent_type,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                }
                for r in session.round_history
            ],
        }
    
    def _dict_to_session(self, data: dict) -> Session:
        """Convert dictionary back to Session."""
        # Build player lookup
        players_by_id = {}
        players_by_name = {}
        
        session = Session(
            id=data["id"],
            current_phase=data.get("current_phase", 1),
            current_round=data.get("current_round", 1),
            is_active=data.get("is_active", True),
            winner=data.get("winner"),
            chain_relations=data.get("chain_relations", {}),
        )
        
        # Recreate players
        for p_data in data.get("players", []):
            player = Player(
                id=p_data["id"],
                name=p_data["name"],
                position=p_data.get("position", 0),
                is_active=p_data.get("is_active", True),
                is_local_player=p_data.get("is_local_player", False),
            )
            session.players.append(player)
            players_by_id[player.id] = player
            players_by_name[player.name.lower()] = player
        
        # Recreate round history
        for r_data in data.get("round_history", []):
            opponent = None
            opp_id = r_data.get("opponent_id")
            opp_name = r_data.get("opponent_name")
            
            if opp_id and opp_id in players_by_id:
                opponent = players_by_id[opp_id]
            elif opp_name and opp_name.lower() in players_by_name:
                opponent = players_by_name[opp_name.lower()]
            
            # Parse round number
            rn_value = r_data.get("round_number")
            if isinstance(rn_value, str):
                try:
                    rn = RoundNumber(rn_value)
                except ValueError:
                    rn = RoundNumber.P1_R1  # fallback
            else:
                rn = RoundNumber.P1_R1
            
            record = RoundRecord(
                round_number=rn,
                phase=r_data.get("phase", 1),
                round=r_data.get("round", 1),
                opponent=opponent,
                opponent_type=RoundType(r_data.get("opponent_type", "user")),
            )
            session.round_history.append(record)
        
        # Restore timestamps
        if data.get("started_at"):
            session.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("ended_at"):
            session.ended_at = datetime.fromisoformat(data["ended_at"])
        if data.get("updated_at"):
            session.updated_at = datetime.fromisoformat(data["updated_at"])
        
        return session


class Exporter:
    """Export/import session data to CSV and JSON formats."""
    
    @staticmethod
    def export_to_csv(session: Session, path: Path | str) -> str:
        """Export session round history to CSV.
        
        Returns the path where the CSV was saved.
        """
        if isinstance(path, str):
            path = Path(path)
        
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "Phase", "Round", "Round_Number", "Opponent_Type",
                "Opponent_Name", "Opponent_Position", "Timestamp"
            ])
            
            # Data rows
            for record in session.round_history:
                writer.writerow([
                    record.phase,
                    record.round,
                    record.round_number.value if isinstance(record.round_number, RoundNumber) else record.round_number,
                    record.opponent_type.value if isinstance(record.opponent_type, RoundType) else record.opponent_type,
                    record.opponent.name if record.opponent else "Monster",
                    record.opponent.position if record.opponent else 0,
                    record.timestamp.isoformat() if record.timestamp else "",
                ])
        
        return str(path)
    
    @staticmethod
    def export_to_json(session: Session, path: Path | str) -> str:
        """Export full session data to JSON (for backup/transfer).
        
        Returns the path where the JSON was saved.
        """
        if isinstance(path, str):
            path = Path(path)
        
        storage = SessionStorage()
        data = storage._session_to_dict(session)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        
        return str(path)
    
    @staticmethod
    def import_from_json(path: Path | str) -> Session:
        """Import a session from JSON file."""
        if isinstance(path, str):
            path = Path(path)
        
        storage = SessionStorage()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return storage._dict_to_session(data)
    
    @staticmethod
    def import_from_csv(path: Path | str) -> Optional[Session]:
        """Import round history from CSV (limited - creates new session).
        
        Note: CSV import cannot fully restore all session data.
        Returns None if import is not possible.
        """
        # CSV import is limited - for full restore use JSON
        return None
