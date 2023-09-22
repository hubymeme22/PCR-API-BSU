from mongoengine import Document, StringField, IntField

# class Person(Document):
#     name = StringField(max_length=50, required=True)
#     age = IntField()

class Accounts(Document):
    name = StringField(max_length=50, required=True)
    username = StringField(max_length=50, required=True)
    email = StringField(max_length=50, required=True)
    password = StringField(max_length=50, required=True)
    permission = StringField(max_length=50, required=True)