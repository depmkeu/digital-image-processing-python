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

# Konversi ke array NumPy untuk analisis warna
img_array = np.array(img)

# Deteksi Mode Warna (Grayscale / RGB)
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

# Pemotongan (Cropping)
print("Masukkan koordinat area yang ingin di-crop:")
xL = int(input("x kiri (xL): "))
yT = int(input("y atas (yT): "))
xR = int(input("x kanan (xR): "))
yB = int(input("y bawah (yB): "))

# Validasi agar tidak keluar batas
if xL < 0 or yT < 0 or xR > w or yB > h or xL >= xR or yT >= yB:
    print("Koordinat cropping tidak valid atau di luar batas citra!")
    exit()

# Hitung ukuran hasil crop
w_new = xR - xL
h_new = yB - yT

print("\n======================= PROPERTI CROPPING =======================")
print(f"- Titik kiri atas    : ({xL}, {yT})")
print(f"- Titik kanan bawah  : ({xR}, {yB})")
print(f"- Lebar hasil (w')   : {w_new} piksel")
print(f"- Tinggi hasil (h')  : {h_new} piksel")
print("=================================================================\n")

# Buat kanvas baru untuk hasil crop
crop_img = Image.new("RGB", (w_new, h_new))

# Terapkan rumus:
# x' = x - xL
# y' = y - yT
for y in range(yT, yB):
    for x in range(xL, xR):
        x_new = x - xL
        y_new = y - yT
        pixel = img.getpixel((x, y))
        crop_img.putpixel((x_new, y_new), pixel)

# Simpan hasil crop
os.makedirs("cropping_result", exist_ok=True)
base_name = os.path.splitext(os.path.basename(image_path))[0]
crop_path = f"cropping_result/{base_name}_cropping.png"
crop_img.save(crop_path)

print(f"Hasil cropping berhasil disimpan di: {crop_path}\n")

# Tampilkan Hasil
plt.figure("Pemotongan (Cropping)", figsize=(10, 5))

# Gambar Asli + area crop
plt.subplot(1, 2, 1)
plt.imshow(img)
plt.title("Citra Asli (dengan area crop)")
plt.axis("off")

# Gambarkan batas cropping
plt.axvline(x=xL, color='lime', linestyle='--', linewidth=2)
plt.axvline(x=xR, color='lime', linestyle='--', linewidth=2)
plt.axhline(y=yT, color='lime', linestyle='--', linewidth=2)
plt.axhline(y=yB, color='lime', linestyle='--', linewidth=2)

# Gambar hasil crop
plt.subplot(1, 2, 2)
plt.imshow(crop_img)
plt.title(f"Hasil Cropping ({xL},{yT}) → ({xR},{yB})")
plt.axis("off")

plt.tight_layout()
plt.show()
