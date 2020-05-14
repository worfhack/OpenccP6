# coding: utf-8

import socket
from contextlib import closing
import argparse
import os.path as path
import os
import pwd
import shutil
import crypt



#Fonction for find a free port to php-fpm
def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]



#  Default Var ####
WEB_ROOT = '/var/www/'
WORK_FOLDER = '/tmp/'
APACHE_SITES_FOLDER = '/etc/apache2/sites-available/'



#Init ClI ARG
parser = argparse.ArgumentParser()
parser.add_argument('--login', help="login ")
parser.add_argument('--domain_primary', help="Domaine principal du site ")
parser.add_argument('--domain_other', required=False, help="Domaine secondaire du site ",  nargs='+')
parser.add_argument('--fpm', required=False, help="Php avec fpm", action="store_true")
parser.add_argument('--fpm_version', required=False, help="Version de fpm")
parser.add_argument('--no_dns', required=False, help="Ajout l'entrée au fichier host", action="store_true")
parser.add_argument('--ssl', required=False, help="Active le https sur le site", action="store_true")
parser.add_argument('--cert', required=False, help="SSL cert certificat file")
parser.add_argument('--key', required=False, help="SSL key certificat file")
parser.add_argument('--force_ssl', required=False, help="Active une redirection vers le  https", action="store_true")
parser.add_argument('--password',    help='mot de passe.')
parser.add_argument('--user',   help='utilisateur.')
args = parser.parse_args()
#####


# Init Vars        ####
domain_primary = getattr(args, 'domain_primary') # Root Domain
domain_other = getattr(args, 'domain_other') # list a secondary domain , for aliases
no_dns = getattr(args, 'no_dns')   # Add Domain to local host file
ssl = getattr(args, 'ssl') #   Create a https version
fpm = getattr(args, 'fpm') #   Add php-fpm to projet
fpm_version = getattr(args, 'fpm_version') #   fpm_version
force_ssl = getattr(args, 'force_ssl') # add a http redirect to http
password = getattr(args,'password') #password for new login
user= getattr(args, 'user') # new user
cert= getattr(args, 'cert') 
key= getattr(args, 'key') 

dir_name = domain_primary

# check if dir_name exists
if not path.exists(dir_name):
    dir_name = path.join(WEB_ROOT, dir_name)
if not path.exists(dir_name):
	os.mkdir(dir_name)
if not path.exists(dir_name):
    raise FileNotFoundError('The path does not exist: %s' % dir_name)
if not path.exists(WORK_FOLDER):
    os.mkdir(WORK_FOLDER)

if ssl == True and (cert == None or key == None) :
	raise Exception('Cert files is required')
if fpm == True:
	if  fpm_version == None:
		raise Exception('Fpm version is required')
	FPM_FOLDER = '/etc/php/'+fpm_version+'/fpm/pool.d/'
	PHP_FPM_VERSION = 'php'+fpm_version+'-fpm'
	port_fpm = find_free_port()
	vhost_fpm = """
	 SuexecUserGroup {USER} {USER}
	    <FilesMatch '\.php$'>
    	SetHandler 'proxy:fcgi://127.0.0.1:{PORT}/'
   	</FilesMatch>

	""".strip().replace('{USER}', user).replace('{PORT}', str(port_fpm))
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
	os.system('sudo systemctl restart ' + PHP_FPM_VERSION)




#Create user Dir  and user
os.system("userdell " + user +  " >/dev/null 2>&1") 

try:
	pwd.getpwnam(user)
except KeyError:
	encPass = crypt.crypt(password,"22")
	os.system("useradd -p "+encPass+ " -s "+ "/bin/bash "+ "-d "+ dir_name + " -m "+ " -c \""+ user+"\" " + user)

#Add new vhost to host file if option no dns
if no_dns ==1:
	file_object = open('/etc/hosts', 'a')
	file_object.write("127.0.0.1   " + domain_primary + "\n")
	for i in domain_other: 
	        file_object.write("127.0.0.1   " + i + "\n")
	file_object.close()

#Prepare apache config

alias = "ServerAlias "
for i in domain_other: 
	alias = alias +" " +i
extra = ""
if force_ssl == 1:
	extra = extra + "RewriteEngine On \n RewriteCond %{HTTPS} !=on \n RewriteRule ^(.*) https://"+domain_primary+"/$1 [R,L]"

#CREATE DEMO FILE

index_file = """
<?php 
phpinfo();
echo "<pre>";
var_dump($_SERVER);
echo "</pre>";
"""
print dir_name
index_file_dst = path.join(dir_name,  "index.php")

with open(index_file_dst, 'w') as file:
	file.write(index_file)


################# Config for http ##################################"



vhost_str = """
<VirtualHost *:80>
    ServerName {DOMAIN}
	{ALIAS}
    DocumentRoot {DIR}
	{FPM}

    <Directory {DIR}>
        AllowOverride All	
        Order Allow,Deny
        Allow from All
    </Directory>
    ErrorLog /var/log/apache2/{DOMAIN}_error.log
    CustomLog /var/log/apache2/{DOMAIN}_access.log combined
   {EXTRA}
</VirtualHost>
""".strip().replace('{DOMAIN}', domain_primary).replace('{DIR}', dir_name).replace('{EXTRA}', extra).replace("{ALIAS}", alias).replace('{FPM}', str(vhost_fpm))


vhost_conf_src = path.join(WORK_FOLDER, domain_primary + ".conf")
vhost_conf_dest = path.join(APACHE_SITES_FOLDER, path.basename(vhost_conf_src))

with open(vhost_conf_src, 'w') as file:
    file.write(vhost_str)
if path.exists(vhost_conf_dest):
	       os.system('sudo rm %s' % vhost_conf_dest)
shutil.copy(vhost_conf_src, vhost_conf_dest)
###############################################

############ Config for ssl mode ###############
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

		{FPM}
	    SSLEngine on
		SSLCertificateFile {CERT}
		SSLCertificateKeyFile {KEY}
    	ErrorLog /var/log/apache2/{DOMAIN_PRIMARY}_error.log
    	CustomLog /var/log/apache2/{DOMAIN_PRIMARY}_access.log combined
   	{EXTRA}	
	</VirtualHost>
	""".strip().replace('{DOMAIN_PRIMARY}', domain_primary).replace('{DIR}', dir_name).replace('{EXTRA}', extra_secure).replace("{ALIAS}", alias).replace('{FPM}', vhost_fpm).replace('{CERT}', cert).replace('{KEY}', key)
	vhost_conf_secure_src = path.join(WORK_FOLDER, domain_primary + "_secure.conf")
	vhost_conf_secure_src = path.join(WORK_FOLDER, domain_primary + "_secure.conf")
	with open(vhost_conf_secure_src, 'w') as file:
    		file.write(vhost_str_secure)
	vhost_conf_secure_dest = path.join(APACHE_SITES_FOLDER, path.basename(vhost_conf_secure_src))
	if path.exists(vhost_conf_secure_dest):
		os.system('sudo rm %s' % vhost_conf_secure_dest)
	shutil.copy(vhost_conf_secure_src, vhost_conf_secure_dest)
	
######################################################################

# activate the site
os.system('sudo a2ensite %s >/dev/null 2>&1 ' % path.basename(vhost_conf_dest) )

if ssl == 1:
	 os.system('sudo a2ensite %s >/dev/null 2>&1' % path.basename(vhost_conf_secure_dest))

os.system('sudo systemctl reload apache2')
print "Your new site is enable"
