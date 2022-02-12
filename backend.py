from pywebio.input import *
from pywebio.output import *
from pywebio import start_server

import pymysql


class Userclass:
    def __init__(self, id, name, badge_uid, wallet):
        self.id = id
        self.name = name
        self.badge_uid = badge_uid
        self.wallet = wallet


class Productclass:
    def __init__(self, id, name, cost, visible):
        self.id = id
        self.nr = id - 1
        self.name = name
        self.cost = cost
        self.visible = visible


# general queries
queries = {"users": "INSERT INTO users(user_name,user_badge,user_wallet) VALUES (%s,%s,0)",
           "transaction": "INSERT INTO register(user_id,register_amount,register_description) VALUES (%i,%i,%s)",
           "inventory": "INSERT INTO inventory(product_id,inventory_amount) VALUES (%s,%s)",
           "register": "INSERT INTO register(user_id,register_description,register_amount) VALUES (%s,%s,%s)",
           "get_users": "SELECT * FROM users",
           "get_products": "SELECT * FROM products",
           "add_product": "INSERT INTO products(product_name,product_cost) VALUES (%s, %s)"
           }


def add_expense(db, cursor, users):
    userlist = []
    userid = {}
    for i in users:
        userlist.append(users[i].name)
        userid[users[i].name] = users[i].id

    user = input_group(
        "Choose user who made the expense",
        [
            radio(
                "Who made the expense?",
                name="name",
                options=userlist
                ,
            ),
        ],
    )
    data = input_group(
        "Expense details",
        [
            input("What store?",
                  name="store",
                  type=TEXT
                  ),
            input("What is the amount?",
                  name="amount",
                  type=FLOAT
                  ),
        ],
    )
    add_to_db(db, cursor, "register", (userid[user['name']], data['store'], data['amount'] * 100))


def main():
    # display main button screen
    adminscreen()


def get_products(db, cursor):
    # Get products from database
    cursor.execute(queries["get_products"])
    items = cursor.fetchall()
    productlist = {}
    # Put products in list
    for nr, (product_id, product_name, product_cost, product_visible) in enumerate(items):
        productlist[nr] = Productclass(product_id, product_name, product_cost, product_visible)
    return productlist


def get_users(db, cursor):
    # Get users details from SQL
    cursor.execute(queries["get_users"])
    items = cursor.fetchall()
    users = {}
    # put userinfo in list
    for user_id, user_name, user_badge, user_wallet in items:
        users[user_badge] = Userclass(user_id, user_name, user_badge, user_wallet)
    return users


def add_to_db(db, cursor, querie, variables):
    cursor = db.cursor()
    cursor.execute(queries[querie], variables)


def btn_click(btn_val):
    # initiate db connection:
    db = pymysql.connect(host="10.9.33.8", user="python_user", password="python_password", db="bar2", )
    db.autocommit(True)
    cursor = db.cursor()

    users = get_users(db, cursor)
    productlist = get_products(db, cursor)
    if btn_val == 'Add products to inventory':
        add_inventory(db, cursor, productlist)
    if btn_val == 'Add expense':
        add_expense(db, cursor, users)
    if btn_val == 'Add new user':
        add_user(db, cursor)
    if btn_val == 'Change username':
        change_username(db, cursor, users)
    if btn_val == 'Change costs':
        change_products(db, cursor, productlist)
    if btn_val == "Change visibility":
        change_product_visibility(db, cursor, productlist)
    if btn_val == "Add new product":
        add_product(db, cursor)


def adminscreen():
    put_table([
        ['Catogories', 'options'],

        ['Products', put_buttons(['Add new product',
                                  'Change costs',
                                  'Change visibility'
                                  ],
                                 onclick=btn_click)],

        ['users', put_buttons(['Add new user',
                               'Change username'
                               ],
                              onclick=btn_click)],

        ['management', put_buttons(['Add expense',
                                    'Add products to inventory'
                                    ],
                                   onclick=btn_click)],
    ])


def convert_hex_to_str(badgenumber):
    badgenumberstr = ''
    for i in badgenumber.split(sep=':'):
        badgenumberstr = badgenumberstr + str(int(i, 16))
    return badgenumberstr


def add_user(db, cursor):
    data = input_group(
        "Adding user, Please scan the nfc badge, and enter details",
        [
            input("What is your Name?",
                  name="name",
                  type=TEXT),
            input("What is the serial number in hex divided by :",
                  name="badgenumber_hex",
                  type=TEXT),
        ],
    )

    # converting hex to string
    try:
        data['badgenumber_hex'] = convert_hex_to_str(data['badgenumber_hex'])
        put_table([['name', data['name']], ['badgenumber', data['badgenumber_hex']]])
        add_to_db(db, cursor, 'users', [data['name'], data['badgenumber_hex']])
    except Exception as e:
        # popup('popup title', 'popup text content', size=PopupSize.SMALL, onclick=main())
        popup('Oops', [
            put_html('<h3>Badge serial number error</h3>'),
            f'html: please use the correct layout, example: AA:BB:3F:8F{e}',

            put_buttons(['back'], onclick=lambda _: close_popup())
        ])


def change_username(db, cursor, users):
    userlist = []
    userid = {}
    for i in users:
        userlist.append(users[i].name)
        userid[users[i].name] = users[i].id

    user = input_group(
        "Choose user who made the expense",
        [
            radio(
                "Who made the expense?",
                name="name",
                options=userlist
                ,
            ),
        ],
    )
    data = input_group(
        "Expense details",
        [
            input("What's the new name?",
                  name="newname",
                  type=TEXT),

        ],
    )

    querie = f"UPDATE `users` SET `user_name` = '{data['newname']}' " \
             f"WHERE `users`.`user_id` = '{userid[user['name']]}'"

    cursor.execute(querie)


def add_inventory(db, cursor, productlist):
    products = []
    for i in productlist:
        products.append(input(productlist[i].name,
                              name=str(productlist[i].id),
                              type=NUMBER,
                              id=productlist[i].id))

    data = input_group(
        "Enter amount of each product you are adding to the bar", products,
    )
    for i in data:
        if data[i]:
            add_to_db(db, cursor, "inventory", (i, data[i]))


def change_products(db, cursor, productlist):
    products = []
    for i in productlist:
        products.append(input(productlist[i].name,
                              name=str(productlist[i].id),
                              type=NUMBER,
                              id=productlist[i].id,
                              placeholder=productlist[i].cost))

    data = input_group(
        "Enter the price for the products", products,
    )
    for i in data:
        if data[i]:
            querie = f"UPDATE `products` SET `product_cost` = '{data[i]}' " \
                     f"WHERE `products`.`product_id` = '{i}'"

            cursor.execute(querie)


def change_product_visibility(db, cursor, productlist):
    products = []
    for i in productlist:
        products.append(radio(productlist[i].name,
                                            name=str(productlist[i].id),
                                            options=[True, False],
                                            id=productlist[i].id,
                                            value=productlist[i].visible))

    data = input_group(
        "Choose 1 for visible, 0 for invisible", products,
    )
    print(data)
    for i in data:
        print(i)
        if data[i]:
            querie = f"UPDATE `products` SET `product_visible` = '1' WHERE `products`.`product_id` = '{i}' "
            cursor.execute(querie)
        if not data[i]:
            querie = f"UPDATE `products` SET `product_visible` = '0' WHERE `products`.`product_id` = '{i}' "
            cursor.execute(querie)


def add_product(db, cursor):
    data = input_group(
        "product details",
        [
            input("Name?", name="name", type=TEXT),
            input("Price", name="cost", type=NUMBER),
        ],
    )
    add_to_db(db, cursor, 'add_product', (data['name'], data['cost']))

def main_screen(db, cursor, productlist):


    put_buttons([
        dict(label=productlist[i].name, value=productlist[i].id, color='success')
        for i in productlist
    ], onclick=btn_click)



if __name__ == '__main__':
    #start_server(main, port=8080)
    main()
