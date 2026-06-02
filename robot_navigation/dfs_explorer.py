"""
╔══════════════════════════════════════════════════════════════╗
║  dfs_explorer.py — Algorithme DFS (Depth-First Search)       ║
║                                                              ║
║  Principe : explore la grille en profondeur d'abord.         ║
║  Suit un chemin jusqu'au bout avant de revenir en arrière.   ║
║  Ne garantit PAS le chemin le plus court.                    ║
║                                                              ║
║  Structure de données : PILE (list) — LIFO                   ║
║    → on ajoute avec append() et on retire avec pop(),        ║
║      ce qui donne la priorité au dernier nœud ajouté.        ║
╚══════════════════════════════════════════════════════════════╝
"""

import time
from node import Node
from path_reconstructor import PathReconstructor

# Les 4 directions cardinales : haut, bas, gauche, droite
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class DFSExplorer:
    def __init__(self, room):
        self.room = room            # référence à la grille (Room)

        # Résultats remplis après search()
        self.explored = []          # liste ordonnée des cases visitées (pour l'animation)
        self.path = []              # chemin solution : liste de (ligne, colonne)
        self.nodes_explored = 0     # compteur de nœuds traités
        self.path_length = 0        # nombre de pas du chemin
        self.exec_time = 0.0        # temps d'exécution en secondes
        self.success = False        # True si la cible a été atteinte

    def search(self):
        """
        Lance la recherche DFS depuis room.start jusqu'à room.target.

        Différence clé avec BFS :
          - BFS utilise une FILE (popleft) → niveau par niveau
          - DFS utilise une PILE (pop)     → en profondeur d'abord

        Algorithme :
          1. Initialise la pile avec le nœud de départ
          2. Tant que la pile n'est pas vide :
             a. Retire le dernier nœud (pop — LIFO)
             b. Si déjà visité → ignore (un nœud peut être ajouté plusieurs fois)
             c. Marque comme visité
             d. Si c'est la cible → reconstruit le chemin et s'arrête
             e. Sinon → ajoute ses voisins non visités dans la pile
          3. Si la pile se vide sans trouver la cible → échec

        Note : le marquage se fait à la SORTIE de la pile (pas à l'ajout),
        contrairement à BFS. C'est pourquoi on vérifie 'if current.state() in visited'.
        """
        start_time = time.time()
        start  = self.room.start
        target = self.room.target

        stack   = []        # PILE : structure principale de DFS
        visited = set()     # ensemble des cases déjà traitées

        start_node = Node(start[0], start[1])
        stack.append(start_node)

        while stack:
            current = stack.pop()   # retire le dernier ajouté (LIFO)

            # Un même nœud peut être dans la pile plusieurs fois → on l'ignore si déjà traité
            if current.state() in visited:
                continue
            visited.add(current.state())
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
                    stack.append(Node(nr, nc, parent=current))  # parent = current

        self.exec_time = time.time() - start_time
        return self.success
