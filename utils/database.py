import sqlite3

setup_query = [
    "CREATE TABLE IF NOT EXISTS settings (guild INTEGER NOT NULL PRIMARY KEY, log_ch INTEGER DEFAULT 0, welcome_channel INTEGER DEFAULT 0, expand BOOLEAN, bot_role INTEGER DEFAULT 0)",
    'CREATE TABLE IF NOT EXISTS role_panels (id INTEGER PRIMARY KEY, name TEXT, guild INTEGER, message_id INTEGER DEFAULT 0, channel_id INTEGER DEFAULT 0)',
    'CREATE TABLE IF NOT EXISTS panel_roles (panel_id INTEGER, role_id INTEGER, FOREIGN KEY(panel_id) REFERENCES role_panels(id))',
    'CREATE TABLE IF NOT EXISTS autoreply (id TEXT(8) PRIMARY KEY, keyword TEXT, reply TEXT, user INTEGER(18), guild INTEGER)',
    'CREATE TABLE IF NOT EXISTS ticket (id TEXT(8) NOT NULL, guild INTEGER NOT NULL, name TEXT NOT NULL, category INTEGER DEFAULT 0, channel INTEGER DEFAULT 0, roles TEXT DEFAULT 0, unlimited BOOLEAN DEFAULT 0)',
    'CREATE TABLE IF NOT EXISTS tickets (id TEXT(8) PRIMARY KEY, ticket_id TEXT, user INTEGER, channel INTEGER, guild INTEGER, number INTEGER, messages TEXT, closed BOOLEAN, responser INTEGER DEFAULT 0, FOREIGN KEY(ticket_id) REFERENCES ticket(id))',
]

def connect():
    return sqlite3.connect('database.db')

def setup():
    with connect() as conn:
        c = conn.cursor()
        for query in setup_query:
            c.execute(query)
        conn.commit()
        return

def get(table, guild: int):
    """
    Retrieve a single record from the specified table where the guild matches.
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM \"{}\" WHERE guild = ?'.format(table), (guild,))
        return c.fetchone()

def get_key(table, key, value, key_column='*'):
    """
    Retrieve a single record from the specified table where the guild matches.
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT {} FROM \"{}\" WHERE \"{}\" = ?'.format(key_column, table, key), (value,))
        return c.fetchall()

def get_all(table):
    """
    Retrieve all records from the specified table.
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM \"{}\"'.format(table))
        return c.fetchall()

def insert(table, columns, values):
    """
    Insert a record into the specified table.
    """
    with connect() as conn:
        c = conn.cursor()
        placeholders = ', '.join(['?'] * len(values))
        c.execute('INSERT INTO \"{}\" ({}) VALUES ({})'.format(table, ", ".join(columns), placeholders), (*values,))
        conn.commit()


def insert_or_update(table, columns, values, key_column='guild', key_value=None):
    """
    Insert or update a record in the specified table.
    """
    with connect() as conn:
        if get_key(table, key_column, key_value):
            update(table, columns, values, key_column, key_value)
        else:
            c = conn.cursor()
            placeholders = ', '.join(['?'] * len(values))
            c.execute('INSERT INTO \"{}\" ({}) VALUES ({})'.format(table,", ".join(columns), placeholders), (*values,))
            conn.commit()

def update(table, columns, values, key_column='guild', key_value=None):
    """
    Update a record in the specified table.
    """
    with connect() as conn:
        c = conn.cursor()
        for column, value in zip(columns, values):
            c.execute('UPDATE \"{}\" SET {} = ? WHERE {} = ?'.format(table, column, key_column), (value, key_value))
        conn.commit()

def delete(table, key_column='guild', key_value=None):
    """
    Delete a record from the specified table where the guild matches.
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM \"{}\" WHERE \"{}\" = ?'.format(table, key_column), (key_value,))
        conn.commit()

def run_sql(sql):
    """
    Execute the specified SQL query.
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute(sql)