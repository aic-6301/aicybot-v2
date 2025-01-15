import sqlite3

setup_query = [
    "CREATE TABLE IF NOT EXISTS \"expand\" (guild INTEGER PRIMARY KEY, bool BOOLEAN)",
    "CREATE TABLE IF NOT EXISTS \"join\" (guild INTEGER PRIMARY KEY, bool BOOLEAN, channel INTEGER DEFAULT NULL)",
    "CREATE TABLE IF NOT EXISTS \"join_bot\" (guild INTEGER PRIMARY KEY, bool BOOLEAN, role INTEGER, channel INTEGER DEFAULT NULL)",
    'CREATE TABLE IF NOT EXISTS role_panels (id INTEGER PRIMARY KEY, name TEXT, guild INTEGER, message_id INTEGER DEFAULT 0, channel_id INTEGER DEFAULT 0)',
    'CREATE TABLE IF NOT EXISTS panel_roles (panel_id INTEGER, role_id INTEGER, FOREIGN KEY(panel_id) REFERENCES role_panels(id))',
    'CREATE TABLE IF NOT EXISTS autoreply (id TEXT(8) PRIMARY KEY, keyword TEXT, reply TEXT, user INTEGER(18), guild INTEGER)',
    'CREATE TABLE IF NOT EXISTS log (guild INTEGER PRIMARY KEY, bool BOOLEAN, channel INTEGER NOT NULL)',
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
        c.execute(f'SELECT * FROM \"{table}\" WHERE guild = ?', (guild,))
        return c.fetchone()

def get_key(table, key, value, key_column='*'):
    """
    Retrieve a single record from the specified table where the guild matches.
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute(f'SELECT {key_column} FROM \"{table}\" WHERE \"{key}\" = ?', (value,))
        return c.fetchall()

def get_all(table):
    """
    Retrieve all records from the specified table.
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute(f'SELECT * FROM \"{table}\"')
        return c.fetchall()

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
            c.execute(f'INSERT INTO \"{table}\" ({", ".join(columns)}) VALUES ({placeholders})', (*values,))
            conn.commit()

def update(table, columns, values, key_column='guild', key_value=None):
    """
    Update a record in the specified table.
    """
    with connect() as conn:
        c = conn.cursor()
        for column, value in zip(columns, values):
            c.execute(f'UPDATE \"{table}\" SET {column} = ? WHERE {key_column} = ?', (value, key_value))
        conn.commit()

def delete(table, key_column='guild', key_value=None):
    """
    Delete a record from the specified table where the guild matches.
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute(f'DELETE FROM \"{table}\" WHERE \"{key_column}\" = ?', (key_value,))
        conn.commit()

def run_sql(sql):
    """
    Execute the specified SQL query.
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute(sql)

# Specific functions using the helper functions
def set(table, key, value, guild: int):
    insert_or_update(table, [key], [value], key_value=guild)

def set_keys(table, *keys, value, guild: int):
    insert_or_update(table, keys, [guild, value], key_value=guild)

def set_channel(table, value, channel: int, guild: int):
    insert_or_update(table, ['guild', 'bool', 'channel'], [guild, value, channel], key_value=guild)

def set_channel_role(table, value, role: int, channel: int, guild: int):
    insert_or_update(table, ['guild', 'bool', 'role', 'channel'], [guild, value, role, channel], key_value=guild)
