from models.Argument import Argument

class Relation:
    def __init__(self, head, tail, relation):
        self.head: Argument = head
        self.tail: Argument = tail
        self.relation = relation