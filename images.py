import shutil
from typing import Literal
import img2pdf
import os
from pathlib import Path
import typer
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image

app = typer.Typer()

# path = "C:/Users/57301/Documents/documents/palmanova/apto/Especificaciones técnicas del proyecto"

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']

@app.command()
def convert_images_to_pdf(folder_path: str):
    
    folder = Path(folder_path)
    if not folder.exists():
        print('ajá pana, qué pasa?')

    images = []
    for filename in sorted(os.listdir(folder)):
        file = folder / filename
        if file.suffix in IMAGE_EXTENSIONS:
            images.append(file.as_posix())

    pdf_file = folder / f'{folder.stem}.pdf'
    pdf_file.open('wb').write(img2pdf.convert(images))

    webbrowser_file = pdf_file.absolute().as_uri()
    print('Las imagenes encontradas en el dirctorio han sido convertidas y unificadas en un archivo pdf')
    print(webbrowser_file)
    # webbrowser.open(pdf_file.absolute().as_uri())


@app.command()
def split_pdf(pdf_filename: str):
    original_name = os.path.splitext(os.path.basename(pdf_filename))[0]

    output_folder = os.path.join(os.path.dirname(pdf_filename), original_name)
    output_folder = Path(output_folder)

    # todo: fail if it's not empty. Unless --force is passed
    if output_folder.exists():
        shutil.rmtree(output_folder)

    output_folder.mkdir()

    reader = PdfReader(pdf_filename)
    for i in range(len(reader.pages)):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])

        output_filename = os.path.join(output_folder, f"{original_name} - {i + 1}.pdf")
        with open(output_filename, "wb") as output_pdf:
            writer.write(output_pdf)
        print(f"Saved: {output_filename}")


@app.command()
def rotate_pdf_page(pdf_filename: str, rotation: int):
    print(rotation)
    directory, filename = os.path.split(pdf_filename)
    # Split the filename and extension
    name, ext = os.path.splitext(filename)
    # Create the new filename
    output_path = os.path.join(directory, f"{name}_rotated{ext}")

    reader = PdfReader(pdf_filename)
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(rotation)
        writer.add_page(page)

    with open(output_path, "wb") as output_file:
        writer.write(output_file)

    print(f"Rotated PDF saved as: {output_path}")


@app.command()
def convert_webp_to_png(webp_filename: str):
    try:
        directory, filename = os.path.split(webp_filename)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(directory, f"{name}.png")

        img = Image.open(webp_filename)
        img.save(output_path)
        print(f"Converted {webp_filename} to {output_path}")
    except FileNotFoundError:
        print(f"Error: File not found: {webp_filename}")
    except Exception as e:
        print(f"An error occurred: {e}")


@app.command()
def hello(name: str = 'pana'):
    print(f'¡Hola, {name.capitalize()}!')

if __name__ == '__main__':
    app()
