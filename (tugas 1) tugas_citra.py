from PIL import Image  # library supaya bisa buka file citra

# 1) Baca citra
path = input("Masukkan path file citra (mis. 'gambar.jpg'): ").strip()  # minta user masukin gambar

# Cek apakah file ada
try:
    img = Image.open(path)  # buka gambar yang dimasukkin user, hasilnya berupa objek citra PIL
except FileNotFoundError:
    print(f"File '{path}' tidak ditemukan. Program berhenti.")
    exit()
except IOError:
    print(f"Tidak bisa membuka file '{path}'. Program berhenti.")
    exit()

# 2) Ambil resolusi asli
width, height = img.size  # tuple (width, height)

print("=== PROPERTI CITRA ===")
print("Mode          :", img.mode)  # nunjukkin mode warnanya (RGB, L, CMYK, dll)
print("Resolusi      : {} x {} piksel".format(width, height))  # nampilin resolusi asli gambar

bands = img.getbands()  # ngecek apa saja kanal warna yang ada di citra
n_channels = len(bands)  # jumlah panjang kanalnya, misal RGB 3 atau grayscale 1
bpp = n_channels * 8  # dikali 8 karena tiap kanalnya disimpen dalam 8 bit 
print("Kedalaman     : {} bit per piksel (8 bit x {} kanal)".format(bpp, n_channels))  # cetak hasilnya

print("\n=== NILAI f(x, y) ===")  # nampilin batas koordinat valid untuk milih pikselnya
print("Koordinat valid: 0 <= x < {}, 0 <= y < {}".format(width, height))

# Validasi input koordinat x dan y
try:
    x = int(input("Masukkan x: ").strip())
    y = int(input("Masukkan y: ").strip())
except ValueError:
    print("Input koordinat tidak valid. Program berhenti.")
    exit()

# Cek apakah koordinat valid
if not (0 <= x < width and 0 <= y < height):  # kalau keluar dari batas resolusi gambar
    print("Koordinat di luar batas citra. Program berhenti.")
    exit()
else:
    # Ambil nilai intensitas piksel yang dimasukkan
    nilai = img.getpixel((x, y))  
    print("f({}, {}) = {}".format(x, y, nilai))

