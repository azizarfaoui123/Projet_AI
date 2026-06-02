"""
╔══════════════════════════════════════════════════════════════╗
║  room.py — Modélisation de la pièce (grille 2D)              ║
║                                                              ║
║  Rôle : représente l'environnement du robot sous forme       ║
║  d'une grille de caractères. Contient aussi les 3 cartes     ║
║  prédéfinies et la génération aléatoire.                     ║
╚══════════════════════════════════════════════════════════════╝

Conventions des cellules :
  '#'  OBSTACLE  — mur, case infranchissable
  '.'  FREE      — case libre, le robot peut y passer
  'R'  ROBOT     — position initiale du robot
  'C'  TARGET    — cible à atteindre
  '*'  PATH      — case faisant partie du chemin solution (affichage uniquement)
"""

import random

# ── Constantes des types de cellules ──────────────────────────
OBSTACLE = '#'
FREE     = '.'
ROBOT    = 'R'
TARGET   = 'C'
PATH     = '*'

# ── Cartes prédéfinies ─────────────────────────────────────────
# Chaque carte est une liste de chaînes de caractères.
# Taille minimale requise : 22 colonnes × 12 lignes.
MAPS = {
    # Carte simple : couloir principal avec quelques détours
    "Simple": [
        "######################",
        "#R...................#",
        "#.##########.........#",
        "#.#........#.#######.#",
        "#.#.######.#.#.......#",
        "#.#.#......#.#.#####.#",
        "#.#.#.####.#.#.#...#.#",
        "#...#......#...#.#.#.#",
        "#####.##########.#.#.#",
        "#.....#..........#...#",
        "#.#####.##########.#.#",
        "#...................C#",
        "######################",
    ],
    # Carte dense : beaucoup d'obstacles, chemin plus tortueux
    "Dense": [
        "######################",
        "#R..#...#...#...#....#",
        "#.#.#.#.#.#.#.#.#.##.#",
        "#.#...#...#...#...#..#",
        "#.########...######..#",
        "#.........#..#.......#",
        "#.#######.#..#.#####.#",
        "#.#.......#..#.#.....#",
        "#.#.#######..#.#.###.#",
        "#.#..........#...#...#",
        "#.############...#.#.#",
        "#................#.C.#",
        "######################",
    ],
    # Carte piège : spirale concentrique, chemin unique et long
    "Piège": [
        "######################",
        "#R...................#",
        "#.##################.#",
        "#.#................#.#",
        "#.#.##############.#.#",
        "#.#.#............#.#.#",
        "#.#.#.##########.#.#.#",
        "#.#.#.#........#.#.#.#",
        "#.#.#.#.######.#.#.#.#",
        "#.#.#.#........#.#.#.#",
        "#.#.#.##########.#.#.#",
        "#.#..............#.C.#",
        "######################",
    ],
}


class Room:
    def __init__(self, grid=None, rows=13, cols=22):
        """
        Paramètres :
          grid  — liste de chaînes (carte prédéfinie). Si None, génération aléatoire.
          rows  — nombre de lignes (utilisé seulement si grid=None)
          cols  — nombre de colonnes (utilisé seulement si grid=None)
        """
        if grid:
            # Convertit chaque ligne en liste de caractères pour pouvoir modifier les cellules
            self.grid = [list(row) for row in grid]
            self.rows = len(self.grid)
            self.cols = max(len(r) for r in self.grid)
        else:
            # Génération aléatoire avec taille minimale garantie
            self.rows = max(rows, 12)
            self.cols = max(cols, 22)
            self.grid = self._generate_random()

        # Localise automatiquement le départ (R) et la cible (C)
        self.start  = self._find(ROBOT)
        self.target = self._find(TARGET)

    def _find(self, char):
        """Parcourt la grille et retourne (ligne, colonne) du caractère cherché."""
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                if cell == char:
                    return (r, c)
        return None  # non trouvé

    def is_valid(self, r, c):
        """
        Vérifie si une case est accessible :
          - dans les limites de la grille
          - pas un obstacle
        Utilisé par BFS et DFS pour filtrer les voisins.
        """
        return (0 <= r < self.rows and
                0 <= c < self.cols and
                self.grid[r][c] != OBSTACLE)

    def get_cell(self, r, c):
        """Retourne le caractère de la cellule (r, c)."""
        return self.grid[r][c]

    def set_cell(self, r, c, val):
        """Modifie la cellule (r, c) — utilisé par le mode édition de l'interface."""
        self.grid[r][c] = val

    def _generate_random(self):
        """
        Génère une grille aléatoire :
          1. Remplit tout de cases libres
          2. Pose des murs sur toute la bordure
          3. Place des obstacles aléatoires (~20% des cases intérieures)
          4. Place le robot en (1,1) et la cible en bas à droite
        """
        grid = [[FREE] * self.cols for _ in range(self.rows)]

        # Bordures (murs extérieurs)
        for r in range(self.rows):
            grid[r][0] = grid[r][self.cols - 1] = OBSTACLE
        for c in range(self.cols):
            grid[0][c] = grid[self.rows - 1][c] = OBSTACLE

        # Obstacles intérieurs aléatoires
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if random.random() < 0.20:
                    grid[r][c] = OBSTACLE

        # Positions fixes du robot et de la cible
        grid[1][1] = ROBOT
        grid[self.rows - 2][self.cols - 2] = TARGET
        return grid

    def copy_grid(self):
        """Retourne une copie profonde de la grille (utile pour sauvegarder un état)."""
        return [row[:] for row in self.grid]
