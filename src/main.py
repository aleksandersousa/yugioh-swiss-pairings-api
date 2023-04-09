import random
from player import Player
from swiss_pairing_system import SwissPairingSystem

to = SwissPairingSystem(dbg=True)

players = [Player('souder'), Player('alterlan'), Player('santana'), Player(
    'gomes'), Player('will'), Player('thunder'), Player('tony')]

for player in players:
    to.add_player(player)

pairings1 = to.pair_round()
to.print_pairs(pairings1)

for table in pairings1:
    if not type(pairings1[table]) is str:
        per = random.randint(1, 100)
        if per < 25:
            to.reportMatch(table, [2, 0, 0])
        elif per < 47:
            to.reportMatch(table, [2, 1, 0])
        elif per < 60:
            to.reportMatch(table, [0, 2, 0])
        elif per < 97:
            to.reportMatch(table, [1, 2, 0])
        elif per < 98:
            to.reportMatch(table, [0, 0, 1])
        else:
            to.reportMatch(table, [1, 1, 1])

print(to.current_result())

pairings2 = to.pair_round()
to.print_pairs(pairings2)

for table in pairings2:
    if not type(pairings2[table]) is str:
        per = random.randint(1, 100)
        if per < 25:
            to.reportMatch(table, [2, 0, 0])
        elif per < 47:
            to.reportMatch(table, [2, 1, 0])
        elif per < 60:
            to.reportMatch(table, [0, 2, 0])
        elif per < 97:
            to.reportMatch(table, [1, 2, 0])
        elif per < 98:
            to.reportMatch(table, [0, 0, 1])
        else:
            to.reportMatch(table, [1, 1, 1])

print(to.current_result())

to.drop_player(players[-1].id)

pairings3 = to.pair_round()
to.print_pairs(pairings3)

for table in pairings3:
    if not type(pairings3[table]) is str:
        per = random.randint(1, 100)
        if per < 25:
            to.reportMatch(table, [2, 0, 0])
        elif per < 47:
            to.reportMatch(table, [2, 1, 0])
        elif per < 60:
            to.reportMatch(table, [0, 2, 0])
        elif per < 97:
            to.reportMatch(table, [1, 2, 0])
        elif per < 98:
            to.reportMatch(table, [0, 0, 1])
        else:
            to.reportMatch(table, [1, 1, 1])

print(to.current_result())

print("o vencedor é: %s" % vars(to.winner()))
