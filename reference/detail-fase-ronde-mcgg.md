# Detail Fase dan Ronde Magic Chess Go Go

Berikut adalah detail pembagian fase dan ronde dalam Magic Chess Go Go:

## Phase 1
- **Ronde i-1:** Lawan Monster
- **Ronde i-2:** Lawan User
- **Ronde i-3:** Lawan User
- **Ronde i-4:** Lawan User

## Phase 2 (dan Phase Selanjutnya)
- **Ronde ii-1:** Lawan User
- **Ronde ii-2:** Lawan User
- **Ronde ii-3:** Lawan Monster
- **Ronde ii-4:** Lawan User
- **Ronde ii-5:** Lawan User
- **Ronde ii-6:** Lawan User

## Phase 3 (dan Phase Selanjutnya)
- **Ronde iii-1:** Lawan User
- **Ronde iii-2:** Lawan User
- **Ronde iii-3:** Lawan Monster
- **Ronde iii-4:** Lawan User
- **Ronde iii-5:** Lawan User
- **Ronde iii-6:** Lawan User

> Catatan: Pola pada phase 2 akan berulang untuk phase berikutnya (iii, iv, dst) dengan urutan ronde yang sama.


Dokumentasi ini membantu memahami urutan lawan pada setiap fase dan ronde di Magic Chess Go Go.

Sistem prediksi lawan di Magic Chess Go Go memungkinkan pemain menebak lawan pada ronde tertentu berdasarkan pola yang sudah teridentifikasi. Berikut ringkasannya:

- **Ronde i-2, i-3, dan ii-1**: Bersifat *random* (tidak bisa diprediksi).
- **Ronde i-4, ii-2, dan ii-4**: Dapat diprediksi berdasarkan urutan lawan sebelumnya.

## Cara Prediksi Lawan (berdasarkan urutan fase)
1. Catat lawan pertama ("mantan pertama") yang kamu hadapi di ronde i-2.
2. Ronde i-3 lawan masih random.
3. **Ronde i-4:** Lawanmu adalah lawan dari "mantan pertama" di ronde i-3.
4. Ronde ii-1 kembali random.
5. **Ronde ii-2:** Lawanmu adalah lawan dari "mantan pertama" di ronde ii-1.
6. **Ronde ii-4:** Lawanmu adalah lawan dari lawanmu di ronde i-4 pada ronde ii-2.
7. Setelah ronde berikutnya, urutan akan berulang atau random lagi jika ada pemain yang tereliminasi.

> Pola prediksi ini hanya berlaku jika semua pemain masih aktif. Jika ada pemain yang keluar/tusun, urutan bisa berubah/random.

Tips: Selalu catat urutan lawan di setiap ronde dan fokus pada ronde prediksi (i-4, ii-2, ii-4) untuk strategi.