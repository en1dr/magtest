import telebot # подключение библиотеки pyTelegramBotAPI
import my_tools


# основной класс, содержащий все параметры текущей игры
class Game(object):
    def __init__(self, cid):
        print('init started')
        self.gametype = ['duel', 'massfight']
        self.gamestate = ['team_selection', 'fighting']
        self.currentstate = None
        self.player_ids = []
        self.player_dict = {}
        self.players = []
        self.aiplayers = []

        self.pending_players = []
        self.pending_team1 = []
        self.pending_team2 = []
        self.marked_id = []

        self.team1 = Team()
        self.team2 = Team()
        self.cid = cid
        self.waitings = None

        self.string = Actionstring(self.cid)
        self.fight = Fight(self, self.team1, self.team2)

    def startfight(self):
        my_tools.fight_loop(self, self.fight)


# Класс команды
class Team(object):
    def __init__(self):
        self.losthp = 0
        self.Name = None
        self.damagetaken = 0
        self.leader = None
        self.players = []
        self.deadplayers = []
        self.actors = []
        self.participators = []

    # Вычисляет суммарный урон всей команде
    def getteamdamage(self):
        for n in self.actors:
            self.damagetaken += n.damagetaken
        return self.damagetaken


# Класс игрока
class Player(object):
    # Инициализация
    def __init__(self, playerchat_id, player_name, Game):
        # Переменные для бота
        self.Suicide = False
        self.name = player_name
        self.chat_id = playerchat_id
        self.info = Actionstring(playerchat_id)
        self.game = Game
        self.fight = Game.fight
        self.choicemessage = None
        self.maxhp = 2000
        self.hp = 2000
        self.disabled = False
        self.alive = True
        self.selectedpowers = []
        self.castready = False


class Actionstring(object):
    def __init__(self, cid):
        self.string = ' '
        self.cid = cid
        self.mod = False

    def add(self, strin):
        self.string = self.string + '\n' + strin
        self.mod = True

    def add(self, strin):
        self.string = self.string + '\n' + strin
        self.mod = True

    def post(self, bot, x, cid=None):
        if self.mod:
            string = str(x + ': ' + self.string)
            if cid is None:
                bot.send_message(self.cid, string)
            else:
                bot.send_message(cid, string)
        self.mod = False
        self.string = str(' ')

    def clear(self):
        self.mod = False
        self.string = str(' ')


class Fight(object):
    def __init__(self, game, team1, team2):
        self.mental = []
        self.activeplayers = []
        self.aiplayers = []
        self.actors = []
        self.round = 0
        self.fightstates = []
        self.fightstate = None
        self.done = False
        self.team1 = team1
        self.team2 = team2
        self.playerpool = []
        self.game = game
        self.string = game.string
        self.Withbots = False
        self.state = ["first", "second", "third"]


games_list = {}
players_list = {}
list_waitingplayers = []
powerlist = []


class Power(object):
    def __init__(self, name, item_id, standart):
        self.name = name
        self.id = item_id
        self.standart = standart
        if self.standart:
            powerlist.append(self)

sorcery = Power(u'\U0001F4AB', 'power_sorcery', True)
life = Power(u'\U0001F331', 'power_life', True)
poison = Power(u'\U0001F40D', 'power_poison', False)
water = Power(u'\U0001F4A7', 'power_water', True)
steam = Power(u'\U0001F4A8', 'power_steam', False)
lightning = Power(u'\U000026A1', 'power_lightning', True)
frost = Power(u'\U00002744', 'power_frost', True)
fire = Power(u'\U0001F525', 'power_fire', True)
shield = Power(u'\U0001F6E1', 'power_shield', True)
earth = Power(u'\U000026F0', 'power_earth', True)

id_powers = list(powerlist)
powers = {p.id: p for p in id_powers}
print(powers)
