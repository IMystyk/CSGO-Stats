from statistics import mode
import jsonpickle
from datetime import timedelta, datetime
from models import Player, Match


def get_player_stats(games, player_name):
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


def get_worst(player, matches):
    lowest_score_match = None
    most_deaths_match = None
    least_kills_match = None
    for match in matches:
        if lowest_score_match is None:
            lowest_score_match = match
        else:
            tmp = match.players[player].get('score')
            if tmp < lowest_score_match.players[player].get('score'):
                lowest_score_match = match
        if most_deaths_match is None:
            most_deaths_match = match
        else:
            tmp = match.players[player].get('deaths')
            if tmp > most_deaths_match.players[player].get('deaths'):
                most_deaths_match = match
        if least_kills_match is None:
            least_kills_match = match
        else:
            tmp = match.players[player].get('kills')
            if tmp < least_kills_match.players[player].get('kills'):
                least_kills_match = match

    return lowest_score_match, most_deaths_match, least_kills_match


def get_best(player, matches):
    highest_score_match = None
    least_deaths_match = None
    most_kills_match = None
    for match in matches:
        if highest_score_match is None:
            highest_score_match = match
        else:
            tmp = match.players[player].get('score')
            if tmp > highest_score_match.players[player].get('score'):
                highest_score_match = match
        if least_deaths_match is None:
            least_deaths_match = match
        else:
            tmp = match.players[player].get('deaths')
            if tmp < least_deaths_match.players[player].get('deaths'):
                least_deaths_match = match
        if most_kills_match is None:
            most_kills_match = match
        else:
            tmp = match.players[player].get('kills')
            if tmp > most_kills_match.players[player].get('kills'):
                most_kills_match = match

    return highest_score_match, least_deaths_match, most_kills_match


if __name__ == "__main__":

    with open('Jaro_MM_results.json', 'r') as input_file:
        input_string = input_file.read()
        matches = jsonpickle.decode(input_string)

    maps = dict()
    for match in matches:
        if match.map_name not in maps.keys():
            maps[match.map_name] = []
        #  Here you filer matches
        if "\u26a1 Jarlloth" in match.players.keys() and "Not Gay But 20 Dolla Is 20 Dolla" not in match.players.keys() and match.date.date() > datetime(2019, 1, 1).date():
            maps[match.map_name].append(match)

    filtered_matches = []
    for match in matches:
        if 16 in match.result and "Mystyk" in match.players.keys():
            if match.players["Mystyk"].get('ping') > 0:
                filtered_matches.append(match)

    map_names = list(maps.keys())
    for map_name in map_names:
        if len(maps[map_name]) == 0:
            maps.pop(map_name)

    mystyk = get_player_stats(maps, 'Mystyk')
    jaro = get_player_stats(maps, "\u26a1 Jarlloth")

    worst_matches = get_worst("Mystyk", filtered_matches)
    best_matches = get_best("Mystyk", filtered_matches)

    player = jaro

    with open('analyzed_data.txt', 'w') as output_file:
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
            output_file.write(f'WIN RATIO {round(map.get("wins")/map.get("games"), 2)}\n')
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
                              f'{round(map.get("scoreboard_positions").count(mode(map.get("scoreboard_positions"))) / len(map.get("scoreboard_positions")),2)}\n')
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

