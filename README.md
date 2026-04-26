# MCGG Matchmaking Analyzer

**Magic Chess Go Go Opponent Prediction Tool**

Tool CLI untuk menganalisis dan memprediksi matchmaking di game Mobile Legends: Magic Chess Go Go.

## Fitur

- **Prediksi Lawan**: Prediksi opponent berdasarkan pola chain prediction
- **Catat Match**: Rekam hasil setiap ronde untuk analisis
- **Confidence Score**: Tingkat kepercayaan prediksi berdasarkan kondisi pemain aktif
- **Riwayat Lengkap**: Simpan dan lihat semua riwayat match
- **Export/Import**: Export ke CSV/JSON untuk backup
- **Multi-bahasa**: Indonesia dan English

## Installation

```bash
pip install mcgg-analyzer
```

Atau untuk development:

```bash
git clone <repo>
cd mcgg-analyzer
pip install -e .
```

## Usage

### Mulai Sesi Baru

```bash
mcgg new-session --player You --player Alice --player Bob --player Charlie --you You
```

### Rekam Hasil Match

```bash
# Ronde 1 (vs Monster)
mcgg record monster --result win

# Ronde 2 (vs Alice)
mcgg record Alice --result lose

# Ronde 3 (vs Bob)
mcgg record Bob --result win
```

### Prediksi Lawan

```bash
mcgg predict
```

### Lihat Status & Riwayat

```bash
mcgg status       # Status saat ini
mcgg history      # Riwayat ronde
mcgg players      # Daftar pemain
```

### Lanjutkan Sesi

```bash
# Lihat semua sesi
mcgg list-sessions

# Lanjutkan sesi
mcgg resume <session_id>
```

### Export Data

```bash
mcgg export-csv --path ./history.csv
mcgg export-json --path ./session.json
```

## Sistem Prediksi MCGG

### Aturan Chain Prediction

Game MCGG memiliki pola matchmaking berantai:

| Ronde | Tipe | Prediksi |
|-------|------|----------|
| i-2 | Random | Tidak bisa diprediksi |
| i-3 | Random | Tidak bisa diprediksi |
| i-4 | Predictable | Lawan dari mantan pertama di i-3 |
| ii-1 | Random | Tidak bisa diprediksi |
| ii-2 | Predictable | Lawan dari mantan pertama di ii-1 |
| ii-4 | Predictable | Lawan dari lawan ii-2 di i-4 |

### Terminologi

- **Mantan Pertama (First Ex)**: Lawan pertama di ronde random phase 1 (i-2)
- **Chain**: Rantai opponent yang digunakan untuk prediksi
- **Confidence**: Tingkat kepercayaan prediksi (turun saat ada pemain tereliminasi)

## Game Rules

MCGG adalah game dengan 8 pemain yang bertanding secara survival:

- Setiap ronde, pemain fight melawan player lain atau monster
- HP habis = tereliminasi
- Pemain terakhir yang bertahan = winner
- Matchmaking menggunakan kombinasi random dan chain prediction

## License

MIT
