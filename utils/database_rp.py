import sqlite3

setup_query = [
    'CREATE TABLE IF NOT EXISTS role_panels (id INTEGER PRIMARY KEY, name TEXT, guild_id INTEGER, message_id INTEGER DEFAULT 0, channel_id INTEGER DEFAULT 0)',
    'CREATE TABLE IF NOT EXISTS panel_roles (panel_id INTEGER, role_id INTEGER, FOREIGN KEY(panel_id) REFERENCES role_panels(id))'
]

def connect():
    """
    データベースに接続します。
    Returns:
        sqlite3.Connection: データベース接続オブジェクト。
    Raises:
        sqlite3.DatabaseError: データベース接続中にエラーが発生した場合。
    """
    return sqlite3.connect('rolepanel.db')

def setup():
    with connect() as conn:
        c = conn.cursor()
        for query in setup_query:
            c.execute(query)
        conn.commit()
        return
        

def get(name: str):
    """
    指定された名前のロールパネルを取得します。
    Args:
        name (str): ロールパネルの名前。
    Returns:
        tuple: ロールパネルの情報。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM role_panels WHERE name = ?', (name,))
        return c.fetchone()

def get_all():
    """
    すべてのロールパネルを取得します。
    Returns:
        list: ロールパネルのリスト。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM role_panels')
        return c.fetchall()

def get_guild_panels(guild_id: int):
    """
    指定されたギルドのロールパネルを取得します。
    Args:
        guild_id (int): ギルドID。
    Returns:
        list: ロールパネルのリスト。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM role_panels WHERE guild_id = ?', (guild_id,))
        return c.fetchall()

def create_rolepanel(name: str, guild_id: int):
    """
    ロールパネルを作成します。
    Args:
        name (str): ロールパネルの名前。
        guild_id (int): ギルドID。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO role_panels (name, guild_id) VALUES (?, ?)', (name, guild_id))
        conn.commit()
        return

def delete_rolepanel(name: str):
    """
    ロールパネルを削除します。
    Args:
        name (str): ロールパネルの名前。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM role_panels WHERE name = ?', (name,))
        conn.commit()
        return

def set_panel_message(name: str, message_id: int, channel_id: int):
    """
    ロールパネルのメッセージIDとチャンネルIDを設定します。
    Args:
        name (str): ロールパネルの名前。
        message_id (int): メッセージID。
        channel_id (int): チャンネルID。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('UPDATE role_panels SET message_id = ?, channel_id = ? WHERE name = ?', (message_id, channel_id, name))
        conn.commit()
        return

def add_role_to_panel(name: str, role_id: int):
    """
    ロールパネルにロールを追加します。
    Args:
        name (str): ロールパネルの名前。
        role_id (int): ロールID。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM role_panels WHERE name = ?', (name,))
        panel_id = c.fetchone()
        if panel_id:
            c.execute('INSERT INTO panel_roles (panel_id, role_id) VALUES (?, ?)', (panel_id[0], role_id))
            conn.commit()
            return
        else:
            raise ValueError('Role panel not found')

def remove_role_from_panel(name: str, role_id: int):
    """
    ロールパネルからロールを削除します。
    Args:
        name (str): ロールパネルの名前。
        role_id (int): ロールID。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM role_panels WHERE name = ?', (name,))
        panel_id = c.fetchone()
        if panel_id:
            c.execute('DELETE FROM panel_roles WHERE panel_id = ? AND role_id = ?', (panel_id[0], role_id))
            conn.commit()
            return
        else:
            raise ValueError('Role panel not found')
        

def get_roles_from_panel(name: str):
    """
    ロールパネルからロールを取得します。
    Args:
        name (str): ロールパネルの名前。
    Returns:
        list: ロールIDのリスト。
    """
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT id FROM role_panels WHERE name = ?', (name,))
        panel_id = c.fetchone()
        if panel_id:
            c.execute('SELECT role_id FROM panel_roles WHERE panel_id = ?', (panel_id[0],))
            return [row[0] for row in c.fetchall()]
        return []