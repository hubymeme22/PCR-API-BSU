from mongoengine import Document, EmbeddedDocument, EmbeddedDocumentField, StringField, IntField, FloatField, ListField

class Accounts(Document):
    name = StringField(max_length=50, required=True)
    username = StringField(max_length=50, required=True)
    email = StringField(max_length=50, required=True)
    password = StringField(max_length=50, required=True)
    permission = StringField(max_length=50, required=True)


# Target model
class Success(EmbeddedDocument):
    indicator = StringField()
    budget = FloatField()
    division = StringField()
    accomplishment = StringField()
    rating = ListField(IntField())
    remarks = ListField(StringField())
    assigned_to = ListField(StringField())

class Targets(Document):
    name = StringField()
    success = ListField(EmbeddedDocumentField(Success))


# Offices model
class Offices(Document):
    name = StringField()
    head = StringField()
    opcr = ListField(StringField())