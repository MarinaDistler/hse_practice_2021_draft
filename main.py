class Position:
    def __init__(self, who_wins=-1, winning_score=0):
        self.who_wins = who_wins  # 2 - это ничья
        self.winning_score = winning_score
        self.good_moves = []
        self.catching_the_take = -1
        self.catching_the_transmission = -1
        self.opponents_moves = {}


class PositionWithCountMoves(Position):
    def __init__(self, who_wins=-1, when_wins=-1, winning_score=0):
        self.who_wins = who_wins  # 2 - это ничья
        self.when_wins = when_wins
        self.winning_score = winning_score
        self.good_moves = []
        self.catching_the_take = -1
        self.catching_the_transmission = -1
        self.opponents_moves = {}


class OdnomastkaDurak:
    def __init__(self, cards, player):  # cards - текущие карты в формате массива
        self.moves_tree = {}  # уже просчитанные позиции
        self.pole = -1  # карта лежащая на столе
        self.cards = 0  # текущие карты в формате числа
        self.max_size = len(cards)
        self.size = len(cards)
        self.reverse = 0
        self.now_player = player
        self.names_of_cards = [i for i in range(1, self.size + 1)]
        self.degrees = [2 ** i for i in range(self.size + 2)]
        for i in range(self.size):
            self.cards += cards[i] * (2 ** i)
        self.cards += self.degrees[self.size]  # обозначает начало
        if player == 1:
            self.change_player()  # теперь считаем, что первый ходит игрок 0

    def who_wins(self):
        if self.moves_tree.get(self.cards) is None:
            self.build_moves_tree()
        return (self.moves_tree[self.cards].who_wins + self.reverse) % 2

    def winning_score(self):
        if self.moves_tree.get(self.cards) is None:
            self.build_moves_tree()
        return self.moves_tree[self.cards].winning_score

    def has_player_position(self, pos, player):
        return self.degrees[pos] & self.cards == player * self.degrees[pos]

    def change_player(self):
        self.cards = (self.degrees[self.size] - 1) ^ self.cards
        self.reverse = (self.reverse + 1) % 2

    def remove(self, pos1, pos2):
        if pos1 < pos2:
            pos1, pos2 = pos2, pos1
        self.cards = self.cards % self.degrees[pos1] + ((self.cards // self.degrees[pos1 + 1]) << pos1)
        self.cards = self.cards % self.degrees[pos2] + ((self.cards // self.degrees[pos2 + 1]) << pos2)
        self.size -= 2

    def add(self, pos, player):
        self.cards = self.cards % self.degrees[pos] + player * self.degrees[pos] + (
                (self.cards // self.degrees[pos]) << (pos + 1))
        self.size += 1

    def change_position(self, pos):
        if (2 ** pos) & self.cards == 0:
            self.cards += self.degrees[pos]
        else:
            self.cards -= self.degrees[pos]

    def is_end(self):
        return (self.cards == self.degrees[self.size] or self.cards == (self.degrees[self.size + 1] - 1))

    def move_by_computer(self):
        if self.moves_tree.get(self.cards) is None:
            self.build_moves_tree()
        if self.is_end():
            return -1  # игра окончена
        if self.pole == -1:
            self.now_player = (self.now_player + 1) % 2
            if self.moves_tree[self.cards].catching_the_take != -1:
                self.pole = self.moves_tree[self.cards].catching_the_take
                return self.names_of_cards[self.moves_tree[self.cards].catching_the_take]
            elif self.moves_tree[self.cards].catching_the_transmission != -1:
                self.pole = self.moves_tree[self.cards].catching_the_transmission
                return self.names_of_cards[self.moves_tree[self.cards].catching_the_transmission]
            else:
                self.pole = self.moves_tree[self.cards].good_moves[0]
                return self.names_of_cards[self.moves_tree[self.cards].good_moves[0]]
        else:
            t = self.pole
            self.pole = -1
            res = self.moves_tree[self.cards].opponents_moves[t]
            if res == t:
                self.now_player = (self.now_player + 1) % 2
                self.change_position(res)
                return self.names_of_cards[res]
            self.remove(res, t)
            res = self.names_of_cards[res]
            self.names_of_cards.remove(res)
            self.names_of_cards.remove(self.names_of_cards[t])
            self.change_player()
            return res

    def move_by_player(self, pos):  # код ошибки -1, pos=-1 значит принять карту
        if self.is_end():
            return -1  # игра окончена
        if pos == -1:
            if self.pole == -1:
                return -1
            else:
                self.now_player = (self.now_player + 1) % 2
                self.change_position(self.pole)
                self.pole = -1
        else:
            for i in range(self.size):
                if self.names_of_cards[i] == pos:
                    pos = i
                    break
            if self.pole == -1:
                if not self.has_player_position(pos, 0):
                    return -1
                self.pole = pos
                self.now_player = (self.now_player + 1) % 2
            else:
                if (not self.has_player_position(pos, 1)) or pos <= self.pole:
                    return -1
                self.remove(self.pole, pos)
                self.names_of_cards.remove(self.names_of_cards[pos])
                self.names_of_cards.remove(self.names_of_cards[self.pole])
                self.pole = -1
                self.change_player()
        return 0

    def write_position(self, p, pole, is_catching):
        self.moves_tree[self.cards].who_wins = p.who_wins
        self.moves_tree[self.cards].winning_score = p.winning_score
        self.moves_tree[self.cards].catching_the_transmission = -1
        self.moves_tree[self.cards].catching_the_take = -1
        self.moves_tree[self.cards].good_moves = [pole]
        if is_catching and self.moves_tree[self.cards].opponents_moves[pole] != pole:
            self.moves_tree[self.cards].catching_the_transmission = pole
        elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole:
            self.moves_tree[self.cards].catching_the_take = pole

    def build_moves_tree_opponent(self):
        pole = self.pole
        self.change_position(pole)
        self.pole = -1
        self.build_moves_tree()
        take = self.cards
        who_wins_take = self.moves_tree[take].who_wins
        self.change_position(pole)
        protection = pole  # карта защиты
        while protection < self.size and self.has_player_position(protection, 0):
            protection += 1
        p = Position(who_wins_take, self.moves_tree[take].winning_score)  # что получится после этого хода
        self.moves_tree[self.cards].opponents_moves[pole] = pole
        is_catching = False
        if protection != self.size:
            self.remove(pole, protection)
            self.change_player()  # из-за этого ответ кто выиграл для этого случая будет обратный
            transmission = self.cards
            self.build_moves_tree()
            self.change_player()
            self.add(pole, 0)
            self.add(protection, 1)
            is_catching = True
            who_wins_transmission = (self.moves_tree[transmission].who_wins + 1) % 2
            if who_wins_take == 0 and who_wins_transmission == 1:
                p = Position(1, self.moves_tree[transmission].winning_score)
                self.moves_tree[self.cards].opponents_moves[pole] = protection
            elif who_wins_take == 1 and who_wins_transmission == 1:
                p.who_wins = 1
                if self.moves_tree[take].winning_score < self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = protection
                elif self.moves_tree[take].winning_score == self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = pole
                    is_catching = False
            elif who_wins_take == 0 and who_wins_transmission == 0:
                p.who_wins = 0
                if self.moves_tree[take].winning_score > self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = protection
                elif self.moves_tree[take].winning_score == self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = pole
                    is_catching = False
        if self.moves_tree[self.cards].who_wins == -1 or (
                self.moves_tree[self.cards].who_wins == 1 and p.who_wins == 0):
            self.write_position(p, pole, is_catching)
        elif self.moves_tree[self.cards].who_wins == 0 and p.who_wins == 0:
            if self.moves_tree[self.cards].winning_score < p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[self.cards].winning_score == p.winning_score:
                self.moves_tree[self.cards].good_moves.append(pole)
                if is_catching and self.moves_tree[self.cards].opponents_moves[pole] == protection:
                    self.moves_tree[self.cards].catching_the_transmission = pole
                elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole and \
                        self.moves_tree[self.cards].catching_the_take == -1:
                    self.moves_tree[self.cards].catching_the_take = pole
        elif self.moves_tree[self.cards].who_wins == 1 and p.who_wins == 1:
            if self.moves_tree[self.cards].winning_score > p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[self.cards].winning_score == p.winning_score:
                self.moves_tree[self.cards].good_moves.append(pole)
                if is_catching and self.moves_tree[self.cards].opponents_moves[pole] == protection:
                    self.moves_tree[self.cards].catching_the_transmission = pole
                elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole and \
                        self.moves_tree[self.cards].catching_the_take == -1:
                    self.moves_tree[self.cards].catching_the_take = pole

    def build_moves_tree(self):
        if not self.moves_tree.get(self.cards) is None:
            return
        if self.cards == self.degrees[self.size]:  # проверить случай ничьи 01
            self.moves_tree[self.cards] = Position(1, self.size)
            return
        if self.cards == (self.degrees[self.size + 1] - 1):
            self.moves_tree[self.cards] = Position(0, self.size)
            return
        self.moves_tree[self.cards] = Position()
        for i in range(self.size):
            if self.has_player_position(i, 0):
                self.pole = i
                self.build_moves_tree_opponent()
        self.pole = -1

    def print(self):
        copy_cards = self.cards
        cards = [0] * self.size
        i = 0
        while copy_cards != 0 and i < self.size:
            cards[i] = (copy_cards % 2 + self.reverse) % 2
            copy_cards //= 2
            i += 1
        ind = 0
        j = 0
        for i in range(self.size):
            kol = 0
            while self.names_of_cards[i] != j + 1:
                kol += 1
                j += 1
            j += 1
            if i == 0:
                cards = [' '] * kol + cards
            else:
                cards = cards[:ind] + [' '] * kol + cards[ind:]
            ind += kol + 1
        kol = 0
        while self.max_size >= j + 1:
            kol += 1
            j += 1
        cards = cards + [' '] * kol
        if self.pole == -1:
            return cards
        else:
            return self.pole + 1, cards


class OdnomastkaDurakWithCountMoves(OdnomastkaDurak):
    def when_wins(self):
        if self.moves_tree.get(self.cards) is None:
            self.build_moves_tree()
        return self.moves_tree[self.cards].when_wins

    def write_position(self, p, pole, is_catching):
        self.moves_tree[self.cards].who_wins = p.who_wins
        self.moves_tree[self.cards].when_wins = p.when_wins
        self.moves_tree[self.cards].winning_score = p.winning_score
        self.moves_tree[self.cards].catching_the_transmission = -1
        self.moves_tree[self.cards].catching_the_take = -1
        self.moves_tree[self.cards].good_moves = [pole]
        if is_catching and self.moves_tree[self.cards].opponents_moves[pole] != pole:
            self.moves_tree[self.cards].catching_the_transmission = pole
        elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole:
            self.moves_tree[self.cards].catching_the_take = pole

    def build_moves_tree_opponent(self):
        pole = self.pole
        self.change_position(pole)
        self.pole = -1
        self.build_moves_tree()
        take = self.cards
        who_wins_take = self.moves_tree[take].who_wins
        self.change_position(pole)
        protection = pole  # карта защиты
        while protection < self.size and self.has_player_position(protection, 0):
            protection += 1
        is_catching = False
        p = PositionWithCountMoves(who_wins_take, self.moves_tree[take].when_wins + 1,
                                   self.moves_tree[take].winning_score)  # что получится после этого хода
        self.moves_tree[self.cards].opponents_moves[pole] = pole
        if protection != self.size:
            self.remove(pole, protection)
            self.change_player()  # из-за этого ответ кто выиграл для этого случая будет обратный
            transmission = self.cards
            self.build_moves_tree()
            self.change_player()
            self.add(pole, 0)
            self.add(protection, 1)
            is_catching = True
            who_wins_transmission = (self.moves_tree[transmission].who_wins + 1) % 2
            if who_wins_take == 0 and who_wins_transmission == 1:
                p = PositionWithCountMoves(1, self.moves_tree[transmission].when_wins + 1,
                                           self.moves_tree[transmission].winning_score)
                self.moves_tree[self.cards].opponents_moves[pole] = protection
            elif who_wins_take == 1 and who_wins_transmission == 1:
                p.who_wins = 1
                if self.moves_tree[take].winning_score < self.moves_tree[transmission].winning_score:
                    p.when_wins = self.moves_tree[transmission].when_wins + 1
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = protection
                elif self.moves_tree[take].winning_score == self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    if self.moves_tree[transmission].when_wins < self.moves_tree[take].when_wins:
                        p.when_wins = self.moves_tree[transmission].when_wins + 1
                        self.moves_tree[self.cards].opponents_moves[pole] = protection
                    if self.moves_tree[transmission].when_wins == self.moves_tree[take].when_wins:
                        is_catching = False
            elif who_wins_take == 0 and who_wins_transmission == 0:
                p.who_wins = 0
                if self.moves_tree[take].winning_score > self.moves_tree[transmission].winning_score:
                    p.when_wins = self.moves_tree[transmission].when_wins + 1
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = protection
                elif self.moves_tree[take].winning_score == self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    if self.moves_tree[transmission].when_wins > self.moves_tree[take].when_wins:
                        p.when_wins = self.moves_tree[transmission].when_wins + 1
                        self.moves_tree[self.cards].opponents_moves[pole] = protection
                    if self.moves_tree[transmission].when_wins == self.moves_tree[take].when_wins:
                        is_catching = False
        if self.moves_tree[self.cards].who_wins == -1 or (
                self.moves_tree[self.cards].who_wins == 1 and p.who_wins == 0):
            self.write_position(p, pole, is_catching)
        elif self.moves_tree[self.cards].who_wins == 0 and p.who_wins == 0:
            if self.moves_tree[self.cards].winning_score < p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[self.cards].winning_score == p.winning_score:
                if self.moves_tree[self.cards].when_wins > p.when_wins:
                    self.write_position(p, pole, is_catching)
                elif self.moves_tree[self.cards].when_wins == p.when_wins:
                    self.moves_tree[self.cards].good_moves.append(pole)
                    if is_catching and self.moves_tree[self.cards].opponents_moves[pole] == protection:
                        self.moves_tree[self.cards].catching_the_transmission = pole
                    elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole and \
                            self.moves_tree[self.cards].catching_the_take == -1:
                        self.moves_tree[self.cards].catching_the_take = pole
        elif self.moves_tree[self.cards].who_wins == 1 and p.who_wins == 1:
            if self.moves_tree[self.cards].winning_score > p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[self.cards].winning_score == p.winning_score:
                if self.moves_tree[self.cards].when_wins < p.when_wins:
                    self.write_position(p, pole, is_catching)
                elif self.moves_tree[self.cards].when_wins == p.when_wins:
                    self.moves_tree[self.cards].good_moves.append(pole)
                    if is_catching and self.moves_tree[self.cards].opponents_moves[pole] == protection:
                        self.moves_tree[self.cards].catching_the_transmission = pole
                    elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole and \
                            self.moves_tree[self.cards].catching_the_take == -1:
                        self.moves_tree[self.cards].catching_the_take = pole

    def build_moves_tree(self):
        if not self.moves_tree.get(self.cards) is None:
            return
        if self.cards == self.degrees[self.size]:  # проверить случай ничьи 01
            self.moves_tree[self.cards] = PositionWithCountMoves(1, 0, self.size)
            return
        if self.cards == (self.degrees[self.size + 1] - 1):
            self.moves_tree[self.cards] = PositionWithCountMoves(0, 0, self.size)
            return
        self.moves_tree[self.cards] = PositionWithCountMoves()
        for i in range(self.size):
            if self.has_player_position(i, 0):
                self.pole = i
                self.build_moves_tree_opponent()
        self.pole = -1


class OdnomastkaD_Durak(OdnomastkaDurak):
    def who_wins(self):
        if self.moves_tree.get(self.cards) is None:
            self.build_moves_tree()
        if self.winning_score() == 0:
            return 2
        return (self.moves_tree[self.cards].who_wins + self.reverse) % 2


class OdnomastkaD_DurakWithCountMoves(OdnomastkaDurakWithCountMoves):
    def who_wins(self):
        if self.moves_tree.get(self.cards) is None:
            self.build_moves_tree()
        if self.moves_tree[self.cards].who_wins == 2:
            return 2
        return (self.moves_tree[self.cards].who_wins + self.reverse) % 2

    def build_moves_tree_opponent(self):
        pole = self.pole
        self.change_position(pole)
        self.pole = -1
        self.build_moves_tree()
        take = self.cards
        who_wins_take = self.moves_tree[take].who_wins
        self.change_position(pole)
        protection = pole  # карта защиты
        while protection < self.size and self.has_player_position(protection, 0):
            protection += 1
        is_catching = False
        p = PositionWithCountMoves(who_wins_take, self.moves_tree[take].when_wins + 1,
                                   self.moves_tree[take].winning_score)  # что получится после этого хода
        if who_wins_take == 2:
            p.when_wins = -1
        self.moves_tree[self.cards].opponents_moves[pole] = pole
        if protection != self.size:
            self.remove(pole, protection)
            self.change_player()  # из-за этого ответ кто выиграл для этого случая будет обратный
            transmission = self.cards
            self.build_moves_tree()
            self.change_player()
            self.add(pole, 0)
            self.add(protection, 1)
            is_catching = True
            who_wins_transmission = (self.moves_tree[transmission].who_wins + 1) % 2
            if self.moves_tree[transmission].who_wins == 2:
                who_wins_transmission = 2
            if (who_wins_take == 0 or who_wins_take == 2) and who_wins_transmission == 1:
                p = PositionWithCountMoves(who_wins_transmission, self.moves_tree[transmission].when_wins + 1,
                                           self.moves_tree[transmission].winning_score)
                self.moves_tree[self.cards].opponents_moves[pole] = protection
            elif who_wins_take == 0 and who_wins_transmission == 2:
                p = PositionWithCountMoves(2, -1, 0)
                self.moves_tree[self.cards].opponents_moves[pole] = protection
            elif who_wins_take == 1 and who_wins_transmission == 1:
                p.who_wins = 1
                if self.moves_tree[take].winning_score < self.moves_tree[transmission].winning_score:
                    p.when_wins = self.moves_tree[transmission].when_wins + 1
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = protection
                elif self.moves_tree[take].winning_score == self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    if self.moves_tree[transmission].when_wins < self.moves_tree[take].when_wins:
                        p.when_wins = self.moves_tree[transmission].when_wins + 1
                        self.moves_tree[self.cards].opponents_moves[pole] = protection
                    if self.moves_tree[transmission].when_wins == self.moves_tree[take].when_wins:
                        is_catching = False
            elif who_wins_take == 0 and who_wins_transmission == 0:
                p.who_wins = 0
                if self.moves_tree[take].winning_score > self.moves_tree[transmission].winning_score:
                    p.when_wins = self.moves_tree[transmission].when_wins + 1
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[self.cards].opponents_moves[pole] = protection
                elif self.moves_tree[take].winning_score == self.moves_tree[transmission].winning_score:
                    p.winning_score = self.moves_tree[transmission].winning_score
                    if self.moves_tree[transmission].when_wins > self.moves_tree[take].when_wins:
                        p.when_wins = self.moves_tree[transmission].when_wins + 1
                        self.moves_tree[self.cards].opponents_moves[pole] = protection
                    if self.moves_tree[transmission].when_wins == self.moves_tree[take].when_wins:
                        is_catching = False
            elif who_wins_take == 2 and who_wins_transmission == 2:
                is_catching = False
        if self.moves_tree[self.cards].who_wins == -1 or (
                self.moves_tree[self.cards].who_wins == 1 and (p.who_wins == 0 or p.who_wins == 2)) or (
                self.moves_tree[self.cards].who_wins == 2 and p.who_wins == 0):
            self.write_position(p, pole, is_catching)
        elif self.moves_tree[self.cards].who_wins == 0 and p.who_wins == 0:
            if self.moves_tree[self.cards].winning_score < p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[self.cards].winning_score == p.winning_score:
                if self.moves_tree[self.cards].when_wins > p.when_wins:
                    self.write_position(p, pole, is_catching)
                elif self.moves_tree[self.cards].when_wins == p.when_wins:
                    self.moves_tree[self.cards].good_moves.append(pole)
                    if is_catching and self.moves_tree[self.cards].opponents_moves[pole] == protection:
                        self.moves_tree[self.cards].catching_the_transmission = pole
                    elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole and \
                            self.moves_tree[self.cards].catching_the_take == -1:
                        self.moves_tree[self.cards].catching_the_take = pole
        elif self.moves_tree[self.cards].who_wins == 1 and p.who_wins == 1:
            if self.moves_tree[self.cards].winning_score > p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[self.cards].winning_score == p.winning_score:
                if self.moves_tree[self.cards].when_wins < p.when_wins:
                    self.write_position(p, pole, is_catching)
                elif self.moves_tree[self.cards].when_wins == p.when_wins:
                    self.moves_tree[self.cards].good_moves.append(pole)
                    if is_catching and self.moves_tree[self.cards].opponents_moves[pole] == protection:
                        self.moves_tree[self.cards].catching_the_transmission = pole
                    elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole and \
                            self.moves_tree[self.cards].catching_the_take == -1:
                        self.moves_tree[self.cards].catching_the_take = pole
        elif self.moves_tree[self.cards].who_wins == 2 and p.who_wins == 2:
            self.moves_tree[self.cards].good_moves.append(pole)
            if is_catching and self.moves_tree[self.cards].opponents_moves[pole] == protection:
                self.moves_tree[self.cards].catching_the_transmission = pole
            elif is_catching and self.moves_tree[self.cards].opponents_moves[pole] == pole and \
                    self.moves_tree[self.cards].catching_the_take == -1:
                self.moves_tree[self.cards].catching_the_take = pole

    def build_moves_tree(self):
        if not self.moves_tree.get(self.cards) is None:
            return
        if self.size == 0:
            self.moves_tree[self.cards] = PositionWithCountMoves(2, -1, 0)
            return
        if self.cards == self.degrees[self.size]:  # проверить случай ничьи 01
            self.moves_tree[self.cards] = PositionWithCountMoves(1, 0, self.size)
            return
        if self.cards == (self.degrees[self.size + 1] - 1):
            self.moves_tree[self.cards] = PositionWithCountMoves(0, 0, self.size)
            return
        self.moves_tree[self.cards] = PositionWithCountMoves()
        for i in range(self.size):
            if self.has_player_position(i, 0):
                self.pole = i
                self.build_moves_tree_opponent()
        self.pole = -1


class OdnomastkaDurakWithWeights(OdnomastkaDurak):
    def __init__(self, cards, player, weights):  # cards - текущие карты в формате массива, weights - массив весов
        self.moves_tree = {}  # уже просчитанные позиции
        self.pole = -1  # карта лежащая на столе
        self.cards = 0  # текущие карты в формате числа
        self.max_size = len(cards)
        self.size = len(cards)
        self.reverse = 0
        self.now_player = player
        self.weights = tuple(weights)
        self.names_of_cards = [i for i in range(1, self.size + 1)]
        self.degrees = [2 ** i for i in range(self.size + 2)]
        for i in range(self.size):
            self.cards += cards[i] * (2 ** i)
        self.cards += self.degrees[self.size]  # обозначает начало
        if player == 1:
            self.change_player()  # теперь считаем, что первый ходит игрок 0

    def who_wins(self):
        if self.moves_tree.get((self.cards, self.weights)) is None:
            self.build_moves_tree()
        return (self.moves_tree[(self.cards, self.weights)].who_wins + self.reverse) % 2

    def winning_score(self):
        if self.moves_tree.get((self.cards, self.weights)) is None:
            self.build_moves_tree()
        return self.moves_tree[(self.cards, self.weights)].winning_score

    def remove(self, pos1, pos2):
        if pos1 < pos2:
            pos1, pos2 = pos2, pos1
        self.cards = self.cards % self.degrees[pos1] + ((self.cards // self.degrees[pos1 + 1]) << pos1)
        self.cards = self.cards % self.degrees[pos2] + ((self.cards // self.degrees[pos2 + 1]) << pos2)
        self.weights = self.weights[:pos2] + self.weights[pos2 + 1:pos1] + self.weights[pos1 + 1:]
        self.size -= 2

    def add(self, pos1, player1, weight1, pos2, player2, weight2):  # pos1 < pos2
        self.cards = self.cards % self.degrees[pos1] + player1 * self.degrees[pos1] + (
                (self.cards // self.degrees[pos1]) << (pos1 + 1))
        self.cards = self.cards % self.degrees[pos2] + player2 * self.degrees[pos2] + (
                (self.cards // self.degrees[pos2]) << (pos2 + 1))
        self.weights = self.weights[:pos1] + (weight1,) + self.weights[pos1:]
        self.weights = self.weights[:pos2] + (weight2,) + self.weights[pos2:]
        self.size += 2

    def move_by_computer(self):
        if self.moves_tree.get((self.cards, self.weights)) is None:
            self.build_moves_tree()
        if self.is_end():
            return -1  # игра окончена
        now = (self.cards, self.weights)
        if self.pole == -1:
            self.now_player = (self.now_player + 1) % 2
            if self.moves_tree[now].catching_the_take != -1:
                self.pole = self.moves_tree[now].catching_the_take
                return self.names_of_cards[self.moves_tree[now].catching_the_take]
            elif self.moves_tree[now].catching_the_transmission != -1:
                self.pole = self.moves_tree[now].catching_the_transmission
                return self.names_of_cards[self.moves_tree[now].catching_the_transmission]
            else:
                self.pole = self.moves_tree[now].good_moves[0]
                return self.names_of_cards[self.moves_tree[now].good_moves[0]]
        else:
            t = self.pole
            self.pole = -1
            res = self.moves_tree[now].opponents_moves[t]
            if res == t:
                self.now_player = (self.now_player + 1) % 2
                self.change_position(res)
                return self.names_of_cards[res]
            self.remove(res, t)
            res = self.names_of_cards[res]
            self.names_of_cards.remove(res)
            self.names_of_cards.remove(self.names_of_cards[t])
            self.change_player()
            return res

    def write_position(self, p, pole, is_catching):
        now = (self.cards, self.weights)
        self.moves_tree[now].who_wins = p.who_wins
        self.moves_tree[now].winning_score = p.winning_score
        self.moves_tree[now].catching_the_transmission = -1
        self.moves_tree[now].catching_the_take = -1
        self.moves_tree[now].good_moves = [pole]
        if is_catching and self.moves_tree[now].opponents_moves[pole] != pole:
            self.moves_tree[now].catching_the_transmission = pole
        elif is_catching and self.moves_tree[now].opponents_moves[pole] == pole:
            self.moves_tree[now].catching_the_take = pole

    def build_moves_tree_opponent(self):
        now = (self.cards, self.weights)
        pole = self.pole
        self.change_position(pole)
        self.pole = -1
        self.build_moves_tree()
        take = (self.cards, self.weights)
        self.change_position(pole)
        protection = pole  # карта защиты
        p = Position(self.moves_tree[take].who_wins, self.moves_tree[take].winning_score)  # что получится после этого хода
        self.moves_tree[now].opponents_moves[pole] = pole
        is_catching = False
        has_equal = False
        while protection + 1 < self.size:
            protection += 1
            if self.has_player_position(protection, 1):
                w1, w2 = self.weights[pole], self.weights[protection]
                self.remove(pole, protection)
                self.change_player()  # из-за этого ответ кто выиграл для этого случая будет обратный
                transmission = (self.cards, self.weights)
                self.build_moves_tree()
                self.change_player()
                self.add(pole, 0, w1, protection, 1, w2)
                who_wins_transmission = (self.moves_tree[transmission].who_wins + 1) % 2
                if self.moves_tree[take].who_wins == who_wins_transmission and \
                        self.moves_tree[take].winning_score == self.moves_tree[transmission].winning_score:
                    has_equal = True
                if p.who_wins == 0 and who_wins_transmission == 1:
                    p = Position(1, self.moves_tree[transmission].winning_score)
                    self.moves_tree[now].opponents_moves[pole] = protection
                elif p.who_wins == 1 and who_wins_transmission == 1 and\
                        abs(p.winning_score) < abs(self.moves_tree[transmission].winning_score):
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[now].opponents_moves[pole] = protection
                elif p.who_wins == 0 and who_wins_transmission == 0 and \
                        abs(p.winning_score) > abs(self.moves_tree[transmission].winning_score):
                    p.winning_score = self.moves_tree[transmission].winning_score
                    self.moves_tree[now].opponents_moves[pole] = protection
                if p.who_wins != self.moves_tree[take].who_wins or \
                        p.winning_score != self.moves_tree[take].winning_score or not has_equal:
                    is_catching = True
        if self.moves_tree[now].who_wins == -1 or (
                self.moves_tree[now].who_wins == 1 and p.who_wins == 0):
            self.write_position(p, pole, is_catching)
        elif self.moves_tree[now].who_wins == 0 and p.who_wins == 0:
            if self.moves_tree[now].winning_score < p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[now].winning_score == p.winning_score:
                self.moves_tree[now].good_moves.append(pole)
                if is_catching and self.moves_tree[now].opponents_moves[pole] != pole:
                    self.moves_tree[now].catching_the_transmission = pole
                elif is_catching and self.moves_tree[now].opponents_moves[pole] == pole and \
                        self.moves_tree[now].catching_the_take == -1:
                    self.moves_tree[now].catching_the_take = pole
        elif self.moves_tree[now].who_wins == 1 and p.who_wins == 1:
            if self.moves_tree[now].winning_score > p.winning_score:
                self.write_position(p, pole, is_catching)
            elif self.moves_tree[now].winning_score == p.winning_score:
                self.moves_tree[now].good_moves.append(pole)
                if is_catching and self.moves_tree[now].opponents_moves[pole] != pole:
                    self.moves_tree[now].catching_the_transmission = pole
                elif is_catching and self.moves_tree[now].opponents_moves[pole] == pole and \
                        self.moves_tree[now].catching_the_take == -1:
                    self.moves_tree[now].catching_the_take = pole

    def build_moves_tree(self):
        now = (self.cards, self.weights)
        if not self.moves_tree.get(now) is None:
            return
        if self.cards == self.degrees[self.size]:
            if sum(self.weights) < 0:
                self.moves_tree[now] = Position(0, sum(self.weights))
                return
            self.moves_tree[now] = Position(1, sum(self.weights))
            return
        if self.cards == (self.degrees[self.size + 1] - 1):
            if sum(self.weights) < 0:
                self.moves_tree[now] = Position(1, sum(self.weights))
                return
            self.moves_tree[now] = Position(0, sum(self.weights))
            return
        self.moves_tree[now] = Position()
        for i in range(self.size):
            if self.has_player_position(i, 0):
                self.pole = i
                self.build_moves_tree_opponent()
        self.pole = -1


class OdnomastkaD_DurakWithWeights(OdnomastkaDurakWithWeights):
    def who_wins(self):
        if self.moves_tree.get((self.cards, self.weights)) is None:
            self.build_moves_tree()
        if self.winning_score() == 0:
            return 2
        return (self.moves_tree[(self.cards, self.weights)].who_wins + self.reverse) % 2



def generate(pos, n, my_input):
    if len(pos) == n:
        for i in pos:
            my_input.write(i + ' ')
        my_input.write('\n')
        return
    mpos = pos + ['0']
    generate(mpos, n, my_input)
    mpos[-1] = '1'
    generate(mpos, n, my_input)


def main_print2():
    my_input = open('input_all.txt', 'w')
    for i in range(1, 13):
        generate([], i, my_input)
    my_input.close()


def main_print3():
    my_input = open('input_all.txt', 'r')
    output = open('output_all_d_durak.txt', 'w')
    for i in my_input:
        vector = list(map(int, i.split()))
        d = OdnomastkaD_Durak(vector, 0)
        output.write(str(d.who_wins()) + ' ')
        # output.write(str(d.when_wins())+' ')
        output.write(str(d.winning_score()) + ' ')
        for i in d.moves_tree[d.cards].good_moves:
            output.write(str(i + 1) + ' ')
        if d.moves_tree[d.cards].catching_the_take == -1:
            output.write("нет ")
        else:
            output.write(str(d.moves_tree[d.cards].catching_the_take + 1) + ' ')
        if d.moves_tree[d.cards].catching_the_transmission == -1:
            output.write("нет ")
        else:
            output.write(str(d.moves_tree[d.cards].catching_the_transmission + 1) + ' ')
        output.write('\n')
    my_input.close()
    output.close()


def main_check():
    my_input = open('input_all.txt', 'r')
    my_input1 = open('output_all_d_durak.txt', 'r')
    a1 = my_input.readlines()
    a2 = my_input1.readlines()
    for i in range(len(a1)):
        if i % 100 == 0:
            print(i)
        vector = list(map(int, a1[i].split()))
        d = OdnomastkaD_Durak(vector, 0)
        #d = OdnomastkaDurak(vector, 0)
        # t = str(d.who_wins()) + ' ' + str(d.when_wins()) + ' ' + str(d.winning_score()) + ' '
        t = str(d.who_wins()) + ' ' + str(d.winning_score()) + ' '
        #for j in d.moves_tree[(d.cards, d.weights)].good_moves:
        for j in d.moves_tree[d.cards].good_moves:
            t = t + str(j + 1) + ' '
        '''
        if d.moves_tree[(d.cards, d.weights)].catching_the_take == -1:
            t += "нет "
        else:
            t += str(d.moves_tree[(d.cards, d.weights)].catching_the_take + 1) + ' '
        if d.moves_tree[(d.cards, d.weights)].catching_the_transmission == -1:
            t += "нет "
        else:
            t += str(d.moves_tree[(d.cards, d.weights)].catching_the_transmission + 1) + ' '
        t += '\n'
        '''
        if d.moves_tree[d.cards].catching_the_take == -1:
            t += "нет "
        else:
            t += str(d.moves_tree[d.cards].catching_the_take + 1) + ' '
        if d.moves_tree[d.cards].catching_the_transmission == -1:
            t += "нет "
        else:
            t += str(d.moves_tree[d.cards].catching_the_transmission + 1) + ' '
        t += '\n'

        if t != a2[i]:
            print(a1[i], '\n', t, a2[i])
        #if t.split()[2:] != a2[i].split()[2:]:
        #    print(a1[i], '\n', t, a2[i])
    print('all good')
    my_input1.close()
    my_input.close()


def main_print():
    my_input = open('input.txt', 'r')
    output = open('output.txt', 'w')
    ind = 1
    for i in my_input:
        vector, weight = i.split(',')[0], i.split(',')[1]
        vector = list(map(int, vector.split()))
        weight = list(map(int, weight.split()))
        d = OdnomastkaDurakWithWeights(vector, 0, weight)
        output.write(str(ind) + ') Вектор карт: ' + str(d.print()) + '\n')
        output.write('Вектор весов: ' + str(d.weights) + '\n')
        output.write('Первый игрок: 0\n')
        output.write('Кто выиграет: ' + str(d.who_wins()) + '\n')
        output.write('С счетом: ' + str(d.winning_score()) + '\n')
        output.write("Оптимальные ходы: ")
        now = (d.cards, d.weights)
        for i in d.moves_tree[now].good_moves:
            output.write(str(i + 1) + ' ')
        output.write('\n')
        if d.moves_tree[now].catching_the_take == -1:
            output.write("Ловля взятие: нет\n")
        else:
            output.write("Ловля взятие: " + str(d.moves_tree[now].catching_the_take + 1) + '\n')
        if d.moves_tree[now].catching_the_transmission == -1:
            output.write("Ловля пропускание: нет\n")
        else:
            output.write("Ловля пропускание: " +
                         str(d.moves_tree[now].catching_the_transmission + 1) + '\n')
        output.write('\n')

        d = OdnomastkaDurakWithWeights(vector, 1, weight)
        output.write('Вектор карт: ' + str(d.print()) + '\n')
        output.write('Вектор весов: ' + str(d.weights) + '\n')
        output.write('Первый игрок: 1\n')
        output.write('Кто выиграет: ' + str(d.who_wins()) + '\n')
        output.write('С счетом: ' + str(d.winning_score()) + '\n')
        output.write("Оптимальные ходы: ")
        now = (d.cards, d.weights)
        for i in d.moves_tree[now].good_moves:
            output.write(str(i + 1) + ' ')
        output.write('\n')
        if d.moves_tree[now].catching_the_take == -1:
            output.write("Ловля взятие: нет\n")
        else:
            output.write("Ловля взятие: " + str(d.moves_tree[now].catching_the_take + 1) + '\n')
        if d.moves_tree[now].catching_the_transmission == -1:
            output.write("Ловля пропускание: нет\n")
        else:
            output.write("Ловля пропускание: " +
                         str(d.moves_tree[now].catching_the_transmission + 1) + '\n')
        output.write('\n')
        ind += 1
    my_input.close()
    output.close()


def main_game():
    vector = list(map(int, input("Вектор карт: ").split()))
    weight = list(map(int, input("Вектор весов: ").split()))
    player = int(input("Первый игрок: "))
    # type = int(input("Дурак - 0 или Д-Дурак - 1: "))
    # type2 = int(input("Компъютер/Компъютер - 0 или Игрок/Компъютер - 1: "))
    type = 0
    type2 = 0
    if type == 1:
        d = OdnomastkaD_DurakWithWeights(vector, player, weight)
    else:
        d = OdnomastkaDurakWithWeights(vector, player, weight)
        d2 = OdnomastkaDurak(vector, player)
    print('Кто выиграет:', d.who_wins())
    print('С счетом', d.winning_score())
    if type2 == 0:
        print("Оптимальные ходы: ", end='')
        for i in d.moves_tree[(d.cards, d.weights)].good_moves:
            print(i + 1, end=' ')
        print()
        if d.moves_tree[(d.cards, d.weights)].catching_the_take  == -1:
            print("Ловля взятие: нет")
        else:
            print("Ловля взятие:", d.moves_tree[(d.cards, d.weights)].catching_the_take + 1)
        if d.moves_tree[(d.cards, d.weights)].catching_the_transmission == -1:
            print("Ловля пропускание: нет")
        else:
            print("Ловля пропускание:", d.moves_tree[(d.cards, d.weights)].catching_the_transmission + 1)

        d2 = OdnomastkaDurak(vector, player)
        print('Кто выиграет:', d2.who_wins())
        print('С счетом', d2.winning_score())
        print("Оптимальные ходы: ", end='')
        for i in d2.moves_tree[d2.cards].good_moves:
            print(i + 1, end=' ')
        print()
        print("Ловля взятие", d2.moves_tree[d2.cards].catching_the_take + 1)
        print("Ловля пропускание", d2.moves_tree[d2.cards].catching_the_transmission + 1)

        if d2.moves_tree[d2.cards].good_moves != d.moves_tree[(d.cards, d.weights)].good_moves:
            print("!!!!")

        pole = d.move_by_computer()
        while pole != -1:
            print("карта:", pole)
            print(d.print())
            pole = d.move_by_computer()
    else:
        print("-1 значит принять карту, компьютер играет за 0, -2 значит сходить компьютеру")
        print(d.print())
        while not d.is_end():
            if d.now_player == 0:
                pole = d.move_by_computer()
                print("карта:", pole)
                print(d.print())
            else:
                t = int(input())
                if t == -2:
                    pole = d.move_by_computer()
                    print("карта:", pole)
                else:
                    d.move_by_player(t)
                print(d.print())
            print(d.names_of_cards)


if __name__ == '__main__':
    main_check()
    #main_game()
    #main_print()
# 0 1 0 1  0 1 0 1  0 1 0 1  0 1 0 1  0 1
# 0 1 0 1  0 1 0 1  0 1 0 1  0 1 0 1  0 1 0 1

# 0 1 0 1  0 1 0 1  0 1 0 1  0 1 0 1  0 1 0 1  0 1 0 1  0 1
# 1 1 1 1  1 1 1 1  1 1 1 1  1 1 1 1  1 1 1 1   1 1 1 1   1 1
# 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1
# Вектор весов: 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16
# 12 - 10 сек, 14 - минута


'''
 0 1 0 1 0 1 1 0
 1 0 1 1 1 0 0 0
 0 1 1 0 0 1
 1 1 0 0 1 1 0 1
 0 1 1 0 1 0 0
 0 1 1 0
 0 1 0 0 1 0 1
 0 0 1 0 1 0 1 1
 0 0 1 1 0 1 0
'''