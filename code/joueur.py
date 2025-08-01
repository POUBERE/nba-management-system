from datetime import datetime
from personne import Personne
from statistique_joueur import StatistiqueJoueur
from enum import Enum

class PosteJoueur(Enum):
    """Énumération pour les postes de joueur"""
    POINT_GUARD = "Point Guard"
    SHOOTING_GUARD = "Shooting Guard"
    SMALL_FORWARD = "Small Forward"
    POWER_FORWARD = "Power Forward"
    CENTER = "Center"


class Joueur(Personne):
    """Classe représentant un joueur NBA"""

    def __init__(self, nom, origine, annee_debut, poste):
        super().__init__(nom, origine)

        if not isinstance(annee_debut, int) or annee_debut < 1946:
            raise ValueError("L'année de début doit être un entier >= 1946")

        if isinstance(poste, str):
            # Conversion depuis string vers enum pour compatibilité
            poste_map = {
                "Point Guard": PosteJoueur.POINT_GUARD,
                "Shooting Guard": PosteJoueur.SHOOTING_GUARD,
                "Small Forward": PosteJoueur.SMALL_FORWARD,
                "Power Forward": PosteJoueur.POWER_FORWARD,
                "Center": PosteJoueur.CENTER
            }
            if poste not in poste_map:
                raise ValueError(f"Poste invalide: {poste}")
            poste = poste_map[poste]
        elif not isinstance(poste, PosteJoueur):
            raise ValueError("Le poste doit être un PosteJoueur")

        self._annee_debut = annee_debut
        self._poste = poste
        self._statistiques = []
        self._equipe = None

    @property
    def annee_debut(self):
        return self._annee_debut

    @property
    def poste(self):
        return self._poste

    @property
    def equipe(self):
        return self._equipe

    @equipe.setter
    def equipe(self, equipe):
        if equipe is not None and not hasattr(equipe, 'nom'):
            raise ValueError("L'équipe doit avoir un attribut 'nom'")
        self._equipe = equipe

    def ajouter_statistiques(self, temps_jeu, points, passes, rebonds, date_match=None):
        """Ajouter des statistiques pour ce joueur"""
        try:
            stat = StatistiqueJoueur(temps_jeu, points, passes, rebonds, date_match)
            self._statistiques.append(stat)
            return True
        except ValueError as e:
            raise e

    def calculer_moyennes(self):
        """Calculer les moyennes des statistiques"""
        if not self._statistiques:
            return None

        total_temps = sum(stat.temps_jeu for stat in self._statistiques)
        total_points = sum(stat.points for stat in self._statistiques)
        total_passes = sum(stat.passes for stat in self._statistiques)
        total_rebonds = sum(stat.rebonds for stat in self._statistiques)
        nb_matchs = len(self._statistiques)

        return {
            'temps_jeu': total_temps / nb_matchs,
            'points': total_points / nb_matchs,
            'passes': total_passes / nb_matchs,
            'rebonds': total_rebonds / nb_matchs,
            'matchs_joues': nb_matchs,
            'efficacite_moyenne': sum(stat.calculer_efficacite() for stat in self._statistiques) / nb_matchs
        }

    def obtenir_meilleures_stats(self):
        """Retourne les meilleures statistiques du joueur"""
        if not self._statistiques:
            return None

        meilleur_points = max(self._statistiques, key=lambda s: s.points)
        meilleur_passes = max(self._statistiques, key=lambda s: s.passes)
        meilleur_rebonds = max(self._statistiques, key=lambda s: s.rebonds)

        return {
            'meilleur_score': meilleur_points.points,
            'meilleur_passes': meilleur_passes.passes,
            'meilleur_rebonds': meilleur_rebonds.rebonds
        }

    def afficher_informations(self):
        """Implémentation de la méthode abstraite"""
        return f"Joueur: {self._nom} - {self._poste.value} ({self._origine})"

    def __str__(self):
        return f"{self._nom} ({self._poste.value}) - {self._origine}"
