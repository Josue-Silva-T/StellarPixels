import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from time import sleep

# IDs
ID_PRINCIPAL = "left_nav_links"
ID_DATA_IMG = "indexlist"

# URL principal
URL_BASE = "https://pds-imaging.jpl.nasa.gov/volumes/mro.html"

# url´s finales
coleccion_imagenes = {}
lock = threading.Lock()

# Expresiones regulares
rx_enlaces = re.compile(r"/volumes/mro/release(?P<num>\d+)\.html$")
rx_imagenes = re.compile(r"/data/mro/ctx/mrox_\d{4}/$")

# ----- util red -----
# (opcional) una sesión por hilo para reusar conexiones TCP
_thread_local = threading.local()
def _session():
    if not hasattr(_thread_local, "s"):
        _thread_local.s = requests.Session()
    return _thread_local.s

def _obtener_sesion(url_base: str = URL_BASE) -> BeautifulSoup:
    resp = _session().get(url_base, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

# ----- scraping -----
def _obtener_tabla(soup: BeautifulSoup, id_tabla: str):
    tabla = soup.find(id=id_tabla)
    if not tabla:
        raise RuntimeError(f"No se encontró id={id_tabla}")
    return tabla

def _obtener_elementos_tabla(tabla, tag: str, attr: str, er: re.Pattern, base_url: str):
    elementos = []
    for el in tabla.select(f"{tag}[{attr}]"):  # p.ej. a[href]
        val = el.get(attr, "").strip()
        if val and er.search(val):
            elementos.append(urljoin(base_url, val))
    return elementos

def obtener_versiones():
    global coleccion_imagenes
    soup = _obtener_sesion(URL_BASE)
    tabla = _obtener_tabla(soup, ID_PRINCIPAL)
    versiones = _obtener_elementos_tabla(tabla, "a", "href", rx_enlaces, URL_BASE)
    for version in versiones:
        key = version.split("/")[-1].replace(".html", "")
        coleccion_imagenes[key] = []
    return versiones  # URLs absolutas a releaseN.html

def _obtener_elementos(soup: BeautifulSoup, id_table: str, tag: str, attr: str, er: re.Pattern, base_url: str):
    tabla = soup.find(id=id_table)
    if not tabla:
        return []
    urls = []
    for el in tabla.select(f"{tag}[{attr}]"):
        val = el.get(attr, "").strip()
        if val and er.search(val):
            urls.append(urljoin(base_url, val))
    return urls

def obtener_img(session, id_table: str, key: str):
    REGEX_IMG = re.compile(r".+\.img$", re.I)
    global coleccion_imagenes
    tabla = session.find(id=id_table)
    if not tabla:
        return
    for fila in tabla.find_all("tr"):
        tds = fila.find_all("td")
        if len(tds) < 2:
            continue
        link_tag = tds[1].find("a")
        if not link_tag:
            continue
        nombre = link_tag.text.strip()
        if REGEX_IMG.fullmatch(nombre):
            with lock:
                coleccion_imagenes[key].append(nombre)

def obtener_directorios(session, id_table):
    directorios_validos = []
    tabla = session.find(id=id_table)
    if not tabla:
        return directorios_validos
    for fila in tabla.find_all("tr"):
        tds = fila.find_all("td")
        if len(tds) < 2:
            continue
        link_tag = tds[1].find("a")
        if not link_tag:
            continue
        nombre = link_tag.text.strip()
        if nombre.endswith("/"):
            directorios_validos.append(nombre)
    return directorios_validos

def gestionar_directorios(urls, key):
    # procesa todos los directorios de una release (secuencial dentro del hilo)
    for url in urls:
        try:
            sesion = _obtener_sesion(url)
            sesion = _obtener_sesion(f"{url}data/")
            obtener_img(sesion, ID_DATA_IMG, key)
        except Exception as e:
            # registra pero no detiene el resto
            #print(f"[WARN] {key} -> {url}: {e}")
            pass

# ----- MAIN con pool de hilos (relleno automático) -----
if __name__ == "__main__":
    versiones = obtener_versiones()

    # Límite de hilos concurrentes (ajusta 5–10 según tu preferencia)
    MAX_WORKERS = 30

    futures = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for version_url in versiones:
            key = version_url.split("/")[-1].replace(".html", "")
            soup_rel = _obtener_sesion(version_url)
            dirs_ctx = _obtener_elementos(soup_rel, ID_PRINCIPAL, "a", "href", rx_imagenes, version_url)

            # Enviar tarea al pool (el pool ejecutará hasta MAX_WORKERS a la vez, y
            # cuando termine una, toma la siguiente automáticamente)
            futures.append(pool.submit(gestionar_directorios, dirs_ctx, key))

        # (opcional) ir recogiendo resultados/errores conforme terminan
        for fut in as_completed(futures):
            try:
                fut.result()  # propaga excepciones si las hubo
            except Exception as e:
                print("[ERROR hilo]", e)

    print(coleccion_imagenes)
    # Si quieres ver cuántas imágenes por release:
    # for k, v in coleccion_imagenes.items():
    #     print(k, len(v))
