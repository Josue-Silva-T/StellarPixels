import numpy as np
from PIL import Image
i = 10
while i != 16:
    # Parámetros del archivo
    archivo_img = f"CRU_0000{i}_9999_XN_99N999W.IMG"
    alto = 1024
    ancho = 5056
    offset = 1 * 5056  # LABEL_RECORDS * RECORD_BYTES → saltar el encabezado de 1 registro

    # Leer archivo completo
    with open(archivo_img, "rb") as f:
        f.seek(offset)  # saltar cabecera
        data = np.fromfile(f, dtype=np.uint8, count=alto*ancho)

    # Darle forma de matriz 2D
    data = data.reshape((alto, ancho))

    # Guardar como PNG
    Image.fromarray(data).save(f"{archivo_img}.png")
    print("Imagen guardada como CTX_salida.png")
    i += 1
