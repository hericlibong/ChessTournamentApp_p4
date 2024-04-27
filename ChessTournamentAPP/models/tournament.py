

from datetime import datetime
import uuid
from models.round import Round
from models.match import Match
from models.player import Player
import random



class Tournament:
    """ Gestion de tournois d'échecs. """
    def __init__(self, name: str, location: str, description: str, start_date: str, end_date: str,
                 total_round: int = 4, t_id: str = None, current_round: int = 0, rounds=None, registered_players=None):
        self.t_id = t_id if t_id else str(uuid.uuid4())[:8]
        self.name = name
        self.location = location
        self.description = description
        self.current_round = current_round
        self.rounds = rounds if rounds else []
        self.registered_players = registered_players if registered_players else []
        self.total_round = total_round
        self.start_date = self.safe_strptime(start_date, "%d/%m/%Y"  )
        self.end_date = self.safe_strptime(end_date, "%d/%m/%Y")

    def to_dict(self):
        return {
            "t_id": self.t_id,
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date.strftime("%d/%m/%Y") if self.start_date else "Invalid date",
            "end_date": self.end_date.strftime("%d/%m/%Y") if self.end_date else "Invalid date",
            "description": self.description,
            "current_round": self.current_round,
            "rounds": [round.to_dict() for round in self.rounds],
            "registered_players": [player.to_dict() for player in self.registered_players],
            "total_round": self.total_round
        }
    

    # def safe_strptime(self, date_str, date_format="%d/%m/%Y"):
    #     """Safely converts date string to datetime object."""
    #     if isinstance(date_str, str):
    #         try:
    #             return datetime.strptime(date_str, date_format)
    #         except ValueError as e:
    #             print(f"Erreur de format de date : {e}")
    #     else:
    #         print(f"Erreur de type: attendu str, reçu {type(date_str).__name__}")
    #     return None
    
    def safe_strptime(self, date_str, date_format="%Y-%m-%d"):
        """ Essaie de convertir une chaîne en datetime, renvoie None si échec. """
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            print(f"Erreur de format de date: {date_str}, attendu {date_format}")
            return None

    
    # def is_active(self):
    #     return self.current_round < self.total_round and self.end_date > datetime.now()

    def initialize_rounds(self):
        number_of_rounds = len(self.registered_players) - 1 if len(self.registered_players) % 2 == 0 else len(self.registered_players)
        self.rounds = [Round(name=f"Round {i + 1}") for i in range(number_of_rounds)]
        self.total_round = number_of_rounds

    def start_tournament(self):
        if len(self.registered_players) < 2:
            print("Not enough players to start the tournament.")
            return
        self.initialize_rounds()
        self.generate_matches()
        if self.rounds:
            self.rounds[0].start_time = datetime.now()
            print(f"Tournament '{self.name}' started with {len(self.registered_players)} players and {len(self.rounds)} rounds.")
        else:
            print("Failed to initialize rounds properly.")

    def generate_matches(self):
        for round in self.rounds:
            players = self.registered_players[:]
            random.shuffle(players)
            matches = []
            it = iter(players)
            while len(players) > 1:
                player1 = players.pop(0)
                player2 = next((p for p in players if p.unique_id not in player1.past_opponents), None)
                if player2:
                    matches.append(Match(players=(player1, player2)))
                    player1.past_opponents.add(player2.unique_id)
                    player2.past_opponents.add(player1.unique_id)
                    players.remove(player2)
                else:
                    players.append(player1)
            round.matches.extend(matches)

    

    def update_scores(self, round_index, match_index, score1, score2):
        match = self.rounds[round_index].matches[match_index]
        match.set_results((score1, score2))

    # def register_player(self, player, check_active=True):
    #     """ Ajoute un joueur au tournoi. Vérifie si le tournoi est actif si spécifié. """
    #     if check_active and not self.is_active():
    #         print(f"Le tournoi '{self.name}' n'est pas actif ou est déjà terminé.")
    #         return
    #     if player not in self.registered_players:
    #         player.past_opponents.clear()  # Réinitialiser les adversaires passés du joueur
    #         self.registered_players.append(player)
    #         print(f"{player.firstname} {player.name} a été ajouté(e) au tournoi '{self.name}'.")
    #     else:
    #         print(f"{player.firstname} {player.name} est déjà inscrit(e) à ce tournoi.")

    # Les autres méthodes restent inchangées

    def register_player(self, player):
        """ Enregistre un joueur dans le tournoi si le tournoi est actif. """
        if not self.is_active():
            print(f"Le tournoi '{self.name}' n'est pas actif ou est déjà terminé.")
            return
        if player not in self.registered_players:
            player.past_opponents.clear()
            self.registered_players.append(player)
            print(f"{player.firstname} {player.name} a été ajouté(e) au tournoi '{self.name}'.")
        else:
            print(f"{player.firstname} {player.name} est déjà inscrit(e) à ce tournoi.")

    def is_active(self):
        """ Vérifie si le tournoi est toujours en cours. """
        return self.current_round < self.total_round and self.end_date > datetime.now()

    def add_round(self, round_name, start_time=None):
        if not self.is_active():
            print("Le round ne peut pas être ajouté. Le Tournoi n'est pas actif.")
            return
        new_round = Round(name=round_name, start_time=start_time)
        self.rounds.append(new_round)
        print(f"Le Round '{round_name}' a été ajouté au tournament '{self.name}'.")

    def start_round(self, round_name):
        if not self.is_active():
            print(f"Impossible de démarrer un round. Le tournoi '{self.name}' n'est pas actif")
            return
        previous_round_completed = True
        for index, round in enumerate(self.rounds):
            if round.name == round_name:
                if index > 0:
                    previous_round_completed = self.rounds[index - 1].is_complete
                if not previous_round_completed:
                    print(f"Cannot start {round_name}. Previous round not completed.")
                    return
                if round.start_time is None:
                    round.start_time = datetime.now()
                    print(f"Round '{round_name}' has started.")
                    return
                else:
                    print(f"Round '{round_name}' has already started.")
                    return
        else:
            print(f"No round named '{round_name}' found.")

    # def end_round(self, round_name):
    #     for round in self.rounds:
    #         if round.name == round_name:
    #             round.end_round()
    #             return
    #     else:
    #         print(f"No round named '{round_name}' found.")

    # def end_round(self, round_name):
    #     """Recherche le round spécifié et déclenche la fin de ce round, enregistre l'heure de fin."""
    #     found = False
    #     for round in self.rounds:
    #         if round.name == round_name:
    #             if round.is_complete:
    #                 print(f"Round '{round_name}' has already been completed at {round.end_time}.")
    #             else:
    #                 round.end_time = datetime.now()  # Enregistrement de l'heure de fin
    #                 round.is_complete = True
    #                 print(f"Round '{round_name}' has ended. End Time: {round.end_time}")
    #             found = True
    #             break
    #     if not found:
    #         print(f"No round named '{round_name}' found.")

    
    # def end_round(self, round_name):
    #     """Termine un round spécifié par son nom."""
    #     for round in self.rounds:
    #         if round.name == round_name and not round.is_complete:
    #             round.end_round()  # Appel à la méthode de Round
    #             print(f"Round '{round_name}' est terminé.")
    #             break
    #     else:
    #         print(f"No round named '{round_name}' found or it is already completed.")









