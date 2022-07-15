### zabbix-pgpool-cluster
***
Один из способов мониторинга **pgpool-класстера**. По сути, вывод команды - `show pool_nodes` переложил в json-формат и отдаю его на zabbix-server
***

#### Как развернуть?

1) Подключаемся в базе, создаем новую роль и задаем пароль. Далее для созданного пользователя даем права на просмотр таблицы - `pg_monitor` 
    ```
    $ psql
    postgres=# create role zabbix_user with login;
    postgres=# grant pg_monitor to zabbix_user;
    postgres=# \password zabbix_user
    ```

2) Для доступа в pgpool-кластеру добавляем записи в pool_hba.conf
    ```
    # Zabbix pgpool mon
    host    all         zabbix_user      <ip pool node>/32         scram-sha-256
    host    all         zabbix_user      <ip pool node>/32         scram-sha-256
    host    all         zabbix_user      <ip pool node>/32         scram-sha-256
    ```
    Вместо `<ip pool node>` - указываем адреса pgpool-нод. Заставляем сервис pgpool перечивать конфигурацию: `systemctl reload pgpool`
    
3) Опционально, в зависимости от конфигурации бекендов. Нужно будет добавить в `pg_hba.conf` - файл, аналогичные правила. 
4) В `pool_passwd` - добавляем пользователя. Делается это командой:
    ```
    $ su - postgres
    $ pg_enc -m -k ~/.pgpoolkey -u zabbix_user -p
    db password: **********
    ```
5) Для безпаролевого доступа к кластеру, в домашнем каталоге пользователя `zabbix` (обычно это `/var/lib/zabbix`) создаем файл `.pgpass` и добавляем строчки:
    ```
    #host:port:db_name:user_name:password
    192.168.1.1:9999:postgres:zabbix_user:Password
    ```
6) Меняем права к файлу `.pgpass` (Меняем владельца и группу):
    ```
    $ chmod 600 /var/lib/zabbix/.pgpass
    ```
7) Файлы `settings.py` и `zbx-pgpool.py` переносим в домашний каталог пользователя zabbix. 
8) В файле `settings.py` - меняем в переменных значения на свои. Например:
    ```
    # DB connection settings
    pg_host = "192.168.1.1"
    pg_port = "9999"
    pg_user = "zabbix_user"
    pg_base = "postgres"
    ```
9) Делаем скрипты исполняемыми, меняем владельца. Работу скрипта можно проверить так: 
    ```
    # Вернет все бекенды
    $ sudo -u zabbix python3 zbx-pgpool.py discovery 
    
    # Вернет статку по бекенду pgpool_node1
    $ sudo -u zabbix python3 zbx-pgpool.py pgpool_node1
    ```
10) В каталог `/etc/zabbix/zabbix_agent.d/` копируем файл - `zbx_pgpool.conf`. И релодим zabbix-agent.
11) На вебморде заббикса делаем импорт шаблона - `pgpool_template.yaml`
12) Создаем новый хост, указываем кластерный ip и вешаем шаблон. 

PS. Скрипты нужно раскидать на всех pgpool-нодах, в одной и той же аналогии. 
