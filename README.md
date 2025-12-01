# IF3070-K03-G29-AkuBagasAI-Tubes1
> Tugas Besar 1 Dasar Inteligensi Arfisial

# About
Ini merupakan Tugas Besar 1 mata kuliah Dasar Inteligensi Artifisial yang memiliki tujuan agar dapat memahami bagaimana cara mengimplementasikan dan mengevaluasi algoritma-algoritma local search untuk mencari solusi yang optimal dan efisien dalam pengepakan barang (bin packing problem). Optimal dan efisien ini berarti dapat menempatkan sekumpulan barang dengan ukuran yang berbeda-beda ke dalam sejumlah kontainer dengan kapasitas yang sama dengan tujuan akhir dapat menggunakan jumlah kontainer sedikit mungkin.   

Dalam Tugas Besar 1 ini, kami diharapkan dapat mengimplementasikan algoritma local search seperti Simulated Annealing, Genetic Algorithm, Steepest Ascent Hill-Climbing, Stochastic Hill-Climbing, Random Restart Hill-Climbing, dan Hill-Climbing with Sideways Move. Skema yang harus dilakukan dalam proses eksperimen Tugas Besar 1 ini adalah mencatat state awal, state akhir, nilai objective function yang dicapai pada akhir eksperimen, durasi proses pencarian solusi optimal, banyaknya iterasi. banyaknya restart, frekuensi stuck, jumlah populasi, probabilitas mutasi, serta plot nilai objective function terhadap banyak iterasi yang dilalui selama proses eksperimen. Skema eksperimen ini berbeda-beda untuk setiap pendekatan algoritma local search yang telah kami lakukan dalam Tugas Besar 1 ini. 

# Contributors
| NIM       | Nama                     |Pembagian Tugas            |
|-----------|--------------------------|---------------------------|
| 18223115  | Bagas Noor Fadhilah      | ClI, Simulated Annealing  |
| 18223126  | Theresia Ivana M.S.      | Genetic Algorithm         |
| 18223140  | Raihan Muhammad Daffa    | Hill Climbing + bonus HC  |

# Daftar Algoritma Pencarian Lokal 
### Simulated Annealing
Algoritma simulated annealing adalah sebuah algoritma pencarian lokal yang mengikuti prinsip pada fisika yaitu pada probabilitas Boltzmann yang menunjukkan bahwa state dengan energi yang rendah akan selalu memiliki probabilitas lebih tinggi untuk terisi daripada keadaan dengan energi lebih tinggi karena ketika energi tinggi partikel pada tingkat atom akan saling bertumbukan karena pada sistem yang berenergi tinggi partikel-partikel cenderung bergerak dengan kencang.
### Steepest Ascent Hill Climbing
Algoritma steepest ascent hill climbing adalah sebuah algoritma pencarian lokal yang bertujuan untuk menemukan solusi terbaik dengan memperbaiki current state secara iteratif. Algoritma ini diinisiasi dengan state yang acak di mana semua bin berisi item dan weightnya memiliki nilai konstan, namun secara posisi memiliki state yang tidak teratur. Algoritma ini seolah-olah sedang mendaki gunung dengan melihat semua langkah-langkah yang memungkinkan dan menemukan sebuah langkah yang memberikan pengalaman kenaikan paling tinggi (secara curam). Namun, algoritma ini memiliki kelemahan utama yaitu optimum lokal. Algoritma ini hanya melihat dari sebuah puncak (shoulder, local optimum, flat). Namun, tidak melihat puncak yang lainnya yang memiliki ketinggian yang lebih tinggi. Dan langkah-langkah lainnya terlihat menurun dan tidak bisa diraih lebih tinggi. 
### Stochastic Hill Climbing
Berbeda dengan steepest ascent hill climbing, stochastic hill climbing tidak mengevaluasi semua neighbor dari current state. Stochastic hill climbing hanya memilih satu neighbor yang dipilih secara acak pada setiap iterasi untuk dievaluasi. Inisiasi dari algoritma ini sama seperti steepest ascent hill climbing. Jika salah satu hasil tetangga (neighbor) secara acak memiliki nilai yang lebih baik, maka akan langsung berpindah dan langsung mengabaikan tetangga lainnya. Sebaliknya jika salah satu hasil tetangga memiliki nilai yang lebih buruk, maka akan langsung mengabaikan opsi dan harus mencari salah satu tetangga acak yang lebih baik dari sekarang (current). Kelebihan utama dari stochastic hill climbing daripada steepest hill climbing adalah algoritma ini memiliki kecepatan yang tinggi. Steepest ascent hill climbing melihat keseluruhan langkah yang ada, sementara stochastic langsung memilih salah satu opsi dengan (5 atau 10 langkah). Namun, algoritma ini lebih mudah untuk terjebak (stuck) di optimum lokal karena semua langkah acak memiliki kemungkinan besar untuk menurun, selain itu, langkah menuju puncak menjadi aneh dan tidak efisien meskipun langkahnya tetap naik. 
### Random Restart Hill Climbing
Jika Steepest ascent hill climbing dan stochastic hill climbing memiliki kemungkinan untuk terjebak (stuck) pada optimum lokal, maka random restart hill climbing merupakan strategi baru untuk memecahkan permasalahan yang ada pada steepest ascent dan stochastic hill climbing. Sama seperti steepest ascent hill climbing, Algoritma ini diinisiasi dengan state yang acak di mana semua bin berisi item dan weightnya memiliki nilai konstan, namun secara posisi memiliki state yang tidak teratur. Random restart hill climbing melihat semua neighbor dari current state yang dihasilkan dari pembaharuan neighbor dan bergerak ke neighbor yang lebih baik secara objective functionnya. Keunggulan utama dari random restart hill climbing adalah ketika mencapai optimum lokal, algoritma ini akan mencoba dari awal secara random di tempat lain, sehingga algoritma ini akan mustahil untuk terjebak di lokal optimum tertentu. 
### Sideway Moves Hill Climbing
Jika random restart hill climbing diibaratkan “menyerah sebelum berperang”, maka hill climbing with sideway moves diibaratkan “gegabah ketika berperang”. Algoritma Hill Climbing dengan Sideway Moves digunakan untuk mengatasi masalah yang spesifik yang disebut plateau. JIka berada di plateau (dataran), tidak ada pergerakan untuk menuju ke atas karena tidak ada langkah naik dan akan terjebak. Maka dari itu,  algoritma ini memperbolehkan untuk melakukan langkah menyamping (misalnya jika tidak ada tetangga yang lebih baik, tetapi tetangga tersebut memiliki nilai sama, maka boleh pindah ke tetangga tersebut.) Kondisi tersebut didapatkan dari dua hal, jika semua tetangga turun dan tidak ada peluang untuk naik, maka akan berhenti. Jika beberapa tetangga memiliki nilai yang sama maka bisa menggunakan sideways move. Namun, pergerakan menyamping memiliki limitasi bahwa tidak bisa selamanya bisa melakukan gerak menyamping (sideway moves).
### Genetic Algorithm
Genetic Algorithm adalah sebuah algoritma pencarian lokal yang bertujuan untuk memodifikasi gen yang terletak pada kromosom masing-masing dari individu yang terdapat pada suatu populasi. Genetic Algorithm ini merupakan algoritma yang tercipta berdasarkan referensi proses seleksi alam Charles Darwin dan Herbert Spencer, yaitu survival of the fittest. 


# HOW TO RUN
### Menggunakan UV
Gunakan cara ini jika pada laptop Anda sudah ada UV
- Untuk powershell
  ```bash
  # Kloning repositori
  git clone https://github.com/rinmdfa25/IF3070-K03-G29-AkuBagasAI-Tubes1.git

  # Masuk ke direktori dimana main.py ada 
  cd .\src\

  # Setup akan dilakukan secara otomatis oleh UV
  UV run main.py
  ```
Untuk instalasi UV bisa dilihat di https://docs.astral.sh/uv/getting-started/installation/
### Menggunakan ekstensi python pada VScode
Gunakan cara ini jika VScode sudah memiliki ekstensi python
- Untuk powershell
  ```bash
  # Kloning repositori
  git clone https://github.com/rinmdfa25/IF3070-K03-G29-AkuBagasAI-Tubes1.git
  ```
Klik tombol "run python file" yang berada di bagian atas kanan visual editor
### Menggunakan setup Virtual Environment
Gunakan cara ini jika python sudah ada dalam system environment laptop Anda. Pastikan bahwa versi python adalah  >= 3.12.X
- Untuk powershell
  ```bash
  # Kloning repositori
  git clone https://github.com/rinmdfa25/IF3070-K03-G29-AkuBagasAI-Tubes1.git

  # Inisialisasi virtual environment
  python -m venv .venv

  # Aktivasi virtual environment
  .venv/Scripts/Activate.ps1
  # Instalasi dependensi berdasarkan pyproject.toml pada file root
  pip install -e .

  # Masuk ke direktori dimana main.py ada  
  cd .\src\
  # Run projek
  python main.py
  ```
