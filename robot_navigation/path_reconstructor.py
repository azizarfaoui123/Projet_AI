"""
╔══════════════════════════════════════════════════════════════╗
║  path_reconstructor.py — Reconstruction du chemin solution   ║
║                                                              ║
║  Rôle : une fois la cible atteinte par BFS ou DFS, on a le   ║
║  Node cible. Ce module remonte la chaîne de parents          ║
║  (cible → ... → départ) et retourne la liste ordonnée        ║
║  des positions du départ jusqu'à la cible.                   ║
╚══════════════════════════════════════════════════════════════╝
"""


class PathReconstructor:
    @staticmethod
    def reconstruct(node):
        """
        Remonte la chaîne node.parent jusqu'à None (le nœud de départ).

        Exemple :
          node cible → parent → parent → ... → node départ (parent=None)

        On collecte les positions dans l'ordre inverse, puis on retourne
        la liste retournée → chemin du départ à la cible.
        """
        path = []
        current = node
        while current is not None:
            path.append(current.state())  # ajoute (ligne, colonne)
            current = current.parent      # remonte d'un niveau
        path.reverse()                    # inverse : départ → cible
        return path
