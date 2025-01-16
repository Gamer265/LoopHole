from decouple import config

class Var:
    MONGO_SRV = config("MONGO_SRV")
    SESSION_STRING = config("SESSION_STRING")
