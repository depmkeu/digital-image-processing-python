## Rumus (Laplacian):
## Laplacian 5-point:
##   [ 0, -1,  0]
##   [-1,  4, -1]
##   [ 0, -1,  0]
## Laplacian 9-point I:
##   [-1, -1, -1]
##   [-1,  8, -1]
##   [-1, -1, -1]
## Laplacian 9-point II
##   [-2,  1, -2]
##   [ 1,  4,  1]
##   [-2,  1, -2]
## Hasil: absolute value and clipped to [0,255]

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

# INPUT
path = input("Masukkan nama file citra: ").strip()
try:
    img_rgb = Image.open(path).convert("RGB")
except:
    print("File tidak ditemukan! Pastikan nama file benar.")
    exit()

img_array = np.array(img_rgb)
w, h = img_rgb.size

# Deteksi mode warna
if len(img_array.shape) == 2:
    mode = "Grayscale"
    bands = ["L"]
elif img_array.shape[2] == 3 and np.array_equal(img_array[:,:,0], img_array[:,:,1]) and np.array_equal(img_array[:,:,1], img_array[:,:,2]):
    mode = "Grayscale"
    bands = ["L"]
else:
    mode = "RGB"
    bands = ["R","G","B"]

rasio_aspek = round(w / h, 2)
format_file = os.path.splitext(path)[1].upper()
ukuran_file_kb = round(os.path.getsize(path) / 1024, 2)
nama = os.path.basename(path)

print("\n======================= PROPERTI CITRA =======================")
print(f"Nama Citra           : {nama}")
print(f"- Format file        : {format_file}")
print(f"- Mode warna         : {mode}")
print(f"- Resolusi           : {w} x {h} piksel (lebar x tinggi)")
print(f"- Jumlah kanal warna : {len(bands)} ({', '.join(bands)})")
print(f"- Kedalaman warna    : 8 bit per kanal")
print(f"- Rasio aspek        : {rasio_aspek}")
print(f"- Ukuran file        : {ukuran_file_kb} KB")
print("==============================================================\n")

# Grayscale untuk operasi
img_gray = img_rgb.convert("L")
pixels = img_gray.load()
w, h = img_gray.size

lap5 = np.zeros((h, w), dtype=np.uint8)
lap9_1 = np.zeros((h, w), dtype=np.uint8)
lap9_2 = np.zeros((h, w), dtype=np.uint8)

for y in range(1, h-1):
    for x in range(1, w-1):
        p = [[pixels[x+i, y+j] for i in range(-1,2)] for j in range(-1,2)]

        # Laplacian 5-point (k5)
        k5 = (0 * p[0][0] + -1 * p[0][1] + 0 * p[0][2]
              + -1 * p[1][0] + 4 * p[1][1] + -1 * p[1][2]
              + 0 * p[2][0] + -1 * p[2][1] + 0 * p[2][2])

        # Laplacian 9-point I (k9_1)
        k9_1 = (-p[0][0] - p[0][1] - p[0][2]
                - p[1][0] + 8 * p[1][1] - p[1][2]
                - p[2][0] - p[2][1] - p[2][2])

        # Laplacian 9-point II (k9_2)
        k9_2 = (-2*p[0][0] + 1*p[0][1] - 2*p[0][2]
                + 1*p[1][0] + 4*p[1][1] + 1*p[1][2]
                - 2*p[2][0] + 1*p[2][1] - 2*p[2][2])

        lap5[y, x] = min(abs(k5), 255)
        lap9_1[y, x] = min(abs(k9_1), 255)
        lap9_2[y, x] = min(abs(k9_2), 255)

# Simpan
os.makedirs("edge_results", exist_ok=True)
Image.fromarray(lap5).save("edge_results/laplacian_5.png")
Image.fromarray(lap9_1).save("edge_results/laplacian_9_1.png")
Image.fromarray(lap9_2).save("edge_results/laplacian_9_2.png")

print("Hasil Laplacian disimpan di 'edge_results' (laplacian_*.png)\n")

# Tampilkan
plt.figure(figsize=(15,9))
plt.subplot(2,3,1); plt.imshow(img_rgb); plt.title("Original RGB"); plt.axis("off")
plt.subplot(2,3,2); plt.imshow(img_gray, cmap="gray"); plt.title("Grayscale"); plt.axis("off")
plt.subplot(2,3,3); plt.imshow(lap5, cmap="gray"); plt.title("Laplacian 5-point"); plt.axis("off")
plt.subplot(2,3,4); plt.imshow(lap9_1, cmap="gray"); plt.title("Laplacian 9-point I"); plt.axis("off")
plt.subplot(2,3,5); plt.imshow(lap9_2, cmap="gray"); plt.title("Laplacian 9-point II"); plt.axis("off")
plt.tight_layout(); plt.show()
