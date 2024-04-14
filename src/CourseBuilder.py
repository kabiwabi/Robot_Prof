import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import RDFS, FOAF, XSD
import urllib.parse

vivo = Namespace("http://vivoweb.org/ontology/core#")


def sanitize_string(part):
    return urllib.parse.quote_plus(part.replace(' ', '_'))


def is_valid_url(url):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_courses():
    csv_file_path = 'res/CATALOG.csv'
    dataframe = pd.read_csv(csv_file_path)

    courses = []
    for index, row in dataframe.iterrows():
        faculty = sanitize_string(str(row['Faculty']))
        course_code = sanitize_string(str(row['Course code']))
        course_num = sanitize_string(str(row['Course number']))
        courses.append((faculty, course_code, course_num, row['Course Name']))

    return courses


def build_course_graph():
    g = Graph()
    g.bind("vivo", vivo)
    # Define the Course class
    g.add((vivo.Course, RDF.type, RDFS.Class))

    csv_file_path = 'res/CATALOG.csv'
    dataframe = pd.read_csv(csv_file_path)

    concordia_uri = URIRef("http://example.org/vocab/ConcordiaUniversity")

    courses = []
    for index, row in dataframe.iterrows():
        course_code = sanitize_string(str(row['Course code']))
        course_num = sanitize_string(str(row['Course number']))
        faculty = sanitize_string(str(row['Faculty']))
        website = row['Website']
        course_uri = URIRef(f"http://example.org/vocab/{course_code}-{course_num}")

        g.add((course_uri, RDF.type, vivo.Course))
        g.add((course_uri, RDFS.label, Literal(row['Course Name'])))
        g.add((course_uri, vivo.courseCode, Literal(course_code)))
        g.add((course_uri, vivo.courseNumber, Literal(course_num)))
        g.add((course_uri, vivo.description, Literal(row['Description'])))
        g.add((course_uri, vivo.offeredBy, concordia_uri))
        if website and str(website).strip() and is_valid_url(str(website)):
            g.add((course_uri, RDFS.seeAlso, URIRef(str(website))))

    g.serialize(destination='output/course.ttl', format='turtle')
    return g
