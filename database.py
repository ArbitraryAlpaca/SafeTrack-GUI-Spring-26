import sqlite3
from datetime import datetime

def init_db(db:str ="nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f'''CREATE TABLE IF NOT EXISTS nodes
                    (time TEXT,
                    node_id INTEGER,
                    longitude REAL,
                    latitude REAL,
                    status TEXT)''')

# NOT TO BE USED BY BACKEND (only for debug purposes currently)
def add_to_db(vals:tuple, db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        conn.execute(f"INSERT INTO nodes VALUES (?,?,?,?,?)",vals)

# Deletes rows before given time
def delete_before_time(time, db:str ="nodes.db"):
    time_format = "%Y-%m-%d %H:%M:%S"
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        try:
            time = datetime.fromisoformat(time)
            time = time.strftime(time_format)

            cur.execute(f'''DELETE FROM nodes WHERE time < ?''', (time,))
            conn.commit()
            cur.close()
        except ValueError:
            print("***ERROR: TIME FORMATTING FAILED (YYYY-MM-DD HH:MM:SS)***")
            return -1

def print_db(db:str = "nodes.db"):
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM nodes")
        data = cur.fetchall()
        for row in data:
            print(row)

def get_node_info(node_id:int,db:str = "nodes.db") -> list:
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM nodes WHERE node_id = ?",(node_id,))
        node_data = cur.fetchall()
    return node_data

def get_recent_info(node_id:int, db:str = "nodes.db") -> list:
    try:
        return [get_node_info(node_id,db)[-1]]
    except IndexError:
        return []

# Returns most recent GPS location
def get_GPS(node_id:int, db:str = "nodes.db") -> tuple:
    try:
        data = get_recent_info(node_id, db)
        return data[0][2],data[0][3]
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


if __name__ == "__main__":
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ex_vals = (t,3,33.41946454694378, -111.93544878156348,"ALERT")
    add_to_db(ex_vals)
    print_db()

