# Ekuidistan_Plugin
Eqkuidistan Plugin adalah sebuah plugin QGIS yang dirancang untuk membuat garis ekuidistan. Garis ekuidistan adalah garis di mana setiap titiknya memiliki jarak yang sama dari titik-titik terdekat pada garis input.
Plugin ini menggunakan algoritma diagram Voronoi untuk menghasilkan garis ekuidistan dengan tingkat presisi tinggi.

## Fitur Utama
- Menggunakan algoritma diagram Voronoi untuk menghasilkan garis ekuidistan dengan tingkat presisi tinggi.
- Mempertimbangkan faktor-faktor penting dalam delimitasi maritim, seperti:
  - **Bobot Pulau Kecil**: Mempertimbangkan pengaruh pulau kecil dalam perhitungan.
  - **Negara yang Bersebelahan**: Mempertimbangkan interaksi garis dasar dari negara-negara yang berbatasan.
  - **Negara yang Berhadapan**: Memastikan garis ekuidistan mencerminkan hubungan geografis yang seimbang.

## Saksikan Saya!

Jika Anda ingin melihat Plugin Eqkuidistan beraksi, cukup klik video di bawah ini.

- **Negara Berhadapan (Opoosite States)**  
 
- **Negara Bersebelahan (Adjacent States)**  


- **Kasus Half Effect**  

### 1. Memilih Layer Input
- Di dialog plugin, pilih dua layer garis yang akan digunakan sebagai input (misalnya, garis pangkal dari dua negara).
- Pastikan kedua layer memiliki sistem koordinat yang sama.

### 2. Pengaturan Bobot Pulau Kecil
- Jika ada pulau kecil yang mempengaruhi batas maritim, pilih layer pulau kecil tersebut pada kotak **smallisland** dan atur bobotnya sesuai dengan kebutuhan (misalnya, pilih antara **Full Effect** atau **No Effect**).

### 3. Menjalankan Proses
- Pilih opsi untuk menghitung garis ekuidistan berdasarkan negara yang bersebelahan atau berhadapan.
- Klik tombol yang sesuai (misalnya, **"Opposite Line"** untuk negara yang berhadapan atau **"Adjacent Line"** untuk negara yang bersebelahan) untuk memulai proses.

### 4. Melihat Hasil
- Setelah proses selesai, hasil garis ekuidistan akan ditampilkan di peta QGIS.
- Anda dapat menyimpan hasilnya sebagai layer baru atau mengekspornya ke format yang diinginkan.
- 
## Instalasi

1. Buka QGIS.
2. Pergi ke menu `Plugins` > `Manage and Install Plugins`.
3. Cari `Eqkuidistan` dan klik `Install`.

