import rasterio
from rasterio import shutil as rio_shutil

with rasterio.open("CRU_000002_9999_XN_99N999W.IMG") as src:
    rio_shutil.copy(src, "imagen2.tif", driver="GTiff")
