import copy
import json

from Utils.Helpers import Helpers
from Utils.Fingerprint import Fingerprint
from Files.CsvLogic.Characters import Characters
from Files.CsvLogic.Skins import Skins
from Files.CsvLogic.Cards import Cards


class Player:
    try:
        with open('config.json', 'r', encoding='utf-8') as config:
            settings = json.load(config)
    except FileNotFoundError:
        Helpers().create_config()
        with open('config.json', 'r', encoding='utf-8') as config:
            settings = json.load(config)

    skins_id = Skins().get_skins_id()
    brawlers_id = Characters().get_brawlers_id()

    ID = 0
    token = None

    trophies = settings['Trophies']
    tickets = settings['Tickets']
    gems = settings['Gems']
    resources = [
        {'ID': 1, 'Amount': settings['BrawlBoxTokens']},
        {'ID': 8, 'Amount': settings['Gold']},
        {'ID': 9, 'Amount': settings['BigBoxTokens']},
        {'ID': 10, 'Amount': settings['StarPoints']}
    ]
    high_trophies = settings['Trophies']
    trophy_reward = 1
    exp_points = settings['ExperiencePoints']
    profile_icon = 0
    name_color = 0
    selected_brawler = 0
    region = settings['Region']
    content_creator = 'Classic Brawl'
    name_set = False
    name = 'Guest'
    map_id = 0
    use_gadget = True
    starpower = 76
    gadget = 255
    home_brawler = 0
    home_skin = 0
    leaderboard_type = 0
    leaderboard_is_global = False
    bp_activated = False
    token_doubler = 0
    welcome_msg_viewed = False
    theme_id = settings['ThemeID']
    content_creator_codes = settings['ContentCreatorCodes']
    maintenance = settings['Maintenance']
    maintenance_time = settings['SecondsTillMaintenanceOver']
    patch = settings['Patch']
    patch_url = settings['PatchURL']
    patch_sha = Fingerprint.loadFinger('GameAssets/fingerprint.json')
    update_url = settings['UpdateURL']
    clubWarsEnabled = settings['ClubWarsEnabled']
    status = 0
    leaderboardData = []

    delivery_items = {}
    box_rewards = {}
    db = None
    battle_tick = 0
    unlocked_skins = []

    selected_skins = {f'{id}': 0 for id in brawlers_id}
    brawlers_unlocked = [0, 1]
    brawlers_card_id = [Cards().get_unlock_by_brawler_id(x) for x in brawlers_unlocked]
    brawlers_spg = Cards().get_spg_id()

    def_trophies = 0
    def_high_trophies = 99999
    brawlers_trophies = {f'{id}': def_trophies for id in brawlers_id}
    brawlers_high_trophies = {f'{id}': def_high_trophies for id in brawlers_id}
    def_level = 0
    brawlers_level = {f'{id}': def_level for id in brawlers_id}
    def_pp = 0
    brawlers_powerpoints = {f'{id}': def_pp for id in brawlers_id}

    club_id = 0
    club_role = 0
    message_tick = 0
    clients = {}

    _MUTABLE_DEFAULTS = (
        'resources',
        'content_creator_codes',
        'leaderboardData',
        'delivery_items',
        'box_rewards',
        'unlocked_skins',
        'selected_skins',
        'brawlers_unlocked',
        'brawlers_card_id',
        'brawlers_spg',
        'brawlers_trophies',
        'brawlers_high_trophies',
        'brawlers_level',
        'brawlers_powerpoints',
        'clients'
    )

    _SCALAR_DEFAULTS = (
        'ID', 'token', 'trophies', 'tickets', 'gems', 'high_trophies',
        'trophy_reward', 'exp_points', 'profile_icon', 'name_color',
        'selected_brawler', 'region', 'content_creator', 'name_set', 'name',
        'map_id', 'use_gadget', 'starpower', 'gadget', 'home_brawler',
        'home_skin', 'leaderboard_type', 'leaderboard_is_global',
        'bp_activated', 'token_doubler', 'welcome_msg_viewed', 'theme_id',
        'maintenance', 'maintenance_time', 'patch', 'patch_url', 'patch_sha',
        'update_url', 'clubWarsEnabled', 'status', 'db', 'battle_tick',
        'club_id', 'club_role', 'message_tick'
    )

    def __init__(self, device):
        self.device = device
        for name in self._MUTABLE_DEFAULTS:
            setattr(self, name, copy.deepcopy(getattr(type(self), name)))
        for name in self._SCALAR_DEFAULTS:
            setattr(self, name, getattr(type(self), name))
