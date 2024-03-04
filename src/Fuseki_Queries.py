from SPARQLWrapper import SPARQLWrapper, JSON
import re
def initSparqlWrapper():
    return  SPARQLWrapper("http://localhost:3030/Robot_Prof/sparql")

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


# Fuseki query 13: to get {students:grade} who completed a given {course: number}
def FusekiQuery13(sparql, value_stu):
    escaped_value_student = re.escape(value_stu)
    sparql.query(
        """        
    PREFIX vivo: <http://vivoweb.org/ontology/core#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT ?name ?stuId ?sem ?grade  WHERE{
    ?stu a vivo:Student .
    ?stu vivo:HasId ?stuId .
    ?stu foaf:name ?name .
    ?stu vivo:HasTaken ?subjectURI .
    ?subjectURI vivo:Semester ?sem .
    ?subjectURI vivo:Grade ?grade .
  filter regex(?name,\"%s\","i")
    }
    """%(escaped_value_student)
        )

    sparql.setReturnFormat("json")
    try:
        #NOTE: This does not work yet
        ret=sparql.queryAndConvert()
       # print(f"\nFuseki Response Q12:\nThese students have complete {escaped_value_course} {escaped_value_id}:")
        #for result in ret['results']['bindings']:
            #print(result['name']['value']+" "+result['stuId']['value'])
    except Exception as e:
            print(e)
