from SPARQLWrapper import SPARQLWrapper, JSON
import re
def initSparqlWrapper():
    return  SPARQLWrapper("http://localhost:3030/Robot_Prof/sparql")

# Fuseki query 1: to get all courses and their universities
def FusekiQuery1(sparql):
    sparql.setQuery(
        """
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?course ?name ?university WHERE {
            ?course a vivo:Course .
            ?course rdfs:label ?name .
            ?course vivo:offeredBy ?university .            
        }
        """
    )
    sparql.setReturnFormat("json")
    try:
        ret=sparql.queryAndConvert()
        print(f"\nFuseki Response Q1:")
        for result in ret['results']['bindings']:
            print(f"{result['course']['value']} {result['name']['value']} {result['university']['value']}")
    except Exception as e:
        print(e)
# Fuseki query 2: to find what course covers a specific topic
def FusekiQuery2(sparql, keyword):
    escaped_keyword = re.escape(keyword)
    sparql.setQuery("""    
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?courseName WHERE {
            ?course a vivo:Course .
            ?course rdfs:label ?courseName .
            ?course vivo:description ?description .
            FILTER regex(str(?description), \"%s\", "i") .
            }
    """%(keyword))
    sparql.setReturnFormat("json")

    try:
        ret=sparql.queryAndConvert()
        print(f"\nFuseki Response Q2:\nCourses that discuss topic {keyword}:")
        for result in ret['results']['bindings']:
            print(result['courseName']['value'])
    except Exception as e:
        print(e)

# Fuseki query 11: to get [grade] of [student] who completed a given [course] [number]
def FusekiQuery11(sparql, value_stu, value_id, value_course):
    escaped_value_id = re.escape(value_id)
    escaped_value_course = re.escape(value_course)
    escaped_value_student = re.escape(value_stu)

    sparql.setQuery(
        """  
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?grade ?name WHERE{
            ?stu a vivo:Student .
            ?stu vivo:HasId ?stuId .
            ?stu foaf:name ?name .
          	?stu vivo:HasTaken ?subjectURI .
          	?subjectURI vivo:Grade ?grade .
          FILTER regex(str(?subjectURI),\"%s\","i") .
          FILTER regex(str(?subjectURI),\"%s\","i") .
          FILTER regex(str(?stu),\"%s\","i") .
        }
        """%(escaped_value_id,escaped_value_id,escaped_value_student)
    )
    sparql.setReturnFormat("json")
    try:
        ret=sparql.queryAndConvert()
        print(f"\nFuseki Response Q11:\nThis {escaped_value_student} has completed {escaped_value_course} {escaped_value_id} with grade:")
        for result in ret['results']['bindings']:
            print(result['grade']['value'])
    except Exception as e:
        print(e)



#Fuseki query 12:   to get {students:grade} who completed a given {course: number}
def FusekiQuery12(sparql, value_id, value_course):

    escaped_value_id = re.escape(value_id)
    escaped_value_course = re.escape(value_course)
    sparql.setQuery(
        """
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name ?stuId WHERE {
            ?stu a vivo:Student .
            ?stu vivo:HasId ?stuId .
            ?stu foaf:name ?name .
  	        ?stu vivo:HasTaken ?subjectURI .
            FILTER
            regex(str(?subjectURI), \"%s\", "i").
            FILTER
            regex(str(?subjectURI), \"%s\", "i").
        }
        """%(escaped_value_id, escaped_value_course)
    )
    sparql.setReturnFormat("json")
    try:
        ret=sparql.queryAndConvert()
        print(f"\nFuseki Response Q12:\nThese students have complete {escaped_value_course} {escaped_value_id}:")
        for result in ret['results']['bindings']:
            print(result['name']['value']+" "+result['stuId']['value'])
    except Exception as e:
        print(e)


# Fuseki query 13: Print student transcript
#Note: this needs course ie: subject URI
def FusekiQuery13(sparql, value_stu):
    escaped_value_student = re.escape(value_stu)
    sparql.setQuery(
    """     
    PREFIX vivo: <http://vivoweb.org/ontology/core#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?name ?stuId ?sem ?grade ?subjectURI  WHERE {
    ?stu vivo:HasId ?stuId .
    ?stu foaf:name ?name .
    ?stu vivo:HasTaken ?subjectURI .
    ?subjectURI vivo:Semester ?sem .
    ?subjectURI vivo:Grade ?grade .
    FILTER regex(str(?name),\"%s\","i") .
    }
    """%(escaped_value_student)
    )

    sparql.setReturnFormat("json")
    try:
        ret=sparql.queryAndConvert()

        print(f"\nFuseki Response Q13:\nTranscript for student:")
        for result in ret['results']['bindings']:
            print(f"{result['name']['value']} {result['stuId']['value']} {result['sem']['value']} {result['subjectURI']['value']} {result['grade']['value']} ")
    except Exception as e:
            print(e)
