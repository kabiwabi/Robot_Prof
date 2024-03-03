import re
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import RDFS, FOAF, DCTERMS, XSD
import urllib.parse
import StudentGenerator as SG

# Define the namespaces
vivo = Namespace("http://vivoweb.org/ontology/core#")
schema = Namespace("http://schema.org/")

# Function to replace spaces with underscores and URL-encode for valid URIs
def sanitize_string(part):
    return urllib.parse.quote_plus(part.replace(' ', '_'))

# SPARQL query to find what course covers a specific topic
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
def get_students_who_completed_course(graph,value_id,value_course):
    escaped_value_id = re.escape(value_id)
    escaped_value_course = re.escape(value_course)

    # filter regex(str(?student),"http://example.org/Student/Ballard,Darcy","i")
    # filter regex(str(?s),"BIO","i")
    query_result = graph.query(
        """        
SELECT ?student ?grade ?subjectURI ?courseNum WHERE{
	?subjectURI a vivo:Course  . 
  	?subjectURI vivo:courseNumber ?courseNum .
    ?subjectURI vivo:courseCode ?course . 
  	?student a ex:Student .
  	?student vivo:Semester ?x .
  	?x vivo:TookCourse ?subjectURI  .	 
  	?subjectURI vivo:Grade ?grade .
  FILTER regex(str(?courseNum),"330","i") .
  FILTER regex(str(?course),"BIOL","i")
}
        """,
        initBindings={'Svalue_id': Literal(escaped_value_id,datatype=XSD.string),'Svalue_course': Literal(escaped_value_course,datatype=XSD.string)}
    )
    return query_result
    return [(str(row.student),str(row.grade),str(row.s),str(row.id)) for row in query_result]

# SPARQL query to get all courses and their universities
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
def main():
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
    courses= []
    course2={}

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

        course2[faculty] = (course_code,course_num,row['Course Name']);
        courses.append((faculty,course_code,course_num,row['Course Name']))

    # serialize the graph to a file
    turtle_file_path = './output/graph.ttl'
    g2=SG.GenerateandReturn(courses)
    g=g+g2
    students_who_completed_x=get_students_who_completed_course(g,"330","BIOL")
    for o,t,th,fo in students_who_completed_x:
        print(f"{o} {t} {th} {fo}")
    g.serialize(destination=turtle_file_path, format='turtle')

    # first query: get all courses and their universities
    courses_and_universities = get_courses_and_universities(g)
    # for course_uri, course_name, university in courses_and_universities:
    #     print(f"Course URI: {course_uri}, Course Name: {course_name}, Offered By: {university}")

    #
    # # second query: find what course covers a specific topic
    # topic_keyword = "artificial intelligence"
    # courses_discussing_topic = what_course_contains_topic(g, topic_keyword)
    # print(f"Courses discussing '{topic_keyword}':")
    # for course in courses_discussing_topic:
    #     print(course)

if __name__ == '__main__':
    main()