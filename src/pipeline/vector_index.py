class VectorIndex:
    def __init__(self, name, inputs, embedding_model, catalog, schema, table):
        self.name = name
        self.inputs = inputs
        self.embedding_model = embedding_model
        self.catalog = catalog
        self.schema = schema
        self.table = table
