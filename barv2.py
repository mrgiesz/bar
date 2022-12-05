import streamlit as st
import pymysql

# database configuration
db = pymysql.connect(host="10.9.33.8",
                     user="username",
                     password="password",
                     database="bar")
cursor = db.cursor()


class product():
    def __init__(self, id, name, cost, visible):
        self.id = id
        self.nr = id - 1
        self.name = name
        self.cost = cost
        self.visible = visible
        self.fancy_name = "{:<7}".format(self.name)


class user():
    def __init__(self, id, name, badge_uid, wallet):
        self.id = id
        self.name = name
        self.badge_uid = badge_uid
        self.wallet = wallet


# variables

# Database query's
queries = {}
queries["products"] = "SELECT * FROM products"
queries["users"] = "SELECT * FROM users"
queries[
    "transaction"] = "INSERT INTO transactions(user_id,product_id,transaction_cost,transaction_amount) VALUES (%s,%s,%s,%s)"
queries["substraction"] = "UPDATE users SET user_wallet = %s WHERE id = %s"
queries["addition"] = "INSERT INTO register(user_id,register_amount,register_description) VALUES (%s,%s,%s)"

# PRODUCT SECTION

# Get products from database
cursor.execute(queries["products"])
items = cursor.fetchall()

productlist = {}
# Put products in list
for nr, (product_id, product_name, product_cost, visible) in enumerate(items):
    productlist[nr] = product(product_id, product_name, product_cost, visible)

# USER SECTION

userlist = {}

# Get users details from SQL
cursor.execute(queries["users"])
items = cursor.fetchall()

# put userinfo in list
for user_id, user_name, user_badge, user_wallet in items:
    userlist[user_badge] = user(user_id, user_name, user_badge, user_wallet)

# Website stuff
#create session item
if 'selected_products' not in st.session_state:
    st.session_state.selected_products = {}

#run through productlist and create buttons and session items
for i in productlist:
    if productlist[i].visible == True:
        if 'selected_products'[productlist[i].id] not in st.session_state:
            st.session_state.selected_products[productlist[i].id] = 0

        if st.button(productlist[i].name):
            st.session_state.selected_products[productlist[i].id] += 1
            st.write(f"{productlist[i].name} has been pressed {st.session_state.selected_products[productlist[i].id]} times")

