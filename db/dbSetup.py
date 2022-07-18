from model import db, SavedTotal

db.connect()
db.create_tables([SavedTotal])

# only need to run `python dbSetup.py` once to create the database
# or if you need to modify the database
# you don't need to run this everytime you run the server
