import logging
from logic import modelOperations, utils
from models.Argument import Argument
from models.Relation import Relation
from models.ZoneLabels import ZoneLabel

logger = logging.getLogger(__name__)

class Section:
    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.inferenced_text = []
        self.arguments: list[Argument] = []
        self.relations: list[Relation] = []
        self.zone_labels: list[ZoneLabel] = []

    def populate_inferenced_text(self, calculate_zone_labels=True):
        modified_text = utils.remove_paranthesis(self.body)
        section_sents = modelOperations.get_section_sentences(modified_text)
        joined_batches = [' '.join(batch) for batch in section_sents]
        self.inferenced_text = modelOperations.generate_augmented_text(joined_batches)

        if self.inferenced_text is not None:
            # extracted_components = [utils.extract_components(inferenced) for inferenced in self.inferenced_text]
            extracted_components = [utils.extract_components_with_zones(inferenced) for inferenced in self.inferenced_text]

            for component in extracted_components:
                for item in component:
                    # self.arguments.append(utils.extract_argument_info(item, self.body, self.title))
                    # self.arguments.append(utils.extract_argument_info_with_zoning(item, self.body, self.title))
                    self.arguments.append(utils.extract_argument_info_with_zoning(item, modified_text, self.title))

            extracted_relations = [utils.extract_relations(inferenced, self.title) for inferenced in self.inferenced_text]
            # extracted_relations = [utils.extract_relations_with_zones(inferenced, self.title) for inferenced in self.inferenced_text]
            for relations in extracted_relations:
                for relation in relations:
                    self.relations.append(relation)

            if calculate_zone_labels:
                # argument zoning
                sentences = [sent for section_sent in section_sents for sent in section_sent]
                label_sentence_pair = modelOperations.inference_from_model(sentences)
                self.zone_labels.extend([ZoneLabel(label, sentence, self.title) for sentence, label in label_sentence_pair])
        else:
            logger.log(logging.WARNING, "No inferenced text found for section {} and possible text: {}".format(self.title, joined_batches))