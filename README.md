# Cheat Clip Pro

**Cheat Clip Pro** adalah aplikasi untuk membantu mengambil bagian video, menyusun klip pendek, melakukan render, menambahkan subtitle, melihat pratinjau, dan mengunduh hasil render maupun paket ZIP.

> **Catatan penting:** APK Android adalah antarmuka aplikasi. Proses analisis, download sumber, dan render dijalankan oleh backend Python yang harus aktif di perangkat/server. Pada konfigurasi Android saat ini, APK terhubung ke backend lokal di `http://localhost:8000`.

## Fitur

- Analisis video dan pemilihan segmen klip.
- Pengunduhan video/segmen menggunakan backend.
- Pengaturan klip dan proses batch render.
- Subtitle dan pengaturan tampilan video.
- Pratinjau hasil render.
- Unduh video hasil render dan paket ZIP.

Fitur yang tersedia dapat berubah mengikuti versi aplikasi.

## Instalasi Android

### 1. Pasang APK

1. Buka halaman [GitHub Actions](https://github.com/kzeee-dev/cheat-clip-pro/actions).
2. Pilih workflow **Build Android APK** dan buka run dengan status **Success**.
3. Di bagian **Artifacts**, unduh `cheat-clip-pro-debug-apk`.
4. Ekstrak file ZIP artifact.
5. Buka `app-debug.apk` di Android dan ikuti proses instalasi. Jika diminta, izinkan instalasi aplikasi dari sumber tersebut.

> Artifact Actions bersifat sementara dan dapat kedaluwarsa. Untuk distribusi jangka panjang, gunakan halaman **Releases** setelah tersedia rilis APK.

### 2. Siapkan backend di Android

APK memerlukan backend yang berjalan di perangkat yang sama pada port **8000**. Salah satu cara yang digunakan proyek ini adalah Termux + Ubuntu melalui proot-distro.

1. Pasang **Termux** dari sumber resminya (F-Droid atau repositori GitHub resmi Termux).
2. Buka Termux, lalu jalankan:

```bash
pkg update && pkg upgrade -y
pkg install git nodejs-lts proot-distro ffmpeg curl -y
proot-distro install ubuntu
```

3. Masuk ke Ubuntu dan pasang kebutuhan sistem:

```bash
proot-distro login ubuntu
apt update
apt install -y python3 python3-pip python3-venv ffmpeg git
exit
```

4. Kembali ke Termux, clone proyek:

```bash
cd ~
git clone https://github.com/kzeee-dev/cheat-clip-pro.git
cd cheat-clip-pro
```

5. Buat virtual environment Python dan pasang dependency backend. Jalankan dari Termux:

```bash
proot-distro login ubuntu -- bash -lc 'cd /data/data/com.termux/files/home/cheat-clip-pro && python3 -m venv .venv && .venv/bin/python -m pip install --upgrade pip && .venv/bin/python -m pip install -r backend/requirements.txt'
```

Instalasi dependency AI/video bisa besar dan lama. Jika perintah selesai tanpa error, jalankan backend dari Termux:

```bash
bash start.sh
```

Tunggu sampai terminal menampilkan bahwa server berjalan di port `8000`. Pada penggunaan pertama, skrip akan memeriksa Python dan memasang dependency dari `backend/requirements.txt` bila belum tersedia. Paket AI seperti PyTorch dan Whisper berukuran besar; instalasi pertama dapat memakan waktu lama, data internet, dan ruang penyimpanan yang cukup. Jangan tutup Termux selama proses berjalan.

Jika muncul pesan `node: command not found` saat skrip masuk ke Ubuntu, jalankan alternatif berikut dari Termux (bukan dari prompt Ubuntu):

```bash
proot-distro login ubuntu -- bash -lc 'export PATH="/data/data/com.termux/files/usr/bin:$PATH"; cd /data/data/com.termux/files/home/cheat-clip-pro; node scripts/start-backend.js'
```

6. Setelah server aktif, biarkan sesi Termux tetap terbuka dan pindah ke aplikasi **Cheat Clip Pro**. APK Android pada konfigurasi ini menghubungkan diri ke backend lokal `http://localhost:8000`.

7. Untuk menghentikan backend, kembali ke sesi Termux yang menjalankannya lalu tekan `CTRL + C`. Untuk penggunaan berikutnya, buka Termux, masuk ke folder proyek (`cd ~/cheat-clip-pro`), lalu jalankan `bash start.sh` lagi.

**Jika muncul `node: command not found` di Ubuntu**, jalankan backend dengan path Node.js Termux:

```bash
proot-distro login ubuntu -- bash -lc 'export PATH="/data/data/com.termux/files/usr/bin:$PATH"; cd /data/data/com.termux/files/home/cheat-clip-pro; node scripts/start-backend.js'
```

### 3. Menggunakan aplikasi

1. Pastikan backend sudah aktif.
2. Buka Cheat Clip Pro.
3. Masukkan sumber video dan API key yang diminta aplikasi (jika menggunakan fitur AI).
4. Pilih segmen dan pengaturan klip.
5. Jalankan render, periksa hasilnya melalui pratinjau, lalu unduh video atau ZIP.

## Instalasi untuk Windows / macOS / Linux

### Kebutuhan

- Node.js 22 atau lebih baru.
- Python 3.12 direkomendasikan.
- FFmpeg.
- Git.

### Langkah instalasi

Clone repository:

```bash
git clone https://github.com/kzeee-dev/cheat-clip-pro.git
cd cheat-clip-pro
```

Install dependency frontend:

```bash
npm ci
```

Buat virtual environment Python dan install dependency backend.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
```

Pastikan FFmpeg tersedia di PATH, lalu jalankan:

```bash
npm run dev
```

Aplikasi web tersedia di `http://localhost:5173` dan backend API di `http://localhost:8000`. Dokumentasi API tersedia di `http://localhost:8000/docs`.

> Instalasi backend memerlukan dependency pemrosesan video dan AI yang cukup besar. Waktu instalasi bergantung pada sistem operasi, arsitektur CPU, dan koneksi internet.

## Build APK sendiri

1. Buka tab **Actions** di repository.
2. Pilih workflow **Android debug APK**.
3. Klik **Run workflow** dan pilih branch yang ingin dibangun.
4. Tunggu sampai workflow berstatus **Success**.
5. Unduh artifact `cheat-clip-pro-debug-apk`, lalu ekstrak untuk mendapatkan APK.

Workflow menggunakan Node.js 22 dan Java 21 untuk membangun APK debug.

## Konfigurasi dan keamanan

- Jangan commit file `.env`, API key, password, token, atau file cookies.
- Jangan membagikan file cookies YouTube kepada orang lain. Cookies dapat memberikan akses ke sesi akun.
- API key Gemini dapat dimasukkan melalui antarmuka aplikasi bila fitur tersebut memintanya.
- Jika backend dipasang di server lain, konfigurasi alamat API dan akses jaringan harus disesuaikan. APK Android pada konfigurasi saat ini menggunakan `localhost:8000`.

## Troubleshooting

| Masalah | Yang perlu diperiksa |
|---|---|
| Aplikasi tidak terhubung ke backend | Pastikan Termux dan backend masih berjalan pada port 8000. |
| `node: command not found` | Tambahkan direktori Node.js Termux ke PATH seperti contoh di atas. |
| FFmpeg tidak ditemukan | Install FFmpeg di lingkungan tempat backend dijalankan dan pastikan tersedia di PATH. |
| Instalasi dependency gagal | Periksa versi Python, arsitektur perangkat, ruang penyimpanan, dan log pip. |
| Download video gagal | Periksa koneksi internet, dukungan sumber video, dan konfigurasi cookies bila diperlukan. |
| APK tidak bisa dipasang sebagai pembaruan | Versi debug dari build yang berbeda bisa memiliki tanda tangan berbeda. Jika Android menolak pembaruan, simpan data penting lalu hapus versi lama sebelum memasang APK baru. |

## Batasan dan tanggung jawab penggunaan

Gunakan aplikasi hanya untuk video yang kamu miliki, berhak gunakan, atau diizinkan untuk diunduh dan diproses. Patuhi ketentuan layanan platform sumber video serta hukum hak cipta yang berlaku. Cheat Clip Pro tidak berafiliasi dengan YouTube atau platform pihak ketiga lainnya.

## Kontribusi dan lisensi

Saran, laporan bug, dan kontribusi dapat dikirim melalui [GitHub Issues](https://github.com/kzeee-dev/cheat-clip-pro/issues).

**Lisensi proyek belum ditetapkan.** Jangan menganggap source code ini telah diberikan di bawah lisensi open-source tertentu sampai file lisensi resmi ditambahkan.
