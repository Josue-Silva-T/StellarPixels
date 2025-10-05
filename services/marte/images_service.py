import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# IDs
ID_PRINCIPAL = "left_nav_links"
ID_DATA_IMG = "indexlist"

# URL principal
URL_BASE = "https://pds-imaging.jpl.nasa.gov/volumes/mro.html"

# Expresiones regulares
rx_enlaces = re.compile(r"/volumes/mro/release(?P<num>\d+)\.html$")
rx_imagenes = re.compile(r"/data/mro/ctx/mrox_\d{4}/$")

def _obtener_sesion(url_base: str = URL_BASE) -> BeautifulSoup:
    resp = requests.get(url_base, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def _obtener_tabla(soup: BeautifulSoup, id_tabla: str):
    tabla = soup.find(id=id_tabla)
    if not tabla:
        raise RuntimeError(f"No se encontró id={id_tabla}")
    return tabla

def _obtener_elementos_tabla(tabla, tag: str, attr: str, er: re.Pattern, base_url: str):
    """Devuelve URLs absolutas para los elementos tag[attr] cuyo attr matchee er."""
    elementos = []
    for el in tabla.select(f"{tag}[{attr}]"):  # p.ej. a[href]
        val = el.get(attr, "").strip()        # p.ej. href
        if val and er.search(val):
            elementos.append(urljoin(base_url, val))
    return elementos

def obtener_versiones():
    soup = _obtener_sesion(URL_BASE)
    tabla = _obtener_tabla(soup, ID_PRINCIPAL)
    # Devuelve URLs absolutas a las releaseN.html
    return _obtener_elementos_tabla(tabla, "a", "href", rx_enlaces, URL_BASE)

def _obtener_elementos(
    soup: BeautifulSoup,
    id_table: str,
    tag: str,
    attr: str,
    er: re.Pattern,
    base_url: str,
):
    """Devuelve URLs absolutas encontradas en #id_table que hacen match con er."""
    tabla = soup.find(id=id_table)
    if not tabla:
        return []
    urls = []
    for el in tabla.select(f"{tag}[{attr}]"):
        val = el.get(attr, "").strip()
        if val and er.search(val):
            urls.append(urljoin(base_url, val))
    return urls

def obtener_img(session, id_table):
    REGEX_IMG = re.compile(r".+\.img$", re.I)  # acepta .img o .IMG
    archivos_validos = []
    tabla = session.find(id=id_table)
    for fila in tabla.find_all("tr"):
        tds = fila.find_all("td")
        if len(tds) < 2:
            continue
        link_tag = tds[1].find('a')
        if not link_tag:
            continue
        nombre = link_tag.text.strip()
        if REGEX_IMG.fullmatch(nombre):   # valida toda la cadena
            archivos_validos.append(nombre)
    return archivos_validos

def obtener_directorios(session, id_table):
  directorios_validos = []
  tabla = session.find(id=id_table)

  for fila in tabla.find_all("tr"):
    tds = fila.find_all("td")
    if len(tds) < 2:
      continue
    link_tag = tds[1].find('a')
    if not link_tag:
      continue
    nombre = link_tag.text.strip()
    if not nombre:
      continue
    if nombre.endswith('/'):
      directorios_validos.append(nombre)
  return directorios_validos


if __name__ == "__main__":
    versiones = obtener_versiones()  # p.ej. .../release1.html, .../release2.html, ...
    imagenes = []
    imagenes_bn = []
    i = 0
    for version_url in versiones:
        soup_rel = _obtener_sesion(version_url)
        # Aquí usamos como base_url LA PÁGINA DE LA RELEASE,
        # para que urljoin haga bien la ruta absoluta.
        dirs_ctx = _obtener_elementos(soup_rel, ID_PRINCIPAL, "a", "href", rx_imagenes, version_url)
        print(dirs_ctx)
        imagenes.extend(dirs_ctx)  # aplanamos en una sola lista
        for imagen in imagenes:
          sesion = _obtener_sesion(imagen)
          directorios = obtener_directorios(sesion, ID_DATA_IMG)
          print(directorios)
          i+=1
          print(i)
    #       sesion = _obtener_sesion(f"{imagen}{directorios[2]}")
    #       coleccion_imagenes = obtener_img(sesion, ID_DATA_IMG)
    #       for img_href in coleccion_imagenes:
    #         imagenes_bn.append(f"{imagen}{directorios[2]}{img_href}")
    # print(imagenes_bn)
  
    
    
