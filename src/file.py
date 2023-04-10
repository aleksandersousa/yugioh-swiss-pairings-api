import json
import os

from player import Player

files_path = 'files/active_tournaments.txt'


class File():
    def write_tournament_id(self, id):
        if not os.path.isdir('files'):
            os.mkdir('files')

        check_file = os.path.isfile(files_path)

        if check_file:
            with open(files_path, 'a') as f:
                f.write(id + '\n')
        else:
            with open(files_path, 'w') as f:
                f.write(id + '\n')

    def delete_tournament_id(self, id):
        check_file = os.path.isfile(files_path)

        if check_file:
            with open(files_path, 'r+') as f:
                new_f = f.readlines()
                f.seek(0)
                for line in new_f:
                    if id not in line:
                        f.write(line)
                f.truncate()

            return 'success'

        return 'file_not_found'

    def save_tournament_data(self, tournament_id, data):
        with open('files/%s.json' % (tournament_id), 'w') as f:
            json.dump(data, f)

    def load_tournament_data(self, tournament_id, tournament):
        with open('files/%s.json' % (tournament_id), 'r') as f:
            data = json.load(f)

        for player in data['players_dict']:
            p = Player(name=player['name'], id=player['id'], score=player['score'],
                       tiebreaker=player['tiebreaker'], results=player['results'])
            tournament.add_player(p)

        for player in data['players_dict']:
            p = tournament.players_dict[player['id']]

            for opponent_id in player['opponents']:
                if opponent_id in tournament.players_dict:
                    op = tournament.players_dict[opponent_id]
                    p.opponents.append(op)

        tournament.current_round = data['current_round']
        tournament.open_table = data['open_table']
        tournament.starting_table = data['starting_table']
        tournament.round_pairings = data['round_pairings']
        tournament.max_group = data['max_group']
        tournament.tiebreaker_lists = data['tiebreaker_lists']
        tournament.tiebreaker_totals = data['tiebreaker_totals']
        tournament.tables_out = data['tables_out']

    def delete_tournament_data(self, tournament_id):
        check_file = os.path.isfile('files/%s.json' % (tournament_id))

        if check_file:
            os.remove('files/%s.json' % (tournament_id))
            return 'success'

        return 'file_not_found'
