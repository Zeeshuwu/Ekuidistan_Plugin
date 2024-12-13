# Ekuidistan Plugin
Ekuidistan Plugin adalah sebuah plugin QGIS 3.0 keatas yang dirancang untuk membuat garis ekuidistan. Garis ekuidistan adalah garis di mana setiap titiknya memiliki jarak yang sama dari titik-titik terdekat pada garis input.
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
- Selanjutnya memilih kepemilikan pulau kecil tersebut, milik siapakah layer pulau kecil tersebut apakah negara A atau negara B.

### 3. Menjalankan Proses
- Pilih opsi untuk menghitung garis ekuidistan berdasarkan negara yang bersebelahan atau berhadapan.
- Klik tombol yang sesuai (misalnya, **"Opposite Line"** untuk negara yang berhadapan atau **"Adjacent Line"** untuk negara yang bersebelahan) untuk memulai proses.

### 4. Melihat Hasil
- Setelah proses selesai, hasil garis ekuidistan akan ditampilkan di peta QGIS.
- Anda dapat menyimpan hasilnya sebagai layer baru atau mengekspornya ke format yang diinginkan.


## Kasus Spesial Half Effect
Dalam pembuatan Median line Half Effect, memerlukan beberapa langkah tambahan, dimana Half Effect sejatinya merupakan garis ekuidistan diantara batas Median Full effect dan Nill Effect pada dua negara, berikut langkahnya :

- **Langkah 1**: Memilih dua negara besar yang harus dibuat ekuidistannya, abaikan pulau kecilnya, pilih no Effect
  
- **Langkah 2**: Setelah itu, pilih kembali dua negara tersebut, tetapi kali ini pilih **Full Effect** dengan memilih layer pulau kecil serta pemiliknya yang sesuai. Ini akan memastikan bahwa pengaruh pulau kecil diperhitungkan dalam perhitungan garis ekuidistan.

- **Langkah 3**: Setelah mendapatkan hasil dari kedua pengaturan tersebut, pilih **Median Line** hasil dari **Full Effect** dan **Median Line** hasil dari **No Effect** sebagai inputan. Dengan cara ini, Anda akan menghasilkan **Median Line** baru di antara keduanya. Median line ini adalah median line untuk **Half Effect**.


## Instalasi

1. Buka QGIS.
2. Pergi ke menu `Plugins` > `Manage and Install Plugins`.
3. Cari `Eqkuidistan` dan klik `Install`.

