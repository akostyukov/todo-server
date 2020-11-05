from app.auth.views import login_page, register_page, login, register, logout
from app.tasks.views import task_list, add_task, delete_task, done_task, clear_all

urls = [
    ('/', 'get', task_list),
    ('/', 'post', add_task),
    (r'/delete/(?P<task_id>\d+)', 'get', delete_task),
    (r'/done/(?P<task_id>\d+)', 'get', done_task),
    ('/clear', 'get', clear_all),
    ('/login', 'get', login_page),
    ('/register', 'get', register_page),
    ('/login', 'post', login),
    ('/register', 'post', register),
    ('/logout', 'get', logout),
]
