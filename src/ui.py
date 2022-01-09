from agents.informationBroker import InformationBrokerAgent
from agents.user import UserAgent
from agents.brokerDirectory import BrokerDirectoryAgent

from agents.productVault import ProductVaultAgent

from utils import Location

users = []
active_user = None
next_user_id = 0

main_options = [('Zmień/dodaj użytkownika', change_user, None),
                ('Sprawdź powiadomienia', print_notifications, None),
                ('Dodaj zgłoszenie', add_request, None),
                ('Wyświetl listę własnych zgłoszeń', retrieve_requests, True),
                ('Wyświetl listę wszystkich zgłoszeń', retrieve_requests, False)
                ('Dodaj produkt do banku', add_product_to_vault, None),
                ('Wyświetl produkty w banku', retrieve_vault_products, None),
                ('Zarządzanie systemem agentów', manage_services, None)]

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
    print(prompt)
    for i, option in enumerate(options):
        print(i, option[0])
    chosen = custom_input()

    return (i, options[chosen])

def execute_from_menu(options):
    (_, chosen) = print_menu(options)
    if chosen[2] is None:
        chosen[1]()
    else:
        chosen[1](chosen[2])

def change_user():
    options = [('Dodaj nowego użytkownika', add_new_user, None)]
    for i, user in enumerate(users):
        options.append((user[0], set_active_user, i))
    execute_from_menu(options)

def add_new_user():
    global next_user_id, users
    username = input('Podaj nazwę użytkownika:')
    x = custom_input('Podaj współrzędną x użytkownika', float)
    y = custom_input('Podaj współrzędną y użytkownika', float)
    useragent1 = UserAgent('user' + str(next_user_id) + '@localhost', "aasd")
    next_user_id += 1
    useragent1.start()
    users.append((username, useragent1))
    useragent1.set('location', Location(x, y))
    useragent1.add_behaviour(UserAgent.ServicesReqBehav())

def set_active_user(num):
    global users, active_user
    active_user = users[num][1]

def print_notifications():
    global active_user
    active_user.get('notifications')

def choose_category(vault=False):
    global active_user
    parameter = if vault 'vault_categories' else 'categories'
    category_list = None
    while category_list is None:
        category_list = active_user.get(parameter)
    (i, _) = print_menu(category_list, 'Wybierz kategorię z listy:')
    return i

def add_request():
    global active_user
    category = choose_category()
    comment = input('Dodaj komentarz do zgłoszenia: ')
    active_user.set('new_request', {'category': category, 'comment': comment})
    active_user.add_behaviour(UserAgent.AddRequestBehav())

def retrieve_requests(own=False):
    global active_user
    active_user.add_behaviour(UserAgent.AskForRequestsBehav())
    requests = None
    while requests is None:
        requests = active_user.get('requests')

    options = []
    for request in requests:
        if request['username'] == active_user.jid:
            if own:
                options.append(str(request), cancel_request, request['id'])
        else:
            if not own:
                options.append(str(request), accept_request, request['id'])

    execute_from_menu(options)

def cancel_request(id):
    global active_user
    active_user.set("request_to_cancel", id)
    active_user.add_behaviour(UserAgent.CancelBehav())

def accept_request(id):
    global active_user
    active_user.set("request_to_accept", id)
    active_user.add_behaviour(UserAgent.AcceptBehav())







