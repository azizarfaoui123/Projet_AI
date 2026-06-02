"""
╔══════════════════════════════════════════════════════════════╗
║  node.py — Représentation d'un état de l'espace de recherche ║
║                                                              ║
║  Rôle : chaque case visitée par BFS ou DFS est un Node.      ║
║  Un Node mémorise sa position ET son parent, ce qui permet   ║
║  de remonter le chemin solution depuis la cible jusqu'au     ║
║  départ (utilisé par PathReconstructor).                     ║
╚══════════════════════════════════════════════════════════════╝
"""


class Node:
    def __init__(self, row, col, parent=None):
        self.row = row        # ligne dans la grille
        self.col = col        # colonne dans la grille
        self.parent = parent  # Node précédent dans le chemin (None pour le départ)

    def state(self):
        """Retourne la position sous forme de tuple (ligne, colonne).
        Utilisé comme clé dans les ensembles 'visited'."""
        return (self.row, self.col)

    def __eq__(self, other):
        """Deux nodes sont égaux s'ils ont la même position."""
        return isinstance(other, Node) and self.state() == other.state()

    def __hash__(self):
        """Permet d'utiliser Node dans un set ou dict."""
        return hash(self.state())

    def __repr__(self):
        return f"Node({self.row}, {self.col})"
