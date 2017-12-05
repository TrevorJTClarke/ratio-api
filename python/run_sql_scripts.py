import psycopg2
import os


# If you append new coins to either of these, it will work without recreating the others.
CRYPTOS = dict(
    BTC='Bitcoin',
    ETH='Ethereum',
    BCH='Bitcoin Cash',
    XRP='Ripple',
    DASH='Dash',
    LTC='Litecoin',
    BTG='Bitcoin Gold'
    # NEO' ??
)
FIATS = dict(
    USD='US Dollar',
    EUR='Euro',
    JPY='Japanese Yen')
EXCHANGES = [('PLACEHOLDER', 'Placeholder', 'Base Currency', 'placeholderdotcom')]  # TODO: Get exchanges
PW = os.environ.get('RATIOAPIPW')

if not PW:
    raise Exception("Set db password with 'export RATIOAPIPW=yourpassword'")

try:
    conn = psycopg2.connect(dbname='ratio-api', user='ratio-api', host='localhost', password=PW)
except Exception as e:
    raise Exception(e)

# First time create the table that tells us if we already executed one-time table-creation scripts:
with conn.cursor() as cur:
    cur.execute("""
create table if not exists script_runs (
script varchar(128) NOT NULL,
run timestamp NOT NULL
);
create table if not exists currency (
key serial primary key,
symbol varchar(32) UNIQUE,
name varchar(128)
);
create table if not exists exchange (
key serial primary key,
symbol varchar(32) UNIQUE,
name varchar(128),
base varchar(16),  /* Maybe base should be a key id from currency table */
domain varchar(256)
);
    """)
# For ad hoc scripts check if there are new scripts
with conn.cursor() as cur:
    cur.execute('select script from script_runs')
    past_runs = set(i[0] for i in cur.fetchall())  # Bc it fetches as [('a.sql',), ('b.sql')]

currencies = CRYPTOS
currencies.update(FIATS)
new_currencies = set(currencies.keys()) - past_runs

for symbol in new_currencies:
    cur = conn.cursor()
    # Add record to currency table:
    cur.execute('insert into currency(symbol, name) values (%s, %s)', (symbol, currencies[symbol],))

    # Create currency to currency table for every combination, and unique to every exchange:
    # i.e. "btc-buy-bitfinex", "btc-sell-Bittrex"
    # If there's multiple base currencies for an exchange, we should create multiple base tables
    for exchange, _, _, _ in EXCHANGES:
        for tablename in [symbol + '-buy-' + exchange, symbol + '-sell-' + exchange]:
            cur.execute("""
create table if not exists "%s" (
trade_id varchar(32) primary key,
timestamp timestamp,
rate decimal,
amount decimal,
total decimal
);
            """ % tablename)

    cur.execute('insert into script_runs(script, run) values (%s, now())', (symbol,))
    cur.close()

# Find new ad-hoc scripts in sql_scripts directory:
past_script_runs = past_runs - currencies.keys()
new_scripts = set(os.listdir('python/sql_scripts')) - past_script_runs

for script_path in new_scripts:
    if os.path.splitext(script_path) != '.sql':
        continue  # This only works for sql scripts rn

    with open(script_path) as script_file, conn.cursor() as cur:
        cur.execute(script_file.read())
        cur.execute('insert into script_runs(script, run) values (%s, now())', (script_path,))

conn.commit()
