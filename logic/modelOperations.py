import torch
from transformers import pipeline, BartForConditionalGeneration, BartTokenizer, T5Tokenizer, T5ForConditionalGeneration, \
    AutoTokenizer, AutoModelForSequenceClassification

from sentence_transformers import SentenceTransformer, util
from config import ConfigManager
import spacy

config = ConfigManager().config
nlp = spacy.load("en_core_web_sm")  # Load a small English NLP model
ZONE_LABELS = ['BACKGROUND', 'OBJECTIVE', 'METHODS', 'RESULTS', 'CONCLUSIONS']
ZONE_ID2LABEL = {idx: label for idx, label in enumerate(ZONE_LABELS)}
ZONE_LABEL2ID = {label: idx for idx, label in enumerate(ZONE_LABELS)}

def generate_augmented_text(text):
    # model_name = config.model_name

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # model = BartForConditionalGeneration.from_pretrained(model_name).to(device)
    # tokenizer = BartTokenizer.from_pretrained(model_name)
    model, tokenizer = get_model_and_tokenizer(device)
    # max_length = model.config.max_position_embeddings
    max_length = 1024

    if (len(text) > 0):
        input = (tokenizer(text, return_tensors="pt", padding='max_length', truncation=True, max_length=max_length)
                 .to(device))

        try:
            outputs = model.generate(**input, max_new_tokens=max_length)
            generated_text = [tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
            return generated_text
        except Exception as e:
            # Log or handle errors during generation
            raise RuntimeError(f"Error generating augmented text: {e}")


def inference_from_model(texts):
    zone_model = config.zone_model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    zoning_tokenizer = AutoTokenizer.from_pretrained(zone_model)
    zoning_model = AutoModelForSequenceClassification.from_pretrained(zone_model).to(device)

    inputs = zoning_tokenizer(texts, return_tensors="pt", truncation=True, padding="max_length", max_length=512)
    model_inputs = {key: val.to(device) for key, val in inputs.items()}
    # Get model predictions
    with torch.no_grad():
        outputs = zoning_model(**model_inputs)
        logits = outputs.logits
        preds = torch.argmax(logits, dim=-1)
        items = [pred.item() for pred in preds]
        labels = [item for item in items]

    return [(text, ZONE_ID2LABEL[label]) for text, label in zip(texts,labels)]

def get_section_sentences(content, max_length=1024):
    doc = nlp(content)
    sentences = [sent.text for sent in doc.sents]
    eligible_sents = []
    text_length = 0
    section_sentences = []

    for idx, sent in enumerate(sentences):
        words = [word for word in sent.split(' ')]
        text_length += len(words)
        if text_length > max_length:
            text_length = 0
            section_sentences.append(eligible_sents)
            eligible_sents = []
        eligible_sents.append(sent)

        if idx == len(sentences) - 1:
            section_sentences.append(eligible_sents)
    return section_sentences

def get_model_and_tokenizer(device):
    model = tokenizer = None
    if config.model_type == "BART":
        model = BartForConditionalGeneration.from_pretrained(config.model_name).to(device)
        tokenizer = BartTokenizer.from_pretrained(config.model_name)
    elif config.model_type == "T5":
        model = T5ForConditionalGeneration.from_pretrained(config.model_name).to(device)
        tokenizer = T5Tokenizer.from_pretrained(config.model_name)

    return model, tokenizer


def get_sentence_embeddings(model, base_sentence, sentence):
    embedding1 = model.encode(base_sentence, convert_to_tensor=True)
    embedding2 = model.encode(sentence, convert_to_tensor=True)

    similarity_score = util.pytorch_cos_sim(embedding1, embedding2)
    return similarity_score
