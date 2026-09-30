"""
gps.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP305
Integrantes:
    - Míriam Mingo Revuelta
    - Ángela Porres Cobb
"""

import math
import osmnx as ox
from callejero import MAX_SPEEDS, carga_callejero, busca_direccion, carga_grafo, procesa_grafo, AddressNotFoundError, ServiceNotAvailableError
from grafo_pesado import camino_minimo, INFTY

 
def tiempo_recorrer_arista(G, u, v):
    arista = G[u][v]  # Seleccionamos la primera arista entre u y v
    dist = arista.get("length", INFTY) # Coge la distancia y si no hay, la establece como infinita
    vmax = arista.get("maxspeed") # Coge la velocidad máxima en esa arista
    
    try:
        if type(vmax) == list: # En caso de que una arista tenga más de una velocidad, se utilizará la primera    ????????????????
            vmax = float(vmax[0])
        else:
            vmax = float(vmax)
    except:
        # En caso de que la arista no tenga como atributo vmax, se establecerá una velocidad por defecto 
        # dependiendo del tipo de vía
        tipo_via = arista.get("highway")
        if type(tipo_via) == list:  # En caso de que una arista tenga más de un tipo de via, se utilizará la primera   ????????????????????
            vmax = float(MAX_SPEEDS[tipo_via[0]])
        else:
            vmax = float(MAX_SPEEDS[tipo_via])

    v_ms = vmax * 1000/3600   # Convertimos los km/h a m/s
    return dist / v_ms  # Devolvemos el tiempo en segundos para recorrer la arista entre u y v


def nodo_mas_cercano(G, lat, lon):
    """Devuelve el nodo más cercano del grafo a la coordenada a esa latitud y longuitud"""
    return ox.distance.nearest_nodes(G, X=lon, Y=lat)
 
def elegir_modo_ruta():
    print("\nSelecciona el modo de ruta:")
    print("1) Ruta más corta")
    print("2) Ruta más rápida")
    print("3) Ruta con más rápida considerando los semáforos")
    op = input("Ruta: ").strip()

    # G[u][v][0] selecciona la primera arista entre u y v
    if op == "1":
        # Seleccionamos la primera arista entre u y v (da igual cual elijamos porque todas medirán lo mismo)
        # Sacamos la distancia entre estos dos vértices y lo devolvemos
        return lambda G,u,v: G[u][v].get("length", INFTY)  # Distancia entre u y v
    
    elif op == "2":
        return tiempo_recorrer_arista  # Devolvemos la funcion tiempo para usarla posteriormente 
            
    elif op == "3":
        def tiempo_semaforos(G, u, v):
            t_viaje = tiempo_recorrer_arista(G, u, v)

            # El atributo degree es el número de calles conectadas a ese nodo, por lo que solo en caso de que tenga
            # más de una entrada y una salida, será una intersección.
            if G.degree[v] >= 3:  
                prob = 0.8
                t_parada = 30
                return t_viaje + prob * t_parada
            
            return t_viaje

        return tiempo_semaforos

    else:
        print("Opción inválida, usando ruta más corta")
        return lambda G,u,v: G[u][v].get("length", INFTY)
 
def angulo_entre_vectores(p1, p2, p3):
    """
    Calcula el ángulo entre los vectores p1->p2 y p2->p3.
    Devuelve un ángulo positivo = giro a la izquierda
    y un ángulo negativo = giro a la derecha.
    """
    v1 = (p2[0] - p1[0], p2[1] - p1[1])  # p1->p2
    v2 = (p3[0] - p2[0], p3[1] - p2[1])  # p2->p3

    # Producto vectorial
    prod_vectorial = v1[0]*v2[1] - v1[1]*v2[0]
    # Producto escalar
    prod_escalar = v1[0]*v2[0] + v1[1]*v2[1]

    ang = math.atan2(prod_vectorial, prod_escalar)
    return ang  # radianes


def generar_instrucciones(G, ruta):
    """Genera instrucciones del estilo de un GPS a partir de una lista de nodos"""
    instrucciones = []

    if len(ruta) < 2:  # En caso de que origen destino sean el mismo nodo
        return ["Ruta demasiado corta"]
    
    nodo_prev = ruta[0] # Seleccionamos el primer nodo del camino
    arista = G[nodo_prev][ruta[1]]  # Arista entre el nodo_prev y el segundo nodo del camino
    calle_actual = arista.get("name", "calle desconocida") 

    instrucciones.append(f"Comience avanzando por {calle_actual}.")
    distancia = 0

    for i in range(1, len(ruta)):
        nodo_actual = ruta[i - 1]
        nodo_sig = ruta[i]

        arista = G[nodo_actual][nodo_sig]  
        nombre_calle = arista.get("name", "calle desconocida")
        longitud = arista.get("length", 0)

        distancia += longitud

        if nombre_calle != calle_actual:
            if i >= 2:  # Solo en caso de que haya al menos 3 nodos en la ruta 

                # Caluclamos el ángulo entre los tres nodos consecutivos, y con el signo sabemos si hay que
                # que girar a la izquierda o a la derecha

                # Obtenemos las coordenadas de cada punto
                p1 = (G.nodes[ruta[i-2]]['x'], G.nodes[ruta[i-2]]['y'])
                p2 = (G.nodes[ruta[i-1]]['x'], G.nodes[ruta[i-1]]['y'])
                p3 = (G.nodes[ruta[i]]['x'], G.nodes[ruta[i]]['y'])

                # Calculamos 
                angulo = angulo_entre_vectores(p1, p2, p3)

                if angulo > 0:
                    giro = "a la izquierda"
                else:
                    giro = "a la derecha"
            else:
                giro = ""

            instrucciones.append(f"Continúe {distancia:.0f} m por {calle_actual}")
            instrucciones.append(f"Gire {giro} hacia {nombre_calle}")           
            calle_actual = nombre_calle
            distancia = 0  # Como ha cambiado de calle reseteamos la distancia

    instrucciones.append(f"Continúe {distancia:.0f} m por {calle_actual} hasta el destino")
    return instrucciones


def dibujar_ruta(G, ruta):
    """
    Dibuja gráficamente la ruta que hemos calculado entre dos direcciones
    extablecidas por el usuario.
    """
    # Obtenemos los nodos como arrays de coordenadas
    xs = [G.nodes[n]['x'] for n in ruta] # Sacamos todas las longitudes de los nodos de la ruta
    ys = [G.nodes[n]['y'] for n in ruta] # Sacamos todas las latitudes de los nodos de la ruta

    # Creamos el rectángulo más pequeño que contiene todas las coordenadas
    zoom = 0.002   # (Aumentar el valor para ver más zona)
    oeste, este = min(xs)-zoom, max(xs)+zoom
    sur, norte = min(ys)-zoom, max(ys)+zoom

    # Recortamos el grafo a esa zona
    # Generamos un grafo de calles solo dentro de los límites: norte, sur, este, oeste
    # network_type='drive': con esto seleccionamos calles solo para vehículos
    G_recortado_coche = ox.graph_from_bbox(north=norte, south=sur, east=este, west=oeste, network_type='drive') 

    # Dibujamos
    fig, ax = ox.plot_graph_route(
        G_recortado_coche,
        ruta,
        route_color="red",
        route_linewidth=4,
        node_size=0,
        bgcolor="white")
 


if __name__ == "__main__":
    try:
        callejero = carga_callejero()
    except FileNotFoundError as error:
        print(f"ERROR: {error}")

    try:
        G_multi = carga_grafo()
    except ServiceNotAvailableError as error:
        print(f"ERROR: {error}")

    G = procesa_grafo(G_multi)
    print("Grafo de Madrid sin duplicados cargado correctamente")

    print("\nGPS DE MADRID")
    continuar = True
    while continuar:
        origen = input("Introduzca la dirección de origen: ").strip()
        if origen == "":
            print("Saliendo del GPS...")
            continuar = False
        else:
            destino = input("Introduzca la dirección de destino: ").strip()
            if destino == "":
                print("Saliendo del GPS...")
                continuar = False
            
            else:
                seguir = True
                try:
                    (lat_orig, lon_orig) = busca_direccion(origen, callejero)
                    (lat_dest, lon_dest) = busca_direccion(destino, callejero)
                    print("Origen y Destino válidos")
                
                except AddressNotFoundError as error:
                    print(error)
                    seguir = False
                
                if seguir:
                    nodo_origen = nodo_mas_cercano(G, lat_orig, lon_orig)
                    nodo_destino = nodo_mas_cercano(G, lat_dest, lon_dest)
                    
                    modo_ruta = elegir_modo_ruta()  # Función de peso elegida por el usuario
                    
                    # Creamos una lista ordenada de nodos desde el nodo origen hasta el nodo destino
                    ruta = camino_minimo(G, modo_ruta, nodo_origen, nodo_destino)
                    
                    if not ruta:
                        print("No existe ninguna ruta válida entre los lugares seleccionados.")
                    else:
                        instrucciones = generar_instrucciones(G, ruta)
                        
                        print("\n   INSTRUCCIONES DE LA RUTAA")
                        for ins in instrucciones:
                            print(" -", ins)
                        
                        dibujar_ruta(G, ruta)
