import cv2 #membaca gambar, mengolah gambar, melakukan transformasi piksel
import numpy as np #membuat array (matriks piksel), operasi matematika, membuat array kosong
import matplotlib.pyplot as plt #menampilkan hasil

## 1) INPUT
img_path = input("Masukkan nama file gambar: ").strip()
img_bgr = cv2.imread(img_path)
if img_bgr is None:
    print("Gambar tidak ditemukan:", img_path)
    raise SystemExit

## convert BGR -> RGB untuk matplotlib
img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
h, w = img.shape[:2]

## 2) TITIK KOTAK A,C,B,D SESUAI SOAL
## A = (0,0)          kiri atas
## C = (w-1,0)        kanan atas
## B = (w-1,h-1)      kanan bawah
## D = (0,h-1)        kiri bawah
Ax, Ay = 0, 0
Cx, Cy = w - 1, 0
Bx, By = w - 1, h - 1
Dx, Dy = 0, h - 1

## 3) STRUKTUR OUTPUT
## segitiga_img  => kanvas kosong utk menampung hanya segitiga
## sisa_img      => kanvas kosong menampung bagian lain
## h_flip        => kanvas kosong menampung hasil pencerminan horizontal 
## combo         => kanvas kosong hasil kombinasi
## zeros_like(img) => membuat array baru berukuran persis kaya img, isinya semua 0 → gambar hitam

segitiga_img = np.zeros_like(img)
sisa_img     = np.zeros_like(img)
h_flip       = np.zeros_like(img)
combo        = np.zeros_like(img)

## 4) CEK APAKAH TITIK P BERADA DI DALAM SEGITIGA (C–D–A) DENGAN RUMUS LUAS
##    - Kalau titik P berada DI DALAM segitiga, maka:
##         luas(P, C, D) + luas(P, D, A) + luas(P, A, C)
##     akan sama (atau hampir sama) dengan: luas(C, D, A)    
##  
#      area(triangle PQR) = abs( x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2) ) / 2
## 1. Hitung luas segitiga besar: area(C, D, A)
##  2. Untuk setiap piksel (x, y), hitung:
##     area1 = area(P, C, D)
##     area2 = area(P, D, A)
##     area3 = area(P, A, C)
## 3. Jika area1 + area2 + area3 ≈ area_total (selisih < tol),
##     maka pixel P berada di dalam segitiga.

## Hitung area_total segitiga C-D-A
area_CDA = abs( # biar ga negatif
    (Cx * (Dy - Ay) + Dx * (Ay - Cy) + Ax * (Cy - Dy))
) / 2.0

## toleransi untuk floating error
tol = 1e-6

## 5) LOOP PER-PIXEL: buat segitiga_img dan sisa_img
## Menentukan apakah pixel berada di dalam segitiga 
for y in range(h): #membaca setiap piksel dalam gambar
    for x in range(w): #y vertikal(baris) dan x horizontal(kolom)

        # hitung area(P, C, D)
        area_PCD = abs(
            (x * (Cy - Dy) + Cx * (Dy - y) + Dx * (y - Cy))
        ) / 2.0

        # hitung area(P, D, A)
        area_PDA = abs(
            (x * (Dy - Ay) + Dx * (Ay - y) + Ax * (y - Dy))
        ) / 2.0

        # hitung area(P, A, C)
        area_PAC = abs(
            (x * (Ay - Cy) + Ax * (Cy - y) + Cx * (y - Ay))
        ) / 2.0

## Memisahkan pixel ke segitiga_img atau sisa_img
        # jika jumlah area sama dengan area_CDA (dengan toleransi) => di dalam segitiga
        if abs((area_PCD + area_PDA + area_PAC) - area_CDA) <= tol:
            ## pixel termasuk segitiga C-D-A
            segitiga_img[y, x] = img[y, x]
        else:
            ## pixel ada di sisa gambar
            sisa_img[y, x] = img[y, x]
            
## Membuat dua transformasi:
        # sekaligus buat h_flip dan combo di sini (agar tidak perlu loop terpisah)
        ## Pencerminan horizontal: x' = w - 1 - x ; y' = y
        xh = (w - 1) - x
        yh = y
        h_flip[yh, xh] = img[y, x]

        ## Pencerminan kombinasi: x' = w - 1 - x ; y' = h - 1 - y
        xc = (w - 1) - x
        yc = (h - 1) - y
        combo[yc, xc] = img[y, x]

## 6) VISUALISASI 6 PANEL
plt.figure(figsize=(18, 10)) #lebar x tinggi (dalam inch)

# plt.subplot(jumlah_baris, jumlah_kolom, posisi_ke)

# (1) Gambar Asli + Garis Potong C->D
ax1 = plt.subplot(2, 3, 1) # panel kiri atas
ax1.imshow(img)
ax1.plot([Cx, Dx], [Cy, Dy], '--', color='yellow', linewidth=2)  ## garis kuning putus-putus pemotong C->D
ax1.set_title("Gambar Asli + Garis Potong C→D")
ax1.text(Ax+3, Ay+12, "A", color='red') 
#Ax+3 geser tulisan huruf A ke kanan 3 pixel, Ay+12 geser tulisan huruf A turun 12 pixel
ax1.text(Cx-18, Cy+12, "C", color='red')
#Cx-18 geser tulisan huruf C ke kiri 18 pixel, Cy+12 geser tulisan huruf C ke bawah 12 pixel
ax1.text(Bx-18, By-12, "B", color='red')
ax1.text(Dx+3, Dy-12, "D", color='red')
ax1.axis('off')

# (2) Segitiga C-D-A
ax2 = plt.subplot(2, 3, 2) #panel tengah atas
ax2.imshow(segitiga_img) #menampilkan gambar ke layar
ax2.set_title("Segitiga Dipotong")
ax2.axis('off') # menghilangkan sumbu (axis) pada plot, tdk menampilkan angka koordinat dll

# (3) Sisa gambar
ax3 = plt.subplot(2, 3, 3) #panel kanan atas
ax3.imshow(sisa_img)
ax3.set_title("Sisa Gambar Setelah Dipotong")
ax3.axis('off')

# (4) Pencerminan Horizontal
ax4 = plt.subplot(2, 3, 4) #panel kanan bawah
ax4.imshow(h_flip)
ax4.set_title("Pencerminan Horizontal (x' = w - 1 - x)")
ax4.axis('off')

# (5) Pencerminan Kombinasi
ax5 = plt.subplot(2, 3, 5)
ax5.imshow(combo)
ax5.set_title("Pencerminan Kombinasi (x' = w-1-x, y' = h-1-y)")
ax5.axis('off')

# (6) Hasil akhir + label urutan B-D-A-C
ax6 = plt.subplot(2, 3, 6)
ax6.imshow(combo)
ax6.set_title("HASIL AKHIR → URUTAN TITIK: B – D – A – C")

## Hitung koordinat titik setelah kombinasi (manual kalkulasi)
A_after = ((w - 1) - Ax, (h - 1) - Ay)
C_after = ((w - 1) - Cx, (h - 1) - Cy)
B_after = ((w - 1) - Bx, (h - 1) - By)
D_after = ((w - 1) - Dx, (h - 1) - Dy)

order_names = ['B', 'D', 'A', 'C']
order_coords = [B_after, D_after, A_after, C_after]

for i, name in enumerate(order_names): #i= nomor urut 0,1,2,3 dan name huruf titik B,D,A,C
    x_c, y_c = order_coords[i]
    ax6.scatter([x_c], [y_c], s=80, c='lime') #menggambar titik berwarna lime di (x_c (x titik), y_c(y titik)). s=80 menentukan ukuran titik
    ax6.text(x_c + 8, y_c + 8, f"{name}", color='yellow', fontsize=12, weight='bold')

# menggambar panah dari titik ke titik berikutnya
## ketika i=0 → hubungkan titik 0 → 1 (B → D)
## ketika i=1 → hubungkan titik 1 → 2 (D → A)
## ketika i=2 → hubungkan titik 2 → 3 (A → C)
## ketika i=3 → hubungkan titik 3 → 0 (C → B)
## (karena (3+1) % 4 = 0)

for i in range(len(order_coords)):
    x0, y0 = order_coords[i]
    x1, y1 = order_coords[(i+1) % len(order_coords)]
    ax6.annotate("", xy=(x1, y1), xytext=(x0, y0),
                 arrowprops=dict(arrowstyle="->", color="yellow", lw=1.2))

ax6.axis('off')

plt.tight_layout()
plt.savefig("hasil_cobacoba1.png", dpi=150)
plt.show()

print("Selesai. File disimpan: cobacoba1.png")
print("Kesimpulan: urutan akhir titik setelah kombinasi = B – D – A – C")