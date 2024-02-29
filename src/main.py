import re
import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import RDFS
import urllib.parse

#replace spaces with underscores
def sanitize_string(part):
    return urllib.parse.quote_plus(part.replace(' ', '_'))

# SPARQL query to find what course covers X topic
def what_course_contains_topic(graph, keyword):
    # Escape special characters for SPARQL regex
    escaped_keyword = re.escape(keyword)

    query_result = graph.query(
        """
        SELECT ?courseName WHERE {
            ?course ex:courseName ?courseName .
            ?course ex:description ?description .
            FILTER regex(?description, ?keyword, "i")
        }
        """,
        initBindings={'keyword': Literal(escaped_keyword)}
    )
    return [str(row.courseName) for row in query_result]


def main():
    # Read the excel file
    csv_file_path = './res/CATALOG.csv'  # Update with the path to your CSV file
    dataframe = pd.read_csv(csv_file_path)

    # Create the RDF graph
    g = Graph()

    # Define the namespace(s)
    ex = Namespace("http://example.org/vocab/")
    g.bind("ex", ex)

    # Define the URI for Concordia university
    concordia_uri = URIRef("http://example.org/vocab/ConcordiaUniversity")

    # Define Concordia university as a resource of type ex:University
    g.add((concordia_uri, RDF.type, ex.University))
    g.add((concordia_uri, RDFS.label, Literal("Concordia University")))

    # Iterate over the conconrdia courses excel file and add them to the graph
    for index, row in dataframe.iterrows():
        # sanitize excel because spaces etc
        course_code = sanitize_string(str(row['Course code']))
        course_number = sanitize_string(str(row['Course number']))

        # Create a new subject URI for each course
        course_uri = URIRef(f"http://example.org/vocab/{course_code}_{course_number}")

        # Add triples
        g.add((course_uri, RDF.type, ex.Course))
        g.add((course_uri, ex.courseName, Literal(row['Course Name'])))
        g.add((course_uri, ex.courseCode, Literal(row['Course code'])))
        g.add((course_uri, ex.courseNumber, Literal(row['Course number'])))
        g.add((course_uri, ex.description, Literal(row['Description'])))

        # Link the course to Concordia university
        g.add((course_uri, ex.offeredBy, concordia_uri))

        # This is where we add more triples to build our knowledge graph

    # Serialize the graph to a Turtle file
    turtle_file_path = './output/graph.ttl'  # Update with the path to your Turtle file
    g.serialize(destination=turtle_file_path, format='turtle')

    # Give me all the courses and their universities
    query_result = g.query(
        """
        SELECT ?course ?name ?university WHERE {
            ?course a ex:Course .
            ?course ex:courseName ?name .
            ?course ex:offeredBy ?university .
        }
        """
    )

    for row in query_result:
        print(f"Course URI: {row.course}, Course Name: {row.name}, Offered By: {row.university}")

    # What courses contain this topic?
    topic_keyword = "Machine Learning"
    courses_discussing_topic = what_course_contains_topic(g, topic_keyword)
    print(f"Courses discussing '{topic_keyword}':")
    for course in courses_discussing_topic:
        print(course)


if __name__ == '__main__':
    main()