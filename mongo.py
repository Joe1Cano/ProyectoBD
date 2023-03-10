from pymongo import MongoClient
import certifi 


MONGO_URI = "mongodb+srv://prueba:abc1234@cluster0.eaaksxc.mongodb.net/?retryWrites=true&w=majority"
ca = certifi.where()

def dbConnection():
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=ca)
        db = client["Proyect_db"]
    except ConnectionError:
        print("Error en la base de datos")
    return db