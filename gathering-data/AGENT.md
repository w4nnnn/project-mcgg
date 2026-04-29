# Gathering-Data Project (GUI Sederhana)

## Tujuan Project

- Project ini hanya untuk input dan penyimpanan data pairing (matchup) pemain Magic Chess Go Go (MCGG) per sesi.
- Fokus project: GUI Tkinter untuk memudahkan input data dan edit ronde.
- Tidak ada fitur analisis, report, atau rule prediksi lawan.

## Aturan Data (Survival)

- Pemain aktif per sesi fleksibel: 2 sampai 8 pemain.
- Pairing per ronde tidak wajib penuh.
- Jika pairing ganjil, boleh 1 pairing `MIRROR` (maksimal 1 per ronde).
- Tetap anti-duplicate: pemain tidak boleh muncul lebih dari sekali dalam ronde yang sama.

## Format Data JSON

Setiap file sesi hanya berisi:
- `id`: id sesi
- `players`: list nama pemain aktif
- `matches`: list pairing tiap ronde, dengan field:
  - `round_label`, `phase`, `round_no`, `player1`, `player2`

Contoh:

```json
{
  "id": "baf0d926",
  "players": ["K H E N 2.", "Computer1", "Computer2"],
  "matches": [
    {"round_label": "i-2", "phase": 1, "round_no": 2, "player1": "K H E N 2.", "player2": "Computer2"},
    {"round_label": "i-2", "phase": 1, "round_no": 2, "player1": "Computer1", "player2": "MIRROR"}
  ]
}
```

## Catatan

- Project ini GUI-only.
- Entry point: `mcgg-data`.
- Data disimpan sebagai JSON per sesi di folder `data/sessions`.
