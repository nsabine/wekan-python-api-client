import datetime

class Board:
    def __init__(self, api, board_data):
        self.api = api
        self.data = board_data
        self.id = board_data["_id"]
        self.title = board_data["title"]

    def get_cardslists(self, filter=''):
        cardslists_data = self.api.api_call("/api/boards/{}/lists".format(self.id))
        return [Cardslist(self.api, self, cardslist_data) for cardslist_data in cardslists_data if filter in cardslist_data["title"]]

    def get_cardslists_sorted(self, filter=''):
        cardslists = self.get_cardslists(filter)
        sorted_cardslists = []
        for cardslist in cardslists:
          cardslist_details = cardslist.get_details()
          sorted_cardslists.insert([cardslist_details['sort']], cardslist)
        return sort_cardslists

    def get_swimlanes(self, filter=''):
        swimlanes_data = self.api.api_call("/api/boards/{}/swimlanes".format(self.id))
        return [Swimlane(self.api, self, swimlane_data) for swimlane_data in swimlanes_data if filter in swimlane_data["title"]]

    def pprint(self, indent=0):
        pprint = "{}- {}".format("  "*indent, self.title)
        for cardslist in self.get_cardslists():
            pprint += "\n{}".format(cardslist.pprint(indent + 1))
        return pprint

    def htmlprint(self, indent=0):
        pprint = "{}- {} <br />".format("&nbsp;"*indent, self.title)
        for cardslist in self.get_cardslists_sorted():
            pprint += "{}".format(cardslist.htmlprint(indent + 1))
        return pprint


class Swimlane:
    def __init__(self, api, board, swimlane_data):
        self.api = api
        self.board = board
        self.data = swimlane_data
        self.id = swimlane_data["_id"]
        self.title = swimlane_data["title"]

    def get_cards(self, filter=''):
        cards_data = self.api.api_call("/api/boards/{}/swimlanes/{}/cards".format(self.board.id, self.id))
        return [Card(self.api, self, card_data) for card_data in cards_data if filter in card_data["title"]]

    def pprint(self, indent=0):
        pprint = "{}- {}".format("  " * indent, self.title)
        for cards in self.get_cards():
            pprint += "\n{}".format(cards.pprint(indent + 1))
        return pprint

    def htmlprint(self, indent=0):
        pprint = "{}- {} <br />".format("&nbsp;" * indent, self.title)
        for cards in self.get_cards():
            pprint += "{}".format(cards.htmlprint(indent + 1))
        return pprint


class Cardslist:
    def __init__(self, api, board, cardslist_data):
        self.api = api
        self.board = board
        self.data = cardslist_data
        self.id = cardslist_data["_id"]
        self.title = cardslist_data["title"]
        self.details = None

    def get_details(self):
        if self.details is None:
          self.details = self.api.api_call("/api/boards/{}/lists/{}".format(self.board.id, self.id))
        return self.details

    def get_cards(self, id=''):
        cards_data = self.api.api_call("/api/boards/{}/lists/{}/cards".format(self.board.id, self.id))
        return [Card(self.api, self, card_data) for card_data in cards_data if id in card_data['_id']]

    def pprint(self, indent=0):
        pprint = "{}- {}".format("  " * indent, self.title)
        for cards in self.get_cards():
            pprint += "\n{}".format(cards.pprint(indent + 1))
        return pprint

    def htmlprint(self, indent=0):
        pprint = "{}- {} <br />".format("&nbsp;" * indent, self.title)
        for cards in self.get_cards():
            pprint += "{}".format(cards.htmlprint(indent + 1))
        return pprint

    # default the swimlane to the first one in the list, if not specified
    def add_card(self, card_title, card_description="", user_id="", swimlane=""):
        if not swimlane:
            swimlane = self.board.get_swimlanes()[0].id
        else:
            swimlanes = self.board.get_swimlanes( swimlane )
            if swimlanes:
                swimlane = swimlanes[0]
            else:
                raise Exception("Swimlane '%s' couldn't be found!!" % swimlane)

        if not user_id:
            user_id = self.api.user_id

        data={
            'title': card_title,
            'description': card_description,
            'authorId': user_id,
            'swimlaneId': swimlane,
            }
        id = self.api.api_call("/api/boards/{}/lists/{}/cards".format(self.board.id, self.id), data)
        # return the newly created card
        return self.get_cards( id['_id'] )


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
        pprint = "{}- {} {}".format("  " * indent, self.title, self.api.api_url + "/b/" + self.cardslist.board.id + "/" + self.cardslist.board.title + "/" + self.id)
        cardinfo = self.get_card_info()
        if "dueAt" in cardinfo:
            pdate = datetime.datetime.strptime(cardinfo["dueAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
            pprint += "\n{}- Due at: {}".format("  " * (indent+1), pdate)
        for checklist in self.get_checklists():
            pprint += "\n{}".format(checklist.pprint(indent + 1))
        return pprint

    def htmlprint(self, indent=0):
        url = self.api.api_url + "/b/" + self.cardslist.board.id + "/" + self.cardslist.board.title + "/" + self.id
        pprint = "{}- <a href='{}'>{}</a> <br />".format("&nbsp;" * indent, url, self.title)
        cardinfo = self.get_card_info()
        if "dueAt" in cardinfo:
            pdate = datetime.datetime.strptime(cardinfo["dueAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
            pprint += "{}- Due at: {} <br />".format("&nbsp;" * (indent+1), pdate)
        for checklist in self.get_checklists():
            pprint += checklist.htmlprint(indent + 1)
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

    def htmlprint(self, indent=0):
        pprint = "{}- {} <br />".format("&nbsp;" * indent, self.title)
        for item in self.get_items():
            pprint += item.htmlprint(indent + 1)
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

    def htmlprint(self, indent=0):
        pprint = "{}- [{}] {} <br />".format("&nbsp;" * indent, "X" if self.is_finished else " ", self.title)
        return pprint
