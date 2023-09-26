from mongoengine import Document, StringField, IntField, EmbeddedDocument, ListField, EmbeddedDocumentField, DictField, ReferenceField

# class Person(Document):
#     name = StringField(max_length=50, required=True)
#     age = IntField()

class Accounts(Document):
    name = StringField(max_length=50, required=True)
    username = StringField(max_length=50, required=True)
    email = StringField(max_length=50, required=True)
    password = StringField(max_length=50, required=True)
    permission = StringField(max_length=50, required=True)
    
    
class Office(EmbeddedDocument):
    name = StringField()
    head = ReferenceField(Accounts)
    opcr_ids = ListField(StringField()) 
class Campus(Document):
    name = StringField(required=True)
    offices = DictField(field=EmbeddedDocumentField(Office))
