import re
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import RDFS, FOAF, DCTERMS, XSD
import urllib.parse

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

    for index, row in dataframe.iterrows():
        course_code = sanitize_string(str(row['Course code']))
        course_uri = URIRef(f"http://example.org/vocab/{course_code}")

        g.add((course_uri, RDF.type, vivo.Course))
        g.add((course_uri, RDFS.label, Literal(row['Course Name'])))
        g.add((course_uri, vivo.courseNumber, Literal(course_code)))
        g.add((course_uri, vivo.description, Literal(row['Description'])))
        g.add((course_uri, vivo.offeredBy, concordia_uri))

    # serialize the graph to a file
    turtle_file_path = './output/graph.ttl'
    g.serialize(destination=turtle_file_path, format='turtle')

    # first query: get all courses and their universities
    courses_and_universities = get_courses_and_universities(g)
    for course_uri, course_name, university in courses_and_universities:
        print(f"Course URI: {course_uri}, Course Name: {course_name}, Offered By: {university}")


    # second query: find what course covers a specific topic
    topic_keyword = "artificial intelligence"
    courses_discussing_topic = what_course_contains_topic(g, topic_keyword)
    print(f"Courses discussing '{topic_keyword}':")
    for course in courses_discussing_topic:
        print(course)

if __name__ == '__main__':
    main()