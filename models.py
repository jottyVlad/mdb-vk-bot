from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()
    peer_id = fields.IntField()
    coins = fields.IntField(default=100)
    energy = fields.IntField(default=4)
    warns = fields.IntField(default=0)

    class Meta:
        table = 'users'

    def __str__(self):
        return str(self.user_id)

class GlobalUser(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()
    global_role = fields.ForeignKeyField('models.GlobalRole')

    class Meta: 
        table = 'global_users'

    def __str__(self):
        return str(self.user_id)

class Conversation(Model):
    id = fields.IntField(pk=True)
    peer_id = fields.IntField()

    class Meta:
        table = 'conversations'

    def __str__(self):
        return str(self.peer_id)

class GlobalRole(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=256)

    class Meta:
        table = 'global_roles'
    
    def __str__(self):
        return str(self.name)