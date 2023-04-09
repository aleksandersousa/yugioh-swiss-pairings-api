import random
import networkx as nx

from player import Player


class SwissPairingSystem():
    def __init__(self, starting_table=1, dbg=False) -> None:
        # For debbuging
        self.dbg = dbg

        # Will hold all player data
        self.players_dict = {}

        # Current round for the event
        self.current_round = 0
        # The next table we are going to assign paired players to
        self.open_table = 0
        # The starting table number
        self.starting_table = starting_table
        # Pairings for the current round
        self.round_pairings = {}

        # this defines the max number of players in a network point range before we split it up. Lower the number, faster the calculations
        self.max_group = 10

        # Contains lists of players sorted by how many points they currently have
        self.tiebreaker_lists = {}

        # Contains a list of points in the event from high to low
        self.tiebreaker_totals = []

        # Contains the list of tables that haven't reported for the current round
        self.tables_out = []

    def add_player(self, player):
        """
        Holds player data that are in the event.
        Each player entry is a dictonary named by ID#
        """

        self.players_dict[player.id] = player

    def drop_player(self, player_id):
        del self.players_dict[player_id]

    def pair_players(self, player1_id, player2_id):
        self.players_dict[player1_id].opponents.append(self.players_dict[player2_id])
        self.players_dict[player2_id].opponents.append(self.players_dict[player1_id])

        self.round_pairings[self.open_table] = [player1_id, player2_id]
        self.tables_out.append(self.open_table)

        self.open_table += 1

    def assign_bye(self, player1_id):
        self.players_dict[player1_id].results.append([2, 0, 0])

        self.players_dict[player1_id].opponents.append(Player(name="bye"))

        # Add points for "winning"
        self.players_dict[player1_id].win_match()

    def calculate_tiebreakers(self):
        for player_id in self.players_dict:
            self.players_dict[player_id].calculate_tiebreaker()

    def pair_round(self):
        """
        Process overview:
            1.) Create lists of players with each point value

            2.) Create a list of all current points and sort from highest to lowest

            3.) Loop through each list of points and assign players opponents based with same points

            4.) Check for left over players and assign a pair down
        """

        if not len(self.tables_out):
            self.current_round += 1

            # Clear old round pairings
            self.round_pairings = {}
            self.open_table = self.starting_table

            # Contains lists of players sorted by the tiebreaker value they currently have
            self.tiebreaker_lists = tiebreaker_lists = {}

            # Contains a list of points in the event from high to low
            self.tiebreaker_totals = tiebreaker_totals = []

            # Counts our groupings for each point amount
            self.count_tiebreakers = {}

            # bye player
            bye_player_id = ''

            # Add all players to pointLists
            for player_id in self.players_dict:
                current_player = self.players_dict[player_id]

                # If this tiebreaker amount isn't in the list, add it
                if "%s_1" % current_player.tiebreaker not in tiebreaker_lists:
                    tiebreaker_lists["%s_1" % current_player.tiebreaker] = []
                    self.count_tiebreakers[current_player.tiebreaker] = 1

                # Breakers the players into groups of their current points up to the max group allowed.
                # Smaller groups mean faster calculations
                if len(tiebreaker_lists["%s_%s" % (current_player.tiebreaker, self.count_tiebreakers[current_player.tiebreaker])]) > self.max_group:
                    self.count_tiebreakers[current_player.tiebreaker] += 1
                    tiebreaker_lists["%s_%s" %
                                     (current_player.tiebreaker, self.count_tiebreakers[current_player.tiebreaker])] = []

                # Add our player to the correct group
                tiebreaker_lists["%s_%s" %
                                 (current_player.tiebreaker, self.count_tiebreakers[current_player.tiebreaker])].append(player_id)

            # Add all points in use to tiebreaker_totals
            for tiebreakers in tiebreaker_lists:
                tiebreaker_totals.append(tiebreakers)

            # Sort our point groups based on points
            tiebreaker_totals.sort(reverse=True, key=lambda s: int(s.split('_')[0]))

            # Actually pair the players utilizing graph theory networkx
            for tiebreakers in tiebreaker_totals:
                # Create the graph object and add all players to it
                bracketGraph = nx.Graph()
                bracketGraph.add_nodes_from(tiebreaker_lists[tiebreakers])

                # Create edges between all players in the graph who haven't already played
                for player_id in bracketGraph.nodes():
                    for opponent_id in bracketGraph.nodes():
                        if opponent_id not in self.players_dict[player_id].opponents and player_id != opponent_id:
                            # Weight edges randomly between 1 and 9 to ensure pairings are not always the same with the same list of players
                            wgt = random.randint(1, 9)

                            # If a player has more points, weigh them the highest so they get paired first
                            if self.players_dict[player_id].tiebreaker > int(tiebreakers.split('_')[0]) or self.players_dict[opponent_id].tiebreaker > int(tiebreakers.split('_')[0]):
                                wgt = 10

                            # Create edge
                            bracketGraph.add_edge(player_id, opponent_id, weight=wgt)

                # Generate pairings from the created graph
                pairings = dict(nx.max_weight_matching(bracketGraph))

                # Actually pair the players based on the matching we found
                for t in pairings:
                    if t in tiebreaker_lists[tiebreakers]:
                        self.pair_players(t, pairings[t])
                        tiebreaker_lists[tiebreakers].remove(t)
                        tiebreaker_lists[tiebreakers].remove(pairings[t])

                # Check if we have an odd man out that we need to pair down
                if len(tiebreaker_lists[tiebreakers]) > 0:
                    # Check to make sure we aren't at the last player in the event
                    if tiebreaker_totals.index(tiebreakers) + 1 == len(tiebreaker_totals):
                        while len(tiebreaker_lists[tiebreakers]) > 0:
                            # If they are the last player give them a bye
                            bye_player_id = tiebreaker_lists[tiebreakers].pop(0)
                            self.assign_bye(bye_player_id)
                    else:
                        # Add our player to the next point group down
                        next_tiebreakers = tiebreaker_totals[tiebreaker_totals.index(tiebreakers) + 1]

                        while len(tiebreaker_lists[tiebreakers]) > 0:
                            tiebreaker_lists[next_tiebreakers].append(tiebreaker_lists[tiebreakers].pop(0))

            # Return the pairings for this round
            if bye_player_id:
                bye_pairings = self.round_pairings.copy()
                bye_pairings['bye'] = ['bye', self.players_dict[bye_player_id].id]
                return bye_pairings

            return self.round_pairings
        else:
            # If there are still tables out and we haven't had a forced pairing, return the tables still "playing"
            return self.tables_out

    def reportMatch(self, table, result):
        if table == 'bye':
            return

        # table is an integer of the table number, result is a list
        player1_id = self.round_pairings[table][0]
        player2_id = self.round_pairings[table][1]

        if result[0] == result[1]:
            # If values are the same they drew! Give'em each a point
            self.players_dict[player1_id].draw_match()
            self.players_dict[player1_id].results.append(result)
            self.players_dict[player2_id].draw_match()
            self.players_dict[player2_id].results.append(result)

            self.printdbg("empate mesa %s" % (table))
        else:
            # Figure out who won and assing points
            if result[0] > result[1]:
                self.players_dict[player1_id].win_match()
                self.players_dict[player1_id].results.append(result)

                otresult = [result[1], result[0], result[2]]
                self.players_dict[player2_id].results.append(otresult)

                self.printdbg("o player: %s da mesa: %s ganhou" % (self.players_dict[player1_id].name, table))
            elif result[1] > result[0]:
                self.players_dict[player2_id].win_match()
                self.players_dict[player1_id].results.append(result)

                otresult = [result[1], result[0], result[2]]
                self.players_dict[player2_id].results.append(otresult)

                self.printdbg("o player: %s da mesa: %s ganhou" % (self.players_dict[player2_id].name, table))

        # Remove table reported from open tables
        self.tables_out.remove(table)

        # When the last table reports, update tie breakers automatically
        if not len(self.tables_out):
            self.calculate_tiebreakers()

    def winner(self):
        players = []
        for player_id in self.players_dict:
            players.append(self.players_dict[player_id])

        winner = max(players, key=lambda x: x.tiebreaker)

        return winner

    def print_pairs(self, pairs):
        new_pairs = {}
        for table in pairs:
            player1_id = pairs[table][0]
            player2_id = pairs[table][1]

            if table == 'bye':
                new_pairs[table] = ['bye', self.players_dict[player2_id].name]
            else:
                new_pairs[table] = [self.players_dict[player1_id].name, self.players_dict[player2_id].name]

        print(new_pairs)
        print("")

    def printdbg(self, msg):
        if self.dbg:
            print(msg)
            print("")
