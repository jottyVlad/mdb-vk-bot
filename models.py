from tortoise.models import Model
from tortoise import fields

class User(Model):
    id = fields.IntField(pk=True)
    user_id = fields.IntField()
    peer_id = fields.IntField()
    warns = fields.IntField(default=0)

    class Meta:
        table = 'users'

    def __str__(self):
        return str(self.user_id)

class Conversation(Model):
    id = fields.IntField(pk=True)
    peer_id = fields.IntField()

    class Meta:
        table = 'conversations'

    def __str__(self):
        return str(self.peer_id)
