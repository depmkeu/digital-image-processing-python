import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# =========================
# INPUT + LOAD (GRAYSCALE)
# =========================
file_path = input("Masukkan path citra: ").strip()
img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

if img is None:
    print("ERROR: Gambar tidak ditemukan!")
    raise SystemExit

h, w = img.shape

# =========================
# PARAMETER β + PILIH MASK
# =========================
beta = float(input("Masukkan nilai beta (β), contoh 2: "))
print("Pilih arah mask emboss:")
print("1. Dari arah kiri")
print("2. Dari arah kanan atas")
pilih = input("Masukkan pilihan (1/2): ").strip()

if pilih == "1":
    kernel = np.array([
        [-beta, 0,  beta],
        [-beta, 1,  beta],
        [-beta, 0,  beta]
    ], dtype=np.float32)
elif pilih == "2":
    kernel = np.array([
        [0,    -beta, -beta],
        [beta,  1,    -beta],
        [beta,  beta,  0]
    ], dtype=np.float32)
else:
    print("Pilihan tidak valid!")
    raise SystemExit

# =========================
# EMBOSS (KONVOLUSI 3x3)
# h(x,y) = ΣΣ f(x+i,y+j) * w(i,j)
# =========================
emboss = img.astype(np.float32).copy()

for y in range(1, h - 1):
    for x in range(1, w - 1):
        total = 0.0

        total += img[y-1, x-1] * kernel[0,0]
        total += img[y-1, x  ] * kernel[0,1]
        total += img[y-1, x+1] * kernel[0,2]

        total += img[y  , x-1] * kernel[1,0]
        total += img[y  , x  ] * kernel[1,1]
        total += img[y  , x+1] * kernel[1,2]

        total += img[y+1, x-1] * kernel[2,0]
        total += img[y+1, x  ] * kernel[2,1]
        total += img[y+1, x+1] * kernel[2,2]

        emboss[y, x] = total  # <-- TANPA +128

emboss_u8 = np.clip(emboss, 0, 255).astype(np.uint8)

# =========================
# SIMPAN OUTPUT
# =========================
os.makedirs("emboss_result", exist_ok=True)
base = os.path.splitext(os.path.basename(file_path))[0]
out_path = f"emboss_result/{base}_emboss_mask{pilih}_beta{beta}.png"
cv2.imwrite(out_path, emboss_u8)

print("Hasil emboss disimpan di:", out_path)

# =========================
# TAMPILKAN
# =========================
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.imshow(img, cmap="gray")
plt.title("Citra Asli")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(emboss_u8, cmap="gray")
plt.title(f"Emboss (β={beta}, mask={pilih})")
plt.axis("off")

plt.tight_layout()
plt.show()
