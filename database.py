import sqlite3
from datetime import datetime

# data = [(time, node_id, latitude, longitude, status), ...]

def init_db(db:str ="nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f'''CREATE TABLE IF NOT EXISTS nodes
                (time TEXT,
                node_id INTEGER,
                latitude REAL,
                longitude REAL,
                status TEXT)''')
        
        
def get_db(db:str = "nodes.db") -> list:
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT *, MAX(time) FROM nodes GROUP BY node_id")
        data = cur.fetchall()
    return data

def add_to_db(vals:tuple, db:str = "nodes.db"):
    if isinstance(vals, tuple) and list(map(type,vals)) == [str, int, float, float, str]:
        print(vals, "VALS")
        with sqlite3.connect(db) as conn:
            conn.execute(f"INSERT INTO nodes VALUES (?,?,?,?,?)",vals)
    else:
        print("***ERROR: VALUE FORMATTING FAILED***")

# Deletes rows before given time
def delete_before_time(time, table:str = "nodes", db:str ="nodes.db"):
    time_format = "%Y-%m-%d %H:%M:%S"
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        try:
            time = datetime.fromisoformat(time)
            time = time.strftime(time_format)
            if table == "nodes":
                cur.execute(f'''DELETE FROM nodes WHERE time < ?''', (time,))
                conn.commit()
            elif table == "notifications":
                cur.execute(f'''DELETE FROM notifications WHERE time < ?''', (time,))
                conn.commit()
        except ValueError:
            print("***ERROR: TIME FORMATTING FAILED (YYYY-MM-DD HH:MM:SS)***")
            return -1

def print_db(db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM nodes")
        data = cur.fetchall()
        for row in data:
            print(row, end="\n")

def get_nodes(db:str = "nodes.db") -> list:
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT DISTINCT node_id FROM nodes")
        data = cur.fetchall()
        data = [row[0] for row in data]
    return data if data else []

def get_node_info(node_id:int,db:str = "nodes.db") -> list:
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM nodes WHERE node_id = ? ORDER BY time DESC",(node_id,))
        node_data = cur.fetchall()
    return node_data

def get_recent_info(node_id:int, db:str = "nodes.db") -> list:
    try:
        return [get_node_info(node_id,db)[0]]
    except IndexError:
        return []

# Returns most recent GPS location
def get_GPS(node_id:int, db:str = "nodes.db") -> tuple:
    try:
        data = get_recent_info(node_id, db)
        # Return as stored: (longitude, latitude)
        return data[0][2], data[0][3]
    except IndexError:
        return ()

# Returns most recent status
def get_status(node_id:int, db:str = "nodes.db") -> str:
    try:
        data = get_recent_info(node_id, db)
        return data[0][-1]
    except IndexError:
        return ""

def in_db(node_id:int, db:str = "nodes.db") -> bool:
    if get_status(node_id, db) != "":
        return True
    return False


# Notification functions

# Notif = (time, node_id, status, title, message)

def init_notif_db(db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS notifications (time TEXT, node_id INTEGER, status TEXT,Title TEXT, Message TEXT)")

def add_notif(vals:tuple, db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        conn.execute(f"INSERT INTO notifications VALUES (?,?,?,?,?)",vals)

def get_notifs(db:str = "nodes.db") -> list:
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM notifications")
        data = cur.fetchall()
    return data





'''CAUTION: The following functions are for testing purposes only. Do not use in backend code as they may cause data loss.'''

def CLEAR_DB(db:str = "nodes.db"): 
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM nodes")
        conn.commit()

def CLEAR_NOTIF_DB(db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM notifications")
        conn.commit()


if __name__ == "__main__":
    print_db()



# Login/Users database functions

def init_user_db(db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS users (user_name TEXT PRIMARY KEY, password TEXT, is_admin INTEGER DEFAULT 0, authorized_nodes TEXT DEFAULT '')") # athorized_nodes format = [1,2,3] Where int is node_id. Empty string means access to all nodes.
        conn.commit()
        cur.close()

def add_user(user_name:str, password:str, role:str = "user", authorized_nodes:list = [], db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        conn.execute(f"INSERT INTO users VALUES (?,?,?,?,?)",(user_name, password, 1 if role.lower() == "admin" else 0, str(authorized_nodes)))
        conn.commit()

def get_user(user_name:str, db:str = "nodes.db") -> tuple:
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE user_name = ?",(user_name,))
        data = cur.fetchone()
        data[4] = eval(data[4]) if data and data[4] else []  # Convert string back to list, handle empty string case
    return data

def update_user(user_name:str, password:str = None, role:str = None, authorized_nodes:list = None, db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        if password is not None:
            cur.execute(f"UPDATE users SET password = ? WHERE user_name = ?",(password, user_name))
        if role is not None:
            cur.execute(f"UPDATE users SET is_admin = ? WHERE user_name = ?",(1 if role.lower() == "admin" else 0, user_name))
        if authorized_nodes is not None:
            cur.execute(f"UPDATE users SET authorized_nodes = ? WHERE user_name = ?",(str(authorized_nodes), user_name))
        conn.commit()

def delete_user(user_name:str, db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM users WHERE user_name = ?",(user_name,))
        conn.commit()

def list_users(db:str = "nodes.db") -> list:
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT user_name FROM users")
        data = cur.fetchall()
    return [d[0] for d in data]

def authenticate_user(user_name:str, password:str, db:str = "nodes.db") -> bool:
    user = get_user(user_name, db)
    if user and user[1] == password:
        return True
    return False

def get_auth_nodes(user_name:str, db:str = "nodes.db") -> list:
    user = get_user(user_name, db)
    if user:
        authorized_nodes_list = user[4]  # user[4] is the authorized_nodes list
        if not authorized_nodes_list:  # If empty list, return empty list
            return []  # Access to all nodes
        return authorized_nodes_list
    return []

def is_admin(user_name:str, db:str = "nodes.db") -> bool:
    user = get_user(user_name, db)
    if user and user[2] == 1:
        return True
    return False

# For testing purposes only. Do not use in backend code as they may cause data loss.

def CLEAR_USER_DB(db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM users")
        conn.commit()

def print_users(db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users")
        data = cur.fetchall()
        for row in data:
            print(row, end="\n")

def print_user_db(db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users")
        data = cur.fetchall()
        for row in data:
            print(row, end="\n")