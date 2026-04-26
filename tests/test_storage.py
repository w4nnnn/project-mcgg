"""Tests for storage layer."""

import pytest
import tempfile
from pathlib import Path
from mcgg.models import Session, Player, RoundType
from mcgg.storage import SessionStorage, Exporter


class TestSessionStorage:
    """Test cases for SessionStorage."""
    
    def setup_method(self):
        """Set up test fixtures with temp directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = SessionStorage(self.temp_dir)
    
    def test_save_and_load_session(self):
        """Test saving and loading a session."""
        session = Session()
        session.add_player(Player(name="You", position=1, is_local_player=True))
        session.add_player(Player(name="Alice", position=2))
        
        # Save
        path = self.storage.save_session(session)
        assert Path(path).exists()
        
        # Load
        loaded = self.storage.load_session(session.id)
        assert loaded is not None
        assert loaded.id == session.id
        assert len(loaded.players) == 2
        assert loaded.players[0].name == "You"
    
    def test_load_nonexistent_session(self):
        """Test loading a session that doesn't exist."""
        loaded = self.storage.load_session("nonexistent_id")
        assert loaded is None
    
    def test_list_sessions(self):
        """Test listing saved sessions."""
        # Create and save multiple sessions
        for i in range(3):
            s = Session()
            s.add_player(Player(name=f"Player{i}", position=1))
            self.storage.save_session(s)
        
        sessions = self.storage.list_sessions()
        assert len(sessions) == 3
    
    def test_delete_session(self):
        """Test deleting a session."""
        session = Session()
        session.add_player(Player(name="Test", position=1))
        
        self.storage.save_session(session)
        assert self.storage.load_session(session.id) is not None
        
        self.storage.delete_session(session.id)
        assert self.storage.load_session(session.id) is None


class TestExporter:
    """Test cases for Exporter."""
    
    def test_export_to_csv(self):
        """Test CSV export."""
        session = Session()
        session.add_player(Player(name="You", position=1, is_local_player=True))
        session.add_player(Player(name="Alice", position=2))
        session.add_player(Player(name="Bob", position=3))
        
        # Add some rounds
        session.add_round(session.players[1])  # vs Alice
        session.advance_round()
        session.add_round(session.players[2])  # vs Bob
        
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = Exporter.export_to_csv(session, f.name)
            assert Path(path).exists()
            
            # Read and check content
            content = Path(path).read_text()
            assert "Phase" in content
            assert "Alice" in content
            assert "Bob" in content
    
    def test_export_to_json(self):
        """Test JSON export."""
        session = Session()
        session.add_player(Player(name="You", position=1))
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Exporter.export_to_json(session, f.name)
            assert Path(path).exists()
            
            # Check it's valid JSON
            import json
            data = json.loads(Path(path).read_text())
            assert data["id"] == session.id
