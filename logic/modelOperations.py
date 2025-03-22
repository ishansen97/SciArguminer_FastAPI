import torch
from transformers import pipeline, BartForConditionalGeneration, BartTokenizer, T5Tokenizer, T5ForConditionalGeneration

from config import ConfigManager
import spacy

config = ConfigManager().config
nlp = spacy.load("en_core_web_sm")  # Load a small English NLP model


def generate_augmented_text(text):
    # model_name = config.model_name

    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = torch.device("cpu")
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
