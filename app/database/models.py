from mongoengine import Document, EmbeddedDocument, EmbeddedDocumentField, StringField, IntField, FloatField, ListField, DateField, BooleanField, ObjectIdField
from bson.objectid import ObjectId

class Accounts(Document):
    name = StringField(max_length=50, required=True)
    email = StringField(max_length=50, required=True)
    username = StringField(max_length=50, required=True)
    password = StringField(max_length=50, required=True)
    permission = StringField(max_length=50, required=True)
    superior = StringField(default='', required=False)

class Sessions(Document):
    userid = StringField(max_length=30, required=True)
    token = StringField(max_length=50, required=True)
    permission = StringField(max_length=50, required=True)
    expiration = DateField()

# OPCR model
class _success(EmbeddedDocument):
    oid = ObjectIdField(required=True, default=ObjectId, unique=True, primary_key=True, sparse=True)
    indicator = StringField()
    budget = FloatField()
    division = StringField()
    accomplishment = StringField()
    rating = ListField(IntField())
    remarks = ListField(StringField())
    assigned_to = ListField(StringField())

class Targets(EmbeddedDocument):
    oid = ObjectIdField(required=True, default=ObjectId, unique=True, primary_key=True)
    name = StringField()
    success = ListField(EmbeddedDocumentField(_success))

class OPCR(Document):
    targets = ListField(EmbeddedDocumentField(Targets))
    accepted = BooleanField(default=False)
    archived = BooleanField(default=False)
    status = StringField(default='in progress')
    owner = StringField()


# Campuses model
class _offices(EmbeddedDocument):
    oid = ObjectIdField(required=True, default=ObjectId, unique=True, primary_key=True)
    name = StringField()
    head = ObjectIdField(required=False, default=ObjectId, unique=True)
    opcr = ListField(StringField())

class Campuses(Document):
    name = StringField()
    offices = ListField(EmbeddedDocumentField(_offices))
    pmt = ListField(ObjectIdField(default=ObjectId, unique=True))