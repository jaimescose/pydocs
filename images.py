import shutil
import img2pdf
import os
from pathlib import Path
import typer
from PyPDF2 import PdfReader, PdfWriter

app = typer.Typer()

# path = "C:/Users/57301/Documents/documents/palmanova/apto/Especificaciones técnicas del proyecto"

IMAGE_EXTENSIONS = ['.jpg', '.jpeg']

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
def hello(name: str = 'pana'):
    print(f'¡Hola, {name.capitalize()}!')

if __name__ == '__main__':
    app()
