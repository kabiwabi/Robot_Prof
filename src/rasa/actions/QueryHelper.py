import re
from rdflib import Literal, XSD

def sanitize_string(part):
    return re.sub(r'\s+', '_', part)

def escape_string(value):
    return re.escape(value)

def literal_string(value):
    return Literal(value, datatype=XSD.string)