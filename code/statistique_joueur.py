from datetime import datetime

class StatistiqueJoueur:
    """Classe représentant les statistiques d'un joueur pour un match"""

    def __init__(self, temps_jeu, points, passes, rebonds, date_match=None):
        self._valider_statistiques(temps_jeu, points, passes, rebonds)

        self._temps_jeu = temps_jeu  # en minutes
        self._points = points
        self._passes = passes  # passes décisives
        self._rebonds = rebonds
        self._date_match = date_match or datetime.now()

    def _valider_statistiques(self, temps_jeu, points, passes, rebonds):
        """Valide les statistiques fournies"""
        if temps_jeu < 0 or temps_jeu > 48:
            raise ValueError("Le temps de jeu doit être entre 0 et 48 minutes")
        if points < 0:
            raise ValueError("Les points ne peuvent pas être négatifs")
        if passes < 0:
            raise ValueError("Les passes ne peuvent pas être négatives")
        if rebonds < 0:
            raise ValueError("Les rebonds ne peuvent pas être négatifs")

    @property
    def temps_jeu(self):
        return self._temps_jeu

    @property
    def points(self):
        return self._points

    @property
    def passes(self):
        return self._passes

    @property
    def rebonds(self):
        return self._rebonds

    @property
    def date_match(self):
        return self._date_match

    def calculer_efficacite(self):
        """Calcule un indice d'efficacité simple"""
        if self._temps_jeu == 0:
            return 0
        return (self._points + self._passes + self._rebonds) / self._temps_jeu

    def __str__(self):
        return f"Stats: {self._points}pts, {self._passes}pd, {self._rebonds}reb en {self._temps_jeu}min"
