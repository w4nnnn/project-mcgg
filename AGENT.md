# MCGG Matchmaking Analyzer - agent handoff summary

This document gives you the current technical state of the project so you can
continue implementation quickly and safely.

## Project summary

`mcgg` is a Python CLI/TUI tool for tracking and predicting opponents in Mobile
Legends: Magic Chess Go Go (MCGG). The current guided TUI flow (`mcgg tui`)
unifies session setup, prediction, and round recording, then intentionally
stops after round `ii-4` with a summary.

The codebase has active user-driven behavior changes, especially in round rules
and TUI prompts. Always verify against the local reference files in
`reference/`.

## Current architecture

The project uses a thin interface layer and a shared domain core.

- **Interface layer**: `src/mcgg/cli.py` (Typer + Rich guided flow).
- **Domain models**: `src/mcgg/models.py` (`Session`, `RoundRecord`, `Player`,
  `Prediction`, and `RoundNumber`).
- **Prediction logic**: `src/mcgg/engine.py` (`PredictionEngine`).
- **Persistence**: `src/mcgg/storage.py` (`SessionStorage`, JSON persistence,
  CSV/JSON export).
- **Entry point**: `src/mcgg/__main__.py` imports `mcgg.cli`.

## Guided TUI behavior (current)

The `tui` command is no longer a generic command menu. It is a guided round
pipeline.

1. You choose mode with arrow input: `new`, `resume`, or `exit`.
2. For `new`, you input 7 opponents one by one, and local player is auto-set to
   `Kamu`.
3. Each round shows status and round type.
4. Predictable rounds run prediction first.
5. If prediction is valid, the predicted opponent is auto-used (no repeated
   opponent question).
6. Non-predictable player rounds use arrow-based opponent selection.
7. Chain follow-up questions (for other players) also use arrow selection and
   apply exclusion rules.
8. Round data is saved, and the flow advances automatically.
9. After recording `ii-4`, guided flow prints:
   - played-opponent order (`i-2`, `i-3`, `i-4`, `ii-1`, `ii-2`, `ii-4`),
   - next predicted order (`ii-5`, `ii-6`) when chain data is sufficient.
10. Guided flow exits automatically after that summary.

## Round pattern rules (implemented)

Current round type pattern in `RoundNumber` is:

- **Phase 1**: `i-1` monster, `i-2` player, `i-3` player, `i-4` player.
- **Phase 2+**: always `player, player, monster, player, player, player`.

This is implemented through dynamic properties:

- `is_monster_round`: phase 1 -> round 1, phase 2+ -> round 3.
- `is_predictable`: phase 1 -> round 4, phase 2+ -> rounds 2, 4, 5, 6.

`RoundNumber` currently supports roman phases up to `viii` (phase 8).

## Chain prediction rules (current engine state)

`PredictionEngine` currently uses `Session.chain_relations` first, then falls
back to recorded round data if needed.

- `i-4`: `You -> first_ex(i-2) -> first_ex opponent at i-3`.
- `ii-2`: updated per latest request:
  `You -> first_ex(i-2) -> first_ex opponent at ii-1`.
- `ii-4`: based on `ii-2` opponent chain at `i-4`.
- `ii-5`: based on `ii-4` opponent chain at `ii-2`.
- `ii-6`: based on `ii-5` opponent chain at `ii-3`.

Note: `ii-5`/`ii-6` rules are still implemented for prediction output, but they
are no longer part of an infinite guided loop.

## Data model and persistence notes

`Session` includes:

- `players`
- `round_history`
- `current_phase` and `current_round`
- `chain_relations: dict[str, str]`

Chain keys use the format: `"{phase}-{round}:{source_player_lower}"`.

`SessionStorage` already persists and restores `chain_relations`, so guided TUI
sessions remain resumable with chain context.

## TUI selection/exclusion behavior (important)

The guided flow intentionally filters options to reduce repeated prompts.

- Main opponent picker excludes your previous opponent when possible.
- Chain picker excludes:
  - local player (`Kamu`),
  - source player itself,
  - your current opponent in that round (if provided).

This behavior was explicitly requested and is part of current expected UX.

## Command overview

Main commands are:

- `new-session`, `resume`, `record`, `predict`, `status`, `history`, `players`
- `end-session`, `list-sessions`, `export-csv`, `export-json`, `import-json`
- `tui` (primary guided flow)

## Testing and quality status

Recent test coverage includes:

- chain relation persistence,
- `i-4` chain mapping,
- updated `ii-2` rule using phase-1 first ex chain at `ii-1`,
- `ii-5` chain mapping.

When you modify prediction or guided flow, run:

```bash
python -m pytest tests -v
```

If `pytest` is unavailable locally, install dev dependencies first.

## Known active risks

The code is evolving quickly around user-specific rules. Keep these risks in
mind.

- Reference docs may conflict with older assumptions in comments or README.
- Guided UX and prediction rules are tightly coupled; update both together.
- Exclusion-heavy selectors can run out of options; preserve fallback behavior.

## Recommended next steps for the next agent

If you continue development, start with these steps.

1. Re-read `reference/informasi-mcgg.md` and reconcile any remaining rule drift
   in engine comments and README examples.
2. Add/extend tests for guided end-summary formatting and fallback message when
   post-`ii-4` chain data is incomplete.
3. Add focused tests for phase 4+ behavior to lock the `2 player + 1 monster +
   3 player` cycle.
4. Optionally refactor `cli.py` guided flow helpers into smaller modules for
   maintainability.
