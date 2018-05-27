import Game_classes
import config
import telebot
import threading
import time


types = telebot.types
bot = telebot.TeleBot(config.token)

'''
def get_game_from_chat(cid):
    try:
        return Main_classes.existing_games[cid]
    except KeyError:
        return None


def get_game_from_player(cid):
    try:
        return Main_classes.dict_players[cid]
    except KeyError:
        print('Игрок не найден!')
        return None


def send_inventory(player):
    keyboard = types.InlineKeyboardMarkup()
    for p in player.itemlist:
        Aviable = True
        if p.id[0:5] == 'iteme' and player.energy < 2:
            Aviable = False
        if Aviable:
            keyboard.add(types.InlineKeyboardButton(text=p.name, callback_data=str(p.id + str(player.fight.round))))
    keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('cancel')))
    bot.send_message(player.chat_id, 'Выберите предмет.', reply_markup=keyboard)
    
    
def send_skills(player):
    keyboard = types.InlineKeyboardMarkup()
    for p in player.itemlist:
        if not p.standart:
            keyboard.add(types.InlineKeyboardButton(text=p.name, callback_data=str(p.id + str(player.fight.round))))
    keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data=str('cancel')))
    bot.send_message(player.chat_id, 'Выберите навык.', reply_markup=keyboard) '''


def delete_game(Game):
    for p in Game.pending_players:
        try:
            del Game_classes.players_list[p.chat_id]
        except KeyError:
            pass
    del Game_classes.games_list[Game.cid]
    del Game


# Закончить набор игроков и начать сражение
def start_fight(cid):
    game = Game_classes.games_list[cid]
    game.waitingtimer.cancel()
    game.currentstate = game.gamestate[1]
    game.waitingtimer.cancel()
    t = threading.Thread(target=prepare_fight, args=[game])
    t.daemon = True
    t.start()


def prepare_fight(game):
    # Организация словаря
    game.player_dict = {p.chat_id: p for p in game.players}
    #game.currentstate = 'weapon'
    bot.send_message(game.cid, 'Время убивать!\n' \
                    '\n\n _В битве на выживание нельзя оставаться безучастным. Любой, кто не будет сражаться на твоей стороне - враг, которого ты должен сокрушить. \nСкрипторус Мунификантус_' \
        , parse_mode = 'markdown')
    for p in game.players:
        game.fight.activeplayers.append(p)
        p.team.actors.append(p)
    #какой нибудь раздатчик
    '''
    game.weaponcounter = len(game.players)
    game.waitings = True
    for p in game.players:
        get_weapon(p)
    timer = threading.Timer(90.0, game.change)
    timer.start()
    while game.weaponcounter > 0 and game.waitings is True:
        time.sleep(3)
    if game.weaponcounter == 0:
        bot.send_message(game.cid, 'Оружие выбрано.')
    else:
        for p in game.players:
            if p.weapon is None:
                p.weapon = Weapon_list.weaponlist[random.randint(0, len(Weapon_list.weaponlist) - 1)]
        bot.send_message(game.cid, 'Оружие выбрано или случайно распределено.')
    timer.cancel()
    '''
    game.currentstate = 'fighting'
    # Последняя подготовка
#    for p in game.players:
#        p.fight.string.add('Оружие ' + p.name + ' - ' + p.weapon.name)

    print('Красные - ' + ', '.join([p.name for p in game.team1.players]))
    print('Синие - ' + ', '.join([p.name for p in game.team2.players]))
    #game.fight.string.post(bot, 'Выбор оружия')

    game.startfight()


def fight_loop(game, fight):

    fight.team1 = game.team1
    fight.team2 = game.team2
    fight.team1.leader = game.team1.actors[0]
    fight.team2.leader = game.team2.actors[0]
    fight.actors = fight.aiplayers + fight.activeplayers
    for p in game.players:
        #if p.chat_id == 86190439:
            #p.abilities.append(special_abilities.Isaev)
            #special_abilities.Isaev.aquare(p.abilities, p)
        p.hp = p.maxhp
        p.Alive = True
        p.team.participators.append(p)
    while fight.team1.actors != [] and fight.team2.actors != [] and fight.round != 50:
        fight.string.add('Красные => array of Players(' + ', '.join([p.name for p in game.team1.actors]) + ')')
        fight.string.add('Синие => array of Players(' + ', '.join([p.name for p in game.team2.actors]) + ')')
        get_playerpool(fight)
        send_actions(fight)
        wait_response(fight)
        #manifest_actions(fight)
        #get_results(fight)
        #refresh_turn(fight)
        #kill_players(fight)
        fight.string.post(bot, 'Жалкая попытка одолеть соперника №' + str(fight.round))
    end(fight, game)
    delete_game(game)

def end(fight, game):
    bot.send_message(game.cid, "Игра окончена! Здесь будет проверка условий победы.")


# Собираем пул активных игроков
def get_playerpool(fight):
    fight.round += 1
    fight.fightstate = 'playerpool'
    for p in fight.activeplayers:
        if p.disabled:
            p.turn = 'disabled'
        elif p.alive:
            fight.playerpool.append(p)
        elif 'Zombie' in p.passive:
            if p.zombiecounter > 0:
                fight.playerpool.append(p)

# Рассылаем варианты действий
def send_actions(fight):
    for p in fight.actors:
        account_targets(p)
    for p in fight.playerpool:
        send_action(p, fight)
        print('Послан список действий для ' + p.name)

# Определяем список возможных целей
def account_targets(player):
    if player.team == player.fight.team1:
        player.targets = player.game.team2.actors
    elif player.team == player.game.team2:
        player.targets = player.game.team1.actors


# Описание вариантов действий
def send_action(p, fight):
    keyboard = types.InlineKeyboardMarkup()

    if not p.castready:
        keyboard.add(*[types.InlineKeyboardButton(text=power.name, callback_data=str(power.id) + str(fight.round))
                        for power in Game_classes.powerlist])
        callback_button2 = types.InlineKeyboardButton(text=u'\U0001F52E Каст', callback_data=str('start_magic' + str(fight.round)))
        keyboard.add(callback_button2)
    #else:
        callback_button_target = types.InlineKeyboardButton(text='Цель', callback_data=str('target' + str(fight.round)))
        keyboard.add(callback_button_target)
        callback_button_area = types.InlineKeyboardButton(text='Область', callback_data=str('area' + str(fight.round)))
        keyboard.add(callback_button_area)
        callback_button_selfcast = types.InlineKeyboardButton(text='На себя', callback_data=str('selfcast' + str(fight.round)))
        keyboard.add(callback_button_selfcast)
        callback_button_cancel = types.InlineKeyboardButton(text='Отмена', callback_data=str('cancel' + str(fight.round)))
        keyboard.add(callback_button_cancel)
    p.choicemessage = bot.send_message(p.chat_id, player_turn_info(p).string, reply_markup=keyboard)
    p.info.clear()


def player_turn_info(player):
    player.info.add(str(player.fight.round) + ' попытка')
    player.info.add(str(player.hp) + u'\U00002665' + '/ ' + str(player.maxhp) + ' ')
    return player.info


# Ожидание ответа
def wait_response(fight):
    fight.done = False
    fight.fightstate = 'waiting'
    print('Ждем хода: ')
    for n in fight.playerpool:
        print(n.name)
    timer = threading.Timer(120.0, timerd, [fight])
    timer.start()
    i = 1
    while fight.playerpool and fight.done is False:
        if len(fight.playerpool) == 1 and i == 1:
            i += 1
        time.sleep(5)
    if fight.done:
        for p in fight.playerpool:
            print('Удаляем ход ' + p.name)
            p.turn = 'skip' + str(fight.round)
            bot.edit_message_text(chat_id=p.chat_id, message_id=p.choicemessage.message_id,
                                  text=str(fight.round) + " попытка... ¯\_(ツ)_/¯ ")
        fight.playerpool = []
    timer.cancel()
    del timer


# Переключение счетчика
def timerd(fight):
    fight.done = True