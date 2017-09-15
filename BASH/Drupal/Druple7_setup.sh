#!/bin/bash
#
######################################################################
#
#	Name:		 	drupal7_install_script.sh
#	Author:			Chris Fedun 05/09/2017
#	Description:	install script Configuration for Drupal 7
#	Copyright (C) 2017  Christopher Fedun
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
######################################################################
if [[ $EUID > 0 ]]
  then echo 'Please run as root.'
  exit
fi
LOGFILE=/root/script.log
work_dir=$(pwd)
Setup_dir=/root/
IPTABLES=/sbin/iptables
IP6TABLES=/sbin/ip6tables
MODPROBE=/sbin/modprobe


function initial_dependencies
{
sudo apt-key adv --keyserver pgp.mit.edu --recv-keys 5072E1F5
echo "deb http://download.webmin.com/download/repository sarge contrib" >> /etc/apt/sources.list
wget http://www.webmin.com/jcameron-key.asc
sudo apt-key add jcameron-key.asc


apt-get update -q
apt-get upgrade -y -q
apt-get dist-upgrade -y -q
apt-get install -y -q debconf-utils sudo ipcalc
apt-get install pwgen curl git quotatool expect -y -q
}


function passwords
{
SQL_root_passwd="letmein"
#SQL_root_passwd=$(pwgen -s 20 1)
PHPMyAdmin_user_passwd=$(pwgen -s 20 1)
PHPMyAdmin_setup_passwd=$(pwgen -s 20 1)

drupaluser="drupal7e_dbuser"
drupaluser_passwd="letmein"
#drupaluser_passwd=$(pwgen -s 25 1)
drupal_DB="drupal7e_drupalville"

mkdir $Setup_dir\MYSQL
mkdir $Setup_dir\PHPMyAdmin
mkdir $Setup_dir\Drupal

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

touch $Setup_dir\Drupal/pass.txt
echo "user= $drupaluser" >> $Setup_dir\Drupal/pass.txt
echo "drupal_DB= $drupal_DB" >> $Setup_dir\Drupal/pass.txt
echo "passwd= $drupaluser_passwd" >> $Setup_dir\Drupal/pass.txt
chmod u=rw,go= $Setup_dir\Drupal/pass.txt
}

function install_func
{
####deb_conf#####
debconf-set-selections <<< "openssh-server  openssh-server/permit-root-login        boolean true"

debconf-set-selections <<< "mysql-server-5.7 mysql-server/root_password password $SQL_root_passwd"
debconf-set-selections <<< "mysql-server-5.7 mysql-server/root_password_again password $SQL_root_passwd"

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

##### OpenSSH/OpenSSL/OpenDKIM #####
apt-get install -y -q ssh openssl openssh-server \
openssh-client opendkim opendkim-tools

##### Apache and MYSQL Install #####
echo "[+] Installing Apache..."
#apt-get update -q 1> /dev/null
echo "[+] Installing MYSQL..."
apt-get install -q -y -o Dpkg::Options::="--force-confdef" \
-o Dpkg::Options::="--force-confold" apache2 mysql-server

##### PHP #####
echo "[+] Installing PHP..."
apt-get install php php-pear libapache2-mod-php php-cli php-mcrypt php-mysql -y -q


##### PHPMyAdmin #####
echo "[+] Installing PHPMyAdmin..."
apt-get install -q -y -o Dpkg::Options::="--force-confdef" \
-o Dpkg::Options::="--force-confold" phpmyadmin

##### Apache Config #####
# Enable Clean htaccess for Drupal ## Clean URLs
sed -ri "
	/<Directory \/var\/www\/>/ {
		N
			/\tOptions Indexes FollowSymLinks/ {
				N
					/\tAllowOverride None/ {
						s:(<Directory /var/www/>\n\tOptions Indexes FollowSymLinks\n\tAllowOverride) None:\1 All:
					}
			}
	}
" /etc/apache2/apache2.conf
#Enable the SSL encryption module and the Rewrite module
a2enmod rewrite ssl

#Enable the virtual host for HTTPS
a2ensite default-ssl
ufw allow in "Apache Full"
service apache2 reload


##### Drupal Install #####

mkdir ~/drupal
touch ~/drupal/drupaluser_passwd.txt
echo "$drupaluser_passwd" >> ~/drupal/drupaluser_passwd.txt
chmod u=rw,go= ~/drupal/drupaluser_passwd.txt
mkdir -p /var/www/html
cd /var/www/html
wget https://ftp.drupal.org/files/projects/drupal-7.56.tar.gz
tar --strip-components=1 -xvzf drupal-7.56.tar.gz

cp /var/www/html/sites/default/default.settings.php /var/www/html/sites/default/settings.php
chown -R www-data:www-data /var/www/

python $work_dir/Drupal7_setup.py /var/www/html/sites/default/settings.php $drupal_DB $drupaluser $drupaluser_passwd
}
#cd /var/www
function MySQL_setup
{
root_db_pass=$(cat /etc/.my.cnf | grep -o "password=.*" | cut -f2- -d=)
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

echo "[mysqld]" >> /etc/mysql/my.cnf
echo "innodb_large_prefix=true" >> /etc/mysql/my.cnf
echo "innodb_file_format=barracuda" >> /etc/mysql/my.cnf
echo "innodb_file_per_table=true" >> /etc/mysql/my.cnf
service mysql restart
##### Secure MYSQL
#expect $work_dir/mysql_secure.exp $SQL_root_passwd
}

function lab1
{
apt-get install libxss1 libappindicator1 libindicator7
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome*.deb
apt-get install gphpedit
}
function ip_tables
{

### Flush existing rules ###
echo "[+] Flushing existing iptables rules..."

$IPTABLES -F
$IPTABLES -F -t nat
$IPTABLES -X

### Load connection-tracking modules. ###
$MODPROBE ip_conntrack
$MODPROBE iptable_nat
$MODPROBE ip_conntrack_ftp
$MODPROBE ip_nat_ftp

##### CREATE LOG_DROP CHAIN ##### ### next create one per chain
echo "[+] Setting up LOG_DROP chain..."
$IPTABLES -N LOG_DROP
$IPTABLES -A LOG_DROP -p icmp -j LOG --log-prefix 'ICMP Block ' --log-ip-options
$IPTABLES -A LOG_DROP -p icmp -j DROP
$IPTABLES -A LOG_DROP -m conntrack --ctstate INVALID -j LOG --log-prefix "DROP INVALID " --log-ip-options --log-tcp-options
$IPTABLES -A LOG_DROP -m conntrack --ctstate INVALID -j DROP
$IPTABLES -A LOG_DROP -j LOG --log-prefix "DROP " --log-level 4 --log-ip-options --log-tcp-options
$IPTABLES -A LOG_DROP -j DROP

$IPTABLES -t mangle -N LOG_DROP
$IPTABLES -t mangle -A LOG_DROP -p icmp -j LOG --log-prefix 'ICMP Block ' --log-ip-options
$IPTABLES -t mangle -A LOG_DROP -p icmp -j DROP
$IPTABLES -t mangle -A LOG_DROP -m conntrack --ctstate INVALID -j LOG --log-prefix "DROP INVALID " --log-ip-options --log-tcp-options
$IPTABLES -t mangle -A LOG_DROP -m conntrack --ctstate INVALID -j DROP
$IPTABLES -t mangle -A LOG_DROP -j LOG --log-prefix "DROP " --log-level 4 --log-ip-options --log-tcp-options
$IPTABLES -t mangle -A LOG_DROP -j DROP

### Protection against port scanning ###
$IPTABLES -N port-scanning
$IPTABLES -A port-scanning -p tcp --tcp-flags SYN,ACK,FIN,RST RST -m limit --limit 1/s --limit-burst 2 -j RETURN
$IPTABLES -A port-scanning -j LOG --log-prefix "DROP Port-Scanning " --log-tcp-options --log-ip-options
$IPTABLES -A port-scanning -j DROP

##### INPUT chain #####
echo "[+] Setting up INPUT chain..."

### State tracking rules ###
$IPTABLES -A INPUT -m conntrack --ctstate INVALID -j LOG_DROP
$IPTABLES -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

### Protection against port scanning ###
$IPTABLES -A INPUT -p tcp --tcp-flags SYN,ACK,FIN,RST RST -j port-scanning



### ACCEPT rules ###
#$IPTABLES -A INPUT -i $IFACE_INT -p tcp -s $INT_NET --dport 22 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 21 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 25 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 43 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 80 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 443 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 53 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p udp --dport 53 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 123 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 943 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 10000 -m conntrack --ctstate NEW -j ACCEPT

# SMTP and SMTPS #
$IPTABLES -A INPUT -p tcp --dport 25 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 465 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 587 -m conntrack --ctstate NEW -j ACCEPT
# IMAP and IMAPS #
$IPTABLES -A INPUT -p tcp --dport 143 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 993 -m conntrack --ctstate NEW -j ACCEPT
# POP3 and POP3S #
$IPTABLES -A INPUT -p tcp --dport 110 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p tcp --dport 995 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A INPUT -p icmp --icmp-type echo-request -j ACCEPT

### Default INPUT LOG rule ###
$IPTABLES -A INPUT ! -i lo -j LOG_DROP

### Make sure that loopback traffic is accepted ###
$IPTABLES -A INPUT -i lo -j ACCEPT
$IP6TABLES -A INPUT -i lo -j ACCEPT

##### FORWARD chain #####
echo "[+] Setting up FORWARD chain..."

### State tracking rules ###
$IPTABLES -A FORWARD -m conntrack --ctstate INVALID -j LOG_DROP
$IPTABLES -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
### Default FORWARD LOG rule ###
$IPTABLES -A FORWARD ! -i lo -j LOG_DROP

##### OUTPUT chain #####
echo "[+] Setting up OUTPUT chain..."
### State tracking rules ###
$IPTABLES -A OUTPUT -m conntrack --ctstate INVALID -j LOG_DROP
$IPTABLES -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

### ACCEPT rules for allowing NEW connections out. ###
$IPTABLES -A OUTPUT -p tcp --dport 21 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p tcp --dport 43 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p tcp --dport 80 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p tcp --dport 443 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p tcp --dport 53 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p udp --dport 53 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p tcp --dport 123 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p udp --dport 123 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p tcp --sport 123 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p udp --sport 123 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p udp --dport 10000 -m conntrack --ctstate NEW -j ACCEPT

# SMTP and SMTPS #
$IPTABLES -A OUTPUT -p tcp --dport 25 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p tcp --dport 465 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p tcp --dport 587 -m conntrack --ctstate NEW -j ACCEPT
# IMAP and IMAPS #
$IPTABLES -A OUTPUT -p tcp --dport 143 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p tcp --dport 993 -m conntrack --ctstate NEW -j ACCEPT
# POP3 and POP3S #
$IPTABLES -A OUTPUT -p tcp --dport 110 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p tcp --dport 995 -m conntrack --ctstate NEW -j ACCEPT
$IPTABLES -A OUTPUT -p icmp --icmp-type echo-request -j ACCEPT

### Default OUTPUT LOG rule ###
$IPTABLES -A OUTPUT ! -o lo -j LOG_DROP

### Make sure that loopback traffic is accepted. ###
$IPTABLES -A OUTPUT -o lo -j ACCEPT
$IP6TABLES -A OUTPUT -o lo -j ACCEPT

##### Forwarding #####
echo "[+] Enabling IP forwarding..."
echo 1 > /proc/sys/net/ipv4/ip_forward

### Setting chain policy settings to DROP. ###
$IPTABLES -P INPUT DROP
$IPTABLES -P OUTPUT DROP
$IPTABLES -P FORWARD DROP
### This policy does not handle IPv6 traffic except to DROP it. ###
echo "[+] Disabling IPv6 traffic..."

$IP6TABLES -P INPUT DROP
$IP6TABLES -P OUTPUT DROP
$IP6TABLES -P FORWARD DROP


##### Persistent Firewall #####
echo "[+] Configuring Persistent Firewall..."

apt-get -q -y -o Dpkg::Options::="--force-confdef" \
-o Dpkg::Options::="--force-confold" install iptables-persistent
}




#####Main
export DEBIAN_FRONTEND=noninteractive

initial_dependencies
passwords
install_func
MySQL_setup
ip_tables


rm -- "$0"
exit