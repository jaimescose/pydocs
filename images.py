import shutil
from typing import Literal
import img2pdf
import os
from pathlib import Path
import typer
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from pillow_heif import register_heif_opener
import subprocess

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

@app.command()
def convert_heic_to_jpeg(input_path: str, recursive: bool = False):
    """
    Converts a HEIC image file or all .HEIC/.HEIF files in a folder to JPEG format.
    Pass a file path to convert a single file, or a folder path to convert all HEIC files inside.
    Use --recursive to search subdirectories.
    """
    try:
        register_heif_opener()

        path = Path(input_path)
        if not path.exists():
            print(f"Error: path not found: {input_path}")
            return

        heic_exts = {'.heic', '.heif'}
        files = []

        if path.is_dir():
            if recursive:
                files = [p for p in sorted(path.rglob('*')) if p.is_file() and p.suffix.lower() in heic_exts]
            else:
                files = [p for p in sorted(path.iterdir()) if p.is_file() and p.suffix.lower() in heic_exts]
        else:
            if path.suffix.lower() in heic_exts:
                files = [path]
            else:
                print(f"Error: file is not a HEIC/HEIF: {input_path}")
                return

        if not files:
            print(f"No HEIC/HEIF files found at: {input_path}")
            return

        for file in files:
            try:
                output_path = file.with_suffix('.jpeg')
                img = Image.open(file)
                # Ensure no alpha channel when saving as JPEG
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    img = img.convert("RGB")
                img.save(output_path, "JPEG")
                print(f"Converted {file} to {output_path}")
            except FileNotFoundError:
                print(f"Error: File not found: {file}")
            except Exception as e:
                print(f"Failed converting {file}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

@app.command()
def convert_wav_to_mp3(wav_filename: str, bitrate: str = "192k"):
    """
    Converts a WAV audio file to MP3.
    Requires pydub and ffmpeg installed.
    """
    try:
        directory, filename = os.path.split(wav_filename)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(directory, f"{name}.mp3")

        # Try to use pydub if available (lazy import to avoid import-time failures)
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_wav(wav_filename)
            audio.export(output_path, format="mp3", bitrate=bitrate)
            print(f"Converted {wav_filename} to {output_path} (via pydub)")
            return
        except Exception:
            # pydub/audioop not available or failed — fall back to ffmpeg CLI
            pass

        # Fallback: require ffmpeg available on PATH
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            print("ffmpeg not found and pydub unavailable. Install ffmpeg or ensure pydub and audioop/pyaudioop are installed.")
            return

        cmd = [ffmpeg, "-y", "-i", wav_filename, "-b:a", bitrate, output_path]
        subprocess.run(cmd, check=True)
        print(f"Converted {wav_filename} to {output_path} (via ffmpeg)")
    except FileNotFoundError:
        print(f"Error: File not found: {wav_filename}")
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    app()
