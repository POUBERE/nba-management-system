from datetime import datetime

class Match:
    """Classe représentant un match NBA"""

    def __init__(self, equipe_domicile, equipe_exterieur, score_domicile, score_exterieur, date):
        self._valider_parametres(equipe_domicile, equipe_exterieur, score_domicile, score_exterieur)

        self._equipe_domicile = equipe_domicile
        self._equipe_exterieur = equipe_exterieur
        self._score_domicile = score_domicile
        self._score_exterieur = score_exterieur
        self._date = self._parser_date(date)
        self._finalise = False

        self._mettre_a_jour_bilans()
        self._finalise = True

    def _valider_parametres(self, equipe_domicile, equipe_exterieur, score_domicile, score_exterieur):
        """Valide les paramètres du match"""
        if not hasattr(equipe_domicile, 'nom') or not hasattr(equipe_exterieur, 'nom'):
            raise ValueError("Les équipes doivent avoir un attribut 'nom'")

        if equipe_domicile == equipe_exterieur:
            raise ValueError("Une équipe ne peut pas jouer contre elle-même")

        if score_domicile < 0 or score_exterieur < 0:
            raise ValueError("Les scores ne peuvent pas être négatifs")

        if not isinstance(score_domicile, int) or not isinstance(score_exterieur, int):
            raise ValueError("Les scores doivent être des entiers")

    def _parser_date(self, date):
        """Parse la date en objet datetime"""
        if isinstance(date, str):
            try:
                return datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Format de date invalide. Utilisez YYYY-MM-DD")
        elif isinstance(date, datetime):
            return date
        else:
            raise ValueError("La date doit être une chaîne ou un objet datetime")

    @property
    def equipe_domicile(self):
        return self._equipe_domicile

    @property
    def equipe_exterieur(self):
        return self._equipe_exterieur

    @property
    def score_domicile(self):
        return self._score_domicile

    @property
    def score_exterieur(self):
        return self._score_exterieur

    @property
    def date(self):
        return self._date

    @property
    def finalise(self):
        return self._finalise

    def _mettre_a_jour_bilans(self):
        """Mettre à jour les bilans des équipes suite au match"""
        if self._score_domicile > self._score_exterieur:
            self._equipe_domicile.ajouter_victoire()
            self._equipe_exterieur.ajouter_defaite()
        elif self._score_exterieur > self._score_domicile:
            self._equipe_exterieur.ajouter_victoire()
            self._equipe_domicile.ajouter_defaite()

    def get_equipe_gagnante(self):
        """Retourner l'équipe gagnante"""
        if self._score_domicile > self._score_exterieur:
            return self._equipe_domicile
        elif self._score_exterieur > self._score_domicile:
            return self._equipe_exterieur
        else:
            return None

    def get_equipe_perdante(self):
        """Retourner l'équipe perdante"""
        if self._score_domicile > self._score_exterieur:
            return self._equipe_exterieur
        elif self._score_exterieur > self._score_domicile:
            return self._equipe_domicile
        else:
            return None

    def get_ecart_points(self):
        """Retourne l'écart de points du match"""
        return abs(self._score_domicile - self._score_exterieur)

    def est_match_serre(self, seuil=5):
        """Détermine si le match était serré (écart <= seuil)"""
        return self.get_ecart_points() <= seuil

    def __str__(self):
        return f"{self._equipe_domicile.nom} {self._score_domicile} - {self._score_exterieur} {self._equipe_exterieur.nom} ({self._date.strftime('%Y-%m-%d')})"
