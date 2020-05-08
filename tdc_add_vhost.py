# coding: utf-8

import socket
from contextlib import closing
import argparse
import os.path as path
import os
import pwd
import shutil
import crypt
WEB_ROOT = '/var/www/'
DEFAULT_PHP = '7.4';
WORK_FOLDER = '/tmp/'
APACHE_SITES_FOLDER = '/etc/apache2/sites-available/'
FPM_FOLDER = '/etc/php/7.4/fpm/pool.d/'
PHP_FPM_VERSION = 'php7.4-fpm'


parser = argparse.ArgumentParser()
parser.add_argument('--login', help="login ")
parser.add_argument('--domain_primary', help="Domaine principal du site ")
parser.add_argument('--domain_other', help="Domaine secondaire du site ",  nargs='+')
parser.add_argument('--no_dns', required=False, help="Ajout l'entrée au fichier host", action="store_true")
parser.add_argument('--ssl', required=False, help="Active le https sur le site", action="store_true")
parser.add_argument('--force_ssl', required=False, help="Active une redirection vers le  https", action="store_true")
parser.add_argument('--create_db', required=False, action='store_true',  help='Create la base de donnée.')
parser.add_argument('--password',    help='mot de passe.')
parser.add_argument('--user',   help='utilisateur.')
parser.add_argument('--force', required=False, action='store_true' , help='Remove exist config if exist')
args = parser.parse_args()


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
port_fpm = find_free_port()


domain_primary = getattr(args, 'domain_primary')
domain_other = getattr(args, 'domain_other')
create_db = getattr(args, 'create_db')
no_dns = getattr(args, 'no_dns')
ssl = getattr(args, 'ssl')
force = getattr(args, 'force')
force_ssl = getattr(args, 'force_ssl')
password = getattr(args,'password')
user= getattr(args, 'user')
dir_name = domain_primary

# check if dir_name exists
if not path.exists(dir_name):
    dir_name = path.join(WEB_ROOT, dir_name)
if not path.exists(dir_name):
	os.mkdir(dir_name)
if not path.exists(dir_name):
    raise FileNotFoundError('The path does not exist: %s' % dir_name)


alias = "ServerAlias "
for i in domain_other: 
	alias = alias +" " +i


# Je créer un utilisateur linux associée au projet 
try:
    pwd.getpwnam(user)
except KeyError:
	encPass = crypt.crypt(password,"22")
	os.system("useradd -p "+encPass+ " -s "+ "/bin/bash "+ "-d "+ dir_name + " -m "+ " -c \""+ user+"\" " + user)



if create_db == 1 and user and user:
	sqlCreateUser =   "GRANT ALL PRIVILEGES ON "+user+".* TO "+user+"@localhost IDENTIFIED BY '"+ password+"' " 
	os.system("  sudo mysqladmin create " + user)
	os.system('mysql -e "'+sqlCreateUser+'"')


if no_dns ==1:
	file_object = open('/etc/hosts', 'a')
	file_object.write("127.0.0.1   " + domain_primary + "\n")
	for i in domain_other: 
	        file_object.write("127.0.0.1   " + i + "\n")
	file_object.close()


if not path.exists(WORK_FOLDER):
    os.mkdir(WORK_FOLDER)

extra = ""
if force_ssl == 1:
	extra = extra + "RewriteEngine On \n RewriteCond %{HTTPS} !=on \n RewriteRule ^(.*) https://"+domain_primary+"/$1 [R,L]"


vhost_str = """
<VirtualHost *:80>
    ServerName {DOMAIN}
	{ALIAS}
    DocumentRoot {DIR}
    SuexecUserGroup {USER} {USER}
    <FilesMatch '\.php$'>
    SetHandler 'proxy:fcgi://127.0.0.1:{PORT}/'
   </FilesMatch>

    <Directory {DIR}>
        AllowOverride All	
        Order Allow,Deny
        Allow from All
    </Directory>
    ErrorLog /var/log/apache2/{DOMAIN}_error.log
    CustomLog /var/log/apache2/{DOMAIN}_access.log combined
   {EXTRA}
</VirtualHost>
""".strip().replace('{DOMAIN}', domain_primary).replace('{DIR}', dir_name).replace('{EXTRA}', extra).replace("{ALIAS}", alias).replace('{USER}', user).replace("{PORT}",str(port_fpm))


vhost_conf_src = path.join(WORK_FOLDER, domain_primary + ".conf")
vhost_conf_dest = path.join(APACHE_SITES_FOLDER, path.basename(vhost_conf_src))

with open(vhost_conf_src, 'w') as file:
    file.write(vhost_str)

if path.exists(vhost_conf_dest):
	if force:
	       os.system('sudo rm %s' % vhost_conf_dest)
	else:
        	raise Exception('The file `%s` already exists.' % vhost_conf_dest)


if ssl :
	extra_secure = "";

	vhost_str_secure = """
	<VirtualHost *:443>
	    ServerName {DOMAIN_PRIMARY}
	{ALIAS}
	    DocumentRoot {DIR}
	    <Directory {DIR}>
	        AllowOverride All	
	        Order Allow,Deny
	        Allow from All
	    </Directory>
	 SuexecUserGroup {USER} {USER}
    <FilesMatch '\.php$'>
    SetHandler 'proxy:fcgi://127.0.0.1:{PORT}/'
   </FilesMatch>


	    SSLEngine on
		SSLCertificateFile /etc/apache2/ssl/mysitename.crt
		SSLCertificateKeyFile /etc/apache2/ssl/mysitename.key
    	ErrorLog /var/log/apache2/{DOMAIN_PRIMARY}_error.log
    	CustomLog /var/log/apache2/{DOMAIN_PRIMARY}_access.log combined
   	{EXTRA}	
	</VirtualHost>
	""".strip().replace('{DOMAIN_PRIMARY}', domain_primary).replace('{DIR}', dir_name).replace('{EXTRA}', extra_secure).replace("{ALIAS}", alias).replace('{USER}', user).replace("{PORT}",str(port_fpm))
	vhost_conf_secure_src = path.join(WORK_FOLDER, domain_primary + "_secure.conf")
	vhost_conf_secure_src = path.join(WORK_FOLDER, domain_primary + "_secure.conf")
	with open(vhost_conf_secure_src, 'w') as file:
    		file.write(vhost_str_secure)
	vhost_conf_secure_dest = path.join(APACHE_SITES_FOLDER, path.basename(vhost_conf_secure_src))
	os.system('sudo rm %s' % vhost_conf_secure_dest)
	shutil.copy(vhost_conf_secure_src, vhost_conf_secure_dest)





shutil.copy(vhost_conf_src, vhost_conf_dest)

fpm_conf = """
[{USER}]
user = www-data
group = www-data

listen = 127.0.0.1:{PORT}
pm = dynamic

pm.max_children = 5

pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
""".strip().replace("{PORT}", str(port_fpm)).replace("{USER}", user)


fpm_conf_src = path.join(WORK_FOLDER, domain_primary + ".conf")
fpm_conf_dest = path.join(FPM_FOLDER, path.basename(fpm_conf_src))

with open(fpm_conf_src, 'w') as file:
    file.write(fpm_conf)

shutil.copy(fpm_conf_src, fpm_conf_dest)





# activate the site
#os.system('sudo a2ensite %s' % path.basename(vhost_conf_dest))

#if ssl == 1:
#	os.system('sudo a2ensite %s' % path.basename(vhost_conf_secure_dest))

# restart apache 2
#os.system('sudo systemctl reload apache2')
#os.system('sudo systemctl restart ' + PHP_FPM_VERSION)
