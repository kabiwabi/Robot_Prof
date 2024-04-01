import os
import PyPDF2
import spacy
from rdflib import Graph, URIRef, Literal, Namespace

EX = Namespace("http://example.org/")
DBR = Namespace("http://dbpedia.org/resource/")


def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ""
        for page in range(reader.numPages):
            text += reader.getPage(page).extractText()
    return text


def preprocess_course_materials(course_dir, output_dir):
    for root, dirs, files in os.walk(course_dir):
        for file in files:
            if file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                text = extract_text_from_pdf(file_path)
                output_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.txt")
                with open(output_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(text)


def load_spacy_model():
    nlp = spacy.load("en_core_web_sm")
    return nlp


def link_entities(text, nlp):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC"]:
            entities.append((ent.text, ent.label_, spacy.kb.get_candidates(nlp, ent.text)))
    return entities


def create_topic_triples(entities, course_uri, event_uri, resource_uri):
    triples = []
    for entity in entities:
        topic_uri = DBR[entity[0].replace(" ", "_")]
        triples.append((course_uri, EX.hasTopic, topic_uri))
        triples.append((event_uri, EX.coversTopic, topic_uri))
        triples.append((resource_uri, EX.mentionsTopic, topic_uri))
    return triples


def add_triples_to_graph(triples, graph):
    for triple in triples:
        graph.add(triple)


def build_knowledge_base(course_dir, output_dir):
    preprocess_course_materials(course_dir, output_dir)

    nlp = load_spacy_model()
    graph = Graph()

    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as input_file:
                    text = input_file.read()
                    entities = link_entities(text, nlp)
                    course_uri = EX[os.path.basename(root)]
                    event_uri = EX[os.path.splitext(file)[0]]
                    resource_uri = EX[file]
                    triples = create_topic_triples(entities, course_uri, event_uri, resource_uri)
                    add_triples_to_graph(triples, graph)

    return graph