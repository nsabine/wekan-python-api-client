import datetime

class Board:
    def __init__(self, api, board_data):
        self.api = api
        self.data = board_data
        self.id = board_data["_id"]
        self.title = board_data["title"]

    def get_cardslists(self):
        cardslists_data = self.api.api_call("/api/boards/{}/lists".format(self.id))
        return [Cardslist(self.api, self, cardslist_data) for cardslist_data in cardslists_data]

    def pprint(self, indent=0):
        pprint = "{}- {}".format("  "*indent, self.title)
        for cardslist in self.get_cardslists():
            pprint += "\n{}".format(cardslist.pprint(indent + 1))
        return pprint


class Cardslist:
    def __init__(self, api, board, cardslist_data):
        self.api = api
        self.board = board
        self.data = cardslist_data
        self.id = cardslist_data["_id"]
        self.title = cardslist_data["title"]

    def get_cards(self):
        cards_data = self.api.api_call("/api/boards/{}/lists/{}/cards".format(self.board.id, self.id))
        return [Card(self.api, self, card_data) for card_data in cards_data]

    def pprint(self, indent=0):
        pprint = "{}- {}".format("  " * indent, self.title)
        for cards in self.get_cards():
            pprint += "\n{}".format(cards.pprint(indent + 1))
        return pprint


class Card:
    def __init__(self, api, cardslist, card_data):
        self.api = api
        self.cardslist = cardslist
        self.data = card_data
        self.id = card_data["_id"]
        self.title = card_data["title"]

    def get_card_info(self):
        info_data = self.api.api_call("/api/boards/{}/lists/{}/cards/{}".format(
            self.cardslist.board.id,
            self.cardslist.id,
            self.id))
        return info_data

    def get_checklists(self):
        checklists_data = self.api.api_call("/api/boards/{}/cards/{}/checklists".format(
            self.cardslist.board.id,
            self.id))
        return [Checklist(self.api, self, checklist_data) for checklist_data in checklists_data]

    def pprint(self, indent=0):
        pprint = "{}- {}".format("  " * indent, self.title)
        cardinfo = self.get_card_info()
        if "dueAt" in cardinfo:
            pdate = datetime.datetime.strptime(cardinfo["dueAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
            pprint += "\n{}- Due at: {}".format("  " * (indent+1), pdate)
        for checklist in self.get_checklists():
            pprint += "\n{}".format(checklist.pprint(indent + 1))
        return pprint


class Checklist:
    def __init__(self, api, card, checklist_data):
        self.api = api
        self.card = card
        self.data = checklist_data
        self.id = checklist_data["_id"]
        self.title = checklist_data["title"]

    def get_items(self):
        items_data = self.api.api_call("/api/boards/{}/cards/{}/checklists/{}".format(
            self.card.cardslist.board.id,
            self.card.id,
            self.id))
        return [ChecklistItem(self.api, self, item_data) for item_data in items_data["items"]]

    def pprint(self, indent=0):
        pprint = "{}- {}".format("  " * indent, self.title)
        for item in self.get_items():
            pprint += "\n{}".format(item.pprint(indent + 1))
        return pprint


class ChecklistItem:
    def __init__(self, api, checklist, item_data):
        self.api = api
        self.checklist = checklist
        self.data = item_data
        self.is_finished = item_data["isFinished"]
        self.title = item_data["title"]

    def pprint(self, indent=0):
        pprint = "{}- [{}] {}".format("  " * indent, "X" if self.is_finished else " ", self.title)
        return pprint
