from datetime import timedelta


class Match:

    def __init__(self, map_name, date, wait_time, duration, result, players):
        """
        :param map_name: string
        :param date: datetime
        :param wait_time: timedelta
        :param duration: timedelta
        :param result: list
        :param players: dictionary
        """
        self.map_name = map_name
        self.date = date
        self.wait_time = wait_time
        self.duration = duration
        self.result = result
        self.players = players

    def __str__(self):
        return f'Date: {self.date}  Map: {self.map_name}  Result: {self.result[0]} - {self.result[1]}'


class Map:

    def __init__(self, name):
        self.name = name
        self.ping = 0
        self.kills = 0
        self.assists = 0
        self.deaths = 0
        self.mvps = 0
        self.hs_kills = 0
        self.score = 0
        self.matches = 0


class Player:

    def __init__(self, nickname, maps):
        self.nickname = nickname
        self.maps = maps

