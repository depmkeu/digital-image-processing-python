import cv2  # Untuk membaca dan menampilkan citra
import matplotlib.pyplot as plt  # Menampilkan grafik histogram
import numpy as np  # Import NumPy untuk konversi ke array

# Ganti dengan path ke gambar Anda
image_path = 'grayscale_output.jpg'

# Ganti dengan nama file keluaran Anda
output_file = 'Della.txt'

# Memuat gambar dalam bentuk matriks (BGR format)
image = cv2.imread(image_path)

if image is None:
    raise FileNotFoundError(f"File '{image_path}' tidak ditemukan.")

# Mendapatkan dimensi citra (tinggi dan lebar)
height, width, _ = image.shape

# Histogram untuk intensitas grayscale
histogram = [0] * 256  # Histogram untuk intensitas 0 sampai 255

# Membuka file keluaran untuk penulisan hasil pengukuran
with open(output_file, 'w', encoding="utf-8") as file:
    file.write("Koordinat Pixel dan Intensitas Grayscale\n")

    # Proses konversi ke grayscale secara manual dan hitung histogram
    grayscale_image = []  # Menyimpan hasil citra grayscale
    for y in range(height):
        row = []  # Menyimpan satu baris dari citra grayscale
        for x in range(width):
            pixel = image[y, x]  # Mendapatkan nilai pixel (BGR)
            B, G, R = pixel  # Pisahkan channel warna (B, G, R)
            
            # Konversi ke intensitas grayscale menggunakan rumus manual
            intensity = int(0.299 * R + 0.587 * G + 0.114 * B)
            
            # Menambah histogram pada intensitas yang dihitung
            histogram[intensity] += 1
            
            # Menyimpan nilai intensitas pada citra grayscale
            row.append(intensity)
            
            # Tulis hasil intensitas dan koordinat ke file
            file.write(f"({x},{y}) => Intensitas Warna: {intensity}\n")
        
        grayscale_image.append(row)  # Menambahkan baris ke gambar grayscale

# Menampilkan citra asli dan hasil konversi grayscale
# Menampilkan gambar asli
cv2.imshow('Original Image', image)

# Mengonversi grayscale_image (list) menjadi array NumPy
grayscale_image_array = np.array(grayscale_image, dtype=np.uint8)

# Menormalisasi agar sesuai dengan rentang 0-255
gray_image_display = cv2.normalize(grayscale_image_array, None, 0, 255, cv2.NORM_MINMAX)

# Menampilkan citra grayscale
cv2.imshow('Grayscale Image', gray_image_display)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Menampilkan histogram
plt.figure(figsize=(8, 6))
plt.title('Histogram Intensitas Grayscale')
plt.xlabel('Intensitas Pixel (0-255)')
plt.ylabel('Frekuensi')
plt.plot(histogram, color='black')
plt.xlim([0, 256])
plt.grid(True)
plt.show()

print(f"Hasil pengukuran disimpan dalam file {output_file}")
