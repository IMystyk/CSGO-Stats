from statistics import mode
import jsonpickle
from datetime import timedelta, datetime
from models import Player, Match
import matplotlib.pyplot as plt
import os
from fpdf import FPDF


def into_maps(matches):
    """
    Returns a dictionary of maps and matches played on them
    :param matches: List of matches
    :return: Dictionary of maps and their matches
    """
    maps = dict()
    for match in matches:
        if match.map_name not in maps.keys():
            maps[match.map_name] = []
        maps[match.map_name].append(match)

    return maps


def get_player_stats(player_name, matches):
    """
    Function returns a Player object, that contains that player's stats sorted into individual maps
    :param player_name: String, name of the given player
    :param matches: List of matches that are taken into account
    :return: Player object
    """
    games = into_maps(matches)

    maps = dict()
    for map in games.keys():
        games_counter = 0
        wait_time = timedelta()
        duration = timedelta()
        ping = 0
        kills = 0
        assists = 0
        deaths = 0
        mvps = 0
        hs_kills = 0
        score = 0
        rounds_won = 0
        rounds_lost = 0
        wins = 0
        loses = 0
        draws = 0
        scoreboard_positions = []
        for game in games[map]:
            games_counter += 1
            wait_time += game.wait_time
            duration += game.duration
            player = game.players.get(player_name)
            #  The list should be filtered before passing to the function, but this is an additional check
            if player is None:
                continue
            ping += player.get('ping')
            kills += player.get('kills')
            assists += player.get('assists')
            deaths += player.get('deaths')
            mvps += player.get('mvp')
            hs_kills += round(player.get('kills') * player.get('hsp') / 100, 0)
            score += player.get('score')
            position = list(game.players.keys()).index(player_name) + 1
            if len(game.players.keys()) > 4:
                if position > 5:
                    position = position - 5
            else:
                if position > 2:
                    position = position - 2
            scoreboard_positions.append(position)
            team = player.get('team')
            if team == 1:
                rounds_won += game.result[0]
                rounds_lost += game.result[1]
            else:
                rounds_won += game.result[1]
                rounds_lost += game.result[0]

            if game.result[0] > game.result[1]:
                if team == 1:
                    wins += 1
                else:
                    loses += 1
            elif game.result[0] < game.result[1]:
                if team == 2:
                    wins += 1
                else:
                    loses += 1
            else:
                draws += 1

        maps[map] = {
            'games': games_counter,
            'wait_time': wait_time,
            'duration': duration,
            'ping': ping,
            'kills': kills,
            'assists': assists,
            'deaths': deaths,
            'mvps': mvps,
            'hs_kills': hs_kills,
            'score': score,
            'rounds_won': rounds_won,
            'rounds_lost': rounds_lost,
            'wins': wins,
            'loses': loses,
            'draws': draws,
            'scoreboard_positions': scoreboard_positions
        }

    return Player(
        player_name,
        maps
    )


def get_spree(player_name, matches, win=True, draw=False):
    """
    Function searches for the longest win streak on every map and returns dictionary with maps and streak on every map
    :param player_name: string, name of a player that is to be searched for in matches
    :param matches: list of matches
    :param win: boolean, whether the spree counts won or lost games
    :param draw: boolean, whether to count draws towards a streak or not
    :return: dictionary of maps and numbers of games won in a row, as well as list of matches in given spree
    """
    maps = into_maps(matches)
    tmp_spree_matches = []
    spree_matches = []
    tmp_spree_counter = 0
    spree_counter = 0
    for match in matches:
        player = match.players.get(player_name)
        team = player.get('team')
        if match.result[0] > match.result[1]:
            if team == 1:
                if win:
                    tmp_spree_counter += 1
                    tmp_spree_matches.append(match)
                else:
                    if spree_counter < tmp_spree_counter:
                        spree_counter = tmp_spree_counter
                        spree_matches = tmp_spree_matches.copy()
                    tmp_spree_counter = 0
                    tmp_spree_matches = []
            else:
                if win:
                    if spree_counter < tmp_spree_counter:
                        spree_counter = tmp_spree_counter
                        spree_matches = tmp_spree_matches.copy()
                    tmp_spree_counter = 0
                    tmp_spree_matches = []
                else:
                    tmp_spree_counter += 1
                    tmp_spree_matches.append(match)
        elif match.result[0] < match.result[1]:
            if team == 2:
                if win:
                    tmp_spree_counter += 1
                    tmp_spree_matches.append(match)
                else:
                    if spree_counter < tmp_spree_counter:
                        spree_counter = tmp_spree_counter
                        spree_matches = tmp_spree_matches.copy()
                    tmp_spree_counter = 0
                    tmp_spree_matches = []
            else:
                if win:
                    if spree_counter < tmp_spree_counter:
                        spree_counter = tmp_spree_counter
                        spree_matches = tmp_spree_matches
                    tmp_spree_counter = 0
                    tmp_spree_matches = []
                else:
                    tmp_spree_counter += 1
                    tmp_spree_matches.append(match)
        else:
            if draw:
                tmp_spree_counter += 1
                tmp_spree_matches.append(match)
            else:
                if spree_counter < tmp_spree_counter:
                    spree_counter = tmp_spree_counter
                    spree_matches = tmp_spree_matches
                tmp_spree_counter = 0
                tmp_spree_matches = []

    if spree_counter < tmp_spree_counter:
        spree_counter = tmp_spree_counter
        spree_matches = tmp_spree_matches

    results = dict()
    results['total'] = [spree_counter, spree_matches]

    for map in maps.keys():
        if len(maps.keys()) > 1:
            results[map], _ = get_spree(player_name, maps[map], win, draw)

    return [spree_counter, spree_matches], results


def get_worst(player_name, matches):
    """
        Function returns a dictionary with player's worst matches in given pool
        :param player_name: string, name of the given player
        :param matches: List of matches that is taken into account
        :return: Dictionary of 3 worst matches
        """
    lowest_score_match = None
    most_deaths_match = None
    least_kills_match = None
    for match in matches:
        if lowest_score_match is None:
            lowest_score_match = match
        else:
            tmp = match.players[player_name].get('score')
            if tmp < lowest_score_match.players[player_name].get('score'):
                lowest_score_match = match
        if most_deaths_match is None:
            most_deaths_match = match
        else:
            tmp = match.players[player_name].get('deaths')
            if tmp > most_deaths_match.players[player_name].get('deaths'):
                most_deaths_match = match
        if least_kills_match is None:
            least_kills_match = match
        else:
            tmp = match.players[player_name].get('kills')
            if tmp < least_kills_match.players[player_name].get('kills'):
                least_kills_match = match

    return {"lowest_score": lowest_score_match, "most_deaths": most_deaths_match, "least_kills": least_kills_match}


def get_best(player_name, matches):
    """
    Function returns a dictionary with player's best matches in given pool
    :param player_name: string, name of the given player
    :param matches: List of matches that is taken into account
    :return: Dictionary of 3 best matches
    """
    highest_score_match = None
    least_deaths_match = None
    most_kills_match = None
    for match in matches:
        if highest_score_match is None:
            highest_score_match = match
        else:
            tmp = match.players[player_name].get('score')
            if tmp > highest_score_match.players[player_name].get('score'):
                highest_score_match = match
        if least_deaths_match is None:
            least_deaths_match = match
        else:
            tmp = match.players[player_name].get('deaths')
            if tmp < least_deaths_match.players[player_name].get('deaths'):
                least_deaths_match = match
        if most_kills_match is None:
            most_kills_match = match
        else:
            tmp = match.players[player_name].get('kills')
            if tmp > most_kills_match.players[player_name].get('kills'):
                most_kills_match = match

    return {"highest_score": highest_score_match, "least_deaths": least_deaths_match, "most_kills": most_kills_match}


def filter_matches(matches, players, begin_date=datetime(2000, 1, 1), finish_date=datetime.now()):
    """
    Filters given list of matches
    :param matches: list of matches to be filtered
    :param players: list of players that must be in game
    :param begin_date: the earliest acceptable match date
    :param finish_date: the latest acceptable match date
    :return: list of filtered matches
    """
    filtered_matches = matches.copy()
    for match in filtered_matches:
        for player in players:
            if player not in match.players.keys():
                try:
                    filtered_matches.remove(match)
                except ValueError:
                    pass
        if match.date.date() <= begin_date.date() or match.date.date() >= finish_date.date():
            try:
                filtered_matches.remove(match)
            except ValueError:
                pass

    return filtered_matches


def print_player_stats(player_name, matches, file_name):
    """
    Function prints given player's stats into the txt file
    :param player_name:
    :param matches: list of matches that are to be taken into account
    :param file_name: string, name of the txt file
    :return: void
    """

    player = get_player_stats(player_name, matches)

    timestamp = datetime.now()
    date = f'{timestamp.year}{timestamp.month}{timestamp.day}{timestamp.hour}{timestamp.minute}{timestamp.second}'

    if not os.path.exists('results/'):
        os.makedirs('results')

    with open('results/' + file_name + date + '.txt', 'w') as output_file:
        total_games = 0
        total_wins = 0
        total_loses = 0
        total_draws = 0
        total_rounds_won = 0
        total_rounds_lost = 0
        total_duration = timedelta()
        total_kills = 0
        total_deaths = 0
        total_assists = 0
        total_score = 0
        total_hs_kills = 0
        total_mvps = 0
        scoreboard_positions = []

        for map_name in player.maps.keys():
            output_file.write(f'{map_name}\n')
            map = player.maps.get(map_name)
            games = map.get("games")
            output_file.write(f'PLAYED {games}\n')
            output_file.write(f'WON {map.get("wins")}\n')
            output_file.write(f'LOST {map.get("loses")}\n')
            output_file.write(f'TIES {map.get("draws")}\n')
            try:
                win_lose_ration = map.get("wins") / map.get("loses")
            except ZeroDivisionError:
                win_lose_ration = map.get("wins")
            output_file.write(f'W/L {round(win_lose_ration, 2)}\n')
            output_file.write(f'WIN RATIO {round(map.get("wins") / map.get("games"), 2)}\n')
            avg_duration = map.get("duration") / games
            avg_duration = str(avg_duration).split('.')[0]
            avg_duration = avg_duration.replace('0', '', 1)
            avg_duration = avg_duration.replace(':', '', 1)
            output_file.write(f'AVG DURATION {avg_duration}\n')
            output_file.write(f'ROUNDS WON {map.get("rounds_won")}\n')
            output_file.write(f'ROUNDS LOST {map.get("rounds_lost")}\n')
            output_file.write('\n')

            output_file.write(f'KILLS {map.get("kills")}\n')
            output_file.write(f'ASSISTS {map.get("assists")}\n')
            output_file.write(f'DEATHS {map.get("deaths")}\n')
            output_file.write(f'HSP {round(map.get("hs_kills") / map.get("kills"), 2)}\n')
            output_file.write(f'AVG KILLS {round(map.get("kills") / games, 2)}\n')
            output_file.write(f'AVG DEATHS {round(map.get("deaths") / games, 2)}\n')
            output_file.write(f'AVG SCORE {round(map.get("score") / games, 2)}\n')
            output_file.write(f'MOST FREQUENT POSITION {mode(map.get("scoreboard_positions"))} in '
                              f'{round(map.get("scoreboard_positions").count(mode(map.get("scoreboard_positions"))) / len(map.get("scoreboard_positions")), 2)}\n')
            try:
                kill_death_ratio = map.get("kills") / map.get('deaths')
            except ZeroDivisionError:
                kill_death_ratio = map.get('kills')
            output_file.write(f'K/D {round(kill_death_ratio, 2)}\n')

            total_games += games
            total_wins += map.get('wins')
            total_loses += map.get('loses')
            total_draws += map.get('draws')
            total_rounds_won += map.get('rounds_won')
            total_rounds_lost += map.get('rounds_lost')
            total_duration += map.get('duration')
            total_kills += map.get('kills')
            total_assists += map.get('assists')
            total_deaths += map.get('deaths')
            total_hs_kills += map.get('hs_kills')
            total_score += map.get('score')
            total_mvps += map.get('mvps')
            scoreboard_positions.extend(map.get('scoreboard_positions'))

            output_file.write('\n')

        output_file.write("TOTAL\n")
        output_file.write(f'PLAYED {total_games}\n')
        output_file.write(f'WON {total_wins}\n')
        output_file.write(f'LOST {total_loses}\n')
        output_file.write(f'TIES {total_draws}\n')
        total_duration = total_duration / total_games
        total_duration = str(total_duration).split('.')[0]
        total_duration = total_duration.replace('0', '', 1)
        total_duration = total_duration.replace(':', '', 1)
        try:
            win_lose_ration = total_wins / total_loses
        except ZeroDivisionError:
            win_lose_ration = total_wins
        output_file.write(f'W/L {round(win_lose_ration, 2)}\n')
        output_file.write(f'WIN RATIO {round(total_wins / total_games, 2)}\n')
        output_file.write(f'AVG DURATION {total_duration}\n')
        output_file.write(f'ROUNDS WON {total_rounds_won}\n')
        output_file.write(f'ROUNDS LOST {total_rounds_lost}\n')
        output_file.write('\n')

        output_file.write(f'KILLS {total_kills}\n')
        output_file.write(f'ASSISTS {total_assists}\n')
        output_file.write(f'DEATHS {total_deaths}\n')
        output_file.write(f'HSP {round(total_hs_kills / total_kills, 2)}\n')
        output_file.write(f'AVG KILLS {round(total_kills / total_games, 2)}\n')
        output_file.write(f'AVG DEATHS {round(total_deaths / total_games, 2)}\n')
        output_file.write(f'AVG SCORE {round(total_score / total_games, 2)}\n')
        output_file.write(f'MOST FREQUENT POSITION {mode(map.get("scoreboard_positions"))} in '
                          f'{round(scoreboard_positions.count(mode(scoreboard_positions)) / len(scoreboard_positions), 2)}\n')
        try:
            kill_death_ratio = total_kills / total_deaths
        except ZeroDivisionError:
            kill_death_ratio = total_kills
        output_file.write(f'K/D {round(kill_death_ratio, 2)}\n')

    generate_pdf(file_name + date)


def read_matches(file_name):
    """
    Function reads matches from a file and returns list of given matches
    :param file_name: String, name of the file
    :return: List of Match objects
    """
    with open(file_name + '.json', 'r') as input_file:
        input_string = input_file.read()
        matches = jsonpickle.decode(input_string)

    return matches


def plot_scores(player_name, matches):
    """
    Function plots graphs representing scores on different maps
    :param player_name: Player whose team will be taken into account (for the purposes of determining win/lose)
    :param matches: List of matches taken into account
    :return:  void
    """
    # Assert competitive or wingman
    if len(matches[0].players.keys()) > 4:
        max_score = 16
    else:
        max_score = 9

    results = dict()
    for i in range(max_score - 1):
        results[f'{i}:{max_score}'] = 0
    results[f'{max_score - 1}:{max_score - 1}'] = 0
    for i in range(max_score - 2, -1, -1):
        results[f'{max_score}:{i}'] = 0

    for match in matches:
        player = match.players.get(player_name)
        team = player.get('team')
        if team == 1:
            result = f'{match.result[0]}:{match.result[1]}'
        else:
            result = f'{match.result[1]}:{match.result[0]}'
        results[result] += 1
    names = list(results.keys())
    values = list(results.values())
    plt.bar(names, values)
    if not os.path.exists('results/plots/'):
        os.makedirs('results/plots')
    plt.title("All time")
    plt.savefig(f'results\plots\\all_time')
    plt.cla()

    maps = into_maps(matches)
    for map in maps.keys():
        for result in results.keys():
            results[result] = 0
        for match in maps[map]:
            player = match.players.get(player_name)
            team = player.get('team')
            if team == 1:
                result = f'{match.result[0]}:{match.result[1]}'
            else:
                result = f'{match.result[1]}:{match.result[0]}'
            results[result] += 1

        names = list(results.keys())
        values = list(results.values())
        plt.bar(names, values)
        plt.title(map)
        plt.savefig(f'results\plots\{map}')
        plt.cla()


def generate_pdf(file_name):
    """
    Function generates pdf file from a txt file
    :param file_name: Name of a text file
    :return:
    """
    pdf = FPDF()
    # Add a page
    pdf.add_page()
    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=15)
    # open the text file in read mode
    f = open("results/" + file_name + ".txt", "r")
    # insert the texts in pdf
    for x in f:
        pdf.cell(200, 10, txt=x, ln=1, align='C')
    # save the pdf with name .pdf
    pdf.output("results/" + file_name + ".pdf")


if __name__ == "__main__":

    matches = read_matches('results')

    #  Here you filter matches
    filtered_matches = filter_matches(matches, ['Mystyk', '\u26a1 Jarlloth'], datetime(2000, 1, 1), datetime.now())

    #   Get longest winning/losing spree
    # _, spree = get_spree('\u26a1 Jarlloth', filtered_matches, True, False)
    #
    # for key in spree.keys():
    #     print(f'{key} {len(spree.get(key)[1])}')
    #     for match in spree.get(key)[1]:
    #         print(match)

    print_player_stats('Mystyk', filtered_matches, 'analyzed_data_mystyk')
    print_player_stats('\u26a1 Jarlloth', filtered_matches, 'analyzed_data_jaro')
    # best_matches = get_best('\u26a1 Jarlloth', filtered_matches)

    plot_scores('Mystyk', filtered_matches)

