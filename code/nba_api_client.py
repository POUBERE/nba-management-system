import requests
import tkinter as tk
from tkinter import ttk, messagebox
import json
from typing import Dict, List, Optional
from datetime import datetime
from nba_gui import NBAGui
from nba_system import NBASystem
from joueur import PosteJoueur
from nba_system import ValidationError


class NBAApiClient:
    """
    Classe pour interagir avec l'API NBA et récupérer des données réelles
    """

    def __init__(self, api_key: str = None, base_url: str = "https://free-nba.p.rapidapi.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'X-RapidAPI-Key': api_key or 'YOUR_API_KEY_HERE',
            'X-RapidAPI-Host': 'free-nba.p.rapidapi.com'
        }

    def get_teams(self) -> List[Dict]:
        """
        Récupérer la liste de toutes les équipes NBA
        """
        try:
            url = f"{self.base_url}/teams"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération des équipes: {e}")
            return []

    def get_players(self, team_id: int = None, page: int = 1, per_page: int = 25) -> List[Dict]:
        """
        Récupérer la liste des joueurs (optionnellement filtrés par équipe)
        """
        try:
            url = f"{self.base_url}/players"
            params = {
                'page': page,
                'per_page': per_page
            }

            if team_id:
                params['team_ids[]'] = team_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération des joueurs: {e}")
            return []

    def get_games(self, season: int = 2023, team_id: int = None, dates: List[str] = None) -> List[Dict]:
        """
        Récupérer les matchs d'une saison
        """
        try:
            url = f"{self.base_url}/games"
            params = {
                'seasons[]': season,
                'per_page': 100
            }

            if team_id:
                params['team_ids[]'] = team_id

            if dates:
                params['dates[]'] = dates

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération des matchs: {e}")
            return []

    def get_stats(self, season: int = 2023, player_id: int = None, game_id: int = None) -> List[Dict]:
        """
        Récupérer les statistiques des joueurs
        """
        try:
            url = f"{self.base_url}/stats"
            params = {
                'seasons[]': season,
                'per_page': 100
            }

            if player_id:
                params['player_ids[]'] = player_id

            if game_id:
                params['game_ids[]'] = game_id

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            return []

    def search_player(self, player_name: str) -> List[Dict]:
        """
        Rechercher un joueur par nom
        """
        try:
            url = f"{self.base_url}/players"
            params = {
                'search': player_name,
                'per_page': 25
            }

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la recherche de joueur: {e}")
            return []


class NBADataImporter:
    """
    Classe pour importer les données de l'API dans notre système NBA
    """

    def __init__(self, nba_system, api_client: NBAApiClient):
        self.nba_system = nba_system
        self.api_client = api_client

    def import_teams(self) -> int:
        """
        Importer toutes les équipes depuis l'API
        """
        teams_data = self.api_client.get_teams()
        imported_count = 0

        for team_data in teams_data:
            try:
                # Adapter les données API au format du système
                nom = team_data.get('full_name', team_data.get('name', ''))
                ville = team_data.get('city', '')

                if nom and ville:
                    self.nba_system.ajouter_equipe(nom, ville)
                    imported_count += 1
            except Exception as e:
                print(f"Erreur lors de l'import de l'équipe {team_data}: {e}")
                continue

        return imported_count

    def import_players_for_team(self, team_name: str, api_team_id: int) -> int:
        """
        Importer les joueurs d'une équipe spécifique
        """
        players_data = self.api_client.get_players(team_id=api_team_id)
        imported_count = 0

        for player_data in players_data:
            try:
                nom = f"{player_data.get('first_name', '')} {player_data.get('last_name', '')}".strip(
                )

                # Adapter les données
                origine = "USA"  # Par défaut, peut être amélioré
                annee = 2020  # Par défaut, peut être amélioré

                # Conversion du poste
                position_map = {
                    'G': 'Point Guard',
                    'F': 'Small Forward',
                    'C': 'Center',
                    'G-F': 'Shooting Guard',
                    'F-C': 'Power Forward'
                }

                poste = position_map.get(
                    player_data.get('position', ''), 'Point Guard')

                if nom and team_name:
                    self.nba_system.ajouter_joueur_a_equipe(
                        team_name, nom, origine, annee, poste
                    )
                    imported_count += 1
            except Exception as e:
                print(f"Erreur lors de l'import du joueur {player_data}: {e}")
                continue

        return imported_count

    def import_games_for_season(self, season: int = 2023) -> int:
        """
        Importer les matchs d'une saison
        """
        games_data = self.api_client.get_games(season=season)
        imported_count = 0

        for game_data in games_data:
            try:
                # Récupérer les équipes
                home_team = game_data.get('home_team', {}).get('full_name', '')
                visitor_team = game_data.get(
                    'visitor_team', {}).get('full_name', '')

                # Récupérer les scores
                home_score = game_data.get('home_team_score', 0)
                visitor_score = game_data.get('visitor_team_score', 0)

                # Récupérer la date
                date_str = game_data.get('date', '')
                if date_str:
                    date_obj = datetime.fromisoformat(
                        date_str.replace('Z', '+00:00'))
                    date_formatted = date_obj.strftime('%Y-%m-%d')
                else:
                    continue

                if home_team and visitor_team and home_score is not None and visitor_score is not None:
                    # Vérifier que les équipes existent dans le système
                    if (self.nba_system.rechercher_equipe(home_team) and
                            self.nba_system.rechercher_equipe(visitor_team)):

                        self.nba_system.ajouter_match(
                            home_team, visitor_team,
                            home_score, visitor_score,
                            date_formatted
                        )
                        imported_count += 1
            except Exception as e:
                print(f"Erreur lors de l'import du match {game_data}: {e}")
                continue

        return imported_count

    def import_player_stats(self, player_name: str, season: int = 2023) -> int:
        """
        Importer les statistiques d'un joueur spécifique
        """
        # Rechercher le joueur dans l'API
        players_data = self.api_client.search_player(player_name)

        if not players_data:
            return 0

        player_api_id = players_data[0].get('id')
        if not player_api_id:
            return 0

        # Récupérer les stats
        stats_data = self.api_client.get_stats(
            season=season, player_id=player_api_id)
        imported_count = 0

        # Récupérer le joueur dans votre système
        joueur = self.nba_system.rechercher_joueur(player_name)
        if not joueur:
            return 0

        for stat_data in stats_data:
            try:
                # Adapter les statistiques
                temps_jeu = stat_data.get('min', '0:00')
                # Convertir MM:SS en minutes décimales
                if ':' in temps_jeu:
                    minutes, seconds = temps_jeu.split(':')
                    temps_decimal = int(minutes) + int(seconds) / 60
                else:
                    temps_decimal = float(temps_jeu) if temps_jeu else 0

                points = stat_data.get('pts', 0) or 0
                passes = stat_data.get('ast', 0) or 0
                rebonds = stat_data.get('reb', 0) or 0

                joueur.ajouter_statistiques(
                    temps_decimal, points, passes, rebonds)
                imported_count += 1

            except Exception as e:
                print(f"Erreur lors de l'import des stats {stat_data}: {e}")
                continue

        return imported_count


# Extension de l'interface pour inclure l'import API
class NBAGuiWithAPI(NBAGui):
    """
    Extension de l'interface avec les fonctionnalités API
    """

    def __init__(self, root):
        super().__init__(root)

        # Initialiser le client API
        self.api_client = NBAApiClient(api_key="YOUR_API_KEY_HERE")
        self.data_importer = NBADataImporter(self.nba_system, self.api_client)

        # Ajouter les boutons API à la barre d'outils
        self.add_api_buttons()

    def add_api_buttons(self):
        """
        Ajouter des boutons pour l'import depuis l'API
        """
        # Trouver la barre d'outils existante et ajouter les boutons

        api_frame = tk.Frame(self.root, bg='#34495e')

        ttk.Button(api_frame, text="🌐 Importer Équipes API",
                   style='Success.TButton',
                   command=self.import_teams_from_api).pack(side=tk.LEFT, padx=3)

        ttk.Button(api_frame, text="👤 Importer Joueurs API",
                   style='Action.TButton',
                   command=self.import_players_from_api).pack(side=tk.LEFT, padx=3)

        ttk.Button(api_frame, text="⚡ Importer Matchs API",
                   style='Action.TButton',
                   command=self.import_games_from_api).pack(side=tk.LEFT, padx=3)

    def import_teams_from_api(self):
        """
        Importer les équipes depuis l'API
        """
        try:
            count = self.data_importer.import_teams()
            self.show_success_popup("Import API",
                                    f"{count} équipes importées depuis l'API!")
            self.actualiser_equipes()
            self.actualiser_comboboxes()
        except Exception as e:
            self.show_error_popup("Erreur API",
                                  f"Erreur lors de l'import: {e}")

    def import_players_from_api(self):
        """
        Importer les joueurs depuis l'API
        """
        # Interface pour sélectionner l'équipe
        try:
            teams_data = self.api_client.get_teams()
            if teams_data:
                # Prendre la première équipe comme exemple
                first_team = teams_data[0]
                team_name = first_team.get('full_name', '')
                team_id = first_team.get('id')

                count = self.data_importer.import_players_for_team(
                    team_name, team_id)
                self.show_success_popup("Import API",
                                        f"{count} joueurs importés pour {team_name}!")
                self.actualiser_joueurs()
        except Exception as e:
            self.show_error_popup("Erreur API",
                                  f"Erreur lors de l'import: {e}")

    def import_games_from_api(self):
        """
        Importer les matchs depuis l'API
        """
        try:
            count = self.data_importer.import_games_for_season(2023)
            self.show_success_popup("Import API",
                                    f"{count} matchs importés depuis l'API!")
            self.actualiser_matchs()
            self.actualiser_equipes()
        except Exception as e:
            self.show_error_popup("Erreur API",
                                  f"Erreur lors de l'import: {e}")
