import random
import os
import tkinter as tk
from tkinter import messagebox

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def afficher_batonnets(tab):
    cls()
    n = len(tab)
    print("Bâtonnets restants : {}".format(tab.count('|')))
    lignes_chiffres = ''
    lignes_batonnets = ''
    for i, val in enumerate(tab):
        if val == '|':
            lignes_chiffres += f"{i+1:2} "
        else:
            lignes_chiffres += "   "
        lignes_batonnets += f" {val} "
    print(lignes_chiffres)
    print(lignes_batonnets)
    print()

def saisie_joueur(tab):
    while True:
        try:
            choix = int(input("Votre tour, retirez 1-3 bâtonnets : "))
            if 1 <= choix <= 3 and choix <= tab.count('|'):
                return choix
        except ValueError:
            pass
        print("Entrée invalide. Choisissez un nombre entre 1 et 3, <= restants.")

import math
import time

class MCTSNode:
    def __init__(self, sticks, parent=None, move=None):
        self.sticks = sticks
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0

    def uct(self, total_simulations, exploration=math.sqrt(2)):
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + exploration * math.sqrt(math.log(total_simulations) / self.visits)

    def is_fully_expanded(self):
        return len(self.children) == min(3, self.sticks)

    def best_child(self, exploration=math.sqrt(2)):
        total_simulations = sum(child.visits for child in self.children)
        return max(self.children, key=lambda c: c.uct(total_simulations, exploration))

def mcts(root_sticks, itermax=1000, time_limit=1.0):
    root = MCTSNode(root_sticks)

    def select(node):
        while node.children:
            node = node.best_child()
        return node

    def expand(node):
        if node.sticks == 0:
            return
        moves = [move for move in range(1, min(3, node.sticks) + 1)]
        for move in moves:
            if not any(child.move == move for child in node.children):
                child = MCTSNode(node.sticks - move, parent=node, move=move)
                node.children.append(child)
                return child
        return node

    def simulate(sticks):
        turn = True  # True for AI, False for opponent
        current_sticks = sticks
        while current_sticks > 0:
            move = random.randint(1, min(3, current_sticks))
            current_sticks -= move
            turn = not turn
        return turn  # True if AI wins

    def backpropagate(node, result):
        while node:
            node.visits += 1
            if result:
                node.wins += 1
            node = node.parent

    start_time = time.time()
    iterations = 0
    while iterations < itermax and (time.time() - start_time) < time_limit:
        node = select(root)
        child = expand(node)
        if child is None:
            child = node
        result = simulate(child.sticks)
        backpropagate(child, result)
        iterations += 1

    best_move = max(root.children, key=lambda c: c.visits).move if root.children else 1
    return best_move

def ia_simple(tab):
    n = tab.count('|')
    # Stratégie gagnante du jeu de Nim
    optimal = n % 4
    if optimal == 0:
        # Si on ne peut pas gagner directement, on utilise MCTS pour choisir le meilleur coup possible
        return mcts(n, itermax=5000, time_limit=2.0)
    else:
        return optimal

def retirer_batonnets(tab, nb):
    count = 0
    for i in range(len(tab)):
        if tab[i] == '|':
            tab[i] = ' '
            count += 1
            if count == nb:
                break

def boucle_de_jeu(initial=21, solo=False):
    tab = ['|' for _ in range(initial)]
    tour_joueur = True
    while tab.count('|') > 0:
        afficher_batonnets(tab)
        if tour_joueur:
            retrait = saisie_joueur(tab)
        else:
            retrait = ia_simple(tab) if solo else saisie_joueur(tab)
            print(f"{'IA' if solo else 'Joueur 2'} retire {retrait} bâtonnet(s).")
            input("Appuyez sur Entrée pour continuer...")
        retirer_batonnets(tab, retrait)
        tour_joueur = not tour_joueur
    perdant = 'vous' if not tour_joueur else ('IA' if solo else 'Joueur 2')
    afficher_batonnets(tab)
    print(f"Game over. Le perdant est {perdant} !")

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QInputDialog
)
import sys

class StickGameQt(QWidget):
    def __init__(self, initial=21, solo=False):
        super().__init__()
        self.solo = solo
        self.initial = initial
        self.tab = ['|' for _ in range(initial)]
        self.tour_joueur = True
        self.setWindowTitle("Jeu des Bâtonnets")
        self.info = QLabel("", self)
        self.sticks_label = QLabel("", self)
        self.buttons = []
        btn_layout = QHBoxLayout()
        for i in range(1, 4):
            btn = QPushButton(f"Retirer {i}", self)
            btn.clicked.connect(lambda checked, x=i: self.retirer(x))
            btn_layout.addWidget(btn)
            self.buttons.append(btn)
        layout = QVBoxLayout()
        layout.addWidget(self.info)
        layout.addWidget(self.sticks_label)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.update_display()

    def update_display(self):
        n = self.tab.count('|')
        self.sticks_label.setText(" ".join(self.tab))
        if n == 0:
            perdant = "vous" if not self.tour_joueur else ("IA" if self.solo else "Joueur 2")
            self.info.setText(f"Game over. Le perdant est {perdant} !")
            for btn in self.buttons:
                btn.setEnabled(False)
            return
        joueur = "Votre tour" if self.tour_joueur else ("Tour de l'IA" if self.solo else "Tour du joueur 2")
        self.info.setText(f"Bâtonnets restants : {n} | {joueur}")
        for btn in self.buttons:
            btn.setEnabled(n >= int(btn.text()[-1]))
        if not self.tour_joueur and self.solo and n > 0:
            QTimer.singleShot(800, self.ia_play)

    def retirer(self, nb):
        if nb > self.tab.count('|'):
            return
        retirer_batonnets(self.tab, nb)
        self.tour_joueur = not self.tour_joueur
        self.update_display()

    def ia_play(self):
        retrait = ia_simple(self.tab)
        self.retirer(retrait)

from PyQt5.QtCore import QTimer

def main_qt():
    app = QApplication(sys.argv)
    mode, ok = QInputDialog.getText(None, "Mode", "Mode: 1=2 joueurs, 2=solo vs IA?")
    solo = (mode or '').strip() == '2'
    window = StickGameQt(solo=solo)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    try:
        main_qt()
    except Exception as e:
        print("Erreur PyQt5, retour au mode console :", e)
        mode = input("Mode: 1=2 joueurs, 2=solo vs IA? ")
        solo = mode.strip() == '2'
        boucle_de_jeu(solo=solo)