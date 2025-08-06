from joueur import Joueur

class Equipe:
    """Classe représentant une équipe NBA"""

    MAX_JOUEURS = 15

    def __init__(self, nom, ville):
        if not nom or not isinstance(nom, str):
            raise ValueError("Le nom de l'équipe doit être une chaîne non vide")
        if not ville or not isinstance(ville, str):
            raise ValueError("La ville doit être une chaîne non vide")

        self._nom = nom
        self._ville = ville
        self._joueurs = []
        self._victoires = 0
        self._defaites = 0

    @property
    def nom(self):
        return self._nom

    @property
    def ville(self):
        return self._ville

    @property
    def joueurs(self):
        return self._joueurs.copy()

    @property
    def victoires(self):
        return self._victoires

    @property
    def defaites(self):
        return self._defaites

    def ajouter_joueur(self, joueur):
        """Ajouter un joueur à l'équipe avec validation"""
        if not isinstance(joueur, Joueur):
            raise TypeError("Seuls les objets Joueur peuvent être ajoutés")

        if len(self._joueurs) >= self.MAX_JOUEURS:
            raise ValueError(f"L'équipe ne peut pas avoir plus de {self.MAX_JOUEURS} joueurs")

        if joueur in self._joueurs:
            return False

        if joueur.equipe is not None:
            raise ValueError(f"Le joueur {joueur.nom} appartient déjà à une équipe")

        self._joueurs.append(joueur)
        joueur.equipe = self
        return True

    def retirer_joueur(self, joueur):
        """Retirer un joueur de l'équipe"""
        if joueur in self._joueurs:
            self._joueurs.remove(joueur)
            joueur.equipe = None
            return True
        return False

    def rechercher_joueur(self, nom):
        """Rechercher un joueur par nom dans l'équipe"""
        for joueur in self._joueurs:
            if joueur.nom.lower() == nom.lower():
                return joueur
        return None

    def ajouter_victoire(self):
        """Ajouter une victoire à l'équipe"""
        self._victoires += 1

    def ajouter_defaite(self):
        """Ajouter une défaite à l'équipe"""
        self._defaites += 1

    def calculer_pourcentage_victoires(self):
        """Calculer le pourcentage de victoires"""
        total_matchs = self._victoires + self._defaites
        if total_matchs == 0:
            return 0.0
        return (self._victoires / total_matchs) * 100

    def obtenir_statistiques_equipe(self):
        """Calculer les statistiques moyennes de l'équipe"""
        if not self._joueurs:
            return None

        joueurs_avec_stats = [j for j in self._joueurs if j.calculer_moyennes()]
        if not joueurs_avec_stats:
            return None

        moyennes_equipe = {
            'points_moyens': 0,
            'passes_moyennes': 0,
            'rebonds_moyens': 0,
            'joueurs_actifs': len(joueurs_avec_stats)
        }

        for joueur in joueurs_avec_stats:
            moyennes = joueur.calculer_moyennes()
            moyennes_equipe['points_moyens'] += moyennes['points']
            moyennes_equipe['passes_moyennes'] += moyennes['passes']
            moyennes_equipe['rebonds_moyens'] += moyennes['rebonds']

        nb_joueurs = len(joueurs_avec_stats)
        moyennes_equipe['points_moyens'] /= nb_joueurs
        moyennes_equipe['passes_moyennes'] /= nb_joueurs
        moyennes_equipe['rebonds_moyens'] /= nb_joueurs

        return moyennes_equipe

    def __str__(self):
        return f"{self._nom} ({self._ville})"

    def __eq__(self, other):
        if not isinstance(other, Equipe):
            return False
        return self._nom == other._nom and self._ville == other._ville
