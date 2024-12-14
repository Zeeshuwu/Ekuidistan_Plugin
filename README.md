# Ekuidistan Plugin
![image](https://github.com/user-attachments/assets/373d6cc2-dc3c-4856-963c-ed1a18e9e0ec)

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
![image](https://github.com/user-attachments/assets/ca027151-52a4-48fe-a5e8-b7c274c583c5)

- Di dialog plugin, pilih dua layer garis yang akan digunakan sebagai input (misalnya, garis pangkal dari dua negara).
- Pastikan kedua layer memiliki sistem koordinat yang sama.

### 2. Pengaturan Bobot Pulau Kecil


- Dalam pemilihan layer A dan layer B juga harus mempertimbangkan keberadaan pulau kecil apakah pulau kecil tersebut memiliki **full effect**, **null effect**, atau **half effect**. Jika kasus pulau kecil tersebut tidak memiliki efek/dampak (null effect), maka layer A dan layer B yang menjadi masukan adalah garis pangkal dua negara yang merupakan daratan utama. 
- Jika kasusnya pulau kecil tersebut memberi dampak pada garis tengah (ekuidistan) yang dihasilkan, maka layer A dan layer B yang menjadi masukan adalah garis pangkal pulau kecil di negara yang memiliki pulau kecil dan garis pangkal daratan utama pada negara lainnya. Dari masukan layer A dan layer B akan menghasilkan keluaran dua garis masukan itu sendiri.


### 3. Menjalankan Proses
- Pilih opsi untuk menghitung garis ekuidistan berdasarkan negara yang bersebelahan atau berhadapan.
- Klik tombol yang sesuai (misalnya, **"Opposite Line"** untuk negara yang berhadapan atau **"Adjacent Line"** untuk negara yang bersebelahan) untuk memulai proses.

### 4. Melihat Hasil
- Setelah proses selesai, hasil garis ekuidistan akan ditampilkan di peta QGIS hasil berupa group layer yang berisi median line, Equidistance point dan boundary layer.
  ![image](https://github.com/user-attachments/assets/fb9c7779-7b87-403b-952d-eb6dbf789990)

- Anda dapat menyimpan hasilnya sebagai layer baru atau mengekspornya ke format yang diinginkan.
- 
*Kasus Pada Opposite States*
![image](https://github.com/user-attachments/assets/b80e9f14-cc25-4e39-931f-61d3d2a00f7f)

*Kasus Pada Adjacent States*



## Kasus Spesial Half Effect
Dalam pembuatan Median line Half Effect, memerlukan beberapa langkah tambahan, dimana Half Effect sejatinya merupakan garis ekuidistan diantara batas Median Full effect dan Nill Effect pada dua negara, berikut langkahnya :

- **Langkah 1**: Memilih dua negara besar yang harus dibuat ekuidistannya, abaikan pulau kecilnya, pilih no Effect
  
- **Langkah 2**: Setelah itu, pilih kembali dua negara tersebut, tetapi kali ini pilih **Full Effect** dengan memilih layer pulau kecil serta pemiliknya yang sesuai. Ini akan memastikan bahwa pengaruh pulau kecil diperhitungkan dalam perhitungan garis ekuidistan. selanjutnya masukkan median **No Effect** pada kolom untuk mengambil emdian line no effect tersebut

- **Langkah 3**:
  
- Setelah mendapatkan hasil dari kedua pengaturan tersebut, pilih **Median Line** hasil dari **Full Effect** dan **Median Line** hasil dari **No Effect** sebagai inputan. Dengan cara ini, Anda akan menghasilkan **Median Line** baru di antara keduanya. Median line ini adalah median line untuk **Half Effect**.




## Instalasi

1. Mendownload semua dependencies dan file pada branch main di repository ini
2. membuka kotak dialog Plugins pada menu Plugins → Manage and Install Plugins, kemudian meng-install plugin dengan cara klik Install from ZIP dan mengisi ZIP file dengan ZIP yang sebelumnya telah diunduh pada GitHub. 
![image](https://github.com/user-attachments/assets/b780138d-5101-4fc4-a395-2ee084211e37)
3. Setelah plugin berhasil di install, maka  plugin dapat ditemukan pada penyimpanan plugin yang telah di install. Dapat dilihat pada gambar dibawah ini
   
  ![image](https://github.com/user-attachments/assets/1922da0f-d6eb-4ef2-b822-d1b545acba07)

4. Maka plugin ekuidistan dapat digunakan

## Credits
Plugin ini dibuat oleh Kelompok 8 PRGG Departemen Teknik Geodesi Universitas Gadjah Mada
1. Mohammad Zulfi Rahadi Putra		
2. Vinsensius Budi Pranata		
3. Zahra Tul Fuada		
4. Dhewa Ragil Saputra	
5. Krishna Duta Wibisono 

Copyright (c) 2024 Kelompok 8 PRGG

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Plugin.



