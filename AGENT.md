# MCGG Matchmaking Analyzer - Agent Documentation

## Project Overview

**MCGG Matchmaking Analyzer** adalah tool CLI/TUI untuk menganalisis dan memprediksi matchmaking dalam game Mobile Legends: Magic Chess Go Go (MCGG).

**Location**: `/home/w4nn/workbrench/project-mcgg/`

## Game Rules Summary

MCGG adalah game battle royale dengan 8 pemain:

- Setiap ronde, pemain fight melawan player lain atau monster
- HP habis = eliminated (tusun)
- Pemain terakhir = winner
- 8 → 7 → 6 → ... → 1

### Fase & Ronde

| Fase | Ronde | Tipe | Predictable |
|------|-------|------|-------------|
| I | i-1 | Monster | ❌ |
| I | i-2 | Player | ❌ (Random) |
| I | i-3 | Player | ❌ (Random) |
| I | i-4 | Player | ✅ Chain |
| II+ | ii-1 | Player | ❌ (Random) |
| II+ | ii-2 | Player | ✅ Chain |
| II+ | ii-3 | Monster | ❌ |
| II+ | ii-4 | Player | ✅ Chain |
| II+ | ii-5 | Player | ✅ Chain |
| II+ | ii-6 | Player | ✅ Chain |

### Chain Prediction Rules

- **Mantan Pertama (First Ex)**: Lawan di ronde random pertama phase tersebut
  - Phase 1: lawan di i-2
  - Phase 2+: lawan di ii-1

- **Chain untuk i-4**: `You → FirstEx (i-2) → FirstEx's opponent at i-3`
- **Chain untuk ii-2**: `You → FirstEx (ii-1) → FirstEx's opponent at ii-1`
- **Chain untuk ii-4**: `You → ii-2 opponent → ii-2's opponent at i-4`
- **Chain untuk ii-5**: `You → ii-4 opponent → ii-4's opponent at ii-2`
- **Chain untuk ii-6**: `You → ii-5 opponent → ii-5's opponent at ii-3`

### Confidence Scoring

- Base: 95% saat semua 8 pemain aktif
- Setiap eliminasi: -10%
- Minimum: 30%

## Tech Stack

- **Python**: 3.9+
- **CLI Framework**: [Typer](https://typer.tiangolo.com/) (CLI commands)
- **UI**: [Rich](https://rich.readthedocs.io/) (styled terminal output)
- **Data Validation**: Pydantic models
- **Storage**: JSON (1 file per session, di `~/.mcgg/data/`)
- **Testing**: pytest

## Project Structure

```
mcgg-analyzer/
├── src/mcgg/
│   ├── __init__.py          # Package init, version
│   ├── __main__.py          # Entry point (python -m mcgg)
│   ├── cli.py               # Typer app, all commands
│   ├── models.py            # Domain models (Player, Session, RoundRecord, Prediction)
│   ├── engine.py            # PredictionEngine, chain logic
│   ├── storage.py           # SessionStorage, Exporter (CSV/JSON)
│   ├── i18n.py              # Internationalization (EN/ID)
│   └── ui/                  # Rich UI components
│       ├── panels.py        # Reusable panels (phase_indicator, prediction, etc)
│       ├── tables.py        # Table formatters
│       └── forms.py         # Input prompts
├── tests/
│   ├── test_engine.py       # Engine + model tests (16 tests)
│   └── test_storage.py      # Storage tests
├── pyproject.toml           # Package config, dependencies
└── README.md                # User documentation
```

## Key Models

### Player
```python
Player(id, name, position, is_active, is_local_player)
```

### Session
```python
Session(id, started_at, updated_at, ended_at, players, round_history,
        current_phase, current_round, is_active, winner)
```
Methods: `add_player()`, `get_player_by_name()`, `advance_round()`, `get_round_record()`, `get_first_ex()`

### RoundRecord
```python
RoundRecord(round_number, phase, round, opponent, opponent_type, result, timestamp)
```

### Prediction
```python
Prediction(predicted_opponent, confidence, based_on_round, prediction_method,
           is_valid, chain_description, warnings)
```

### RoundNumber (Enum)
```
P1_R1='i-1', P1_R2='i-2', ..., P2_R1='ii-1', ...
```
Properties: `is_predictable`, `is_monster_round`, `phase`, `round_within_phase`

## CLI Commands

| Command | Description |
|---------|-------------|
| `new-session` | Mulai sesi baru (--player, --you flags) |
| `resume` | Lanjutkan sesi (argument: session_id) |
| `record` | Rekam hasil match (argument: opponent, --result) |
| `predict` | Prediksi lawan接下来对手 |
| `status` | Show current phase/round |
| `history` | Show round history table |
| `players` | Show player list |
| `end-session` | End current session |
| `list-sessions` | Show all saved sessions |
| `export-csv` | Export to CSV (--path) |
| `export-json` | Export to JSON (--path) |
| `import-json` | Import from JSON |

## Important Conventions

### 1. Import Path
When running as package (`pip install -e .`), imports use `mcgg` not `src.mcgg`:
```python
from mcgg.models import Session  # ✅
from src.mcgg.models import Session  # ❌
```

### 2. Round Advancement
- Phase 1: max 4 rounds (i-1 to i-4)
- Phase 2+: max 6 rounds (ii-1 to ii-6)
- After max, phase increments and round resets to 1

### 3. Session State
- Current session stored in global `current_session` variable in `cli.py`
- Auto-saved to JSON after each `record` command
- Storage location: `~/.mcgg/data/session_{id}.json`

### 4. Player Name Lookup
`session.get_player_by_name()` is case-insensitive

### 5. Language
- Default: Indonesian (ID)
- CLI flag: `--lang id` or `--lang en`
- Global i18n instance via `get_i18n()`

## Running the App

```bash
# Development
cd /home/w4nn/workbrench/project-mcgg
.venv/bin/python -m mcgg <command>

# Or install globally
pip install -e .
mcgg <command>

# Run tests
.venv/bin/python -m pytest tests/ -v
```

## Known Limitations

1. **Chain prediction requires opponent's match data**: You can only predict if you know what your opponents faced in previous rounds. This tool assumes you're tracking all matches in the session.

2. **Prediction accuracy degrades with eliminations**: When players are eliminated, the chain-based prediction becomes less reliable.

3. **Phase 2+ first ex**: The "first ex" concept resets at each new phase (ii-1, iii-1, etc).

## Future Considerations (TUI Conversion)

If converting to TUI:

- **Recommended library**: Textual (from Rich creator)
- Keep existing models, engine, storage unchanged
- Replace `cli.py` with Textual App
- Move `current_session` to app state
- Reuse Rich panels in Textual widgets
- Consider async for periodic auto-save

## Quick Start for New Session

```bash
mcgg new-session --player You --player Alice --player Bob --player Charlie --you You
mcgg record monster --result win        # i-1 (monster, optional to record)
mcgg record Alice --result win          # i-2 (random)
mcgg record Bob --result lose          # i-3 (random)
mcgg predict                          # i-4 - predicts opponent
mcgg record <predicted> --result win    # record actual opponent
mcgg history
```

## File Locations

| Purpose | Path |
|---------|------|
| Project root | `/home/w4nn/workbrench/project-mcgg/` |
| Source code | `src/mcgg/` |
| Sessions | `~/.mcgg/data/` |
| Plans | `.hermes/plans/` |
| Venv | `.venv/` |
