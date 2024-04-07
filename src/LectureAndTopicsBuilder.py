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

    courses = [
        ('COMP', '474', 'Intelligent Systems'),
        ('COMP', '479', 'Information Retrieval and Web Search')
    ]

    # Define lecture topics
    lecture_topics = {
        'COMP-474': [DBPEDIA.Intelligent_system, DBPEDIA.Knowledge_representation_and_reasoning],
        'COMP-479': [DBPEDIA.Information_retrieval, DBPEDIA.Web_search_engine]
    }

    for course_dept, course_num, course_name in courses:
        course_code = f"{course_dept}-{course_num}"
        course_uri = EX[sanitize_string(course_code)]
        g.add((course_uri, RDF.type, VIVO.Course))
        g.add((course_uri, VIVO.courseCode, Literal(course_dept)))
        g.add((course_uri, VIVO.courseNumber, Literal(course_num)))
        g.add((course_uri, RDFS.label, Literal(course_name)))

        lectures_dir = f"src/res/{course_dept}-{course_num}/lectures"
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

            # Add topics to lectures and associated materials
            if course_code in lecture_topics and i <= len(lecture_topics[course_code]):
                topic = lecture_topics[course_code][i - 1]
                g.add((lecture_uri, EX.coversTopic, topic))

                # Add the same topic to associated worksheet, reading, and slides
                worksheet_uri = URIRef(f"file:///src/res/{course_code}/lectures%5Cworksheet_0{i}.pdf")
                reading_uri = URIRef(f"file:///src/res/{course_code}/lectures%5Creading_reading0{i}.pdf")
                slide_uri = URIRef(f"file:///src/res/{course_code}/lectures%5Cslides_0{i}.pdf")
                g.add((lecture_uri, VIVO.hasAssociatedDocument, worksheet_uri))
                g.add((lecture_uri, VIVO.hasAssociatedDocument, reading_uri))
                g.add((lecture_uri, VIVO.hasAssociatedDocument, slide_uri))
                g.add((worksheet_uri, EX.coversTopic, topic))
                g.add((reading_uri, EX.coversTopic, topic))
                g.add((slide_uri, EX.coversTopic, topic))
                g.add((slide_uri, RDF.type, EX.LectureSlides))

        g.add((course_uri, VIVO.numberOfCredits, Literal(4, datatype=XSD.integer)))
        g.add((course_uri, RDFS.seeAlso, EX[f"{course_code}/resources"]))

    g.serialize(destination='src/output/lecture_and_topics.ttl', format='turtle')
    return g
