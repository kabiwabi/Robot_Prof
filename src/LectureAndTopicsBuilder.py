import os
from urllib.parse import quote
from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import RDFS, XSD
from CourseBuilder import sanitize_string
import PyPDF2
import spacy
from spacy.matcher import PhraseMatcher
from spacy.kb import KnowledgeBase

EX = Namespace("http://example.org/")
VIVO = Namespace("http://vivoweb.org/ontology/core#")
DBPEDIA = Namespace("https://dbpedia.org/resource/")


def build_lecture_and_topics_graph():
    g = Graph()
    g.bind('ex', EX)
    g.bind("vivo", VIVO)
    g.bind("dbpedia", DBPEDIA)

    g.add((EX.Lecture, RDF.type, RDFS.Class))
    g.add((EX.Lecture, RDFS.label, Literal("Lecture")))
    g.add((EX.Lecture, RDFS.comment, Literal("A class representing a lecture in a course.")))

    g.add((EX.LectureSlides, RDF.type, RDFS.Class))
    g.add((EX.LectureSlides, RDFS.label, Literal("Lecture Slides")))
    g.add((EX.LectureSlides, RDFS.comment, Literal("A class representing the slides associated with a lecture.")))
    g.add((EX.LectureSlides, RDFS.subClassOf, EX.Lecture))

    g.add((EX.LectureReading, RDF.type, RDFS.Class))
    g.add((EX.LectureReading, RDFS.label, Literal("Lecture Reading")))
    g.add((EX.LectureReading, RDFS.comment,
           Literal("A class representing the reading material associated with a lecture.")))
    g.add((EX.LectureReading, RDFS.subClassOf, EX.Lecture))

    g.add((EX.LectureWorksheet, RDF.type, RDFS.Class))
    g.add((EX.LectureWorksheet, RDFS.label, Literal("Lecture Worksheet")))
    g.add((EX.LectureWorksheet, RDFS.comment, Literal("A class representing the worksheet associated with a lecture.")))
    g.add((EX.LectureWorksheet, RDFS.subClassOf, EX.Lecture))

    # Define domain and range for custom relationships
    g.add((EX.coversTopic, RDF.type, RDF.Property))
    g.add((EX.coversTopic, RDFS.domain, EX.Lecture))
    g.add((EX.coversTopic, RDFS.range, DBPEDIA.Resource))

    g.add((EX.mentionsTopic, RDF.type, RDF.Property))
    g.add((EX.mentionsTopic, RDFS.domain, EX.Lecture))
    g.add((EX.mentionsTopic, RDFS.range, DBPEDIA.Resource))

    courses = [
        ('COMP', '474', 'Intelligent Systems'),
        ('COMP', '479', 'Information Retrieval and Web Search')
    ]

    # Load the spaCy English language model and add the entityfishing pipe
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe('entityfishing')

    # Set the confidence threshold for entity linking
    confidence_threshold = 0.5

    # Perform entity linking using spaCy-fishing
    def link_entities(text):
        doc = nlp(text)
        entities = []
        for ent in doc.ents:
            if ent._.nerd_score is not None and ent._.nerd_score >= confidence_threshold:
                entities.append(ent)
        return entities

    for course_dept, course_num, course_name in courses:
        course_code = f"{course_dept}-{course_num}"
        course_uri = EX[sanitize_string(course_code)]
        g.add((course_uri, RDF.type, VIVO.Course))
        g.add((course_uri, VIVO.courseCode, Literal(course_dept)))
        g.add((course_uri, VIVO.courseNumber, Literal(course_num)))
        g.add((course_uri, RDFS.label, Literal(course_name)))

        lectures_dir = f"res/{course_dept}-{course_num}/lectures"
        lecture_files = os.listdir(lectures_dir)

        for lecture_file in lecture_files:
            lecture_file_path = os.path.join(lectures_dir, lecture_file)
            lecture_file_uri = URIRef(f"file:///{quote(lecture_file_path)}")

            # Differentiate between reading, slides, and worksheets based on file name
            if lecture_file.endswith('.pdf'):
                if 'reading' in lecture_file.lower():
                    g.add((lecture_file_uri, RDF.type, EX.LectureReading))
                    resource_type = 'reading'
                elif 'slides' in lecture_file.lower():
                    g.add((lecture_file_uri, RDF.type, EX.LectureSlides))
                    resource_type = 'slides'
                elif 'worksheet' in lecture_file.lower():
                    g.add((lecture_file_uri, RDF.type, EX.LectureWorksheet))
                    resource_type = 'worksheet'
                else:
                    continue

                # Extract the resource number from the file name
                resource_num = lecture_file.split('_')[-1].split('.')[0]

                # Create the resource URI
                resource_uri = EX[f"{course_code}/{resource_type}{resource_num}"]
                g.add((resource_uri, RDF.type, EX[resource_type.capitalize()]))
                g.add((resource_uri, VIVO.partOf, course_uri))
                g.add((resource_uri, VIVO.hasAssociatedDocument, lecture_file_uri))

                # Extract text from PDF files
                with open(lecture_file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()

                # Save the extracted text to a plain text file
                plain_text_file = f"{course_code}_{resource_type}{resource_num}.txt"
                plain_text_path = os.path.join("res", course_code, "plain_text", plain_text_file)
                os.makedirs(os.path.dirname(plain_text_path), exist_ok=True)
                with open(plain_text_path, 'w', encoding='utf-8') as file:
                    file.write(text)

                # Perform entity linking using spaCy-fishing
                entities = link_entities(text)
                for ent in entities:
                    topic_uri = ent._.url_wikidata
                    g.add((resource_uri, EX.coversTopic, URIRef(topic_uri)))
                    g.add((URIRef(topic_uri), RDFS.label, Literal(ent.text)))
                    g.add((lecture_file_uri, EX.mentionsTopic, URIRef(topic_uri)))
                    g.add((course_uri, VIVO.hasTopic, URIRef(topic_uri)))

        g.add((course_uri, VIVO.numberOfCredits, Literal(4, datatype=XSD.integer)))
        g.add((course_uri, RDFS.seeAlso, EX[f"{course_code}/resources"]))

    g.serialize(destination='output/lecture_and_topics.ttl', format='turtle')
    return g