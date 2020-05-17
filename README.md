# add_vhost.py



Cette outil est un utilitaire pour ajouter de nouveau vhost apache sur des distribution  ubuntu/debian 




### Prérequis

- apache2-suexec-custom (pour le support de fpm)
- ssl (pour le support du https)
- Install /apt.gpg  for install auther php version

### Creer un simple vhost
```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --password  [PASSWORD} --user [USER]
```

### Ajouter un vhost avec plusieur alias de domaine
Using --domain_other option
```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --domain_other [[DOMAIN_1]  [DOMAIN_2] ...]  --password  [PASSWORD} --user [USER]
```
### Ajouter le site au fichier host du serveur 
Using --nos_dns option
```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --password  [PASSWORD} --user [USER] --no_dns
```

### Ajouter un vhost avec support du https
Using 
- --ssl  option 
- --cert option (fichier .cert)
- --key option (fichier .key)
```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --password  [PASSWORD} --user [USER] --ssl  --cert [PATH to cert file] --key [PATh to key files]
```
### Ajouter un vhost avec redirection du http vers https
Using --force_ssl option
```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --password  [PASSWORD} --user [USER] --ssl  --cert [PATH to cert file] --key [PATh to key files] --force_ssl
```

### ajoute un vhost avec php-fpm
Using 
- --fpm (votre version de  php-fpm ) , 7.4 for exemple

```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --domain_other [[DOMAIN_1]  [DOMAIN_2] ...]  --password  [PASSWORD} --user [USER] --fpm [VERSION]
```

