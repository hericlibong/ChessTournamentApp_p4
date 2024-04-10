# application_controller.py

from datetime import datetime
from views.menu_view import MenuView
from views.tournament_views import TournamentView
from views.player_views import PlayerView
from models.tournament import Tournament
from models.player import Player
from util.data_manager import load_tournaments, save_tournaments, load_players, save_players




class ApplicationController:
    def __init__(self):
        self.tournaments = load_tournaments()
        self.players = load_players()  # Charge les joueurs existants

    def run(self):
        while True:
            choice = MenuView.display_main_menu()
            if choice == '1':
                self.manage_tournaments()
            elif choice == '2':
                self.manage_players()
            elif choice == '3':
                print("Exiting Application")
                self.save_data()  # Sauvegarde les données avant de quitter
                break
            else:
                print("Invalid choice, please try again.")

    def manage_tournaments(self):
        while True:
            choice = MenuView.display_tournament_menu()
            if choice == '1':
                self.create_tournament()
            elif choice == '2':
                self.display_tournaments()
            elif choice == '3':
                pass  # Charger un tournoi existant (fonctionnalité à développer)
            elif choice == '4':
                self.update_tournament()
            elif choice == '5':  # Retour au menu principal
                break
            else:
                print("Invalid choice, please try again.")

    def manage_players(self):
        while True:
            choice = MenuView.display_player_menu()
            if choice == '1':
                self.add_player()
            elif choice == '2':
                self.display_players()
            elif choice == '3':
                pass  # Modifier un joueur (fonctionnalité à développer)
            elif choice == '4':  # Retour au menu principal
                break
            else:
                print("Invalid choice, please try again.")

    def save_data(self):
        save_tournaments(self.tournaments)
        save_players(self.players)  # Sauvegarde les joueurs

    # Ici, ajoute les méthodes create_tournament, display_tournaments, add_player, display_players, etc.

    def create_tournament(self):
        tournament_details = TournamentView.create_tournament()
        new_tournament = Tournament(*tournament_details)
        self.tournaments.append(new_tournament)
        self.save_data()
        print(f"Tournament '{new_tournament.name}' has been successfully created.")

    def display_tournaments(self):
        TournamentView.display_tournaments(self.tournaments)

    def add_player(self):
        player_details = PlayerView.create_player()
        new_player = Player(*player_details)
        self.players.append(new_player)
        self.save_data()
        print(f"Player '{new_player.name}' has been successfully added.")

    def display_players(self):
        PlayerView.display_players(self.players)


    
    
    def update_tournament(self):
        TournamentView.display_tournaments(self.tournaments)
        t_id = input("Entrez l'ID du tournoi à modifier : ")
        tournament = next((t for t in self.tournaments if t.t_id == t_id), None)
        
        if tournament:
            print("Quel attribut voulez-vous modifier ?")
            print("1. Nom")
            print("2. Lieu")
            print("3. Date de début")
            print("4. Date de fin")
            print("5. Description")
            choice = input("Entrez votre choix : ")
            
            if choice == '1':
                new_value = input("Entrez le nouveau nom : ")
                tournament.name = new_value
            elif choice == '2':
                new_value = input("Entrez le nouveau lieu : ")
                tournament.location = new_value
            elif choice == '3':
                new_value = input("Entrez la nouvelle date de début (DD/MM/YYYY) : ")
                tournament.start_date = datetime.strptime(new_value, "%d/%m/%Y")
            elif choice == '4':
                new_value = input("Entrez la nouvelle date de fin (DD/MM/YYYY) : ")
                tournament.end_date = datetime.strptime(new_value, "%d/%m/%Y")
            elif choice == '5':
                new_value = input("Entrez la nouvelle description : ")
                tournament.description = new_value
            else:
                print("Choix non valide.")
                return
            
            self.save_data()
            print("Le tournoi a été mis à jour.")
        else:
            print("Tournoi non trouvé.")

 