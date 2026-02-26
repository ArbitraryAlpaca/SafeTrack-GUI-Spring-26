USER:tuple = ()
# USER format: (user_name, password, is_admin, authorized_nodes)
# authorized_nodes is a list of node_ids the user can access; empty list means no nodes. NOne means access to all nodes. This is set at login and used for permission checks throughout the app.