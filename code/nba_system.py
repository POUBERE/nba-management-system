from equipe import Equipe
from joueur import Joueur
from match import Match


class ValidationError(Exception):
    """Exception pour les erreurs de validation"""
    pass


class NBASystem:
    """Classe principale gérant le système NBA"""

    def __init__(self):
        self._equipes = {}
        self._matchs = []
        self._joueurs_index = {}

    def ajouter_equipe(self, nom, ville):
        """Ajouter une nouvelle équipe"""
        if nom in self._equipes:
            raise ValidationError(f"L'équipe {nom} existe déjà!")

        nouvelle_equipe = Equipe(nom, ville)
        self._equipes[nom] = nouvelle_equipe
        return nouvelle_equipe

    def rechercher_equipe(self, nom):
        """Rechercher une équipe par son nom"""
        return self._equipes.get(nom)

    def ajouter_joueur_a_equipe(self, nom_equipe, nom_joueur, origine, annee_debut, poste):
        """Ajouter un joueur à une équipe"""
        equipe = self.rechercher_equipe(nom_equipe)
        if not equipe:
            raise ValidationError(f"Équipe {nom_equipe} non trouvée!")

        if nom_joueur in self._joueurs_index:
            raise ValidationError(f"Le joueur {nom_joueur} existe déjà dans le système!")

        nouveau_joueur = Joueur(nom_joueur, origine, annee_debut, poste)
        if equipe.ajouter_joueur(nouveau_joueur):
            self._joueurs_index[nom_joueur] = nouveau_joueur
            return nouveau_joueur
        else:
            raise ValidationError(f"Impossible d'ajouter {nom_joueur} à l'équipe!")

    def transferer_joueur(self, nom_joueur, nom_nouvelle_equipe):
        """Transférer un joueur vers une nouvelle équipe"""
        joueur = self.rechercher_joueur(nom_joueur)
        nouvelle_equipe = self.rechercher_equipe(nom_nouvelle_equipe)

        if not joueur:
            raise ValidationError(f"Joueur {nom_joueur} non trouvé!")

        if not nouvelle_equipe:
            raise ValidationError(f"Équipe {nom_nouvelle_equipe} non trouvée!")

        if joueur.equipe == nouvelle_equipe:
            raise ValidationError(f"{nom_joueur} est déjà dans {nom_nouvelle_equipe}!")

        if joueur.equipe:
            joueur.equipe.retirer_joueur(joueur)

        nouvelle_equipe.ajouter_joueur(joueur)
        return True

    def rechercher_joueur(self, nom):
        """Rechercher un joueur par son nom"""
        return self._joueurs_index.get(nom)

    def ajouter_match(self, nom_equipe_domicile, nom_equipe_exterieur, score_domicile, score_exterieur, date):
        """Ajouter un nouveau match"""
        equipe_domicile = self.rechercher_equipe(nom_equipe_domicile)
        equipe_exterieur = self.rechercher_equipe(nom_equipe_exterieur)

        if not equipe_domicile:
            raise ValidationError(f"Équipe {nom_equipe_domicile} non trouvée!")

        if not equipe_exterieur:
            raise ValidationError(f"Équipe {nom_equipe_exterieur} non trouvée!")

        nouveau_match = Match(equipe_domicile, equipe_exterieur, score_domicile, score_exterieur, date)
        self._matchs.append(nouveau_match)
        return nouveau_match

    def obtenir_matchs_equipe(self, nom_equipe):
        """Obtenir tous les matchs d'une équipe"""
        equipe = self.rechercher_equipe(nom_equipe)
        if not equipe:
            return []

        matchs_equipe = []
        for match in self._matchs:
            if match.equipe_domicile == equipe or match.equipe_exterieur == equipe:
                matchs_equipe.append(match)
        return matchs_equipe

    def obtenir_top_joueurs(self, critere='points', limite=5):
        """Obtenir le top des joueurs selon un critère"""
        joueurs_avec_stats = []

        for joueur in self._joueurs_index.values():
            moyennes = joueur.calculer_moyennes()
            if moyennes:
                joueurs_avec_stats.append((joueur, moyennes))

        if not joueurs_avec_stats:
            return []

        if critere not in ['points', 'passes', 'rebonds', 'efficacite_moyenne']:
            critere = 'points'

        joueurs_tries = sorted(joueurs_avec_stats, key=lambda x: x[1][critere], reverse=True)
        return joueurs_tries[:limite]

    def obtenir_statistiques_generales(self):
        """Obtenir des statistiques générales du système"""
        total_equipes = len(self._equipes)
        total_joueurs = len(self._joueurs_index)
        total_matchs = len(self._matchs)

        joueurs_actifs = sum(1 for j in self._joueurs_index.values() if j.calculer_moyennes())
        equipes_actives = sum(1 for e in self._equipes.values() if (e.victoires + e.defaites) > 0)

        return {
            'equipes_total': total_equipes,
            'equipes_actives': equipes_actives,
            'joueurs_total': total_joueurs,
            'joueurs_actifs': joueurs_actifs,
            'matchs_total': total_matchs
        }

    def obtenir_classement(self):
        """Obtenir le classement des équipes"""
        equipes_avec_matchs = [e for e in self._equipes.values() if (e.victoires + e.defaites) > 0]

        if not equipes_avec_matchs:
            return []

        return sorted(equipes_avec_matchs,
                      key=lambda e: (e.calculer_pourcentage_victoires(), e.victoires),
                      reverse=True)

    def valider_coherence_systeme(self):
        """Valider la cohérence du système et retourner les incohérences trouvées"""
        incoherences = []

        # Vérifier les joueurs sans équipe
        for nom, joueur in self._joueurs_index.items():
            if joueur.equipe is None:
                incoherences.append(f"Joueur {nom} n'appartient à aucune équipe")

            # Vérifier si le joueur est bien dans l'équipe associée
            elif joueur not in joueur.equipe.joueurs:
                incoherences.append(
                    f"Incohérence: {nom} associé à {joueur.equipe.nom} mais pas dans la liste des joueurs")

        # Vérifier les équipes avec trop de joueurs
        for nom_equipe, equipe in self._equipes.items():
            if len(equipe.joueurs) > equipe.MAX_JOUEURS:
                incoherences.append(f"Équipe {nom_equipe} a {len(equipe.joueurs)} joueurs (max: {equipe.MAX_JOUEURS})")

        # Vérifier les matchs avec des équipes inexistantes
        for i, match in enumerate(self._matchs):
            if match.equipe_domicile.nom not in self._equipes:
                incoherences.append(f"Match {i + 1}: équipe domicile {match.equipe_domicile.nom} n'existe pas")
            if match.equipe_exterieur.nom not in self._equipes:
                incoherences.append(f"Match {i + 1}: équipe extérieur {match.equipe_exterieur.nom} n'existe pas")

        return incoherences
