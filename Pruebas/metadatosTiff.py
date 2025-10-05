import tifffile

archivo = "...\imagenes\imagen.tif"
with tifffile.TiffFile(archivo) as tif:
    for page in tif.pages:
        dimension = page.shape
        print(type(dimension))
        print("Dimensiones:", page.shape)
ancho, alto = dimension
print(f"ancho={ancho}, alto={alto}")
