import pymongo

class MongoDBConnection:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="crud-mongo"):
        self.cliente = pymongo.MongoClient(uri)
        self.bd = self.cliente[db_name]

    def get_collection(self, collection_name):
        """Devuelve una referencia a la colección especificada."""
        return self.bd[collection_name]

    def get_all_documents(self, collection_name):
        """Devuelve todos los documentos de una colección como lista de diccionarios."""
        coleccion = self.get_collection(collection_name)
        return list(coleccion.find())

    def delete_document(self, collection_name, query):
        """Elimina un documento de una colección en base a una consulta."""
        coleccion = self.get_collection(collection_name)
        result = coleccion.delete_one(query)
        return result.deleted_count  # Devuelve el número de documentos eliminados (debería ser 1 o 0)

    def insert_document(self, collection_name, document):
        """Inserta un documento en la coleccion especificada"""
        coleccion = self.get_collection(collection_name)
        result = coleccion.insert_one(document)
        return result.inserted_id #devuelve el id del documento insertado

    #metodo para otener el documento
    def get_document(self, collection_name, filter):
        return self.bd[collection_name].find_one(filter)

    def update_document(self, collection_name, filter, update):
        """Actualiza un documento en la colección especificada según el filtro y los datos de actualización."""
        coleccion = self.get_collection(collection_name)
        result = coleccion.update_one(filter, update)
        return result.modified_count  # Devuelve el número de documentos modificados (debería ser 1 o 0)