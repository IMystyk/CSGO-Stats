from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
from datetime import datetime, timedelta
from models import Match
import jsonpickle


def get_matches():

    matches = []

    # Load page with all the matches
    while True:
        try:
            WebDriverWait(driver, 10).until(
                ec.element_to_be_clickable((By.ID, "load_more_button"))
            )
        except TimeoutException:
            break
        load_matches = driver.find_element(By.ID, "load_more_button")
        load_matches.click()

    result_list = driver.find_elements(By.XPATH, "//table[@class='generic_kv_table csgo_scoreboard_root']/tbody/tr")

    for match_result in result_list:
        try:
            match_general = match_result.find_element(By.CLASS_NAME, "csgo_scoreboard_inner_left")
            match_players = match_result.find_element(By.CLASS_NAME, "csgo_scoreboard_inner_right")
        except NoSuchElementException:
            continue

        match_general = match_general.find_elements(By.XPATH, "./tbody/tr")

        # One element in the list is a score, not a player
        match_players = match_players.find_elements(By.XPATH, "./tbody/tr")

        map_name = match_general[0].text.split()[-1]
        tmp = match_general[1].text.replace(" GMT", "")
        date = datetime.strptime(tmp, '%Y-%m-%d %H:%M:%S')
        tmp_time_str = match_general[3].text.split()[-1]
        tmp_time = datetime.strptime(tmp_time_str, '%M:%S')
        wait_time = timedelta(minutes=tmp_time.minute, seconds=tmp_time.second)
        tmp_time_str = match_general[4].text.split()[-1]
        tmp_time = datetime.strptime(tmp_time_str, '%M:%S')
        match_duration = timedelta(minutes=tmp_time.minute, seconds=tmp_time.second)

        if "matchhistorycompetitive" in driver.current_url:
            match_score = match_players[6].text.split(':')
        else:
            match_score = match_players[3].text.split(':')
        match_score = [int(match_score[0]), int(match_score[-1])]
        team = 1
        players = dict()
        for player in match_players:
            player_stats = player.find_elements(By.XPATH, "./td")
            if len(player_stats) == 0:
                continue
            elif len(player_stats) == 1:
                team = 2
                continue
            player_name = player_stats[0].text
            player_ping = int(player_stats[1].text)
            player_kills = int(player_stats[2].text)
            player_assists = int(player_stats[3].text)
            player_deaths = int(player_stats[4].text)
            player_mvps = player_stats[5].text
            if len(player_mvps) > 1:
                player_mvps = int(player_mvps[1:])
            elif " " not in player_mvps:
                player_mvps = 1
            else:
                player_mvps = 0
            try:
                player_hsp = int(player_stats[6].text.replace("%", ""))
            except ValueError:
                player_hsp = 0
            player_score = int(player_stats[7].text)
            player_team = team

            players[player_name] = {
                "ping": player_ping,
                "kills": player_kills,
                "assists": player_assists,
                "deaths": player_deaths,
                "mvp": player_mvps,
                "hsp": player_hsp,
                "score": player_score,
                "team": player_team
                }

        matches.append(Match(map_name, date, wait_time, match_duration, match_score, players))

    return matches


if __name__ == '__main__':

    driver = webdriver.Firefox()
    driver.get("https://steamcommunity.com/login/")

    try:
        WebDriverWait(driver, 60).until(
            ec.element_to_be_clickable((By.CLASS_NAME, "profile_page"))
        )
    except TimeoutException:
        exit()

    url = driver.current_url
    url += "/gcpd/730/"
    driver.get(url)

    time.sleep(3)
    matches = get_matches()
    json_string = jsonpickle.encode(matches)
    with open('results.json', 'w') as output_file:
        output_file.write(json_string)
    exit()



