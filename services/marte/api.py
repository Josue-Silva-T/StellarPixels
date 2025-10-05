from pathlib import Path
import requests
import io
from io import BytesIO 
from PIL import Image

BASE_URL = "https://pds-imaging.jpl.nasa.gov/solr/pds_archives/search"

def buscar_id(id: str):
    r = requests.get(f"{BASE_URL}?identifier={id}", timeout=30)
    r.raise_for_status()
    data = r.json()
    file_name = data["response"]["docs"][0]["FILE_NAME"]
    url = data['response']['docs'][0]["ATLAS_THUMBNAIL_URL"]
    tiff_name = file_name.rsplit(".", 1)[0] + ".tiff"
    convertir_jpeg_url_a_tiff(url, tiff_name)

def buscar_imagen(name: str):
    r = requests.get(f"{BASE_URL}/?image_content={name}", timeout=60)
    r.raise_for_status()
    data = r.json()
    respuestas = data["response"]["docs"]

    for respuesta in respuestas:
        url = respuesta.get("ATLAS_DATA_URL") or ""
        name_photo = respuesta.get("FILE_NAME_SPECIFICATION", "").split("/")[-1]

        # si el nombre no viene, intenta inferirlo de la URL
        if not name_photo and url:
            name_photo = url.split("?")[0].rstrip("/").split("/")[-1]

        print(f'{url}\n{name_photo}\n')

        if url.lower().endswith(".jp2"):
            # guarda como TIFF sin escribir el JP2
            tiff_name = name_photo.rsplit(".", 1)[0] + ".tiff"
            convertir_jp2_url_a_tiff(url, tiff_name)
        else:
            # opcional: si quieres seguir guardando las browse JPG/PNG
            convertir_jp2_url_a_tiff(url, name_photo)

def guardar_memoria():
    pass

def convertir_jpeg_url_a_tiff(url_imagen, nombre_salida:str):
    """
    Descarga una imagen JPEG desde una URL y la guarda en formato TIFF.

    Parámetros:
        url_imagen (str): URL de la imagen JPEG.
        carpeta_salida (str): Carpeta donde se guardará el .tiff.
        nombre_salida (str | None): Nombre del archivo de salida (sin ruta).
                                    Si es None, se infiere del nombre en la URL.
        timeout (int): Timeout en segundos para la descarga.

    Retorna:
        str: Ruta del archivo TIFF generado.

    Requiere:
        pip install Pillow requests
    """

    output_dir = Path(__file__).resolve().parents[2] / "tiff"
    output_dir.mkdir(parents=True, exist_ok=True)

    base = Path(nombre_salida).stem
    tiff_path = output_dir / f"{base}.tiff"
    # 1) Descargar la imagen
    resp = requests.get(url_imagen, timeout=60)
    resp.raise_for_status()  # Lanza error si la descarga falla

    # (Opcional) Validación ligera del tipo de contenido
    ctype = resp.headers.get("Content-Type", "").lower()
    if "jpeg" not in ctype and "jpg" not in ctype:
        # A veces el servidor no pone el content-type correcto; de todas formas intentamos abrir con PIL
        pass


    # 3) Abrir con PIL y guardar como TIFF
    with Image.open(BytesIO(resp.content)) as img:
        # Asegurar modo compatible (JPEG suele ser RGB)
        if img.mode not in ("RGB", "RGBA", "L"):
            img = img.convert("RGB")
        # Guardar con compresión LZW (sin pérdida) para reducir tamaño
        img.save(tiff_path, format="TIFF", compression="tiff_lzw")

    return tiff_path

def convertir_jp2_url_a_tiff(url: str, tiff_name: str) -> Path:
    # Carpeta fija: ../../tiff relativa a este archivo
    output_dir = Path(__file__).resolve().parents[2] / "tiff"
    output_dir.mkdir(parents=True, exist_ok=True)

    base = Path(tiff_name).stem
    tiff_path = output_dir / f"{base}.tiff"

    Image.MAX_IMAGE_PIXELS = None

    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        buf = io.BytesIO()
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                buf.write(chunk)
        buf.seek(0)

    with Image.open(buf) as im:
        im.load()
        im.save(tiff_path, format="TIFF", compression="tiff_lzw")

    print(f"Convertido a {tiff_path}")
    return tiff_path

# Ejemplo:
buscar_id("1_N1845993031.118")