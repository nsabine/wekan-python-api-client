from wekanapi import WekanApi

api_url = "https://..."
api = WekanApi(api_url, {"username": "...", "password": "..."}, )

boards = api.get_user_boards()

for board in boards:
    print(board.pprint())
