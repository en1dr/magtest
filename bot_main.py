import telebot # подключение библиотеки pyTelegramBotAPI
import config
import threading
import Game_classes
import my_tools
import time


# для запуска скриптов
# from subprocess import call
# создание бота с его токеном API
bot = telebot.TeleBot(config.token)
types = telebot.types

# текст справки
help_string = []
help_string.append("Это простой *тестовый бот*, созданный в обучающих целях.\n\n")
help_string.append("/duel - запускает новую игру;\n")
help_string.append("/join - войти в текущую игру;\n")
help_string.append("/report - направить вопрос или жалобу;\n")
help_string.append("/help - отображает эту справку.")
help_string.append(u'\n\U0001F4A3 \U000026A1 \U0001F331 \U0001F40D \U0001F4A7 \U0001F4A8 \U0001F4AB \U0001F52E \U00002744 \U0001F525 \U0001F6E1 \U000026F0')



def team_select(message, Game):
    if Game.currentstate == Game.gamestate[0] and message.from_user.id not in Game.player_ids \
            and message.chat.id == Game.cid:
        Game.player_ids.append(message.from_user.id)
        Game.players.append(Game_classes.Player(message.from_user.id, message.from_user.first_name, None, Game))
        Game_classes.players_list[message.from_user.id] = Game
        keyboard = types.InlineKeyboardMarkup()
        callback_button1 = types.InlineKeyboardButton(text="Красные", callback_data='team1')
        callback_button2 = types.InlineKeyboardButton(text="Синие", callback_data='team2')
        keyboard.add(callback_button1, callback_button2)
        bot.send_message(message.from_user.id, message.from_user.first_name + ' Выберите команду:', reply_markup=keyboard)

def cancelgame(Game):
    if Game.currentstate == Game.gamestate[0]:
        bot.send_message(Game.cid, "Время вышло - игра отменена.")
        print('Игра отменена - время вышло')
        my_tools.delete_game(Game)
        print('Игра удалена')

# --- команды

@bot.message_handler(commands=['start'])
def send_start(message):
    # отправка простого сообщения
    bot.send_message(message.chat.id, "Привет, я тестовый бот! Отправьте мне /help для вывод справки.")
    print('Вызвана команда start')


@bot.message_handler(commands=['help'])
def send_help(message):
    # отправка сообщения с поддержкой разметки Markdown
    bot.send_message(message.chat.id, "".join(help_string), parse_mode="Markdown")
    print('Вызвана команда help')


@bot.message_handler(commands=['duel'])
def start_game(message):
    ''' if message.chat.id in Main_classes.dict_games:
        # pass
    # else:
        Game = Main_classes.Game(message.chat.id)
        Main_classes.dict_games[message.chat.id] = Game
        Main_classes.dict_games[message.chat.id].gamestate = Main_classes.dict_games[message.chat.id].gamestates[0]
        bot.send_message(message.chat.id, "Используйте команду /join, чтобы вступить в игру. 5 минут до отмены игры.")'''
    #print("Попытка запустить игру в личке " + str(message.chat.type.find('private')))
    print('Chat is private - '+ str('private'== message.chat.type))
    if message.chat.type == 'private':
        print('Private ignore')
        bot.send_message(message.chat.id, "Мы не будем играть с тобой в личке больной социофоб")
    elif message.chat.id not in [-244977665, 0, 1]:
        print('Chat ignore')
        bot.send_message(message.chat.id, "Прототип игры запускается только в эксклюзивных игровых сообществах. " + \
                         "По всем вопросам обращаться к @Cisgender")
    else:
        print("Chat ID is" + str(message.chat.id))
        if message.chat.id in Game_classes.games_list:
            print('Попытка запустить игру повторно')
            pass
        else:
            Game = Game_classes.Game(message.chat.id) # инициализируем объект класса Игра
            Game_classes.games_list[message.chat.id] = Game # заносим объект в список текущих игр
            # переводим игру в состояние "набор игроков"
            Game_classes.games_list[message.chat.id].currentstate = Game_classes.games_list[message.chat.id].gamestate[0]
            Game_classes.games_list[message.chat.id].currenttype = Game_classes.games_list[message.chat.id].gametype[0]
            bot.send_message(message.chat.id, "Начинаем игру. Время войти на арену /join")
            Game.team1.Name = "Красные"
            Game.team2.Name = "Синие"
            Game.waitingtimer = threading.Timer(25, cancelgame, [Game])
            Game.waitingtimer.start()
            print('Запущена новая игра')
            print(Game)
            add_player(message)


@bot.message_handler(commands=["join"])
def add_player(message):
    try:
        Game = Game_classes.games_list[message.chat.id]
        print("Пытаемся получить экземпляр игры" + str(message.chat.id))
    except:
        print('Игра не найдена!')
        return False
    if message.from_user.id in Game_classes.players_list:
        print('Попытка войти в игру повторно!')
        return False
    bot.send_message(message.from_user.id, 'Добро пожаловать. Идёт выбор команды...', parse_mode='markdown')
    bot.send_message(message.chat.id, message.from_user.first_name + " решается выйти на арену кровавой битвы.")
    if Game != None:
        print("Игра существует")
        print("currentstate = " + Game_classes.games_list[message.chat.id].currentstate  + "  Game.gametype[0] = " + Game.gametype[0])
        if Game_classes.games_list[message.chat.id].currentstate == Game.gamestate[0] \
                and Game_classes.games_list[message.chat.id].currenttype == Game.gametype[0] \
                and message.from_user.id not in Game.marked_id \
                and message.chat.id == Game.cid:
                print("Новый игрок в режим дуэли")
                print("Пытаемся запихнуть игрока " + str(message.from_user.first_name) + " ID=" + str(message.from_user.id) + " в команду.")
                player = Game_classes.Player(message.from_user.id, message.from_user.first_name.split(' ')[0][:12], Game)
                Game.pending_players.append(player)
                Game.marked_id.append(player.chat_id)
                Game_classes.players_list[player.chat_id] = Game
                if not Game.pending_team1:
                    Game.pending_team1.append(player)
                    bot.send_message(message.from_user.id, 'Будем сражаться за команду *красных*!', parse_mode='markdown')
                elif not Game.pending_team2:
                    Game.pending_team2.append(player)
                    bot.send_message(message.from_user.id, 'Будем сражаться за команду *синих*!', parse_mode='markdown')
                    start_game(message)
                #team_select(message, Game)
    print(Game)
''' + \
                        "\n\n _В битве на выживание нельзя оставаться безучастным. Любой, кто не будет сражаться на твоей стороне - враг, которого ты должен сокрушить. \nСкрипторус Мунификантус_" \
        , parse_mode = 'markdown')'''


@bot.message_handler(commands=["fight"])
def start_game(message):
    try:
        Game = Game_classes.games_list[message.chat.id]
        print("Пытаемся получить экземпляр игры" + str(message.chat.id))
    except:
        print('Игра не найдена!')
        return False
    if Game is not None:
        if Game.currentstate == Game.gamestate[0]:
            if message.from_user.id in Game_classes.players_list:
                if not Game.pending_team1 or not Game.pending_team2:
                    bot.send_message(message.chat.id, "Слишком мало игроков! :(")
                elif len(Game.pending_players) > len(Game.pending_team1) + len(Game.pending_team1):
                    bot.send_message(message.chat.id, "Рано. Не все выбрали красную команду.")
                elif len(Game.pending_players) == len(Game.pending_team1) + len(Game.pending_team2):
                    Game.currentstate = Game.gamestate[1]
                    for actor in Game.pending_team1:
                        Game.players.append(actor)
                        Game.team1.players.append(actor)
                        actor.team = Game.team1
                    for actor in Game.pending_team2:
                        Game.players.append(actor)
                        Game.team2.players.append(actor)
                        actor.team = Game.team2
                    my_tools.start_fight(message.chat.id)
            else:
                bot.send_message(message.chat.id, 'Это вам не Пёсья игра! Запустить её может только участник', parse_mode='markdown')



@bot.message_handler(commands=["report"])
def report(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Пройти", url="http://natribu.org")
    keyboard.add(url_button)
    bot.send_message(message.chat.id, "Для отправки жалобы или предложений перейди по ссылке ниже.",
                     reply_markup=keyboard)


@bot.message_handler(commands=["admcancel"])
def adm_cancel(message):
    if str(message.from_user.id) == '83697884':
        game = Game_classes.Game(message.chat.id)
        cancelgame(game)
        game.fight.done = True


@bot.callback_query_handler(func=lambda call: True)
def action(call):
    if call.message:
        print("Получена команда по кнопке.")

    #print(Game_classes.players_list)
    try:
        game = Game_classes.players_list[call.from_user.id]
    except KeyError:
        print("Игры нет. Нажали старую кнопку. Игнорируем")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ты какашка!")
        return False

    if Game_classes.players_list[call.from_user.id] == None:
        print("Игрока нет. Нажали старую кнопку. Игнорируем")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="o_O")
        return False

    if game is not None:
        print("Игра найдена.")
        found = True
        actor = None
        try:
            actor = game.player_dict[call.from_user.id]
        except:
            print('ошибка')
            found = False
        if game.currentstate == game.gamestate[1] and found:
            if actor in game.fight.playerpool:
                if call.data[0:5] == 'power':
                    c_power= call.data[0:len(call.data) - len(str(game.fight.round))]
                    print(c_power)
                    print(Game_classes.powers[c_power])
                    actor.selectedpowers.append(Game_classes.powers[c_power])
        #actor.turn = 'move'
        #actor.fight.playerpool.remove(actor)
    if call.data == 'team1' or call.data == 'team1':
        playerchat_id = call.from_user.id
        player_name = call.from_user.first_name
        game.player_ids.append(playerchat_id)
        game.players.append(Game_classes.Player(playerchat_id, player_name, None, game))
        Game_classes.players_list[playerchat_id] = game
        print("Игрок добавлен в список. Выбрана команда " + str(call.data))
        # print("Что-то пошло не так " + str(call.data))
        if game is not None:
            print("Игра найдена.")
        if call.data == 'team1':
            # set_team(Game, call.data, )
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Вы присоединились к команде: " + game.team1.Name)
            print("Игрок вступил в команду: " + str(game.team1.Name))
        if call.data == 'team2':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Вы присоединились к команде: " + game.team2.Name)
            print("Игрок вступил в команду: " + str(game.team2.Name))


bot.polling(none_stop=True)
