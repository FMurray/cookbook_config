class DataSource:
    def __init__(self, name, type, path, format, catalog, schema, table):
        self.name = name
        self.type = type
        self.path = path
        self.format = format
        self.catalog = catalog
        self.schema = schema
        self.table = table
