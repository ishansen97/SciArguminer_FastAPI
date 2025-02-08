from logic import modelOperations, utils
from models.Argument import Argument
from models.Relation import Relation


class Section:
    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.inferenced_text = []
        self.arguments: list[Argument] = []
        self.relations: list[Relation] = []

    def populate_inferenced_text(self):
        section_sents = modelOperations.get_section_sentences(self.body)
        joined_batches = [' '.join(batch) for batch in section_sents]
        self.inferenced_text = modelOperations.generate_augmented_text(joined_batches)
        extracted_components = [utils.extract_components(inferenced) for inferenced in self.inferenced_text]

        for component in extracted_components:
            for item in component:
                self.arguments.append(utils.extract_argument_info(item, self.body))

        extracted_relations = [utils.extract_relations(inferenced) for inferenced in self.inferenced_text]
        for relations in extracted_relations:
            for relation in relations:
                self.relations.append(relation)