import database
# USER format: (user_name, password, is_admin, authorized_nodes)
# authorized_nodes is a list of node_ids the user can access; empty list means no nodes. NOne means access to all nodes. This is set at login and used for permission checks throughout the app.

class User:
    def __init__(self, username:str, password:str, is_admin:int = 0, viewable_nodes:list = []):
        self.username = username
        self.password = password
        self.is_admin = is_admin
        self.viewable_nodes = database.get_nodes() if is_admin else viewable_nodes

    def list_info(self):
        return (self.username, self.password, self.is_admin, str(self.viewable_nodes))
        
def store_db(user:User):
    user_info = user.list_info()
    database.add_user(user_info)



    
        