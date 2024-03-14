import re
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import RDFS, FOAF, DCTERMS, XSD
import urllib.parse
import StudentGenerator as SG

SPARQLSERVER=True
if(SPARQLSERVER):
    import Fuseki_Queries as FQ

# Define the namespaces
vivo = Namespace("http://vivoweb.org/ontology/core#")
schema = Namespace("http://schema.org/")


# Function to replace spaces with underscores and URL-encode for valid URIs
def sanitize_string(part):
    return urllib.parse.quote_plus(part.replace(' ', '_'))


# SPARQL query 1: to get all courses and their universities
def get_courses_and_universities(graph):
    query_result = graph.query(
        """
        SELECT ?course ?name ?university WHERE {
            ?course a vivo:Course .
            ?course rdfs:label ?name .
            ?course vivo:offeredBy ?university .            
        }
        """
    )
    return [(str(row.course), str(row.name), str(row.university)) for row in query_result]
# SPARQL query 2: to find what course covers a specific topic
def what_course_contains_topic(graph, keyword):
    escaped_keyword = re.escape(keyword)
    query_result = graph.query(
        """
        SELECT ?courseName WHERE {
            ?course a vivo:Course .
            ?course rdfs:label ?courseName .
            ?course vivo:description ?description .
            FILTER regex(?description, ?keyword, "i")
        }
        """,
        initBindings={'keyword': Literal(escaped_keyword)}
    )
    return [str(row.courseName) for row in query_result]
# SPARQL query 4: List all [courses] offered by [university] within the [subject] (e.g., “COMP”, “SOEN”).
def all_courses_offered_Uni_in_Subject(graph, value_uni, value_courseName):
    escaped_value_uni = re.escape(value_uni)
    escaped_value_courseName = re.escape(value_courseName)
    query_result = graph.query(
        """
        SELECT ?course ?university WHERE{
            ?course vivo:courseCode ?courseCode .  
  			?course rdfs:label ?name .
            ?course vivo:offeredBy ?university .
            FILTER regex(str(?courseCode), ?value_courseName, "i") .
            FILTER regex(str(?university), ?value_uni,"i") .
        }
        """,
        initBindings={'value_courseName': Literal(escaped_value_courseName), 'value_uni': Literal(escaped_value_uni, datatype=XSD.string)}
    )
    return [(str(row.course), str(row.university)) for row in query_result]
# SPARQL query 10: What competencies [topics] does a student gain after completing [course] [number]?
def competencies_gained_from_course_courseNum(graph, value_courseCode, value_courseNum):
    escaped_value_courseName = re.escape(value_courseCode)
    escaped_value_courseNumber = re.escape(value_courseNum)
    query_result = graph.query(
        """
        SELECT ?description WHERE{
            ?course vivo:courseCode ?courseCode .  
  			?course vivo:courseNumber ?courseNumber .
  			?course vivo:description ?description
            FILTER regex(str(?courseCode), ?value_courseName, "i") .
            FILTER regex(str(?courseNumber), ?value_courseNumber,"i") .
        }
        """,
        initBindings={'value_courseName': Literal(escaped_value_courseName), 'value_courseNumber': Literal(escaped_value_courseNumber, datatype=XSD.string)}
    )
    return [(str(row.description)) for row in query_result]


# SPARQL query 11: to get [grade] of [student] who completed a given [course] [number]
def get_grades_of_student_who_completed_course(graph, value_stu, value_id, value_course):
    escaped_value_id = re.escape(value_id)
    escaped_value_course = re.escape(value_course)
    escaped_value_student = re.escape(value_stu)

    query_result = graph.query(
        """  
SELECT ?grade WHERE{
    ?stu a vivo:Student .
    ?stu vivo:HasId ?stuId .
    ?stu foaf:name ?name .
  	?stu vivo:HasTaken ?subjectURI .
  	?subjectURI vivo:Grade ?grade .
  FILTER regex(str(?subjectURI),?value_id,"i") .
  FILTER regex(str(?subjectURI),?value_course,"i") .
  FILTER regex(str(?stu),?value_student,"i") .
}
        """,
        initBindings={'value_id': Literal(escaped_value_id, datatype=XSD.string),
                      'value_course': Literal(escaped_value_course, datatype=XSD.string),
                      'value_student': Literal(escaped_value_student, datatype=XSD.string)}
    )
    return [str(row.grade) for row in query_result]
# SPARQL query 12:  to get {students:grade} who completed a given {course: number}
def get_students_who_completed_course(graph, value_id, value_course):
    escaped_value_id = re.escape(value_id)
    escaped_value_course = re.escape(value_course)

    query_result = graph.query(
        """  
SELECT ?name ?stuId WHERE{
    ?stu a vivo:Student .
    ?stu vivo:HasId ?stuId .
    ?stu foaf:name ?name .
  	?stu vivo:HasTaken ?subjectURI .
  FILTER regex(str(?subjectURI),?value_id,"i") .
  FILTER regex(str(?subjectURI),?value_course,"i") .
}
        """,
        initBindings={'value_id': Literal(escaped_value_id, datatype=XSD.string),
                      'value_course': Literal(escaped_value_course, datatype=XSD.string)}
    )
    return query_result

# SPARQL query 13: print a transcript for {students}
def get_students_Transcript(graph, value_stu):
    escaped_value_student = re.escape(value_stu)

    query_result = graph.query(
        """        
SELECT ?name ?stuId ?subjectURI ?sem ?grade  WHERE{
    ?stu a vivo:Student .
    ?stu vivo:HasId ?stuId .
    ?stu foaf:name ?name .
    ?stu vivo:HasTaken ?subjectURI .
    ?subjectURI vivo:Semester ?sem .
    ?subjectURI vivo:Grade ?grade .
  filter regex(?name,?value_student,"i")
}
        """,
        initBindings={'value_student': Literal(escaped_value_student, datatype=XSD.string)}
    )
    return query_result

def main():
    if(SPARQLSERVER):
        sparql=FQ.initSparqlWrapper()

    csv_file_path = './res/CATALOG.csv'
    dataframe = pd.read_csv(csv_file_path)

    g = Graph()
    # Bind the namespaces
    g.bind("vivo", vivo)
    g.bind("schema", schema)

    concordia_uri = URIRef("http://example.org/vocab/ConcordiaUniversity")
    g.add((concordia_uri, RDF.type, FOAF.Organization))
    g.add((concordia_uri, RDFS.label, Literal("Concordia University")))
    g.add((concordia_uri, vivo.description, Literal("A public university located in Montreal, Quebec, Canada.")))
    courses = []
    course2 = {}

    for index, row in dataframe.iterrows():
        course_code = sanitize_string(str(row['Course code']))
        course_num = sanitize_string(str(row['Course number']))
        faculty = sanitize_string(str(row['Faculty']))
        course_uri = URIRef(f"http://example.org/vocab/{course_code}")

        g.add((course_uri, RDF.type, vivo.Course))
        g.add((course_uri, RDFS.label, Literal(row['Course Name'])))
        g.add((course_uri, vivo.courseCode, Literal(course_code)))
        g.add((course_uri, vivo.courseNumber, Literal(course_num)))
        g.add((course_uri, vivo.description, Literal(row['Description'])))
        g.add((course_uri, vivo.offeredBy, concordia_uri))

        course2[faculty] = (course_code, course_num, row['Course Name']);
        courses.append((faculty, course_code, course_num, row['Course Name']))

    # serialize the graph to a file
    turtle_file_path = './output/graph.ttl'
    g.serialize(destination=turtle_file_path, format='turtle')

    # generate Student Graph  and combine it with class graph
    g2 = SG.GenerateandReturn(courses)
    g = g + g2

    # serialize the graph to a file
    turtle_file_path = './output/combinedGraph.ttl'
    g.serialize(destination=turtle_file_path, format='turtle')

    # first query: get all courses and their universities
    courses_and_universities = get_courses_and_universities(g)
    for course_uri, course_name, university in courses_and_universities:
        print(f"Course URI: {course_uri}, Course Name: {course_name}, Offered By: {university}")

    # second query: find what course covers a specific topic
    topic_keyword = "artificial intelligence"
    courses_discussing_topic = what_course_contains_topic(g, topic_keyword)
    print(f"\nCourses discussing '{topic_keyword}':")
    for course in courses_discussing_topic:
        print(course)

    #fourth query: all courses belonging to COEN from Concordia
    example = all_courses_offered_Uni_in_Subject(g,"conc","COEN")
    i=1
    print("\n\nQ4: These are the courses within [Coen] offered by [concordia]")
    for  course, uni in (example):
        print(f"{i}: {course} offerend by: {uni}")
        i+=1

    #tenth query:
    sol=competencies_gained_from_course_courseNum(g,"stat","380")
    print("\n\nQ10:")
    for description in sol:
        print(description)

    # eleventh query: get [grade] of [student] who has complete [course] [number]
    students_who_completed_x = get_grades_of_student_who_completed_course(g, "Ilise", "506", "coms")
    print(f"\n Q11:\nIlise Ramsey Completed: Coms 506 with grade of:")
    for grade in students_who_completed_x:
        print(grade)

    # twelth query: which [students] have completed [value_course] [value_id]
    students_who_completed_x = get_students_who_completed_course(g, "506", "Coms")
    print('\nQuery 12')
    for o, t in students_who_completed_x:
        print(f"{o} {t}")

    # thirteenth query: print transcript for a [student] listing all courses along with grade acheived
    student_transcript = get_students_Transcript(g, "Braun")
    print('\nQuery 13')
    #?name ?stuId ?subjectURI ?sem ?grade
    for name,stuID,subject, sem, grade in student_transcript:
        print(f"{name} {sem} {subject} {grade} ")

    if SPARQLSERVER:
        FQ.FusekiQuery1(sparql)
        FQ.FusekiQuery2(sparql,"artificial intelligence")
        FQ.FusekiQuery4(sparql,"conc","coen")
        FQ.FusekiQuery10(sparql,"stat","380")
        FQ.FusekiQuery11(sparql,"Ilise", "506", "coms")
        FQ.FusekiQuery12(sparql,"506", "Coms")
        FQ.FusekiQuery13(sparql,"Braun")

if __name__ == '__main__':
    main()
