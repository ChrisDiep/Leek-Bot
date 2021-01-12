import re
import requests

import json


def clean_input(words):
    """ Removes non-alphanumeric values and joins the input together """
    parsed = ''.join(map(lambda word: re.sub(
        r'[^a-zA-Z0-9]', '', word), words))
    return parsed


def get_champions(version):
    url = f'http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json'
    resp = requests.get(url)
    champions_obj = resp.json()["data"]
    champion_ids = {}
    for champion in champions_obj:
        champion_ids[champions_obj[champion]["key"]] = champion
    return champion_ids


def get_version():
    resp = requests.get(
        'https://ddragon.leagueoflegends.com/api/versions.json')
    return resp.json()[0]


def get_id(version):
    url = f'http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json'
    resp = requests.get(url)
    champions_obj = resp.json()["data"]
    champion_ids = []
    for champion in champions_obj:
        champion_ids.append(int(champions_obj[champion]["key"]))
    return champion_ids


def write_queue_ids():
    queue_ids = json.load(open("dummy_queues.json"))
    queue_obj = {}
    for queue in queue_ids:
        if queue["notes"] is None:
            if queue["description"] is not None:
                queue["description"] = queue["description"].replace(
                    ' games', '')
            queue_obj[queue["queueId"]] = queue
    return queue_obj