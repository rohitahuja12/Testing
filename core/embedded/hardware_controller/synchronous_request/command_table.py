class CommandTable(dict):

    @staticmethod
    def fromDict(inputTable):
        outputTable = {
            "help": lambda: outputTable,
            **inputTable
        }
        return CommandTable(outputTable)

    @staticmethod
    def fromObject(obj):
        # map obj methods onto dict
        objectTable = {
            name:getattr(obj, name)
            for name in dir(obj) 
            if callable(getattr(obj, name))
            and not name.startswith('__')
        }
        return CommandTable.fromDict(objectTable)


