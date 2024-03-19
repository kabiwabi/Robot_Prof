import os
from urllib.parse import quote
from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import RDFS, XSD
from CourseBuilder import sanitize_string

EX = Namespace("http://example.org/")
VIVO = Namespace("http://vivoweb.org/ontology/core#")
DBPEDIA = Namespace("https://dbpedia.org/resource/")

def build_lecture_and_topics_graph():
    g = Graph()
    g.bind('ex', EX)
    g.bind("vivo", VIVO)
    g.bind("dbpedia", DBPEDIA)

    g.add((EX.Lecture, RDF.type, RDFS.Class))
    g.add((EX.LectureSlides, RDFS.subClassOf, EX.Lecture))
    g.add((EX.LectureReading, RDFS.subClassOf, EX.Lecture))
    g.add((EX.LectureWorksheet, RDFS.subClassOf, EX.Lecture))

    courses = [
        ('COMP', '474', 'Intelligent Systems'),
        ('COMP', '479', 'Information Retrieval and Web Search')
    ]

    for course_dept, course_num, course_name in courses:
        course_code = f"{course_dept}-{course_num}"
        course_uri = EX[sanitize_string(course_code)]
        g.add((course_uri, RDF.type, VIVO.Course))
        g.add((course_uri, VIVO.courseCode, Literal(course_dept)))
        g.add((course_uri, VIVO.courseNumber, Literal(course_num)))
        g.add((course_uri, RDFS.label, Literal(course_name)))

        lectures_dir = f"./res/{course_dept}-{course_num}/lectures"
        lecture_files = os.listdir(lectures_dir)

        for i, lecture_file in enumerate(lecture_files, start=1):
            lecture_uri = EX[f"{course_code}/lecture{i}"]
            g.add((lecture_uri, RDF.type, EX.Lecture))
            g.add((lecture_uri, VIVO.rank, Literal(i, datatype=XSD.integer)))
            g.add((lecture_uri, VIVO.partOf, course_uri))

            lecture_file_path = os.path.join(lectures_dir, lecture_file)
            lecture_file_uri = URIRef(f"file:///{quote(lecture_file_path)}")
            g.add((lecture_uri, VIVO.hasAssociatedDocument, lecture_file_uri))

            if lecture_file.endswith('.pdf'):
                if 'slides' in lecture_file.lower():
                    g.add((lecture_file_uri, RDF.type, EX.LectureSlides))
                elif 'worksheet' in lecture_file.lower():
                    g.add((lecture_file_uri, RDF.type, EX.LectureWorksheet))
                elif 'reading' in lecture_file.lower():
                    g.add((lecture_file_uri, RDF.type, EX.LectureReading))

            # Manually adding topics for lectures
            if course_code == 'COMP-474':
                if i == 1:
                    g.add((lecture_uri, RDFS.label, Literal("Introduction to Intelligent Systems")))
                    g.add((lecture_uri, EX.coversTopic, DBPEDIA.Intelligent_system))
                    g.add((lecture_uri, RDFS.seeAlso, EX["COMP-474/lectures/1"]))
                    g.add((DBPEDIA.Intelligent_system, EX.topicSource, Literal("Course Outline")))
                elif i == 2:
                    g.add((lecture_uri, RDFS.label, Literal("Knowledge Representation")))
                    g.add((lecture_uri, EX.coversTopic, DBPEDIA.Knowledge_representation_and_reasoning))
                    g.add((lecture_uri, RDFS.seeAlso, EX["COMP-474/lectures/2"]))
                    g.add((DBPEDIA.Knowledge_representation_and_reasoning, EX.topicSource, Literal("Lecture Slides")))
            elif course_code == 'COMP-479':
                if i == 1:
                    g.add((lecture_uri, RDFS.label, Literal("Introduction to Information Retrieval")))
                    g.add((lecture_uri, EX.coversTopic, DBPEDIA.Information_retrieval))
                    g.add((lecture_uri, RDFS.seeAlso, EX["COMP-479/lectures/1"]))
                    g.add((DBPEDIA.Information_retrieval, EX.topicSource, Literal("Course Outline")))
                elif i == 2:
                    g.add((lecture_uri, RDFS.label, Literal("Web Search Basics")))
                    g.add((lecture_uri, EX.coversTopic, DBPEDIA.Web_search_engine))
                    g.add((lecture_uri, RDFS.seeAlso, EX["COMP-479/lectures/2"]))
                    g.add((DBPEDIA.Web_search_engine, EX.topicSource, Literal("Lecture Slides")))

        g.add((course_uri, VIVO.numberOfCredits, Literal(4, datatype=XSD.integer)))
        g.add((course_uri, RDFS.seeAlso, EX[course_code]))
        g.add((course_uri, RDFS.seeAlso, EX[f"{course_code}/resources"]))

    g.serialize(destination='./output/lecture_and_topics.ttl', format='turtle')
    return g