import random
from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import RDFS, FOAF, XSD

EX = Namespace("http://example.org/")
VIVO = Namespace("http://vivoweb.org/ontology/core#")

GRADES = ('A', 'B', 'C', 'D', 'F')
GRADE_MODIFIERS = ('-', '+', '')
FACULTIES = ('FFA', 'FAS', 'GCS', 'JMSB')
SEMESTERS = [
    VIVO.Summer2022, VIVO.Fall2022, VIVO.Winter2022,
    VIVO.Summer2023, VIVO.Fall2023, VIVO.Winter2023
]


def random_line(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()
    return random.choice(lines)


def generate_student_id():
    return str(random.randrange(100, 999)) + str(random.randrange(0, 999))


def generate_semester(courses, faculty):
    semester = []
    class_count = 0

    for faculty_code, course_code, course_no, course_name in courses:
        if (
                faculty_code == faculty and
                course_code != 'nan' and
                len(course_code) in (3, 4)
        ):
            semester.append((course_code, course_no, course_name))
            class_count += 1

            if class_count == 4:
                break

    return semester


def generate_random_grade():
    grade = random.choice(GRADES)
    modifier = random.choice(GRADE_MODIFIERS)
    return f"{grade}{modifier}"


def add_semester_to_graph(graph, student_uri, semester_uri, semester_classes):
    for course_code, course_num, course_name in semester_classes:
        course_uri = URIRef(f"http://example.org/vocab/{course_code}_{course_num}")

        graph.add((course_uri, RDF.type, URIRef(f"http://example.org/vocab/{course_code}")))
        graph.add((student_uri, VIVO.HasTaken, course_uri))
        graph.add((course_uri, VIVO.Grade, Literal(generate_random_grade())))
        graph.add((course_uri, VIVO.Semester, semester_uri))


def build_student_graph(courses, num_students=2, num_semesters=2):
    g = Graph()
    g.bind('ex', EX)
    g.bind("vivo", VIVO)

    g.add((VIVO.Student, RDF.type, RDFS.Class))
    g.add((VIVO.Student, RDFS.range, FOAF.Person))

    random.seed(1)

    for _ in range(num_students):
        semester_classes = []
        faculty = random.choice(FACULTIES)

        random.shuffle(courses)

        for _ in range(num_semesters):
            semester_classes.append(generate_semester(courses, faculty))
            random.shuffle(courses)

        first_name = random_line("res/first-names.txt")
        last_name = random_line("res/last-names.txt")
        student_id = generate_student_id()
        email = f"{first_name[0:2].lower()}_{last_name[0:3].lower()}@live.concordia.ca"

        student_uri = URIRef(f"http://example.org/Student/{last_name},{first_name}")

        g.add((student_uri, RDF.type, VIVO.Student))
        g.add((student_uri, FOAF.name, Literal(f"{first_name} {last_name}", datatype=XSD.string)))
        g.add((student_uri, VIVO.HasId, Literal(f'{student_id}', datatype=XSD.string)))
        g.add((student_uri, EX.HasEmail, Literal(f'{email}', datatype=XSD.string)))

        if len(semester_classes) <= 6:
            for index, semester_class in enumerate(semester_classes):
                add_semester_to_graph(g, student_uri, SEMESTERS[index], semester_class)

    g.serialize(destination='output/student.ttl', format='turtle')
    return g
