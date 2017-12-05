Here was my new db setup on a Mac. Remember your password you use for the ratio-api user.
```bash
pg_ctl -D /usr/local/var/postgres start

createdb ratio-api
createuser -P ratio-api
# Enter a password

psql
REVOKE connect ON DATABASE "ratio-api" FROM PUBLIC;
GRANT connect ON DATABASE "ratio-api" TO "ratio-api";
CREATE TABLE 
```
My workflow for now is you store the pw in an environment variable, and pass that to the script.
```bash
export RATIOAPIPW=your db user password

python run_sql_scripts.py
```
The script will run some set-up scripts the first time:  
1. At the top of the file are a list of the currencies we discussed. You can append new ones to
it in the future and it'll set up new tables for them.

2. Also at the top is a list of exchanges we can append to

This script will also run ad-hoc scripts. Just put your new script `my_job.sql` in sql_scripts
directory and it'll get run the first time when you run `run_sql_scripts.py`.
There's a db table `script_runs` storing the history of past script runs, so you can re-run a
script by renaming it, or by deleting the record in the db.