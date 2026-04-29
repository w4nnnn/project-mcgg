
# Gathering-Data Project (Sederhana)

## Tujuan Project

- Project ini hanya untuk input dan penyimpanan data pairing (matchup) 8 pemain Magic Chess Go Go (MCGG) per sesi.
- Data pairing disimpan ke file JSON per sesi.
- Tidak ada fitur analisis, report, atau rule prediksi lawan.

## Format Data JSON

Setiap file sesi hanya berisi:
- `id`: id sesi
- `players`: list nama 8 pemain
- `matches`: list pairing tiap ronde, dengan field:
  - `round_label`, `phase`, `round_no`, `player1`, `player2`

Contoh:

```
{
  "id": "baf0d926",
  "players": ["K H E N 2.", "Computer1", ...],
  "matches": [
    {"round_label": "i-2", "phase": 1, "round_no": 2, "player1": "K H E N 2.", "player2": "Computer2"},
    ...
  ]
}
```

## Catatan

- Tidak ada dependensi pada file analysis.py, service.py, cli.py, rounds.py, storage.py, __main__.py (semua sudah dikosongkan/dihapus).
- Project ini hanya menyimpan data pairing, tanpa proses analisis atau laporan apapun.

