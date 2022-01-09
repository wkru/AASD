from typing import Optional

from agents.informationBroker import InformationBrokerAgent
from agents.user import UserAgent
from agents.brokerDirectory import BrokerDirectoryAgent

from agents.productVault import ProductVaultAgent

from misc.review import Token

from utils import Location

users = []
active_user: Optional[UserAgent] = None
next_user_id = 0
new_user_added = False


def custom_input(prompt='Wpisz numer', cls=int):
    while True:
        inp = input(prompt + ': ')
        try:
            res = cls(inp)
            break
        except:
            print('Wpisz poprawną liczbę.')

    return res


def print_menu(options, prompt='Wybierz dostępną opcję:'):
    print('\n' + prompt)
    i = 0
    for i, option in enumerate(options):
        print(i, option[0])
    chosen = custom_input()

    if chosen >= len(options):
        print('Wpisany numer jest niepoprawny.')
        return print_menu(options, prompt)
    return i, options[chosen]


def execute_from_menu(options, prompt='Wybierz dostępną opcję:'):
    (_, chosen) = print_menu(options, prompt)

    if chosen[2] is None:
        chosen[1]()
    else:
        chosen[1](chosen[2])


def change_user():
    global new_user_added
    while True:
        new_user_added = False
        options = [('Dodaj nowego użytkownika', add_new_user, None)]
        for i, user in enumerate(users):
            options.append((user[0], _set_active_user, i))
        execute_from_menu(options)
        if not new_user_added:
            break


def add_new_user():
    global next_user_id, new_user_added
    new_user_added = True
    username = input('Podaj nazwę użytkownika: ')
    x = custom_input('Podaj współrzędną x użytkownika')
    y = custom_input('Podaj współrzędną y użytkownika')
    useragent1 = UserAgent('user' + str(next_user_id) + '@localhost', "aasd")
    next_user_id += 1
    useragent1.start()
    users.append((username, useragent1))
    useragent1.set('location', Location(x, y))
    useragent1.add_behaviour(UserAgent.ServicesReqBehav())


def _set_active_user(num):
    global active_user
    active_user = users[num][1]


def print_notifications():
    notifications = active_user.get('notifications')
    print(notifications)


def choose_category(vault=False):
    parameter = 'vault_categories' if vault else 'categories'
    if vault:
        active_user.add_behaviour(UserAgent.VaultCategoriesReqBehav())
    else:
        active_user.add_behaviour(UserAgent.CategoriesReqBehav())
    try:
        category_list = active_user.get('queue').get(timeout=5)
        options = []
        for category in category_list:
            options.append([category])
        (i, _) = print_menu(options, 'Wybierz kategorię z listy:')
        return i
    except:
        print('Błąd pobierania kategorii!')
        return None


def add_request():
    category = choose_category()
    if category is None:
        return
    comment = input('Dodaj komentarz do zgłoszenia: ')
    active_user.set('new_request', {'category': category, 'comment': comment})
    active_user.add_behaviour(UserAgent.AddRequestBehav())


def retrieve_requests(own=False):
    active_user.add_behaviour(UserAgent.AskForRequestsBehav())
    try:
        requests = active_user.get('queue').get(timeout=5)
    except:
        print('Błąd pobierania aktywnych zgłoszeń!')
        return

    options = []
    for request in requests:
        if request['username'] == str(active_user.jid):
            if own:
                options.append((str(request), _cancel_request, request['id']))
        else:
            if not own:
                options.append((str(request), _accept_request, request['id']))

    if not options:
        print('\nBrak aktywnych zgłoszeń.')
        return

    execute_from_menu(options, 'Wybierz zgłoszenie do anulowania:' if own else 'Wybierz zgłoszenie do zaakceptowania:')


def _cancel_request(id):
    active_user.set("request_to_cancel", id)
    active_user.add_behaviour(UserAgent.CancelBehav())


def _accept_request(id):
    active_user.set("request_to_accept", id)
    active_user.add_behaviour(UserAgent.AcceptBehav())


def add_product_to_vault():
    category = choose_category(vault=True)
    if category is None:
        return
    comment = input('Dodaj komentarz do dodawanego produktu: ')
    location = input('Dodaj lokalizację dodawanego produktu: ')
    active_user.set('vault_add_product_data', {'category': category, 'comment': comment, 'location': location})
    active_user.add_behaviour(UserAgent.VaultAddBehav())


def retrieve_vault_products():
    active_user.add_behaviour(UserAgent.VaultOffersReqBehav())
    try:
        products = active_user.get('queue').get(timeout=5)
    except:
        print('Błąd pobierania aktywnych zgłoszeń!')
        return

    options = []
    for product in products:
        options.append((str(products[product]), _get_product_from_vault, product))

    if not options:
        print('\nBrak produktów w banku.')
        return

    execute_from_menu(options, 'Wybierz produkt do pobrania:')


def _get_product_from_vault(id):
    active_user.set("vault_get_product_data", id)
    active_user.add_behaviour(UserAgent.VaultGetReqBehav())


def add_review():
    tokens = active_user.get('review_tokens')
    if not tokens:
        print('Brak tokenów. Nie można dodać recenzji.')
        return

    options = []
    for t in tokens.values():
        options.append((str(t), _send_review, t))

    execute_from_menu(options, 'Wybierz token do recenzji:')


def _send_review(token: Token):
    contents = input('Dodaj treść recenzji: ')
    rating = input('Dodaj ocenę recenzji: ')

    try:
        rating = int(rating)
    except ValueError:
        print('Nieprawidłowa ocena!')
        return

    print(token)
    review = {
        'contents': contents, 'rating': rating, 'request_id': token.request_id, 'from_': token.from_, 'to': token.to
    }

    active_user.set('kwargs', review)
    active_user.set('target_jid', token.to)
    active_user.add_behaviour(UserAgent.ReviewCreationReqBehav())


def print_reviews():
    options = []
    for username, user in users:
        options.append((str(user.jid), _print_reviews, str(user.jid)))

    execute_from_menu(options, 'Wybierz użytkownika do pobrania recenzji:')


def _print_reviews(jid: str):
    active_user.set('target_jid', jid)
    active_user.add_behaviour(UserAgent.ReviewsReqBehav())
    try:
        reviews = active_user.get('queue').get(timeout=5)
    except:
        print('Błąd pobierania aktywnych zgłoszeń!')
        return
    print(f'Lista recenzji użytkownika {jid}:')
    print(reviews)


def print_leaderboard():
    active_user.add_behaviour(UserAgent.LeaderboardReqBehav())
    try:
        leaderboard = active_user.get('queue').get(timeout=5)
    except:
        print('Błąd pobierania aktywnych zgłoszeń!')
        return
    print('Top pomagaczy')
    for i, user in enumerate(leaderboard):
        print(i+1, user)


def manage_services():
    pass


def run():
    global active_user
    main_options = [('Zmień/dodaj użytkownika', change_user, None),
                    ('Sprawdź powiadomienia', print_notifications, None),
                    ('Dodaj zgłoszenie', add_request, None),
                    ('Wyświetl listę własnych zgłoszeń', retrieve_requests, True),
                    ('Wyświetl listę zgłoszeń innych osób', retrieve_requests, False),
                    ('Dodaj produkt do banku', add_product_to_vault, None),
                    ('Wyświetl produkty w banku', retrieve_vault_products, None),
                    ('Wystaw recenzję', add_review, None),
                    ('Sprawdź recenzje użytkownika', print_reviews, None),
                    ('Wyświetl listę Top Pomagaczy', print_leaderboard, None),
                    ('Zarządzanie systemem agentów', manage_services, None),
                    ('Zakończ program', exit, 0)]

    while True:
        if active_user is None:
            change_user()
        else:
            execute_from_menu(main_options)
