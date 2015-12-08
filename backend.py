# Data namespace
from vdm.namespaces import D

from models import Faculty, Organization, Topic, Country


class DataServiceBackend(object):

    def __init__(self, store, api_path, public_path):
        self.store = store
        # path for service
        self.api_path = api_path.rstrip('/')
        self.public_path = public_path.rstrip('/')

    def local_name(self, uri):
        return uri.split('/')[-1]

    def more_url(self, prefix, uri):
        """
        Build the request path for looking up
        another entity.
        """
        partial = ('/').join(
            [
            self.api_path,
            prefix,
            self.local_name(uri),
            ]
        )
        return partial + '/'

    def add_lookup(self, lset, prefix):
        """
        Helper to build API urls for related resources.
          - rename uri to url.
          - add a more link for looking up related resource
          - rename label to name
        """
        out = []
        for item in lset:
            item['more'] = self.more_url(prefix, item['uri'])
            item['url'] = item['uri']
            item['name'] = item['label']
            del item['label']
            del item['uri']
            out.append(item)
        return out

    def make_image_url(self, resource, prop):
        """
        Helper to assemble image url.
        """
        val = getattr(resource, prop)()
        if val is not None:
            return self.public_path + val
        else:
            return None

    def faculty(self, short_id):
        """
        Assemble a Faculty response.
        """
        if short_id is None:
            raise Exception("No short ID")
        uri = D[short_id]
        fac = Faculty(uri, store=self.store)
        out = {
            'url': uri.toPython(),
            'first': fac.first(),
            'last': fac.last(),
            'middle': fac.middle(),
            'email': fac.email(),
            'thumbnail': self.make_image_url(fac, 'thumbnail'),
            'image': self.make_image_url(fac, 'full_image'),
            'title': fac.title(),
            'overview': fac.overview(),
        }
        # Affilations
        out['affiliations'] = self.add_lookup(fac.membership(), 'ou')
        # Topics
        out['topics'] = self.add_lookup(fac.topics(), 'topic')
        # Countries
        out['countries'] = self.add_lookup(fac.countries(), 'country')
        return out

    def org_unit(self, local_name):
        """
        Assemble an Organization response.
        """
        uri = D[local_name]
        org = Organization(uri, store=self.store)
        out = {
            'name': org.get_label(),
            'overview': org.overview(),
            'thumbnail': self.make_image_url(org, 'thumbnail'),
            'image': self.make_image_url(org, 'full_image'),
            'url': uri.toPython(),
        }
        out['affiliations'] = self.add_lookup(org.affiliates(), 'faculty')
        return out

    def topic(self, local_name):
        """
        Assemble a Topic response.
        """
        uri = D[local_name]
        topic = Topic(uri, store=self.store)
        out = {
            'name': topic.get_label(),
            'url': uri,
        }
        out['faculty'] = self.add_lookup(topic.researchers(), 'faculty')
        return out

    def country(self, local_name):
        """
        Assemble a Country response.
        """
        uri = D[local_name]
        country = Country(uri, store=self.store)
        out = {
            'name': country.get_label(),
            'url': uri,
            'code': country.get_code(),
        }
        out['faculty'] = self.add_lookup(country.researchers(), 'faculty')
        return out
