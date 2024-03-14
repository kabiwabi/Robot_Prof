from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import FOAF, RDFS


vivo = Namespace("http://vivoweb.org/ontology/core#")

def build_university_graph():
    g = Graph()
    g.bind("vivo", vivo)
    g.bind("foaf", FOAF)

    # Define the University class
    g.add((vivo.University, RDF.type, RDFS.Class))

    # Create triples for Concordia Universty
    concordia_uri = URIRef("http://example.org/vocab/ConcordiaUniversity")
    g.add((concordia_uri, RDF.type, vivo.University))
    g.add((concordia_uri, RDFS.label, Literal("Concordia University")))
    g.add((concordia_uri, RDFS.seeAlso, URIRef("http://dbpedia.org/resource/Concordia_University")))
    g.add((concordia_uri, RDFS.seeAlso, URIRef("https://www.wikidata.org/wiki/Q1108272")))
    g.add((concordia_uri, vivo.description, Literal("A public university located in Montreal, Quebec, Canada.")))

    g.serialize(destination='./output/university.ttl', format='turtle')

    # Return the graph
    return g