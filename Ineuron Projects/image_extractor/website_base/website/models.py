from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from flask_login import UserMixin

'''
These models will be used to create tables under the respective keyspace
'''


class User(Model, UserMixin):
    id = columns.UUID(primary_key=True)
    email_id = columns.Text(index=True)
    first_name = columns.Text()
    last_name = columns.Text()
    password = columns.Text()

class sharedUsers(Model, UserMixin):
    id = columns.UUID(primary_key=True)
    folder_id = columns.Text(index=True)
    shared_folder_id = columns.Text()
