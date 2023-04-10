import uuid
from flask import Flask, request, jsonify
from file import File
from player import Player

from swiss_pairing_system import SwissPairingSystem

app = Flask(__name__)

file = File()


def parse_to_data(to):
    data = vars(to)
    data['players_dict'] = [vars(data['players_dict'][i]) for i in data['players_dict']]

    for player in data['players_dict']:
        player['opponents'] = [vars(op)['id'] for op in player['opponents']]

    keys_values = data['round_pairings'].items()
    data['round_pairings'] = {str(key): value for key, value in keys_values}

    return data


@app.route('/')
def home():
    return jsonify({'message': 'server running!'})

# tournament routes


@app.route('/create_tournament', methods=['POST'])
def create_tournament():
    id = str(uuid.uuid4())
    file.write_tournament_id(id)

    return jsonify({'tournament_id': id})


@app.route('/delete_tournament/<id>', methods=['DELETE'])
def delete_tournament(id):
    res = file.delete_tournament_data(id)

    if res != 'success':
        return jsonify({'message': res}), 400

    res = file.delete_tournament_id(id)

    if res != 'success':
        return jsonify({'message': res}), 400

    return '', 204


# parings routes

@app.route('/tournaments/<tournament_id>/add_players', methods=['POST'])
def add_players(tournament_id):
    tournament = SwissPairingSystem()

    player_names = request.get_json()['players']

    for player_name in player_names:
        player = Player(name=player_name)
        tournament.add_player(player)

    data = parse_to_data(tournament)
    file.save_tournament_data(tournament_id, data)

    return jsonify({'tournament': data})


@app.route('/tournaments/<tournament_id>/drop_player/<player_id>', methods=['DELETE'])
def drop_player(tournament_id, player_id):
    tournament = SwissPairingSystem()

    file.load_tournament_data(tournament_id, tournament)

    tournament.drop_player(player_id)

    data = parse_to_data(tournament)
    file.save_tournament_data(tournament_id, data)

    return '', 204


@app.route('/tournaments/<tournament_id>/pair_round', methods=['GET'])
def pair_round(tournament_id):
    tournament = SwissPairingSystem()

    file.load_tournament_data(tournament_id, tournament)

    pairings = tournament.pair_round()
    pairings = tournament.human_friendly_pairs(pairings)

    data = parse_to_data(tournament)
    file.save_tournament_data(tournament_id, data)

    return jsonify({'pairings': pairings})


@app.route('/tournaments/<tournament_id>/report_match', methods=['POST'])
def report_match(tournament_id):
    results = request.get_json()['results']
    tournament = SwissPairingSystem()

    file.load_tournament_data(tournament_id, tournament)

    for result in results:
        tournament.report_match(result['table'], result['result'])

    current_result = tournament.current_result()

    data = parse_to_data(tournament)
    file.save_tournament_data(tournament_id, data)

    return jsonify({'current_result': current_result})


# main driver function
if __name__ == "__main__":
    app.run()
