from flask_alchemydumps import AlchemyDumps
from server.common.database.ref import db

# init Alchemy Dumps
alchemydumps = AlchemyDumps(db)
