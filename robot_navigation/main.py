"""
╔══════════════════════════════════════════════════════════════╗
║  main.py — Point d'entrée du programme                       ║
║                                                              ║
║  Rôle : démarrer l'application tkinter.                      ║
║  C'est le seul fichier à exécuter : python main.py           ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from visualizer import Visualizer  # importe la classe qui gère toute l'interface


def main():
    root = tk.Tk()          # crée la fenêtre principale tkinter
    app = Visualizer(root)  # construit l'interface et charge la carte par défaut
    root.mainloop()         # boucle d'événements : garde la fenêtre ouverte


if __name__ == "__main__":
    main()
