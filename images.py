# import webbrowser
import webbrowser
import img2pdf
import os
from pathlib import Path
import typer

app = typer.Typer()

# path = "C:/Users/57301/Documents/documents/palmanova/apto/Especificaciones técnicas del proyecto"

IMAGE_EXTENSIONS = ['.jpg', '.jpeg']

@app.command()
def convert_images_to_pdf(folder_path: str):
    
    folder = Path(folder_path)
    if not folder.exists():
        print('ajá pana, qué pasa?')

    images = []
    for filename in os.listdir(folder):
        file = folder / filename
        if file.suffix in IMAGE_EXTENSIONS:
            images.append(file.as_posix())

    pdf_file = folder / f'{folder.stem}.pdf'
    pdf_file.open('wb').write(img2pdf.convert(images))

    webbrowser_file = pdf_file.absolute().as_uri()
    print(f'Las imagenes encontradas en el dirctorio han sido convertidas y unificadas en un archivo pdf')
    print(webbrowser_file)
    # webbrowser.open(pdf_file.absolute().as_uri())

if __name__ == '__main__':
    app()
