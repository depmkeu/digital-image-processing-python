from PIL import Image
import matplotlib.pyplot as plt

# 1. LOAD GAMBAR
img = Image.open("gambartgs7kedua.jpg").convert("RGB")
W, H = img.size

# 2. POTONG MENJADI 3 BLOK (2x2)
w = W // 2
h = H // 2

C_tl = img.crop((0, 0, w, h))        # kiri atas
C_tr = img.crop((w, 0, W, h))        # kanan atas
C_bottom = img.crop((0, h, W, H))    # bawah

# 3. ROTASI 180° UNTUK SETIAP BLOK

# --- ROTASI KIRI ATAS ---
src = C_tl.load()
Wb, Hb = C_tl.size
tl_rot = Image.new("RGB", (Wb, Hb)) # wadah untuk hasil rotasi
tl_pix = tl_rot.load()

for y in range(Hb):
    for x in range(Wb):
        # rumus rotasi 180°
        nx = Wb - 1 - x
        ny = Hb - 1 - y
        tl_pix[nx, ny] = src[x, y]

# --- ROTASI KANAN ATAS ---
src = C_tr.load()
Wb, Hb = C_tr.size
tr_rot = Image.new("RGB", (Wb, Hb))
tr_pix = tr_rot.load()

for y in range(Hb):
    for x in range(Wb):
        nx = Wb - 1 - x
        ny = Hb - 1 - y
        tr_pix[nx, ny] = src[x, y]

# --- ROTASI BAGIAN BAWAH ---
src = C_bottom.load()
Wb, Hb = C_bottom.size
bottom_rot = Image.new("RGB", (Wb, Hb))
bot_pix = bottom_rot.load()

for y in range(Hb):
    for x in range(Wb):
        nx = Wb - 1 - x
        ny = Hb - 1 - y
        bot_pix[nx, ny] = src[x, y]

# 4. PENCERMINAN HORIZONTAL UNTUK TL DAN TR

# --- Mirror TL ---
src = tl_rot.load()
Wb, Hb = tl_rot.size
blk1 = Image.new("RGB", (Wb, Hb)) # blok hasil mirror
pix1 = blk1.load()

for y in range(Hb):
    for x in range(Wb):
        nx = Wb - 1 - x # pencerminan horizontal
        pix1[nx, y] = src[x, y]

# --- Mirror TR ---
src = tr_rot.load()
Wb, Hb = tr_rot.size
blk2 = Image.new("RGB", (Wb, Hb))
pix2 = blk2.load()

for y in range(Hb):
    for x in range(Wb):
        nx = Wb - 1 - x # pencerminan horizontal
        pix2[nx, y] = src[x, y]

# 5. SUSUN BLOK KANAN (atas + bawah)
# Blok kanan = hasil mirror kiri atas + hasil mirror kanan atas
right_block = Image.new("RGB", (w, blk1.height + blk2.height))

# Tempel blok atas dan bawah secara vertikal
right_block.paste(blk1, (0, 0))
right_block.paste(blk2, (0, blk1.height))

# 6. SUSUN GAMBAR AFTER
# after_img dibuat sama tinggi & lebar dengan gambar asli
after_img = Image.new("RGB", (W, H), (255, 255, 255))

after_img.paste(bottom_rot, (0, 0))

# Translasi blok kanan agar sejajar
offset = 80
x_pos = W - right_block.width + offset

# y pos = sejajar dengan garis batas horizontal
y_pos = h     # karena tepat di bawah blok atas

# Tempel blok kanan hasil manipulasi
after_img.paste(right_block, (x_pos, y_pos))

# 7. TAMPILKAN BEFORE – AFTER & SIMPAN
plt.figure(figsize=(12, 6))

# --- before ---
plt.subplot(1, 2, 1)
plt.title("Before")
plt.imshow(img)
plt.axis("off")

# --- after ---
plt.subplot(1, 2, 2)
plt.title("After")
plt.imshow(after_img)
plt.axis("off")

plt.tight_layout()
plt.savefig("hasil_cobacoba22.png", dpi=150)
plt.show()

print("Selesai! Hasil tersimpan sebagai 'hasil_cobacoba22.png'")
