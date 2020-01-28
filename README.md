# bar
rfid cashless payment system on orange pi pc

Installation Guide:

Flash rasbian to sd, login with user name root password 1234 change root password create user enable spi and i2c in armbian-config

vi /boot/armbianEnv.txt
add following to /boot/armbianEnv.txt
	overlays=i2c0 spi-spidev
	param_spidev_spi_bus=0
	param_spidev_max_freq=1000000

#create folder /scripts copy all neccesary scripts to that folder
screen.py (will control the 16x2 screen)
MFRC522.py (will control the nfc reader)


#updating and installing software:

apt update && apt upgrade -y
apt install ftp python3-dev python3-smbus python3-pip python3-mysqldb i2c-tools mariadb-server apache2 php php-mysqli php-mbstring autossh
pip3 install setuptools
pip3 install OPi.GPIO

#Run below script to configure mysql database
mysql_secure_installation (configure users and passwords)

#ADD MYSQL USER:
mysql
GRANT ALL ON *.* TO 'python'@'localhost' IDENTIFIED BY '<username>';
FLUSH PRIVILEGES;

INSTALL PHPMYADMIN
wget https://files.phpmyadmin.net/phpMyAdmin/5.0.0/phpMyAdmin-5.0.0-all-languages.zip
unzip phpMyAdmin-5.0.0-all-languages.zip /opt
mv /opt/phpMyAdmin-5.0.0-all-languages /opt/phpMyAdmin
sudo chown -Rfv www-data:www-data /opt/phpMyAdmin
vi /etc/apache2/sites-available/phpmyadmin.conf
paste the following:

<VirtualHost *:9000>
ServerAdmin webmaster@localhost
DocumentRoot /opt/phpMyAdmin
 
<Directory /opt/phpMyAdmin>
Options Indexes FollowSymLinks
AllowOverride none
Require all granted
</Directory>
ErrorLog ${APACHE_LOG_DIR}/error_phpmyadmin.log
CustomLog ${APACHE_LOG_DIR}/access_phpmyadmin.log combined
</VirtualHost>

sudo nano /etc/apache2/ports.conf
Add line: Listen 9000

sudo a2ensite phpmyadmin.conf
sudo systemctl restart apache2

#install needed python libraries
git clone https://github.com/zhaolei/WiringOP.git -b h3
    cd WiringOP
    sudo ./build
git clone https://github.com/duxingkei33/orangepi_PC_gpio_pyH3
    cd orangepi_PC_gpio_pyH3
    python3 setup.py install
git clone https://github.com/lthiery/SPI-Py.git
    cd SPI-Py

go to http://<ip>/phpmyadmin create database bar import sql file with backup database add user python with select/insert/update rights on the database


