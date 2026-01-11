import cv2  # membaca dan menampilkan gambar
import matplotlib.pyplot as plt  # menampilkan grafik histogram

# Fungsi untuk menghitung intensitas warna secara manual (RGB ke grayscale)
def calculate_intensity(pixel):
    R, G, B = pixel
    intensity = (0.299 * R) + (0.587 * G) + (0.114 * B)  # rumus standar (ada ini di buku)
    return round(intensity)  # Bulatkan hasil intensitas menjadi bilangan bulat

# Fungsi untuk menghitung histogram manual
def calculate_histogram(image):
    height, width, _ = image.shape
    hist_r = [0] * 256  # Histogram untuk red channel
    hist_g = [0] * 256  # Histogram untuk green channel
    hist_b = [0] * 256  # Histogram untuk blue channel

    for y in range(height):
        for x in range(width):
            pixel = image[y, x]  # Mendapatkan nilai pixel (B, G, R)
            hist_b[pixel[0]] += 1  # Menambahkan 1 untuk setiap nilai blue
            hist_g[pixel[1]] += 1  # Menambahkan 1 untuk setiap nilai green
            hist_r[pixel[2]] += 1  # Menambahkan 1 untuk setiap nilai red

    return hist_r, hist_g, hist_b

# Fungsi utama
def process_image(image_path, output_file):
    try:
        # Load gambar
        image = cv2.imread(image_path)  # baca gambar format BGR
        if image is None:
            raise FileNotFoundError(f"File '{image_path}' not found.")  # validasi jika gagal

        # Menghitung dimensi dari gambar
        height, width, _ = image.shape

        # Menghitung histogram secara manual
        hist_r, hist_g, hist_b = calculate_histogram(image)

        # Menghitung grayscale secara manual
        grayscale_image = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = image[y, x]  # Mendapatkan nilai pixel (B, G, R)
                intensity = calculate_intensity(pixel)  # Menghitung intensitas
                row.append(intensity)  # Menambahkan ke baris
            grayscale_image.append(row)  # Menambahkan baris ke gambar grayscale

        # Membuka output file untuk menulis
        with open(output_file, 'w') as file:
            file.write("Pixel Coordinates and Intensity (RGB and Intensity Value)\n")
            for y in range(height):
                for x in range(width):
                    pixel = image[y, x]  # Mendapatkan nilai pixel (R, G, B)
                    intensity = calculate_intensity(pixel)
                    file.write(f"({x},{y}) => RGB Value: {pixel}, Color Intensity: {intensity}\n")

        # Menampilkan histogram RGB secara manual
        plt.figure(figsize=(8, 6))
        plt.title('Image Histogram')
        plt.xlabel('Pixel Intensity')
        plt.ylabel('Frequency')
        plt.plot(hist_r, color='red', label='Red')
        plt.plot(hist_g, color='green', label='Green')
        plt.plot(hist_b, color='blue', label='Blue')
        plt.xlim([0, 256])
        plt.legend()
        plt.grid(True)
        plt.show()

        # Menampilkan gambar asli
        cv2.imshow('Original Image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print(f"Output saved to {output_file}")  # info file txt telah disimpan

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    image_path = 'imoet.jpg' 
    output_file = 'Della_Info.txt'  # Output file
    process_image(image_path, output_file)
