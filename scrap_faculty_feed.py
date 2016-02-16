### start sketch
def build_queue(fis_list):
	all_faculty = requests.get(feed_base + "faculty")
	to_be_updated = [f for f in fis_list if f in all_faculty]
	to_be_created = [f for f in fis_list if f not in all_faculty]
	to_be_hidden = [f for f in all_faculty if f not in fis_list]
	return to_be_created, to_be_updated, to_be_hidden

def create(new_faculty_data):
	r = requests.post(feed_base + "faculty", data=new_faculty_data)

# https://tools.ietf.org/html/rfc6902#section-4.2
# http://jsonpatch.com/
# http://williamdurand.fr/2014/02/14/please-do-not-patch-like-an-idiot/

def update(upd_faculty_row):
	rabid = upd_faculty_row['resource_id']
	rsp = requests.get(feed_base + "faculty/" + rabid)
	if rsp:
		req = rsp.update(upd_faculty_row)
	r = requests.put(feed_base + "faculty/" + rabid, data=req)

def hide(hdn_faculty):
	rabid = hdn_faculty_row['resource_id']
	h_data = 	{
				'op': 'remove',
				'path': 'rdf:type',
				'value': blocal+'BrownThing'
				}
	r = requests.patch(feed_base + "faculty/" + rabid, data=h_data)

def process(fis_data):
	fis_list = cleanup(fis_data)
	crt, upd, hdn = build_queue(fis_list)
	for c in crt:
		create(c)
	for u in upd:
		update(u)
	for h in hdn:
		hide(h)

def update(shortId, atts):
	fac = Faculty.find_or_create(rabid=shortId)
	success = fac.update_attr(fis_data)
	if success:
		logging.info("Updated {0}: {1}").format(shortId, atts)
	else:
		logging.warning("Update failed for {0}: {1}").format(shortId, atts)
### end sketch



"""
Load faculty
"""

import csv
from datetime import datetime, date
import os
import sys

import rdflib
from rdflib import Literal, Graph
from vdm.models import (
	BLOCAL,
	BU,
	VIVO,
	RDF,
	RDFS,
	FOAF,
	ns_mgr
)

import common
from common import (
	vstore,
	read_file,
	get_brown_id_map,
	make_uri
)

#logging
import logging

DEBUG = False
#Maximum number of missing shortIds script will tolerate before
#exiting with an exception.
ERROR_MAX = 20

td = datetime.today()
today = date(year=td.year, month=td.month, day=td.day)
TODAY = Literal(today)

feed_base = "http://vivo.brown.edu/rabdata/api/v0.1/fisfeed/"
blocal = "http://vivo.brown.edu/ontology/vivo-brown/"

def process_feed_file(filename):
	#Lookup keys.
	brown_id_map = get_brown_id_map()
	in_data = read_file(filename)
	error_count = 0
	out = {}
	for n, row in enumerate(in_data):
		brown_id = row.get('Brown_ID')
		last = row.get('Preferred_Last_Name')
		first = row.get('Preferred_First_Name')
		middle = row.get('Preferred_Middle_Name')
		#remove trailing periods.
		if middle:
			middle = middle.rstrip('.')
		title = row.get('Current_Person_Title').rstrip('\n').rstrip('\r')
		email = row.get('Employee_Email')
		short_id = row.get('AUTH_ID')
		#Make a string for logging errors.
		estring = "Row %s. %s" % (
			str(n + 1),
			" ".join([f for f in [short_id, first, last, title, email] if f is not None])
		)
		#Stop process if too many errors are found.
		if error_count > ERROR_MAX:
			logging.error("Too many errors. Exiting.")
			raise Exception("Too many missing auth ids to proceed. Verify faculty file.")
		if short_id is None:
			fail = False
			try:
				#Try to fetch short_id from LDAP
				short_id = brown_id_map[brown_id]['short_id']
			except IndexError:
				fail = True
			except KeyError:
				fail = True
			if (short_id is None) or (fail is True):
				logging.warning("Unable to lookup faculty by key. %s." % (estring))
				error_count += 1
				continue
		if (first is None):
			logging.error("Missing first name. %s." % (estring))
			continue
		if (last is None):
			logging.error("Missing last name. %s" % (estring))
			continue
		label = "{0}, {1}".format(last, first)
		uri = make_uri(short_id)
		d = {}
		d['brown_id'] = brown_id
		d['uri'] = uri
		d['label'] = label
		d['first'] = first
		d['last'] = last
		d['middle'] = middle
		d['title'] = title
		d['email'] = email
		d['shortId'] = short_id
		#Add other FIS data that might be needed later here.
		d['workdayID'] = row.get('Workday_ID')
		out[short_id] = d
		if (DEBUG is True) and (n > 15):
			break
	return out

def existing_faculty_set():
	"""
	Query the vstore and get all shortIds for
	exiting faculty.
	"""
	q = """
	SELECT ?fac ?shortId
	WHERE {
		?fac a blocal:BrownThing ;
		     a vivo:FacultyMember ;
			 blocal:shortId ?shortId .
	}
	"""
	if DEBUG is True:
		q += "LIMIT 10"
	out = set()
	for row in vstore.query(q):
		out.add(row.shortId.toPython())
	return out

def incoming_faculty_set(data):
	"""
	A set that can be used for finding
	the difference between existing
	and incoming faculty data.
	"""
	return set(data.keys())

def get_changes(existing, incoming):
	"""
	Return two sets one with additions and the other with subtractions.
	"""
	#Set differences
	new = incoming - existing
	inactive = existing - incoming
	return (new, inactive)

def graph_faculty_data(fac_info):
	"""
	New FIS data for a single row in the feed.
	"""
	#Add graph
	ag = rdflib.Graph()
	shortId = fac_info.get('shortId')
	#Validate the shortId - skip invalid ids.
	valid = common.valid_short_id(shortId)
	if valid is not True:
		logging.warning("Invalid shortId {}.".format(shortId))
		return
	uri = make_uri(shortId)
	ag.add((uri, RDF.type, VIVO.FacultyMember))
	ag.add((uri, RDF.type, BLOCAL.BrownThing))
	ag.add((uri, RDFS.label, Literal(fac_info['label'])))
	ag.add((uri, FOAF.firstName, Literal(fac_info['first'])))
	ag.add((uri, FOAF.lastName, Literal(fac_info['last'])))
	ag.add((uri, VIVO.preferredTitle, Literal(fac_info['title'])))
	ag.add((uri, BLOCAL.shortId, Literal(shortId)))
	#Required data properties - not requireing middle name or email now.
	optional_properties = ['middle', 'email', 'workdayID']
	for k, v in fac_info.items():
	    if (v is None) and (k not in optional_properties):
	        logging.error("Required data missing {} for {}.".format(k, shortId))
	        raise Exception("Required data missing in FIS file at fac_info {0}.".format(shortId))
	#Add optional data properties.
	#Email is now optional
	if fac_info['email'] is None:
	    logging.warning("Missing email for {}.".format(uri))
	else:
		ag.add((uri, VIVO.primaryEmail, Literal(fac_info['email'])))
	#Middle name is optional.
	middle = fac_info.get('middle')
	if middle is not None:
	    ag.add((uri, VIVO.middleName, Literal(middle)))
	#FIS sync date.
	ag.add((uri, BLOCAL.fisUpdated, TODAY))
	#if new is True:
	#	ag.add((uri, BLOCAL.fisCreated, TODAY))
	return ag

def graph_all_faculty(fac_data):
	"""
	Graph the faculty info for all fac in the feed.
	"""
	out = Graph()
	for k, info in fac_data.items():
		out += graph_faculty_data(info)
	return out

def graph_faculty_list(short_ids, fac_data):
	"""
	Create RDF for all the faculty in the list.
	"""
	out = Graph()
	for k, info in fac_data.items():
		if k in short_ids:
			add = graph_faculty_data(info)
			if add is not None:
				out += add
	return out

def deactivate_faculty(short_ids):
	remove = Graph()
	for short in short_ids:
		logging.debug("{0} is inactive faculty.")
		uri = make_uri(short)
		remove.add((uri, RDF.type, BLOCAL.BrownThing))
	return remove

def add_create_date(short_ids):
	add = Graph()
	logging.info("Adding create date for new faculty.")
	for short in short_ids:
		#Don't add a create data if this short id is invalid.
		if common.valid_short_id(short) is True:
			uri = make_uri(short)
			add.add((uri, BLOCAL.fisCreated, TODAY))
	return add

def add_update_date(short_ids):
	add = Graph()
	logging.info("Adding create date for new faculty.")
	for short in short_ids:
		uri = make_uri(short)
		add.add((uri, BLOCAL.fisUpdated, TODAY))
	return add

def existing_faculty_info():
	"""
	Get all faculty info that might be replaced
	with data coming from FIS.
	"""
	q = """
	CONSTRUCT {
	    ?fac a vivo:FacultyMember ;
	    	 a blocal:BrownThing ;
	             rdfs:label ?label ;
	             foaf:firstName ?first ;
	             foaf:lastName ?last ;
	             vivo:preferredTitle ?title ;
	             vivo:primaryEmail ?email ;
	             blocal:shortId ?shortId ;
	             blocal:fisUpdated ?updated .
	}
	WHERE {
		?fac a blocal:BrownThing ;
		     a vivo:FacultyMember ;
			rdfs:label ?label ;
            foaf:firstName ?first ;
            foaf:lastName ?last ;
            vivo:preferredTitle ?title ;
            vivo:primaryEmail ?email ;
            blocal:shortId ?shortId .
        OPTIONAL {
        	?fac blocal:fisUpdated ?updated .
        }
	}
	"""
	rg = vstore.query(q)
	return rg.graph

def existing_fac_info(graph, uri):
	g = rdflib.Graph()
	for p, o in graph.predicate_objects(subject=uri):
		g.add((uri, p, o))
	return g


def existing_to_diff_graph(short_ids, graph):
	g = rdflib.Graph()
	for short in short_ids:
		uri = make_uri(short)
		for p, o in graph.predicate_objects(subject=uri):
			g.add((uri, p, o))
	return g


def info_graph_diff(incoming_faculty_graph, existing_graph):
	#Add
	add = incoming_faculty_graph - existing_graph
	#Remove
	remove = existing_graph - incoming_faculty_graph
	return (add, remove)

def get_sets(fac_data):
	existing = existing_faculty_set()
	incoming = incoming_faculty_set(fac_data)
	new, inactive = get_changes(
            existing,
            incoming
        )
	#This are "staying" faculty - those that just need to be
	#checked for updated data.
	to_update = set(fac_data.keys()) - (new.union(inactive))
	return (new, inactive, to_update)

def sync(filename):
	"""
	Do the entire process.
	"""
	# build a dictionary of faculty data
	# from FIS file, indexed by shortid
	fac_data = process_feed_file(filename)
	# compare IDs in VIVO to shortids in dict
	# Identify which are in VIVO, not in FIS
	# which are in FIS, not in VIVO
	# and which are in both FIS and VIVO (to_update)
	new, inactive, to_update = get_sets(fac_data)
	logging.info("{} new faculty found.".format(len(new)))
	logging.info("{0} inactive faculty found.".format(len(inactive)))
	logging.info("{0} faculty to be updated from FIS.".format(len(to_update)))

	#Our data graphs.
	add_g = Graph()
	remove_g = Graph()
	logging.info("Deactivating inactive faculty.")
	remove_g += deactivate_faculty(inactive)
	logging.info("Adding create date for new faculty.")
	add_g += add_create_date(new)
	#Add info about the new fac.
	add_g += graph_faculty_list(new, fac_data)
	#Check for diff of those that are to be updated.
	#Existing info in VIVO
	logging.info("Creating change RDF for existing faculty.")
	vivo_fac_graph = common.faculty_fis_info()
	#A graph of just the RDF for the faculty that will remain in VIVO.
	my_vivo_fac_graph = existing_to_diff_graph(to_update, vivo_fac_graph)
	#The new info coming from FIS.
	new_info = graph_faculty_list(to_update, fac_data)
	updated_add, updated_remove = info_graph_diff(new_info, my_vivo_fac_graph)
	add_g += updated_add
	remove_g += updated_remove
	#All done.
	return (add_g, remove_g)


if __name__ == "__main__":
	raise Exception("No main function for this process.")