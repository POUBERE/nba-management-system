from abc import ABC, abstractmethod

class Personne(ABC):
    """Classe abstraite de base représentant une personne"""

    def __init__(self, nom, origine):
        if not nom or not isinstance(nom, str):
            raise ValueError("Le nom doit être une chaîne non vide")
        if not origine or not isinstance(origine, str):
            raise ValueError("L'origine doit être une chaîne non vide")

        self._nom = nom
        self._origine = origine

    @property
    def nom(self):
        return self._nom

    @property
    def origine(self):
        return self._origine

    def afficher_info_base(self):
        return f"Nom: {self._nom}, Origine: {self._origine}"

    @abstractmethod
    def afficher_informations(self):
        """Méthode abstraite à implémenter dans les classes filles"""
        pass

    def __eq__(self, other):
        if not isinstance(other, Personne):
            return False
        return self._nom == other._nom and self._origine == other._origine

    def __hash__(self):
        return hash((self._nom, self._origine))