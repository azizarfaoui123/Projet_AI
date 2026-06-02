"""
╔══════════════════════════════════════════════════════════════╗
║  robot.py — Le robot et son déplacement                      ║
║                                                              ║
║  Rôle : une fois le chemin calculé par BFS ou DFS,           ║
║  le Robot suit ce chemin pas à pas.                          ║
║  L'interface appelle move_next() à chaque frame d'animation. ║
╚══════════════════════════════════════════════════════════════╝
"""


class Robot:
    def __init__(self, start_pos):
        """
        start_pos : tuple (ligne, colonne) — position initiale du robot.
        """
        self.row, self.col = start_pos  # position courante
        self.path = []                  # liste de (ligne, colonne) du chemin complet
        self.step_index = 0             # indice de la position courante dans self.path

    def set_path(self, path):
        """
        Charge le chemin calculé par BFS/DFS.
        Remet le compteur à zéro pour repartir du début.
        """
        self.path = path
        self.step_index = 0

    def move_next(self):
        """
        Avance d'un pas sur le chemin.
        Met à jour self.row et self.col.
        Retourne True si le déplacement a eu lieu, False si on est déjà à la fin.
        Appelé à chaque tick de l'animation dans visualizer._animate_move().
        """
        if self.step_index < len(self.path) - 1:
            self.step_index += 1
            self.row, self.col = self.path[self.step_index]
            return True
        return False  # chemin terminé

    def position(self):
        """Retourne la position courante sous forme de tuple (ligne, colonne)."""
        return (self.row, self.col)

    def at_target(self, target):
        """Vérifie si le robot est arrivé à la cible."""
        return self.position() == target
