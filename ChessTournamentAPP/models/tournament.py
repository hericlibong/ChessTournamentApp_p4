# models/tournament.py

from datetime import datetime
import uuid
from models.round import Round
from .match import Match
from .player import Player
import random


class Tournament:
    """Creation de tournois"""
    def __init__(self, name: str, location: str, description: str, start_date: str, end_date: str, 
                 total_round: int = 4, t_id:str = None, current_round: int = 0, rounds=None, registered_players=None):
        """ Initialise l'id, le nom (name), le lieu (location), la date de début (start_date), la date de fin (end_date), 
        la description, le tour actuel (current_round), le nombre total de tour (total round). Ainsi que la liste des joueurs enregistrés,
        et la liste des tours effectués 
        """
        
        self.t_id = t_id if t_id is not None else str(uuid.uuid4())[:8]
        # Génère un nouvel identifiant unique pour chaque tournoi si aucun n'est fourni et prend les 8 premiers caractères et un nouvel ID seulement 
        self.name = name 
        self.name = name
        self.location = location
        # Conversion directe des chaînes de dates en objets datetime, sans validation avancé
        
        self.description = description
        self.current_round =  current_round  # Commence à zéro, indiquant qu'aucun round n'a encore été joué
        self.rounds = rounds if rounds is not None else []  # Liste de tours effectués pendant un tournoi
        self.registered_players = registered_players if registered_players is not None else []  # Initialise avec la valeur fournie ou une liste videe
        self.total_round = total_round  # 4 par défaut mais peut être ajusté
        self.current_matches = set()
        # Vérifie si start_date est une instance de datetime, sinon convertit de str
        if isinstance(start_date, datetime):
            self.start_date = start_date
        else:
            self.start_date = datetime.strptime(start_date, "%d/%m/%Y")
        
        # Vérifie si end_date est une instance de datetime, sinon convertit de str
        if isinstance(end_date, datetime):
            self.end_date = end_date
        else:
            self.end_date = datetime.strptime(end_date, "%d/%m/%Y")




    ## Sérialisation des données ##

    def to_dict(self):
        """Sérialise l'objet Tournament pour la sauvegarde en JSON."""
        return {
            "t_id": str(self.t_id),  # uuid est converti en string
            "name": self.name,
            "location": self.location,
            "start_date": self.start_date.strftime("%d/%m/%Y"),
            "end_date": self.end_date.strftime("%d/%m/%Y"),
            "description": self.description,
            "current_round": self.current_round,
            "rounds": [round.to_dict() for round in self.rounds],  # Supposant que Round a une méthode to_dict
            "registered_players": [player.to_dict() for player in self.registered_players],  # Supposant que Player a une méthode to_dict
            "total_round": self.total_round
        }
    
    
    def is_active(self):
        """Vérifie si le tournoi est actif"""
        return self.current_round < self.total_round and self.end_date > datetime.now()

    
    def initialize_rounds(self):
        """
        Initialise les rounds basés sur le nombre de joueurs inscrits.
        Si le nombre de joueurs est pair, crée un nombre de rounds égal à ce nombre moins un.
        Si le nombre de joueurs est impair, crée autant de rounds que de joueurs.
        Cela garantit qu'un tournoi avec un nombre impair de joueurs permettra à chaque joueur de passer un round sans jouer.
        """
        # Calcul du nombre de rounds en fonction du nombre de joueurs:
        # Si le nombre de joueurs est pair, le nombre de rounds est le nombre de joueurs moins un.
        # Si impair, le nombre de rounds est égal au nombre total de joueurs.
        number_of_rounds = len(self.registered_players) - 1 if len(self.registered_players) % 2 == 0 else len(self.registered_players)

        # Création des objets Round en utilisant une compréhension de liste:
        # Pour chaque round calculé, on crée un objet Round avec un nom indiquant son numéro.
        self.rounds = [Round(name=f"Round {i + 1}") for i in range(number_of_rounds)]

        # Mise à jour de l'attribut total_round avec le nombre de rounds créés.
        # Cela reflète le nombre total de rounds qui seront joués dans le tournoi.
        self.total_round = number_of_rounds



    def start_tournament(self):
        if len(self.registered_players) < 2:
            print("Not enough players to start the tournament.")
            return

       
        self.initialize_rounds()
        self.generate_matches()  # Générer les matches après avoir créé les rounds

        if self.rounds:
            self.rounds[0].start_time = datetime.now()  # Démarrer le premier round
            print(f"Tournament '{self.name}' started with {len(self.registered_players)} players and {len(self.rounds)} rounds.")
        else:
            print("Failed to initialize rounds properly.")


    def shuffle_and_create_rounds(self):
        """Mélange les joueurs et prépare les rounds basés sur le nombre de joueurs."""
        random.shuffle(self.registered_players)
        print("Joueurs mélangés pour le premier round.")
        # Générer les rounds et matches selon les règles définies
        self.generate_matches()


   

    # def generate_matches(self):
    #     # On assume que self.registered_players est toujours non vide
    #     for round in self.rounds:
    #         random.shuffle(self.registered_players)  # Mélanger les joueurs à chaque round
    #         it = iter(self.registered_players)
    #         round.matches = []  # Réinitialiser les matches pour le round

    #         while True:
    #             try:
    #                 player1 = next(it)
    #                 player2 = next(it)
    #                 match = Match(players=(player1, player2))
    #                 round.matches.append(match)
    #             except StopIteration:
    #                 break  # Si le nombre de joueurs est impair, le dernier joueur reste sans match ce round


    def generate_matches(self):
        for round in self.rounds:
            players = self.registered_players[:]
            random.shuffle(players)  # Mélanger les joueurs pour chaque round
            matches = []
            it = iter(players)

            while len(players) > 1:
                player1 = players.pop(0)
                # Recherche du premier joueur disponible qui n'a pas encore joué contre player1
                player2 = next((p for p in players if p.unique_id not in player1.past_opponents), None)
                
                if player2:
                    matches.append(Match(players=(player1, player2)))
                    player1.past_opponents.add(player2.unique_id)  # Utilisation de add() pour un set
                    player2.past_opponents.add(player1.unique_id)  # Utilisation de add() pour un set
                    players.remove(player2)
                else:
                    # Si aucun joueur n'est trouvé (cas improbable sauf configuration très spécifique), replacer player1
                    players.append(player1)

            # Si un joueur reste sans adversaire, il 'saute' ce round (pause)
            if len(players) == 1:
                print(f"{players[0].name} skips this round.")

            round.matches.extend(matches)  # Ajouter les matches générés au round actuel




    

    def add_player(self, player):
        """Ajoute un joueur au tournoi."""
        if player not in self.registered_players:
            self.registered_players.append(player)
            print(f"Player {player.firstname} {player.lastname} added to the tournament.")
        else:
            print("Player already registered in the tournament.")




    def update_scores(self, round_index, match_index, score1, score2):
        """Met à jour les scores pour un match spécifique dans un round donné."""
        match = self.rounds[round_index].matches[match_index]
        match.set_results((score1, score2))
        

    
    
    ### Gestion des joueurs ###

    def register_player(self, player):
        """ Ajoute un joueur au tournoi si le tournoi est actif"""
        if not self.is_active():
            print(f"Le tournoi '{self.name}' n'est pas actif ou est déjà terminé. ")
            return
        if player not in self.registered_players:
            self.registered_players.append(player)
            print(f"{player.firstname} {player.name} a été ajouté(e) au tournoi '{self.name}'.")
        else:
            print(f"{player.firstname} {player.name} est déjà inscrit(e) à ce tournoi.")
    
    
    
    ## Gestion des Rounds ##

    def add_round(self, round_name, start_time=None):
        """ Ajoute un nouveau round au tournoi si le tournoi est actif"""
        if not self.is_active():
            print("Le round ne peut pas être ajouté. Le Tournoi n'est pas actif.")
            return
        new_round = Round(name=round_name, start_time=start_time)
        self.rounds.append(new_round)
        #start_status = f"starting at {start_time}" if start_time else "not started"
        print(f"Le Round '{round_name}' a été ajouté au tournament '{self.name}'.")



    def start_round(self, round_name):
        """Démarre un round spécifié par son nom en définissant le start_time à maintenant si ce n'est pas déjà fait."""
        if not self.is_active():
            print(f"Impossible de démarrer un round. Le tournoi '{self.name}' n'est pas actif")
            return

        previous_round_completed = True  # On suppose que le premier round peut toujours démarrer
        for index, round in enumerate(self.rounds):
            if round.name == round_name:
                # Vérifie si le round précédent est terminé avant de démarrer celui-ci
                if index > 0:  # Il y a un round avant celui-ci
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



    def end_round(self, round_name):
        """Recherche le round spécifié et déclenche la fin de ce round."""
        for round in self.rounds:
            if round.name == round_name:
                round.end_round()
                return
        else:
            print(f"No round named '{round_name}' found.")

    # def end_round(self, round_name):
    #     """Termine un round spécifié par son nom en définissant le end_time à maintenant et en marquant le round comme complet."""
    #     for round in self.rounds:
    #         if round.name == round_name:
    #             if  round.is_complete:
    #                 round.end_time = datetime.now()  # Enregistrer l'heure de fin dès la fin du round
    #                 round.is_complete = True
    #                 print(f"Round '{round_name}' has ended. End Time: {round.end_time}")
    #                 return
    #             else:
    #                 print(f"Round '{round_name}' has already been completed at {round.end_time}.")
    #                 return
    #     else:
    #         print(f"No round named '{round_name}' found.")
    # def end_round(self, round_name):
    #     for round in self.rounds:
    #         if round.name == round_name:
    #             if round.is_complete:
    #                 print(f"Round '{round_name}' has already been completed.")
    #                 return

    #             for match in round.matches:
    #                 # Assurez-vous que tous les matchs ont été complétés avant de terminer le round
    #                 if not match.is_complete:
    #                     print(f"Match between {match.players[0].firstname} {match.players[0].name} and {match.players[1].firstname} {match.players[1].name} is not complete.")
    #                     return

    #             round.end_time = datetime.now()  # Définir l'heure de fin du round
    #             round.is_complete = True
    #             print(f"Round '{round.name}' has been completed.")
    #     else:
    #         print(f"No round named '{round_name}' found.")

    


    # def end_round(self, round_name):
    #     for round in self.rounds:
    #         if round.name == round_name:
    #             if round.is_complete:
    #                 round.end_time = datetime.now()
    #                 print(f"Round '{round_name}' has already been completed.")
    #                 return

    #             #round.end_time = datetime.now()
    #             round.is_complete = True
    #             for match in round.matches:
    #                 print(f"Match between {match.players[0].firstname} {match.players[0].name} and {match.players[1].firstname} {match.players[1].name}")
    #                 result = input("Enter the result (1-0, 0-1, 0.5-0.5): ")
    #                 match.set_results(result)
                
    #             print(f"Round '{round.name}' has been completed.")
    #             return
    #     else:
    #         print(f"No round named '{round_name}' found.")









