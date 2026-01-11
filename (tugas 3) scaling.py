from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os

# Input Gambar
image_path = input("Masukkan nama file gambar: ").strip()

try:
    img = Image.open(image_path).convert("RGB")
except:
    print("File tidak ditemukan!")
    exit()

# Konversi ke array NumPy
img_array = np.array(img)

# Deteksi Mode Warna
if len(img_array.shape) == 2:
    mode = "Grayscale"
    bands = ["L"]
elif img_array.shape[2] == 3 and np.array_equal(img_array[:, :, 0], img_array[:, :, 1]) and np.array_equal(img_array[:, :, 1], img_array[:, :, 2]):
    mode = "Grayscale"
    bands = ["L"]
else:
    mode = "RGB"
    bands = ["R", "G", "B"]

# Properti Citra
w, h = img.size
format_file = os.path.splitext(image_path)[1].upper()
ukuran_file_kb = round(os.path.getsize(image_path) / 1024, 2)
rasio_aspek = round(w / h, 2)

print("\n======================= PROPERTI CITRA =======================")
print(f"- Format file        : {format_file}")
print(f"- Mode warna         : {mode}")
print(f"- Resolusi           : {w} x {h} piksel (lebar x tinggi)")
print(f"- Jumlah kanal warna : {len(bands)} ({', '.join(bands)})")
print(f"- Kedalaman warna    : 8 bit per kanal")
print(f"- Rasio aspek        : {rasio_aspek}")
print(f"- Ukuran file        : {ukuran_file_kb} KB")
print("==============================================================\n")

# Input faktor penskalaan
Sh = float(input("Masukkan faktor skala horizontal (Sh): "))
Sv = float(input("Masukkan faktor skala vertikal (Sv): "))

# Hitung ukuran baru
w_new = int(w * Sh)
h_new = int(h * Sv)

print("\n======================= HASIL PENSKALAAN ======================")
print(f"- Skala Horizontal (Sh): {Sh}")
print(f"- Skala Vertikal (Sv)  : {Sv}")
print(f"- Resolusi Baru        : {w_new} x {h_new} piksel")
print("==============================================================\n")

# Proses penskalaan
scaled_img = Image.new("RGB", (w_new, h_new))

for y_new in range(h_new):
    for x_new in range(w_new):
        # Koordinat asal (sesuai rumus invers: x = x'/Sh, y = y'/Sv)
        x_src = int(x_new / Sh)
        y_src = int(y_new / Sv)

        if 0 <= x_src < w and 0 <= y_src < h:
            pixel = img.getpixel((x_src, y_src))
            scaled_img.putpixel((x_new, y_new), pixel)

# Simpan hasil
os.makedirs("scaling_result", exist_ok=True)
base_name = os.path.splitext(os.path.basename(image_path))[0]
output_path = f"scaling_result/{base_name}_scaling_Sh{Sh}_Sv{Sv}.png"
scaled_img.save(output_path)

print(f"Hasil penskalaan berhasil disimpan di: {output_path}\n")

# Tampilkan hasil
plt.figure("Penskalaan (Scaling)", figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.imshow(img)
plt.title("Citra Asli")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.imshow(scaled_img)
plt.title(f"Hasil Scaling (Sh={Sh}, Sv={Sv})")
plt.axis("off")

plt.tight_layout()
plt.show()
