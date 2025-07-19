
def ia_simple(tab):
    n = tab.count("|")
    optimal = n % 4
    if optimal == 0:
        # Si l'IA ne peut pas forcer la victoire, elle retire 1 bâtonnet par défaut
        return 1
    else:
        # Sinon, elle joue le coup gagnant
        return optimal


def retirer_batonnets(tab, nb):
    count = 0
    for i in range(len(tab)):
        if tab[i] == "|":
            tab[i] = " "
            count += 1
            if count == nb:
                break


from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QInputDialog,
)
import sys


class StickGameQt(QWidget):
    def __init__(self, initial=21, solo=False):
        super().__init__()
        self.solo = solo
        self.initial = initial
        self.tab = ["|" for _ in range(initial)]
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
        n = self.tab.count("|")
        self.sticks_label.setText(" ".join(self.tab))
        if n == 0:
            perdant = (
                "vous" if not self.tour_joueur else ("IA" if self.solo else "Joueur 2")
            )
            self.info.setText(f"Game over. Le perdant est {perdant} !")
            for btn in self.buttons:
                btn.setEnabled(False)
            return
        joueur = (
            "Votre tour"
            if self.tour_joueur
            else ("Tour de l'IA" if self.solo else "Tour du joueur 2")
        )
        self.info.setText(f"Bâtonnets restants : {n} | {joueur}")
        # Désactive les boutons si ce n'est pas le tour du joueur
        if self.solo:
            for btn in self.buttons:
                btn.setEnabled(self.tour_joueur and n >= int(btn.text()[-1]))
        if not self.tour_joueur and self.solo and n > 0:
            QTimer.singleShot(800, self.ia_play)

    def retirer(self, nb):
        if nb > self.tab.count("|"):
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
    solo = (mode or "").strip() == "2"
    window = StickGameQt(solo=solo)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main_qt()