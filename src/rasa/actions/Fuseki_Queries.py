from rdflib import Literal
from rdflib import URIRef
import re
import os
from SPARQLWrapper import SPARQLWrapper, JSON


class FusekiQueries:
    def __init__(self):
        self.sparql = SPARQLWrapper("http://localhost:3030/Robot_Prof/sparql")


def initSparqlWrapper():
    return SPARQLWrapper("http://localhost:3030/Robot_Prof/sparql")


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
        ret = sparql.queryAndConvert()
        return ret["results"]["bindings"]
    except Exception as e:
        print(e)


# Fuseki query 2: to find what course covers a specific topic
def FusekiQuery2(sparql, keyword):
    sparql.setQuery("""    
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?course WHERE {
            ?course a vivo:Course .
            ?course vivo:description ?description .
            FILTER regex(str(?description), \"%s\", "i") .
            }
    """ % (keyword))
    sparql.setReturnFormat("json")

    try:
        ret = sparql.queryAndConvert()
        return ret
    except Exception as e:
        print(e)


# FQ 3
def FusekiQuery3(sparql, course, lecture_number):
    sparql.setQuery("""    
            PREFIX vivo: <http://vivoweb.org/ontology/core#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
			PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
			PREFIX ex: <http://example.org/>			
			PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT ?topic WHERE {
                ?lecture rdf:type ex:Lecture .
                ?lecture vivo:partOf ?course .
                ?lecture vivo:rank %d .
                ?lecture ex:coversTopic ?topic .
                FILTER regex(str(?course),  \"%s\",  "i") .
                }
        """ % (lecture_number, course))
    sparql.setReturnFormat("json")
    try:
        ret = sparql.queryAndConvert()
        return ret
    except Exception as e:
        print(e)


# Fuseki query 4: List all [courses] offered by [university] within the [subject] (e.g., “COMP”, “SOEN”).
def FusekiQuery4(sparql, value_uni, value_courseCode):
    uni_uri = URIRef("http://example.org/vocab/" + value_uni)
    sparql.setQuery("""    
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?course ?name WHERE{
            ?course vivo:courseCode ?courseCode .  
  			?course rdfs:label ?name .
            ?course vivo:offeredBy ?university .
            FILTER regex(str(?courseCode), \"%s\", "i") .
            FILTER regex(str(?university),  \"%s\") .
            }
    """ % (value_courseCode, uni_uri))
    sparql.setReturnFormat("json")

    try:
        ret = sparql.queryAndConvert()
        return ret
    except Exception as e:
        print(e)


# Fuseki query 5:
def FusekiQuery5(sparql, topic, course_dept, course_num):
    sparql.setQuery("""    
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
			PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
			PREFIX ex: <http://example.org/>			
        SELECT ?lecture ?reading ?worksheet ?slides
        WHERE {
            ?lecture rdf:type ex:Lecture .
            ?lecture vivo:partOf ?course .
            ?course vivo:courseCode ?courseDept .
            ?course vivo:courseNumber ?courseNum .
            ?lecture ex:coversTopic ?topic .

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?reading .
                ?reading rdf:type ex:LectureReading .
            }

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?worksheet .
                ?worksheet rdf:type ex:LectureWorksheet .
            }

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?slides .
                ?slides rdf:type ex:LectureSlides .
            }

            FILTER (str(?courseDept) = \"%s\") .
            FILTER (str(?courseNum) = \"%s\") .
            FILTER (str(?topic) = \"%s\") .
        }
    """ % (course_dept, course_num, topic))
    sparql.setReturnFormat("json")

    try:
        ret = sparql.queryAndConvert()
        return ret
    except Exception as e:
        print(e)


# Fuseki  Query #6
def FusekiQuery6(sparql, course, course_number):
    sparql.setQuery(
        """			
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>	
        SELECT ?credits WHERE {
            ?course rdf:type vivo:Course .
            ?course vivo:courseCode ?courseCode .
            ?course vivo:courseNumber ?courseNumber .
            ?course vivo:numberOfCredits ?credits .
            FILTER regex(str(?courseCode), \"%s\", "i") .
            FILTER regex(str(?courseNumber), \"%s\", "i") .
        }
        """ % (course, course_number))
    sparql.setReturnFormat("json")

    try:
        ret = sparql.queryAndConvert()
        return ret
    except Exception as e:
        print(e)


# Fuseki Query #7
def FusekiQuery7(sparql, course, course_number):
    sparql.setQuery(
        """
      	PREFIX vivo: <http://vivoweb.org/ontology/core#>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>  
        SELECT ?resource WHERE {
            ?course rdf:type vivo:Course .
            ?course vivo:courseCode ?courseCode .
            ?course vivo:courseNumber ?courseNumber .
            ?course rdfs:seeAlso ?resource .
            FILTER regex(str(?courseCode), \"%s\", "i") .
            FILTER regex(str(?courseNumber), \"%s\", "i") .
        }
        """ % (course, course_number))
    sparql.setReturnFormat("json")

    try:
        ret = sparql.queryAndConvert()
        return ret
    except Exception as e:
        print(e)


# Fuseki Query #8
def FusekiQuery8(sparql, course_code, course_number, lecture_number):
    sparql.setQuery(
        """			
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>		
        PREFIX ex: <http://example.org/>	
        SELECT ?lecture ?slides ?worksheet ?reading
        WHERE {
            ?lecture rdf:type ex:Lecture .
            ?lecture vivo:partOf ?course .
            ?course vivo:courseCode ?courseCode .
            ?course vivo:courseNumber ?courseNumber .
            ?lecture vivo:rank %d .

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?slides .
                ?slides rdf:type ex:LectureSlides .
            }

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?worksheet .
                ?worksheet rdf:type ex:LectureWorksheet .
            }

            OPTIONAL {
                ?lecture vivo:hasAssociatedDocument ?reading .
                ?reading rdf:type ex:LectureReading .
            }

            FILTER (str(?courseCode) = \"%s\") .
            FILTER (str(?courseNumber) = \"%s\") .
        }
        """ % (lecture_number, course_code, course_number,))
    sparql.setReturnFormat("json")
    try:
        ret = sparql.queryAndConvert()
        return ret
    except Exception as e:
        print(e)


# Query #9
def FusekiQuery9(sparql, topic, course_dept, course_num):
    sparql.setQuery(
        """
		PREFIX vivo: <http://vivoweb.org/ontology/core#>
		PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
		PREFIX ex: <http://example.org/>	
        SELECT ?reading
        WHERE {
            ?lecture rdf:type ex:Lecture .
            ?lecture vivo:partOf ?course .
            ?course vivo:courseCode ?courseDept .
            ?course vivo:courseNumber ?courseNum .
            ?lecture ex:coversTopic ?topic .
            ?lecture vivo:hasAssociatedDocument ?reading .
            ?reading rdf:type ex:LectureReading .
            FILTER (str(?courseDept) = \"%s\") .
            FILTER (str(?courseNum) = \"%s\") .
            FILTER (str(?topic) = \"%s\") .
        }
        """ % (course_dept, course_num, topic))
    sparql.setReturnFormat("json")
    try:
        ret = sparql.queryAndConvert()
        return ret
    except Exception as e:
        print(e)


# Fuseki query 10: What competencies [topics] does a student gain after completing [course] [number]?
def FusekiQuery10(sparql, value_courseCode, value_courseNum):
    sparql.setQuery(
        """
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?description WHERE{
            ?course vivo:courseCode ?courseCode .  
  			?course vivo:courseNumber ?courseNumber .
  			?course vivo:description ?description
            FILTER regex(str(?courseCode), \"%s\", "i") .
            FILTER regex(str(?courseNumber), \"%s\","i") .
        }
        """ % (value_courseCode, value_courseNum))
    sparql.setReturnFormat("json")
    try:
        ret = sparql.queryAndConvert()
        return ret
    except Exception as e:
        print(e)


# Fuseki query 11: to get [grade] of [student] who completed a given [course] [number]
def FusekiQuery11(sparql, value_stu, value_id, value_course):
    sparql.setQuery(
        """  
        PREFIX vivo: <http://vivoweb.org/ontology/core#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?grade WHERE{
            ?stu a vivo:Student .
            ?stu vivo:HasId ?stuId .
            ?stu foaf:name ?name .
          	?stu vivo:HasTaken ?subjectURI .
          	?subjectURI vivo:Grade ?grade .
            FILTER regex(str(?subjectURI),\"%s\","i") .
            FILTER regex(str(?subjectURI),\"%s\","i") .
            FILTER regex(str(?stu),\"%s\","i") .
        }
        """ % (value_course, value_id, value_stu)
    )
    sparql.setReturnFormat("json")
    try:
        ret = sparql.queryAndConvert()
        return ret
        # return ret
    except Exception as e:
        print(e)


# Fuseki query 12:   Which student have completed course
def FusekiQuery12(sparql, course_num, course_code):
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
        """ % (course_num, course_code)
    )
    sparql.setReturnFormat("json")
    try:
        ret = sparql.queryAndConvert()
        return ret
        # print(f"\nFuseki Response Q12:\nThese students have complete {escaped_value_course} {escaped_value_id}:")
        # for result in ret['results']['bindings']:
        #     print(result['name']['value'] + " " + result['stuId']['value'])
    except Exception as e:
        print(e)


# Fuseki query 13: Print student transcript
def FusekiQuery13(sparql, value_stu):
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
        """ % (value_stu)
    )

    sparql.setReturnFormat("json")
    try:
        ret = sparql.queryAndConvert()
        return ret
    except Exception as e:
        print(e)


def execute_fuseki_query(sparql, query_number, *args):
    output_dir = "src/output"
    output_file = f"{output_dir}/fuseki_{query_number}_output.txt"
    with open(output_file, 'w', encoding="utf-8") as file:
        match query_number:
            case 1:
                ret = FusekiQuery1(sparql)
                output = "\nFuseki Response Q1:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    output = f"{result['course']['value']} {result['name']['value']} {result['university']['value']}"
                    print(output)
                    file.write(output +
                               "\n")
            case 2:
                keyword = args
                ret = FusekiQuery2(sparql, keyword)
                output = f"\nFuseki Response Q2:\nCourses that discuss topic {keyword}:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    print(result['course']['value'])
                    file.write(result['course']['value'] + "\n")
            case 3:
                course, lecture_number = args
                ret = FusekiQuery3(sparql, course, lecture_number)
                output = f"\nFueski Response 3: Topics covered in {course} during lecture {lecture_number}:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    print(f"{result['topic']['value']}\n")
                    file.write(f"{result['topic']['value']}\n")
            case 4:
                uni, courseCode = args
                ret = FusekiQuery4(sparql, uni, courseCode)
                output = f"Fueski Response Q4: These are the courses with course code [{courseCode}] offered by [{uni}]"
                print(output)
                file.write(output + "\n")

                for i, result in enumerate(ret['results']['bindings'], start=1):
                    output = f"{i}: {result['course']['value']} {result['name']['value']}"
                    print(output)
                    file.write(output + "\n")

            case 5:
                topic, course_dept, course_num = args
                ret = FusekiQuery5(sparql, topic, course_dept, course_num)
                output = f"\nQuery 5: Materials recommended for {topic} in {course_dept} {course_num}:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    output = f"Lecture: {result['lecture']['value']}\nReading: {result['reading']['value']}\nWorksheet: {result['worksheet']['value']}\nSlides: {result['slides']['value']}\n---"
                    print(output)
                    file.write(output + "\n")

            case 6:
                course, course_number = args
                ret = FusekiQuery6(sparql, course, course_number)
                output = f"\nFuseki Response Q6: Credits for {course} {course_number}:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    print(result['credits']['value'])
                    file.write(result['credits']['value'] + "\n")

            case 7:
                course, course_number = args
                ret = FusekiQuery7(sparql, course, course_number)
                output = f"\nQuery 7: Additional resources for {course} {course_number}:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    print(result['resource']['value'])
                    file.write(result['resource']['value'] + "\n")

            case 8:
                course_code, course_number, lecture_number = args
                ret = FusekiQuery8(sparql, course_code, course_number, lecture_number)
                output = f"\nQuery 8: Content for lecture {lecture_number} in {course_code} {course_number}:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    output = f"Lecture: {result['lecture']['value']}\nReading: {result['reading']['value']}\nWorksheet: {result['worksheet']['value']}\nSlides: {result['slides']['value']}\n---"
                    print(output)
                    file.write(output + "\n")

            case 9:
                topic, course_dept, course_num = args
                ret = FusekiQuery9(sparql, topic, course_dept, course_num)
                output = f"\nQuery 9: Reading materials for {topic} in {course_dept} {course_num}:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    print(result['reading']['value'])
                    file.write(result['reading']['value'] + "\n")

            case 10:
                courseCode, courseNum = args
                ret = FusekiQuery10(sparql, courseCode, courseNum)
                output = f"\nFuseki Response Q10:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    output = f"{result['description']['value']}"
                    print(output)
                    file.write(output + "\n")

            case 11:
                student, course, stuID = args
                ret = FusekiQuery11(sparql, student, course, stuID)
                output = f"\nFuseki Response Q11:\nThis student, {student}, has completed {course} {stuID} with grade:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    output = f"{result['grade']['value']}"
                    print(output)
                    file.write(output + "\n")

            case 12:
                courseNum, courseCode = args
                ret = FusekiQuery12(sparql, courseNum, courseCode)
                output = f"\nFuseki Response Q12:\nThese students have complete {courseCode} {courseNum}:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    output = f"{result['name']['value']} {result['stuId']['value']}"
                    print(output)
                    file.write(output + "\n")
            case 13:
                student = args
                ret = FusekiQuery13(sparql, student)
                output = f"\nFuseki Response Q13:\nTranscript for student:"
                print(output)
                file.write(output + "\n")
                for result in ret['results']['bindings']:
                    output = f"{result['name']['value']} {result['stuId']['value']} {result['sem']['value']} {result['subjectURI']['value']} {result['grade']['value']} "
                    print(output)
                    file.write(output + '\n')
