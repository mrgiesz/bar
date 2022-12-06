import streamlit as st
import pymysql
from collections import defaultdict

st.set_page_config(layout="wide")

# database configuration
db = pymysql.connect(host="10.9.33.8",
                     user="username",
                     password="password",
                     database="bar")
cursor = db.cursor()

# Classes
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
queries["transaction"] = "INSERT INTO transactions(user_id,product_id,transaction_cost,transaction_amount) VALUES (%s,%s,%s,%s)"
queries["substraction"] = "UPDATE users SET user_wallet = %s WHERE id = %s"
queries["addition"] = "INSERT INTO register(user_id,register_amount,register_description) VALUES (%s,%s,%s)"

# PRODUCT SECTION
# Get products from database
cursor.execute(queries["products"])
items = cursor.fetchall()

# dict containing all the products
productlist = {}
# Put products in list
for nr, (product_id, product_name, product_cost, visible) in enumerate(items):
    productlist[nr] = product(product_id, product_name, product_cost, visible)

# USER SECTION

# Get users details from SQL
cursor.execute(queries["users"])
items = cursor.fetchall()

# dict containing all the users
userlist = {}

# put userinfo in list
for user_id, user_name, user_badge, user_wallet in items:
    userlist[user_badge] = user(user_id, user_name, user_badge, user_wallet)

# Website stuff
# column stuff
col1, col2, col3 = st.columns(3)

#create session item
if 'selected_products' not in st.session_state:
    st.session_state.selected_products = defaultdict(lambda: 0)

with col1:
    st.title("knoppenbende"
             )
#run through productlist and create buttons and session items
for i in productlist:
    if productlist[i].visible:
        with col1:
            if st.button(productlist[i].name):
                st.session_state.selected_products[productlist[i].id] += 1
                if st.session_state.selected_products[productlist[i].id] > 1:
                    st.balloons()

with col2:
    st.title("session state")
    st.write(st.session_state)
