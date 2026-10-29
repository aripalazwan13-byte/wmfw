PHOTO SORTER - HUMAS SMKN 1 STABAT
===================================

FITUR
- GUI dinamis dengan tema gelap dan terang.
- Pratinjau foto dan daftar foto dari folder sumber.
- Tombol angka 1-9 untuk menyortir foto dengan cepat.
  1 = Acara
  2 = Fotbar
  3-9 = slot folder tambahan yang dapat dibuat sendiri.
- Foto disalin ke folder hasil; file sumber tidak dipindahkan atau dihapus.
- Watermark opsional: logo di posisi tengah bawah, opacity logo 40%,
  teks kecil @humassmkn1stabat di bawah logo.
- JPG, JPEG, PNG, WebP, BMP, TIF, TIFF.

CARA MENJALANKAN DI WINDOWS
1. Install Python 3.10 atau lebih baru dari python.org.
2. Buka Command Prompt di folder program.
3. Jalankan: pip install -r requirements.txt
4. Jalankan: python photo_sorter.py

PENGGUNAAN
1. Klik Pilih pada Folder foto dan pilih folder berisi foto.
2. Tentukan Folder hasil.
3. Untuk watermark, centang Tambahkan watermark saat menyortir.
4. Pilih logo PNG jika logo tidak bernama logo.png atau berada di folder lain.
5. Pilih foto di daftar, lalu tekan angka 1-9 atau klik tombol folder di bawah.
6. Gunakan tombol panah kiri/kanan untuk berpindah foto.

CATATAN
- Letakkan logo.png di samping photo_sorter.py agar terpilih otomatis.
- Watermark hanya ditambahkan pada salinan di folder hasil, bukan foto asli.
- Tombol 1 dan 2 sudah ditetapkan untuk Acara dan Fotbar.
