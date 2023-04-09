import uuid


WIN_POINTS = 3
DRAW_POINTS = 1


class Player():
    def __init__(self, name) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.score = 0
        self.tiebreaker = 0
        self.results = []
        self.opponents = []

    def win_match(self):
        self.score += WIN_POINTS

    def draw_match(self):
        self.score += DRAW_POINTS

    def calculate_tiebreaker(self):
        op_op_win_percent_total = 0.0
        # Loop through all opponents
        for opponent in self.opponents:
            # get sum of opponents opponents win percent
            op_op_win_percent_total += opponent.calculate_opponents_win_percent()

        # get opponents opponents win percent
        op_op_win_percent = op_op_win_percent_total / len(self.opponents)

        # tiebreaker is xxyyyzzz format,
        # where xx is this player score
        # where yyy is this player opponents win percent
        # where zzz is this player opponents opponents win percent
        self.tiebreaker = int(str(self.score) + str(self.calculate_opponents_win_percent()) +
                              str(int(op_op_win_percent)))

    def calculate_opponents_win_percent(self):
        opponent_win_percents = []
        # Loop through all opponents
        for opponent in self.opponents:
            if opponent.name != "bye":
                # calculate win percent out of the 3 decimal places, minimum of 0.111 per person
                win_percent = opponent.score / (max(float(len(opponent.opponents)) * WIN_POINTS, 0.111))
                opponent_win_percents.append(win_percent)

        # Make sure we have opponents
        if len(opponent_win_percents):
            result = round(sum(opponent_win_percents) / float(len(opponent_win_percents)), 3)

            # if 100% of win_percent return the greatest three number digit to respect yyy format
            if result == 1:
                return 999

            # to format for yyy
            return int(result * 1000)

        # min result available to respect yyy format
        return 111
