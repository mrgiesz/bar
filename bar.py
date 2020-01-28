# importing modules
import smbus
import time
import MySQLdb
import MFRC522
import OPi.GPIO as GPIO

from screen import *
from pyA20.gpio import gpio
from pyA20.gpio import port

# database configuration
db = MySQLdb.connect("localhost","<username>","<password>","<database>")
cursor = db.cursor()

# define GPIO Pins for the buttons
button1=port.PD14
button2=port.PC4

# Initialise GPIO
gpio.init()
gpio.setcfg(button1, gpio.INPUT)
gpio.pullup(button1, gpio.PULLUP)
gpio.setcfg(button2, gpio.INPUT)
gpio.pullup(button2, gpio.PULLUP)

# NFC reader stuff
continue_reading = True


# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

class product():
  def __init__(self,id,name,cost):
    self.id = id
    self.nr = id - 1
    self.name = name
    self.cost = cost
    self.fancy_name = "{:<7}".format(self.name)

class User():
  def __init__(self,id,name,badge_uid,wallet):
    self.id = id
    self.name = name
    self.badge_uid = badge_uid
    self.wallet = wallet

def display_info(text_list,display_time=0.1):
  text_list = [str(a) for a in text_list]
  lcd_string(text_list[0],LCD_LINE_1)
  lcd_string(text_list[1],LCD_LINE_2)
  time.sleep(display_time)

def display_main():
      # print to screen
    global selected_product
    global quantity

    line_text_1 = "Product   Aantal"
    line_text_2 = f"{selected_product.fancy_name}   {quantity}"
    display_info([line_text_1,line_text_2])



def main():
  # Database query's
  queries = {}
  queries["products"] = "SELECT * FROM products"
  queries["users"] = "SELECT * FROM users"
  queries["transaction"] = "INSERT INTO transactions(user_id,product_id,transaction_cost,transaction_amount) VALUES (%s,%s,%s,%s)"
  queries["substraction"] = "UPDATE users SET user_wallet = %s WHERE id = %s"
  queries["addition"] = "INSERT INTO register(user_id,register_amount,register_description) VALUES (%s,%s,%s)"

  # Main program block

  #variables
  global quantity
  quantity = 1
  vproductselection = 0


  # Get products from database
  cursor.execute(queries["products"])
  items = cursor.fetchall()

  productlist = {}
  # Put products in list
  for nr,(product_id,product_name,product_cost) in enumerate(items):
    productlist[nr] = product(product_id,product_name,product_cost)

  global selected_product
  selected_product = productlist[vproductselection]

  # Initialise display
  lcd_init()
  display_main()

  while True:

    #Variables

    # Start reading NFC
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    if status != MIFAREReader.MI_OK:
        time.sleep(0.1)
    if status == MIFAREReader.MI_OK:

        #Variables
        users = {}

        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # Get users details from SQL
        cursor.execute(queries["users"])
        items = cursor.fetchall()

        # put userinfo in list
        for user_id,user_name,user_badge,user_wallet in items:
          users[user_badge] = user(user_id,user_name,user_badge,user_wallet)

        # Get UID from badge in readable format
        current_id = "".join([str(a) for a in uid[0:4]])

        # Check if master card is present
        if current_id in users and users[current_id].name == "Master":

            money = 20
            while users[current_id].name == "Master" or current_id not in users:

                if gpio.input(button1) == 0:
                    money -=  1
                    time.sleep (.01)

                    if (money) < 0:
                      money = 50

                if gpio.input(button2) == 0:
                  money +=  1
                  time.sleep (.01)

                  if (money) > 50:
                    money = 1

                display_info(["OPWAARDEREN MET:",f"{money} EURO"])
                (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

                if status == MIFAREReader.MI_OK:
                  (status,uid) = MIFAREReader.MFRC522_Anticoll()
                temp_id = "".join([str(a) for a in uid[0:4]])

                if temp_id in users:
                  current_id = temp_id

            # variables

            current_user = users[current_id]
            current_saldo_float = current_user.user_wallet / 100
            nieuw_saldo = current_user.user_wallet + (money * 100)
            nieuw_saldo_float = nieuw_saldo / 100
            vsqlsubstrvar = nieuw_saldo,current_user.user_id
            vsqladdition = current_user.user_id,(money * 100),"added by terminal"

            # execute changes to sql database
            cursor.execute(queries["substraction"],\
                           vsqlsubstrvar)
            cursor.execute(queries["addition"],\
                          vsqladdition)
            db.commit()

            # display info on screen
            line_text_1 = f"Bedankt!"
            line_text_2 = f"{current_saldo_float} --> {nieuw_saldo_float}"
            display_info([line_text_1,line_text_2],3)
            vproductselection = 0
            quantity = 1
            display_main()

        elif current_id in users:
            #variables
            selected_user = users[current_id]
            current_user = users[current_id]
            current_saldo_float = current_user.user_wallet / 100
            nieuw_saldo = int(selected_user.user_wallet - (selected_product.product_cost*quantity))
            nieuw_saldo_float = float(nieuw_saldo/100)
            vsqlsubstrvar = nieuw_saldo,selected_user.user_id
            vsqltransvar = selected_user.user_id,\
                           selected_product.product_id,\
                           (selected_product.cost*quantity),\
                           quantity

            # commit changes to SQL server
            cursor.execute(queries["substraction"],\
                           vsqlsubstrvar)

            cursor.execute(queries["transaction"],\
                           vsqltransvar)
            db.commit()

            line_text_1 = f"Hallo {selected_user.user_name}"
            line_text_2 = f"{current_saldo_float} --> {nieuw_saldo_float}"
            display_info([line_text_1,line_text_2],3)

            # return to default value on screen and load default screen
            quantity = 1
            vproductselection = 0
            selected_product = productlist[vproductselection]
            display_main()

        else:
            # display UID of unkown card on screen
            line_text_1 = " Card unknown"
            line_text_2 = f"{current_id}"
            display_info([line_text_1,line_text_2],3)
            display_main()
            print(current_id)

        #reading button 1
    if gpio.input(button1) == 0:
            vproductselection += 1
            time.sleep (.01)
            if (vproductselection) > (len(productlist) - 1):
                vproductselection = 0
            selected_product = productlist[vproductselection]

            display_main()

        #reading button 2
    if gpio.input(button2) == 0:
            quantity +=  1
            time.sleep (.01)
            if (quantity) > 10:
                quantity = 1

            display_main()


if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
