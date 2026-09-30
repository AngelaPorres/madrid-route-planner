"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP305
Integrantes:
    - Míriam Mingo Revuelta
    - Ángela Porres Cobb

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.

Complétese esta descripción según las funcionalidades agregadas por el grupo.
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import re
import os
import matplotlib.pyplot as plt

from typing import Tuple

STREET_FILE_NAME="direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME="madrid.graphml"

MAX_SPEEDS={'living_street': '20',
 'residential': '30',
 'primary_link': '40',
 'unclassified': '40',
 'secondary_link': '40',
 'trunk_link': '40',
 'secondary': '50',
 'tertiary': '50',
 'primary': '50',
 'trunk': '50',
 'tertiary_link':'50',
 'busway': '50',
 'motorway_link': '70',
 'motorway': '100'}


class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass


class AddressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass


############## Parte 2 ##############

def convertir_coordenada(coord:str)->float:
    """
    Convierte una coordenada en formato grados, minutos y segundos a grados decimal
    """
    coord = coord.replace("�", "°")  # Pasamos los símbolos que no reconoce a grados

    # Buscamos dígitos seguidos de °, luego dígitos seguidos de ', después dígitos que pueden ser float 
    # (o no) seguidos de '' y por último una de estas letras N/S/E/W
    patron = r"(\d+)°(\d+)'(\d+(?:\.\d+)?)''?\s*([NSEW])"
    m = re.match(patron, coord.strip())

    grados = float(m.group(1))
    minutos = float(m.group(2))
    segundos = float(m.group(3))
    orientacion = m.group(4)

    g_decimales = grados + minutos/60 + segundos/3600  # Lo pasamos todo a grados

    if orientacion in ["S", "W"]:  # Cambiamos a negativo si es South o West
        g_decimales = -g_decimales

    return g_decimales 


def carga_callejero() -> pd.DataFrame:
    """ 
    Función que carga el callejero de Madrid, lo procesa y devuelve
        un DataFrame con los datos procesados
        
        Args: None
        Returns:
            DataFrame: dataframe con los datos del callejero procesados.
        Raises:
            FileNotFoundError si el fichero csv con las direcciones no existe
    """
    columnas = ['VIA_CLASE', 'VIA_PAR', 'VIA_NOMBRE', 'NUMERO', 'LATITUD', 'LONGITUD']
    
    try:
        df_final = pd.read_csv(STREET_FILE_NAME, sep=";", encoding="cp1252", usecols=columnas)
    except FileNotFoundError:
        raise FileNotFoundError(f"No se encontró el fichero: {STREET_FILE_NAME}")

    df_final["LATITUD_DECIMAL"] = df_final["LATITUD"].apply(convertir_coordenada)
    df_final["LONGITUD_DECIMAL"] = df_final["LONGITUD"].apply(convertir_coordenada)

    # Creamos una columna con la dirección completa para facilitar la búsqueda
    def obtener_direccion_completa(fila_df): 
        via = str(fila_df["VIA_CLASE"]).strip().capitalize()
        par = str(fila_df["VIA_PAR"]).strip().lower()
        nombre = str(fila_df["VIA_NOMBRE"]).strip().title()
        numero = str(fila_df["NUMERO"]).strip()

        if par in ["", "nan"]: 
            return f"{via} {nombre}, {numero}"
        else:
            return f"{via} {par} {nombre}, {numero}"

    df_final["DIRECCION_COMPLETA"] = df_final.apply(obtener_direccion_completa, axis=1)  # De cada fila del df, cogemos lo necesario para obtener una dirección completa

    return df_final
    

def normalizar_entrada_usuario(direccion: str)->str:
    """ Toma la dirección escrita por el usuario y la normaliza quitando tildes y espacios innecesarios"""
    # Ejemplo: "Calle de Diego de León, 34"
    direccion = direccion.strip()

    # Separamos en "calle" y "número"
    partes = direccion.split(",")
    texto = partes[0].strip()      # "Calle de Diego de León"
    numero = partes[1].strip()     # "34"

    palabras = texto.split()

    via = palabras[0]                        # Calle
    par = palabras[1]                        # de
    nombre = " ".join(palabras[2:]).lower()  # Diego De León
    # (Cogemos las palabras después del par y las unimos por espacios para tener el nombre de la calle)

    # Quitamos las tildes manualmente para que coincida con nuestra columna de direcciones completas
    nombre = nombre.replace("ó", "o") \
                   .replace("é", "e") \
                   .replace("í", "i") \
                   .replace("á", "a") \
                   .replace("ú", "u")

    return f"{via} {par} {nombre}, {numero}".lower()


def busca_direccion(direccion:str, callejero:pd.DataFrame) -> Tuple[float,float]:
    """ 
    Función que busca una dirección, dada en el formato calle, numero
    en el DataFrame callejero de Madrid y devuelve el par (latitud, longitud) en grados de la
    ubicación geográfica de dicha dirección
    
    Args:
        direccion (str): Nombre completo de la calle con número, en formato "Calle, num"
        callejero (DataFrame): DataFrame con la información de las calles
    Returns:
        Tuple[float,float]: Par de float (latitud,longitud) de la dirección buscada, expresados en grados
    Raises:
        AdressNotFoundError: Si la dirección no existe en la base de datos
    Example:
        busca_direccion("Calle de Alberto Aguilera, 23", data)=(40.42998055555555,3.7112583333333333)
        busca_direccion("Calle de Alberto Aguilera, 25", data)=(40.43013055555555,3.7126916666666667)
    """
    direccion_usuario = normalizar_entrada_usuario(direccion)

    # Buscamos si la dirección proporcionada está en el dataset
    fila = callejero[callejero["DIRECCION_COMPLETA"].str.lower().str.strip() == direccion_usuario]
    
    if fila.empty:  # (No hay coincidencias)
        raise AddressNotFoundError(f"ERROR. La dirección {direccion_usuario} no existe en la base de datos")
    
    lat = fila["LATITUD_DECIMAL"].iloc[0]
    lon = fila["LONGITUD_DECIMAL"].iloc[0]
    return(lat, lon)


############## Parte 4 ##############

def carga_grafo() -> nx.MultiDiGraph:
    """ Función que crea el grafo de calles de Madrid 
    Returns:
        nx.MultiDiGraph: grafo de calles de Madrid
    Raises:
        ServiceNotAvailableError: Si no es posible recuperar el grafo de OpenStreetMap.
    """
    file = "madrid.graphml"

    # Si el fichero ya existe, lo cargarmos
    if os.path.exists(file):
        print("Cargando grafo de las calles de Madrid...")
        G = ox.load_graphml(file)
        ox.plot_graph(G, node_size=0, edge_linewidth=0.5)  # Dibuja el grafo
        return G

    # Si el fichero no existe, lo descargamos
    try:
        print("Descargando grafo de las calles de Madrid desde OpenStreetMap...")
        G = ox.graph_from_place("Madrid, Spain", network_type="drive")
        ox.save_graphml(G, file)
        ox.plot_graph(G, node_size=0, edge_linewidth=0.5)  # Dibuja el grafo
        return G
    
    except Exception:
        raise ServiceNotAvailableError("No se pudo crear el grafo de Madrid a partir de OpenStreetMap")


def procesa_grafo(multidigrafo:nx.MultiDiGraph) -> nx.DiGraph:
    """ Función que convierte el grafo devuelto por OSMnx en un grafo dirigido sin bucles de NetworkX (Digraph)
    Args:
        multidigrafo: multidigrafo de las calles de Madrid obtenido anteriormente
    Returns:
        nx.DiGraph: Grafo dirigido y sin bucles a partir del multidigrafo dado.
    """
    # Convertimos el multidigrafo a digrafo (aunque aún pueden quedar bucles)
    G = ox.convert.to_digraph(multidigrafo)

    # Eliminamos los bucles
    bucles = nx.selfloop_edges(G)
    G.remove_edges_from(bucles)
    return G


def explorar_grafo(G):
    """Imprime información sobre nodos y aristas del grafo"""
    # Mostrar un nodo (cogemos el primero, por ejemplo)
    nodo = list(G.nodes())[0]
    print("\nEjemplo de nodo:", nodo)
    print(G.nodes[nodo])

    # Mostrar una arista (cogemos la primera)
    u, v = list(G.edges())[0]
    print("\nEjemplo de arista:", (u, v))
    print(G.edges[u, v])


def dibujar_grafo_networkx(G):
    """Dibuja el grafo dirigido usando NetworkX"""
    # Creamos un diccionario de posiciones con esta estructura {nodo: (x, y)}
    pos = {}
    for n in G.nodes:
        x = G.nodes[n]['x']
        y = G.nodes[n]['y']
        pos[n] = (x, y)

    plt.figure(figsize=(10,10))
    nx.draw(G, pos=pos, node_size=0, width=0.3, arrows=False)
    plt.title("Grafo Dirigido de las calles de Madrid")
    plt.show()


if __name__ == "__main__":
    try:
        Gmulti = carga_grafo()
    except ServiceNotAvailableError as error:
        print(f"ERROR: {error}")

    G = procesa_grafo(Gmulti)
    explorar_grafo(G)
    dibujar_grafo_networkx(G)
