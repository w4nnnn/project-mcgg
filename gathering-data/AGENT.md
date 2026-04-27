# Gathering-Data Quick Summary

Dokumen ini dibuat agar agent AI berikutnya bisa paham project `gathering-data` tanpa membaca semua file satu per satu.

## 1) Tujuan Project

- Project terpisah untuk input data matchup **8 pemain** MCGG via TUI.
- Input hanya ronde player-vs-player; ronde monster di-skip otomatis.
- Setiap match disimpan ke JSON per sesi.
- Analisis pola dijalankan saat sesi selesai (`stop`) atau saat `report`.

## 2) Entry Point & Command

- Entry point script: `mcgg-data` (lihat `pyproject.toml`).
- Main module: `pattern_analyzer.cli:main`.
- Command yang tersedia:
  - `tui` -> mulai sesi baru interaktif.
  - `resume --session-id <id>` -> lanjut sesi.
  - `report --session-id <id>` -> tampilkan/generate laporan sesi.
  - `list-sessions` -> list sesi tersimpan.
- Bisa juga jalan via module:
  - `python -m pattern_analyzer tui`

## 3) Arsitektur File Utama

- `src/pattern_analyzer/cli.py`
  - UI/UX terminal, input pemain, input pairing, report print.
  - Pairing sekarang support **arrow selection** (`msvcrt`) di Windows.
  - Prompt pairing informatif:
    - `Pair #N = ?:?` saat pilih pemain pertama.
    - `Pair #N = A:?` saat pilih lawan A.
- `src/pattern_analyzer/service.py`
  - Orkestrasi use-case: create/load session, save round, finish session.
  - Menentukan round label, menyimpan tiap match, advance ke round berikutnya.
- `src/pattern_analyzer/models.py`
  - `SessionState` dataclass (state sesi + metadata + report).
  - Validator: `normalize_players`, `parse_pair`, `validate_round_pairs`.
- `src/pattern_analyzer/rounds.py`
  - Rule round/phase MCGG:
    - Phase 1: 4 round.
    - Phase 2+ : 6 round.
    - Monster round: `i-1`, `ii-3`, `iii-3`, dst.
  - Fungsi `next_player_round()` untuk auto-skip ronde monster.
- `src/pattern_analyzer/storage.py`
  - JSON persistence:
    - folder default `gathering-data/data/sessions`.
    - 1 file per sesi: `<session_id>.json`.
  - API: `save`, `load`, `list_sessions`, `latest_session_id`.
- `src/pattern_analyzer/analysis.py`
  - End-of-session report:
    - frequent matchup (pair berulang),
    - lawan beruntun untuk pemain,
    - warning jika active player per round < 8,
    - confidence `high/medium/low`.

## 4) Alur Runtime TUI

1. User jalankan `tui`.
2. Input 8 nama pemain unik.
3. Session dibuat, posisi awal diset ke **round player pertama** (`i-2`).
4. Tiap ronde:
   - pilih 4 pair dengan arrow (2 pemain per pair, tanpa duplikasi pemain),
   - validasi ronde,
   - simpan **setiap match** ke `session.matches`,
   - simpan ke JSON.
5. Round auto-advance dan auto-skip monster.
6. User bisa lanjut (`Enter`) atau `stop`.
7. Saat `stop`, sistem:
   - `is_finished = true`,
   - generate `report`,
   - simpan final ke JSON,
   - tampilkan ringkasan laporan.

## 5) Format Data JSON (Ringkas)

Setiap file sesi berisi:

- metadata:
  - `id`, `players`, `phase`, `round_no`,
  - `created_at`, `updated_at`, `ended_at`,
  - `is_finished`.
- `matches`: list item seperti:
  - `round_label` (contoh `i-2`),
  - `phase`, `round_no`,
  - `player1`, `player2`,
  - `recorded_at`.
- `report`: object hasil analisis (jika sudah finish/report).

## 6) Validasi Yang Sudah Ada

- Pemain sesi harus tepat 8 nama unik.
- Satu ronde player harus tepat 4 pairing.
- Nama pair harus valid, tidak boleh `A:A`, tidak boleh pemain luar sesi.
- Setiap pemain hanya boleh muncul sekali per ronde.

## 7) Test Coverage Saat Ini

- `tests/test_rounds.py`
  - round label, monster mapping, next round, auto-skip monster.
- `tests/test_service.py`
  - create session start di `i-2`,
  - save round persist ke JSON,
  - skip `ii-3` berjalan,
  - finish session generate report.
- `tests/test_cli.py`
  - flow `run_tui` single round lalu stop,
  - test collect pair builder dengan chooser mock.

## 8) Batasan/Known Gaps

- Arrow UI masih print berbasis baris (belum clear screen/curses style).
- Fallback non-Windows bukan arrow (pakai input teks).
- Analisis masih sederhana (belum chain prediction lanjutan).
- Elimination flow belum ada mekanisme formal (hanya warning berbasis pemain aktif per round dari data).

## 9) Perubahan Aman Untuk Agent Berikutnya

- Aman menambah formatter tampilan TUI di `cli.py`.
- Aman menambah field report di `analysis.py` selama kompatibel dengan JSON lama.
- Jika ubah schema JSON `SessionState`, update:
  - serializer di `storage.py`,
  - test di `tests/test_service.py` dan `tests/test_cli.py`.

