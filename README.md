# DustyDollar
A very simple bank API

When running for the first time, don't forget to migrate the database by running the script at the root folder:
```shell
$ ./migrate_db.sh
```
If you wish to populate it with fake data for your testing, add the following parameter to the script:
```shell
$ ./migrate_db.sh --fake-data-population
```