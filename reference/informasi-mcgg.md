# Informasi Dasar Game: Magic Chess Go Go

## Struktur Permainan

* Total pemain: 8 player
* Mode permainan: survival (eliminasi)
* Tujuan: menjadi pemain terakhir yang bertahan

### Karakteristik:

* Setiap ronde, pemain akan bertarung melawan:

  * Player lain
  * atau Monster (PvE)
* Jika HP habis, pemain akan tereliminasi (tusun)
* Jumlah pemain akan terus berkurang:
  8 → 7 → 6 → ... → 2 → 1 (winner)

---

## Sistem Fase dan Ronde

Berdasarkan dokumentasi :

### Phase 1

* i-1: Lawan Monster
* i-2: Lawan Player
* i-3: Lawan Player
* i-4: Lawan Player

---

### Phase 2

* ii-1: Lawan Player
* ii-2: Lawan Player
* ii-3: Lawan Monster
* ii-4: Lawan Player
* ii-5: Lawan Player
* ii-6: Lawan Player

---

### Phase 3 dan seterusnya

* Pola sama seperti Phase 2:

  * Player
  * Player
  * Monster
  * Player
  * Player
  * Player

---

## Tipe Ronde (Berdasarkan Prediktabilitas)

### Ronde Random

Tidak bisa diprediksi:

* i-2
* i-3
* ii-1

---

### Ronde Semi-Predictable

Bisa diprediksi dengan pola tertentu:

* i-4
* ii-2
* ii-4

---

## Mekanisme Prediksi Lawan

### Konsep utama

Menggunakan hubungan antar lawan (chain)

### Aturan:

1. Catat lawan pertama di ronde i-2 (mantan pertama)

2. Ronde i-3 bersifat random

3. Ronde i-4:

   * Lawan adalah lawan dari mantan pertama di ronde i-3

4. Ronde ii-1 bersifat random

5. Ronde ii-2:

   * Lawan adalah lawan dari mantan pertama di ronde ii-1

6. Ronde ii-4:

   * Lawan adalah lawan dari lawan di ronde i-4 pada ronde ii-2

---

## Catatan Penting

* Pola prediksi lawan hanya berlaku ketika semua 8 pemain masih aktif (belum ada yang tereliminasi).
* Jika terdapat pemain yang tereliminasi (tusun):

  * Sistem matchmaking dapat berubah
  * Urutan lawan bisa menjadi acak (random)
  * Pola prediksi sebelumnya tidak lagi valid secara penuh
* Semakin sedikit jumlah pemain:

  * Kemungkinan bertemu lawan yang sama akan meningkat
  * Akurasi prediksi berbasis pola akan menurun

---

## Kesimpulan Sistem Game

* Game berbasis:

  * 8 player
  * survival elimination
  * round-based combat

* Matchmaking menggunakan kombinasi:

  * random
  * pola berantai (chain prediction)

* Kompleksitas meningkat seiring:

  * jumlah pemain berkurang
  * history ronde semakin panjang

---
