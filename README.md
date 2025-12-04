# IF3070-K03-G29-AkuBagasAI-Tubes1
> Tugas Besar Teknologi Sistem Terintegrasi (Integrated Systems Technology) II3160

# About
Tugas besar ini merupakan latihan untuk membuat sebuah layanan API yang didasari dengan pengembangan berbasis DDD (Domain Driven Design). Layanan yang dikembangkan pada tugas ini adalah sebuah layanan sistem rekomendasi musik yang bersifat PoC (Proof of Concept). Untuk kondisi nyatanya, layanan ini bisa akan diintegrasikan dengan suatu layanan yang lebih besar seperti aplikasi streaming musik. Layanan ini dibangun diatas framework FastAPI milik Python. Perlu digarisbawahi bahwa lagu-lagu yang diambil dari Spotify tidak memiliki feature yang bisa dibandingkan dengan feature dataset lagu di file csv sehingga saya melakukan pembuatan feature artifisial agar layanan PoC ini bisa berjalan.

# Struktur Folder
  ```bash
    .
    ├── pycache
    ├── .venv
    ├── app/
    │ ├── model/
    │ │ ├── __init__.py
    │ │ └── songFeatures.py                 # Model lagu
    │ ├── recommendation/
    │ │ ├── __init__.py
    │ │ ├── dataset.csv                     # Mockup data 84.000 lagu
    │ │ └── recommendationEngine.py         # Cosine similarity
    │ ├── router/
    │ │ ├── __init__.py
    │ │ ├── authentication.py               # Kebutuhan autentikasi
    │ │ ├── calculate_preference.py         # endpoint kalkulasi vektor
    │ │ ├── recommendation.py               # endpoint Rekomendasi lagu
    │ │ └── track_history.py                # endpoint ETL data ke mongoDB
    │ ├── utility/
    │ │ ├── __init__.py
    │ │ └── client.py                       # Singleton client mongoDB
    │ ├── __init__.py
    │ ├── config.py                         # Ekstrak variabel venv.
    │ ├── dependency.py                     # Validasi JWT dan user_id
    │ └── main.py # Entrypoint
    ├── .dockerignore
    ├── .env                                # Variable Lingkungan
    ├── gitignore
    ├── .python-version
    ├── compose.yaml                        # Compose-up
    ├── Dockerfile                          # Konfigurasi Docker Image
    ├── pyproject.toml
    ├── README.md
    └── uv.lock
  ```

# Daftar Endpoint
|Method        | Endpoint               | Fungsi                                                     |
|--------------|------------------------|------------------------------------------------------------|
| GET          | /login                 | Authentikasi OAuth Spotify                                 | 
| GET          | /callback              | Penerimaan data atau callback dari autentikasi Spotify     | 
| GET          | /track-history         | Pengembalian 20 lagu terakhir yang didengar oleh pengguna  | 
| GET          | /calculate-preference  | Perhitungan vektor profil pengguna                         | 
| GET          | /get-recommendation    | Pengembalian 5 lagu yang direkomendasikan oleh sistem      | 

# Prosedur Replikasi Layanan
### Mongodb
1. Lakukan registrasi akun MongoDB di link berikut : https://www.mongodb.com/
2. Masuk ke dashboard MongoDB
3. Create sebuah Cluster
4. Buat sebuah database pada cluster tersebut dengan nama Spotify
5. Kembali ke dashboard utama
6. Dapatkan link database dengan tombol connect new
7. Salin link berikut mongodb+srv://{username}:<db_password>@cluster0.owniowu.mongodb.net/?appName=Cluster0
8. Ubah <db_password> dengan password MongoDB yang diberikan saat melakukan registrasi
### Spotify Developer
1. Buat akun Spotify dengan mengunjungi link berikut : https://developer.spotify.com/
2. Masuk ke Dashboard
3. Klik tombol Create app
4. Masukkan field Redirect URIs dengan (http://127.0.0.1:5000/callback)
5. Isi semua field dan klik Save
6. Salin Client ID serta Client Secret yang diberikan oleh Spotify
### Environment Variables
Buatlah sebuah .env pada direktori utama dan penuhi file berikut dengan variabel dibawah ini
  ```bash
      DATABASE_URI={URI yang diberikan oleh MongoDB pada bagian MongoDB prosedur ke 7}
      CLIENT_SECRET={Client Secret yang diberikan oleh Spotify}
      CLIENT_ID={Client ID yang diberikan oleh Spotify}
      SECRET_KEY={32 Hex}
      AUTH_URL=https://accounts.spotify.com/authorize
      TOKEN_URL=https://accounts.spotify.com/api/token
      API_BASE_URL=https://api.spotify.com/v1/
      REDIRECT_URI={URI yang didefinisikan saat pengisian kolom Redirect URIs}
  ```

# HOW TO RUN
### Menggunakan UV
Gunakan cara ini jika pada laptop Anda sudah ada UV
- Untuk powershell
  ```bash
  # Kloning repositori
  git clone https://github.com/Elbiji/poc-music-recommendation-system.git

  # Sinkronisasi 
  uv sync

  # Run aplikasi
  uv run uvicorn app.main:app --reload --port 5000 
  ```
Untuk instalasi UV bisa dilihat di https://docs.astral.sh/uv/getting-started/installation/
### Menggunakan Docker Compose
Gunakan cara ini jika VScode sudah memiliki ekstensi python
- Untuk powershell
  ```bash
  # Kloning repositori
  git clone https://github.com/Elbiji/poc-music-recommendation-system.git

  # Docker compose running on background
  docker compose up -d 
  ```
Pastikan bahwa dalam laptop Anda ada Docker Desktop Application dan sudah dinyalakan 
### Menggunakan Docker Build
- Untuk powershell
  ```bash
  # Kloning repositori
  git clone https://github.com/Elbiji/poc-music-recommendation-system.git

  # Docker run
  docker run -d ` -p 5000:5000 ` --env-file ./.env ` poc-music-recommendation-system  
  ```
   
