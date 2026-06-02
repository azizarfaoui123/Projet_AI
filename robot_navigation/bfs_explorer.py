"""
╔══════════════════════════════════════════════════════════════╗
║  bfs_explorer.py — Algorithme BFS (Breadth-First Search)     ║
║                                                              ║
║  Principe : explore la grille niveau par niveau (en largeur).║
║  Garantit de trouver le chemin le PLUS COURT dans une grille ║
║  non pondérée.                                               ║
║                                                              ║
║  Structure de données : FILE (deque) — FIFO                  ║
║    → on ajoute à droite (append) et on retire à gauche       ║
║      (popleft), ce qui garantit l'ordre niveau par niveau.   ║
╚══════════════════════════════════════════════════════════════╝
"""

import time
from collections import deque       # file double-extrémité, efficace pour BFS
from node import Node
from path_reconstructor import PathReconstructor

# Les 4 directions cardinales : haut, bas, gauche, droite
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class BFSExplorer:
    def __init__(self, room):
        self.room = room            # référence à la grille (Room)

        # Résultats remplis après search()
        self.explored = []          # liste ordonnée des cases visitées (pour l'animation)
        self.path = []              # chemin solution : liste de (ligne, colonne)
        self.nodes_explored = 0     # compteur de nœuds traités
        self.path_length = 0        # nombre de pas du chemin (= len(path) - 1)
        self.exec_time = 0.0        # temps d'exécution en secondes
        self.success = False        # True si la cible a été atteinte

    def search(self):
        """
        Lance la recherche BFS depuis room.start jusqu'à room.target.

        Algorithme :
          1. Initialise la file avec le nœud de départ
          2. Tant que la file n'est pas vide :
             a. Retire le premier nœud (popleft)
             b. Si c'est la cible → reconstruit le chemin et s'arrête
             c. Sinon → ajoute ses voisins valides non visités dans la file
          3. Si la file se vide sans trouver la cible → échec
        """
        start_time = time.time()
        start  = self.room.start
        target = self.room.target

        queue   = deque()   # FILE : structure principale de BFS
        visited = set()     # ensemble des cases déjà ajoutées à la file (évite les doublons)

        # Initialisation : on part du nœud de départ
        start_node = Node(start[0], start[1])
        queue.append(start_node)
        visited.add(start_node.state())  # marqué visité dès l'ajout (pas à la sortie)

        while queue:
            current = queue.popleft()           # retire le plus ancien (FIFO)
            self.explored.append(current.state())
            self.nodes_explored += 1

            # Test de l'objectif
            if current.state() == target:
                self.path = PathReconstructor.reconstruct(current)
                self.path_length = len(self.path) - 1
                self.success = True
                break

            # Génération des successeurs (4 directions)
            for dr, dc in DIRECTIONS:
                nr, nc = current.row + dr, current.col + dc
                if self.room.is_valid(nr, nc) and (nr, nc) not in visited:
                    visited.add((nr, nc))                          # marquer avant d'ajouter
                    queue.append(Node(nr, nc, parent=current))     # parent = current pour reconstruire

        self.exec_time = time.time() - start_time
        return self.success
