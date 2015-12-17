import sparqldb

import rdflib

sparql = sparqldb.SparqlInterface()

def pythonize(s,p,o):
  return (s.toPython(),p.toPython(),o.toPython())

def store_query_results(rdflib_results, local_set):
  for s,p,o in rdflib_results:
    local_set.add(pythonize(s,p,o))

class RabResource(rdflib.resource.Resource):
    def __init__(self):
      self.statements = set()

    def describe(self, uri):
      try:
        results = sparql.describe(uri)
      except:
        raise("Describe query error!")
      store_query_results(results, self.statements)
      return True

    def remove(self, triple):
        pass

    def new(self):
        pass

    def all(self, filter_map):
        pass

    def find(self, find_by_map):
        pass

    def update(self, property_map):
        pass

    def save(self):
        pass

    def destroy(self):
        pass

    def create(self):
        pass

test_json = {
  "requested_url": "https://vivo.brown.edu/services/data/v1/faculty/dlipscom/", 
  "results": {
    "affiliations": [
      {
        "more": "https://vivo.brown.edu/services/data/v1/ou/org-brown-univ-dept56/", 
        "name": "Neuroscience", 
        "url": "http://vivo.brown.edu/individual/org-brown-univ-dept56"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/ou/org-brown-univ-dept77/", 
        "name": "Brain Science", 
        "url": "http://vivo.brown.edu/individual/org-brown-univ-dept77"
      }
    ], 
    "countries": [], 
    "email": "Diane_Lipscombe@brown.edu", 
    "first": "Diane", 
    "image": "https://vivo.brown.edu/file/n19785/dlipscom.jpg", 
    "last": "Lipscombe", 
    "middle": "null", 
    "overview": "<p>I graduated with a PhD in Pharmacology from University College London in 1986 and then studied\u00a0with Richard W Tsien\u00a0as a postdoctoral associate at Yale University School of Medicine and subsequently at Stanford University Medical School.\u00a0In 1992 I joined the Department of Neuroscience at Brown. I\u00a0study the expression, regulation, and\u00a0function\u00a0of voltage-gated calcium ion channels in different regions of the nervous system. I am also\u00a0interested in their role in chronic pain and psychiatric disorders.\u00a0I\u00a0work closely with undergraduate and graduate students, as well as postdoctoral trainees. I direct NIH funded Predoctoral Training Programs in Neuroscience and co-Direct the Center for the Neurobiology of Cells and Circuits in the Brown Institute for Brain Science.</p>\n", 
    "thumbnail": "https://vivo.brown.edu/file/n5406/dlipscom_thumb.jpg", 
    "title": "Interim Executive Director of the Brown Institute for Brain Science (BIBS),  Professor of Neuroscience", 
    "topics": [
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n44566/", 
        "name": "alternative splicing", 
        "url": "http://vivo.brown.edu/individual/n44566"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n90525/", 
        "name": "analgesic", 
        "url": "http://vivo.brown.edu/individual/n90525"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n76195/", 
        "name": "pain", 
        "url": "http://vivo.brown.edu/individual/n76195"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n93142/", 
        "name": "calcium", 
        "url": "http://vivo.brown.edu/individual/n93142"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n25137/", 
        "name": "brain", 
        "url": "http://vivo.brown.edu/individual/n25137"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n88234/", 
        "name": "gene structure", 
        "url": "http://vivo.brown.edu/individual/n88234"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n70330/", 
        "name": "neuropathic pain", 
        "url": "http://vivo.brown.edu/individual/n70330"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n74029/", 
        "name": "bipolar disorder", 
        "url": "http://vivo.brown.edu/individual/n74029"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n21400/", 
        "name": "neurons", 
        "url": "http://vivo.brown.edu/individual/n21400"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n72428/", 
        "name": "synaptic transmission", 
        "url": "http://vivo.brown.edu/individual/n72428"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n31363/", 
        "name": "ion channels", 
        "url": "http://vivo.brown.edu/individual/n31363"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n25056/", 
        "name": "voltage-gated calcium channels", 
        "url": "http://vivo.brown.edu/individual/n25056"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n65638/", 
        "name": "drugs", 
        "url": "http://vivo.brown.edu/individual/n65638"
      }, 
      {
        "more": "https://vivo.brown.edu/services/data/v1/topic/n49615/", 
        "name": "molecular biology", 
        "url": "http://vivo.brown.edu/individual/n49615"
      }
    ], 
    "url": "http://vivo.brown.edu/individual/dlipscom"
  }
}

def flatten(subj, stmts, result=None):
    if result is None:
        result = list()
    for pred, obj in stmts.items():
        if isinstance(obj, dict):
            flatten(subj, obj, result)
        elif isinstance(obj,list):
            for o in obj:
                flatten(subj, o, result)
        else:
            result.append((subj, pred, obj))
    return result

def nest(stmts):
    result = dict()
    for s in stmts:
        if s[1] in result:
            if isinstance(result[s[1]], list):
                result[s[1]].append(s[2])
            else:
                old = result[s[1]]
                new = s[2]
                result[s[1]] = list()
                result[s[1]].append(old)
                result[s[1]].append(new)
        else:
            result[s[1]] = s[2]
    return result