#!/bin/bash
if [[ $EUID > 0 ]]
  then echo "Please run as root."
  exit
fi
work_dir=$(pwd)
Setup_dir=/root/

#apt-get install libapache2-mod-python
#apt-get install php5 php-pear

apt-get update -q
apt-get upgrade -y -q
apt-get dist-upgrade -y -q
apt-get install -y -q debconf-utils sudo ipcalc
apt-get install pwgen curl php5-cli git quotatool expect -y -q
sudo apt-key adv --keyserver pgp.mit.edu --recv-keys 5072E1F5

SQL_root_passwd=$(pwgen -s 20 1)
PHPMyAdmin_user_passwd=$(pwgen -s 20 1)
PHPMyAdmin_setup_passwd=$(pwgen -s 20 1)

root_db_pass=$(cat /etc/.my.cnf | grep -o "password=.*" | cut -f2- -d=)
drupaluser="drupal7e_dbuser"
drupaluser_passwd=$(pwgen -s 25 1)
drupal_DB="drupal7e_drupalville"

####deb_conf#####
debconf-set-selections <<< "openssh-server  openssh-server/permit-root-login        boolean true"

debconf-set-selections <<< "mysql-server-5.7 mysql-server/root_password password $SQL_root_passwd"
debconf-set-selections <<< "mysql-server-5.7 mysql-server/root_password_again password $SQL_root_passwd"
debconf-set-selections <<< "postfix postfix/protocols       select  all"
debconf-set-selections <<< "postfix postfix/chattr  boolean false"
debconf-set-selections <<< "postfix postfix/recipient_delim string  +"
debconf-set-selections <<< "postfix postfix/mynetworks      string  127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128"
debconf-set-selections <<< "postfix postfix/rfc1035_violation       boolean false"
debconf-set-selections <<< "postfix postfix/mailname        string  $host_name.$domain_name"
debconf-set-selections <<< "postfix postfix/main_mailer_type        select  Internet Site"
debconf-set-selections <<< "postfix postfix/procmail        boolean true"
debconf-set-selections <<< "postfix postfix/mailbox_limit   string  0"
debconf-set-selections <<< "postfix postfix/destinations    string  $host_name.$domain_name, localhost.$domain_name, , localhost"

debconf-set-selections <<< "iptables-persistent iptables-persistent/autosave_v4 boolean true"
debconf-set-selections <<< "iptables-persistent iptables-persistent/autosave_v6 boolean true"

debconf-set-selections <<< "phpmyadmin phpmyadmin/setup-password       password $PHPMyAdmin_setup_passwd"
debconf-set-selections <<< "phpmyadmin phpmyadmin/password-confirm     password $PHPMyAdmin_setup_passwd"
debconf-set-selections <<< "phpmyadmin phpmyadmin/app-password-confirm password $PHPMyAdmin_user_passwd"
debconf-set-selections <<< "phpmyadmin phpmyadmin/mysql/admin-pass     password $SQL_root_passwd"
debconf-set-selections <<< "phpmyadmin phpmyadmin/mysql/app-pass       password $PHPMyAdmin_user_passwd"
debconf-set-selections <<< "phpmyadmin phpmyadmin/database-type        select  mysql"
debconf-set-selections <<< "phpmyadmin phpmyadmin/setup-username       string  admin"
debconf-set-selections <<< "phpmyadmin phpmyadmin/dbconfig-install     boolean true"
debconf-set-selections <<< "phpmyadmin phpmyadmin/internal/skip-preseed        boolean false"
debconf-set-selections <<< "phpmyadmin phpmyadmin/dbconfig-upgrade     boolean true"
debconf-set-selections <<< "phpmyadmin phpmyadmin/mysql/admin-user     string  root"
debconf-set-selections <<< "phpmyadmin phpmyadmin/upgrade-backup       boolean true"
debconf-set-selections <<< "phpmyadmin phpmyadmin/db/dbname    string  phpmyadmin"
debconf-set-selections <<< "phpmyadmin phpmyadmin/db/app-user  string  phpmyadmin"
debconf-set-selections <<< "phpmyadmin phpmyadmin/purge        boolean false"
debconf-set-selections <<< "phpmyadmin phpmyadmin/dbconfig-reinstall   boolean false"
debconf-set-selections <<< "phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2"

mkdir $Setup_dir\MYSQL
mkdir $Setup_dir\PHPMyAdmin

touch /root/.my.cnf
echo '[client]' >> /root/.my.cnf
echo "password=$SQL_root_passwd" >> /root/.my.cnf
chmod u=rw,go= /root/.my.cnf

touch $Setup_dir\MYSQL/pass.txt
echo "$SQL_root_passwd" >> $Setup_dir\MYSQL/pass.txt
chmod u=rw,go= $Setup_dir\MYSQL/pass.txt

touch $Setup_dir\PHPMyAdmin/PHPMyAdmin.txt
echo "$PHPMyAdmin_user_passwd" >> $Setup_dir\PHPMyAdmin/PHPMyAdmin.txt
chmod u=rw,go= $Setup_dir\PHPMyAdmin/PHPMyAdmin.txt

touch $Setup_dir\PHPMyAdmin/PHPMyAdmin-setup_password.txt
echo "$PHPMyAdmin_setup_passwd" >> $Setup_dir\PHPMyAdmin/PHPMyAdmin-setup_password.txt
chmod u=rw,go= $Setup_dir\PHPMyAdmin/PHPMyAdmin-setup_password.txt

##### Apache and MYSQL Install #####
echo "[+] Installing Apache..."
#apt-get update -q 1> /dev/null
echo "[+] Installing MYSQL..."
apt-get install -q -y -o Dpkg::Options::="--force-confdef" \
-o Dpkg::Options::="--force-confold" apache2 mysql-server

##### PHP #####
echo "[+] Installing PHP..."
apt-get install php5 php-pear php5-mysql -y -q
mkdir ~/drupal
touch ~/drupal/drupaluser_passwd.txt
echo "$drupaluser_passwd" >> ~/drupal/drupaluser_passwd.txt
chmod u=rw,go= ~/drupal/drupaluser_passwd.txt
mkdir -p /var/www/html
cd /var/www/html

#cd /var/www
mysql --user=root --password=$root_db_pass << MYSQL_SCRIPT

CREATE DATABASE drupal CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER drupaluser@localhost IDENTIFIED BY '$drupaluser_passwd';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,INDEX,ALTER,CREATE TEMPORARY TABLES,LOCK TABLES ON drupal.* TO drupaluser@localhost;
 FLUSH PRIVILEGES;
 
CREATE DATABASE $drupal_DB CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER $drupaluser@localhost IDENTIFIED BY '$drupaluser_passwd';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,INDEX,ALTER,CREATE TEMPORARY TABLES,LOCK TABLES ON drupal7e_drupalville.* TO $drupaluser@localhost;
 FLUSH PRIVILEGES;
MYSQL_SCRIPT
 
wget https://ftp.drupal.org/files/projects/drupal-7.56.tar.gz
tar --strip-components=1 -xvzf drupal-7.56.tar.gz

cp /var/www/html/sites/default/default.settings.php /var/www/html/sites/default/settings.php
chown -R www-data:www-data /var/www/
#iptables -A INPUT -i lo -p tcp --dport 3306 -m conntrack --ctstate NEW -j ACCEPT
#iptables -A INPUT -i lo -p udp --dport 3306 -m conntrack --ctstate NEW -j ACCEPT
#
#iptables -A OUTPUT -o lo -p tcp --dport 3306 -m conntrack --ctstate NEW -j ACCEPT
#iptables -A OUTPUT -o lo -p udp --dport 3306 -m conntrack --ctstate NEW -j ACCEPT
#iptables -A INPUT -i lo -p tcp --dport 80 -m conntrack --ctstate NEW -j ACCEPT
#iptables -A OUTPUT -o lo -p tcp --dport 80 -m conntrack --ctstate NEW -j ACCEPT
#

echo "[mysqld]" >> /etc/mysql/my.cnf
echo "innodb_large_prefix=true" >> /etc/mysql/my.cnf
echo "innodb_file_format=barracuda" >> /etc/mysql/my.cnf
echo "innodb_file_per_table=true" >> /etc/mysql/my.cnf
service mysql restart

python $work_dir/Drupal7_setup.py /var/www/html/sites/default/settings.php $drupal_DB $drupaluser $drupaluser_passwd
