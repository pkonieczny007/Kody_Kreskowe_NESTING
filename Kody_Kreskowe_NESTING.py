import os
import shutil
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image

# Funkcja do generowania kodu kreskowego jako obraz PNG
def generate_barcode_image(text, output):
    barcode = Code128(text, writer=ImageWriter())
    barcode.save(output)

# Ścieżki katalogów
current_directory = os.getcwd()
kody_directory = os.path.join(current_directory, 'kody')
orginal_directory = os.path.join(current_directory, 'orginal')

# Utwórz katalogi, jeśli nie istnieją
os.makedirs(kody_directory, exist_ok=True)
os.makedirs(orginal_directory, exist_ok=True)

# Pobierz wszystkie pliki PDF
pdf_files = [f for f in os.listdir(current_directory) if f.endswith('.pdf') and not f.endswith('+kod.pdf')]

# Przetwarzanie plików PDF
for pdf_file in pdf_files:
    pdf_path = os.path.join(current_directory, pdf_file)
    barcode_filename = os.path.splitext(pdf_file)[0]
    barcode_image_path = os.path.join(kody_directory, f"{barcode_filename}")
    
    # Generowanie kodu kreskowego jako obraz PNG
    generate_barcode_image(barcode_filename, barcode_image_path)
    
    # Dodajemy rozszerzenie .png do ścieżki pliku obrazu
    barcode_image_path += '.png'
    
    # Wczytywanie oryginalnego PDF
    pdf_reader = PdfReader(pdf_path)
    pdf_writer = PdfWriter()
    
    # Dodawanie kodu kreskowego do pierwszej strony PDF
    for page_num, page in enumerate(pdf_reader.pages):
        if page_num == 0:  # Dodajemy kod kreskowy tylko na pierwszej stronie
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            image = ImageReader(barcode_image_path)
            
            # Zmień wartości x i y, aby zmienić pozycję kodu kreskowego
            x_position = 15  # Pozycja x (odległość od lewej krawędzi) 20
            y_position = 760  # Pozycja y (odległość od dolnej krawędzi) 700ok
            
            can.drawImage(image, x_position, y_position, width=100, height=50)  # Pozycja i rozmiar kodu kreskowego
            can.save()
            
            packet.seek(0)
            new_pdf = PdfReader(packet)
            page.merge_page(new_pdf.pages[0])
        
        pdf_writer.add_page(page)
    
    # Zapis nowego pliku PDF z kodem kreskowym
    new_pdf_path = os.path.join(current_directory, f"{barcode_filename}+kod.pdf")
    with open(new_pdf_path, "wb") as output_pdf:
        pdf_writer.write(output_pdf)
    
    # Przeniesienie oryginalnego pliku PDF do katalogu 'orginal'
    shutil.move(pdf_path, os.path.join(orginal_directory, pdf_file))

print("Przetwarzanie zakończone.")
