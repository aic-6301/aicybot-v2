import sqlite3

setup_query = [
    "CREATE TABLE IF NOT EXISTS \"expand\" (guild INTEGER PRIMARY KEY, bool BOOLEAN)",
    "CREATE TABLE IF NOT EXISTS \"join\" (guild INTEGER PRIMARY KEY, bool BOOLEAN, channel INTEGER DEFAULT NULL)",
    "CREATE TABLE IF NOT EXISTS \"join_bot\" (guild INTEGER PRIMARY KEY, bool BOOLEAN, role INTEGER, channel INTEGER DEFAULT NULL)"
]

def connect():
    return sqlite3.connect('database.db')

def setup():
    with connect() as conn:
        c = conn.cursor()
        for query in setup_query:
            c.execute(query)
        conn.commit()
        
def get(table, guild: int):
    """
    指定されたテーブルからギルドが一致する単一のレコードを取得します。
    Args:
        table (str): クエリを実行するテーブルの名前。
        guild (int): レコードをフィルタリングするギルド識別子。
    Returns:
        tuple: ギルドが一致するテーブルからの単一のレコード、または一致するものがない場合はNone。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute(f'SELECT * FROM \"{table}\" WHERE guild = ?', (guild,))
        return c.fetchone()


def set(table, key, value, guild: int):
    """
    指定されたテーブルにキーと値のペアを挿入します。
    Args:
        table (str): データを挿入するテーブルの名前。
        key (str): 挿入するキー。
        value (str): 挿入する値。
        guild (int): レコードをフィルタリングするギルド識別子。
    Raises:
        sqlite3.DatabaseError: データベース操作中にエラーが発生した場合。
    """
    with connect() as conn:
        if get(table, guild):
            update(table, key, value, guild)
            return
        c = conn.cursor()
        c.execute(f'INSERT INTO \"{table}\" VALUES (?, ?)', (guild, value))
        conn.commit()
        
def set_channel(table, value, channel: int, guild: int):
    """
    指定されたテーブルにキーと値のペアを挿入します。
    Args:
        table (str): データを挿入するテーブルの名前。
        key (str): 挿入するキー。
        value (str): 挿入する値。
        guild (int): レコードをフィルタリングするギルド識別子。
    Raises:
        sqlite3.DatabaseError: データベース操作中にエラーが発生した場合。
    """
    with connect() as conn:
        if get(table, guild):
            update(table, 'bool', value, guild)
            update(table, 'channel', channel, guild)
            return
        c = conn.cursor()
        c.execute(f'INSERT INTO \"{table}\" VALUES (?, ?, ?)', (guild, value, channel))
        conn.commit()

def set_channel_role(table, value, role: int, channel: int, guild: int):
    """
    指定されたテーブルにチャンネルとロールの情報を設定します。
    この関数は、指定されたギルドに対してチャンネルとロールの情報を設定します。
    既にギルドの情報が存在する場合は、ロールとチャンネルの情報を更新します。
    存在しない場合は、新しいレコードを挿入します。
    Args:
        table (str): 操作対象のテーブル名。
        value (Any): 挿入または更新する値。
        role (int): 設定するロールのID。
        channel (int): 設定するチャンネルのID。
        guild (int): 設定するギルドのID。
    Returns:
        None
    """
    
    with connect() as conn:
        if get(table, guild):
            update(table, 'bool', value, guild)
            update(table, 'role', role, guild)
            update(table, 'channel', channel, guild)
            return
        c = conn.cursor()
        c.execute(f'INSERT INTO \"{table}\" VALUES (?, ?, ?, ?)', (guild, value, role, channel))
        conn.commit()

def update(table, key, new_value, guild: int):
    """
    指定されたテーブルの特定のレコードを更新します。
    Args:
        table (str): 更新対象のテーブル名。
        key (str): 更新対象のカラム名。
        value (any): 更新対象のレコードの現在の値。
        new_value (any): 更新後の新しい値。
    Raises:
        sqlite3.Error: データベース操作中にエラーが発生した場合。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute(f'UPDATE \"{table}\" SET {key} = ? WHERE guild = ?', (new_value, guild))
        conn.commit()
        

def delete(table, guild: int):
    """
    指定されたテーブルから特定のキーと値に一致するレコードを削除します。
    Args:
        table (str): レコードを削除するテーブルの名前。
        key (str): 削除条件となるカラムの名前。
        value (Any): 削除条件となるカラムの値。
    Raises:
        sqlite3.DatabaseError: データベース操作中にエラーが発生した場合。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute(f'DELETE FROM \"{table}\" WHERE guild = ?', (guild,))
        conn.commit()