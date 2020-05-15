# add_vhost.py



This script is a pyhton tools to add new Vhost to apache2 in ubuntu/debian instalation 




### Requirement

add_vhost requires somes apaches  to run.
- apache2-suexec-custom (for fpm mode)
- ssl (for ssl)


### Create a simple vhost 
```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --password  [PASSWORD} --user [USER]
```

### Create a simple vhost with multi domain
Using --domain_other option
```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --domain_other [[DOMAIN_1]  [DOMAIN_2] ...]  --password  [PASSWORD} --user [USER]
```
### add vhost to host file 
Using --nos_dns option
```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --password  [PASSWORD} --user [USER] --no_dns
```

### add vhost with https 
Using 
- --ssl  option 
- --cert option (cert files)
- --key option (key files)
```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --password  [PASSWORD} --user [USER] --ssl  --cert [PATH to cert file] --key [PATh to key files]
```
### add vhost with redirection from http to https 
Using --force_ssl option
```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --password  [PASSWORD} --user [USER] --ssl  --cert [PATH to cert file] --key [PATh to key files] --force_ssl
```

### add vhost using fpm-php 
Using 
- --fpm  option 
- --fpm_version (version of your php-fpm ) , 7.4 for exemple

```sh
$ python add_vhost.py   --domain_primary [DOMAIN]  --domain_other [[DOMAIN_1]  [DOMAIN_2] ...]  --password  [PASSWORD} --user [USER] --fpm  --fpm_version [VERSION]
```

