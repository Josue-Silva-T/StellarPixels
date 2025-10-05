import requests

i= 1
while i != 2:
    # URL de un archivo de ejemplo (imagen CTX)
    if(i>=10):
        url = f"https://planetarydata.jpl.nasa.gov/img/data/mro/ctx/mrox_0001/data/CRU_0000{i}_9999_XN_99N999W.IMG"
    elif(i<10):
        url = f"https://planetarydata.jpl.nasa.gov/img/data/mro/ctx/mrox_1478/data/G19_025498_1427_XN_37S168W.IMG"
    
    file_name = url.split("/")[-1]

    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Descargado: {file_name}")
    else:
        print("Error al descargar")
    i += 1
