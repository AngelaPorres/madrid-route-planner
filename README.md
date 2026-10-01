# Madrid Route Planner 🗺️

A route planning application for Madrid developed in **Python** using graph algorithms and real-world street network data from **OpenStreetMap**.

The project models Madrid's road network as a weighted graph and calculates routes between two addresses using an implementation of **Dijkstra's shortest path algorithm**.

## 🚗 Features

The application allows the user to enter an origin and destination address in Madrid and choose between three routing modes:

- **Shortest route** — minimizes total distance
- **Fastest route** — minimizes estimated travel time based on road speed limits
- **Fastest route considering traffic lights** — incorporates an estimated delay at intersections

Once the route is calculated, the application:

- Finds the closest graph nodes to the selected addresses
- Calculates the optimal path using Dijkstra's algorithm
- Generates turn-by-turn driving instructions
- Identifies left and right turns using geometric calculations
- Displays the resulting route on the Madrid street network

## 🧠 Algorithms & Concepts

### Dijkstra's Algorithm

The shortest path algorithm is implemented from scratch using a priority queue.

Different edge-weight functions can be used depending on the selected routing mode, allowing the same algorithm to optimize either distance or estimated travel time.

### Weighted Graphs

Madrid's road network is represented as a weighted directed graph:

- **Nodes** represent locations/intersections
- **Edges** represent road segments
- **Weights** represent distance or estimated travel time

### Route Instructions

The application generates driving instructions by detecting changes between streets and calculating the angle between consecutive road segments to determine whether the route turns left or right.

## 🛠️ Technologies

- **Python**
- **NetworkX** — graph representation and processing
- **OSMnx** — OpenStreetMap road network data and route visualization
- **Matplotlib** — visualization

## 📂 Project Structure

```text
madrid-route-planner/
│
├── gps.py              # Main application and route instructions
├── callejero.py        # Address and Madrid street-network processing
├── grafo_pesado.py     # Graph algorithms
├── requirements.txt    # Project dependencies
├── .gitignore
└── README.md
```

## 🚀 How to Run

1. Clone or download this repository.

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python gps.py
```

4. Enter an origin and destination address when prompted and select the desired routing mode.

> The application may require an internet connection to retrieve OpenStreetMap data when it is not already available locally.

## 👩‍💻 Authors

**Míriam Mingo Revuelta**  
**Ángela Porres Cobb**

Mathematical Engineering and Artificial Intelligence  
Universidad Pontificia Comillas – ICAI 
