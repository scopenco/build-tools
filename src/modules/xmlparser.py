#!/usr/bin/env python
# (c) 2009 Andrey V. Scopenco andrey@scopenco.net
# $Id$
# xml processing module

import os
import sys
import xml.sax
import logging


class xml_object:
    """ Superclass for xml object. Init base methods for all sub classes. """

    def _validate_attributes(self, tag, attributes, goodattributes, config):
        """ Makes sure 'attributes' does not contain any attribute not
            listed in 'goodattributes'. """

        all_good = True
        for attr in attributes.keys():
            if not attr in goodattributes:
                logging.critical(
                    "unknown %s attribute '%s' in role %s" %
                    (tag, attr, config))
                sys.exit(1)
                all_good = False
        return all_good
#end def _validate_attributes


class xml_handler(xml.sax.handler.ContentHandler):
    """
    SAX handler. Find tags 'project' 'role' 'package' and append.
    look at xml project and get list roles and packages
    user classes xml_project xml_package xml_role
    """

    def __init__(self, path, config):

        #parse config
        self.path = path
        self.config = config

        self.projects = []
        self.roles = []
        self.packages = []
        self.repositories = []
    #end def __init__

    def startElement(self, tag, attributes):
        """ SAX processing, called per node in the config stream. """

        if tag == 'project':
            self._check_before_append(self.projects, xml_project(
                attributes, self.path, self.config).output())
        elif tag == 'role':
            self._check_before_append(self.roles, xml_role(
                attributes, self.path, self.config).output())
        elif tag == 'package':
            self._check_before_append(self.packages, xml_package(
                attributes, self.path, self.config).output())
        elif tag == 'repository':
            self._check_before_append(self.repositories, xml_repository(
                attributes, self.path, self.config).output())
        else:
            logging.critical(
                "unrecognized tag '%s' in role %s%s" %
                (tag, self.path, self.config))
            sys.exit(1)
    #end def startElement

    def _check_before_store(self, option, value):
        if value:
            option = value
    #end def _check_before_store

    def _check_before_append(self, option, value):
        if value:
            option.append(value)
    #end def _check_before_append
#end class ProjectHandler


class xml_project(xml_object):
    """ Class for xml object 'project'. """

    def __init__(self, attributes, path, config):

        #parse config
        self.path = path
        self.config = config

        # appent attrs like '_x_name' '_x_key'
        for attr in attributes.keys():
            setattr(self, '_x_%s' % attr, attributes.get(attr))
    #end def __init__

    def output(self):
        """ Convert attributs for output. """

        # dict used for output
        out = {}

        # ex: ['__doc__', '__module__', '_x_name',
        # '_x_summary', 'config', 'path']
        attrlist = [method for method in dir(self) if not callable(
            getattr(self, method))]

        # get attrs like '_x_' and append to out
        for attr in attrlist:
            splited_attr = attr.split('_x_')
            if len(splited_attr) == 2:
                out[splited_attr[1]] = getattr(self, attr)

        return out
    #end def output
#end class xml_project


class xml_role(xml_object):
    """ Class for xml object 'role'. """

    def __init__(self, attributes, path, config):

        #parse config
        self.path = path
        self.config = config

        #Attributes
        self._path = None
        self._title = None

        if not self._validate_attributes(
                'role', attributes, ('path', 'title'),
                '%s/%s' % (self.path, self.config)):
            return

        self._path = attributes.get('path')
        self._title = attributes.get('title')

        # Validate attributs
        if self._path:
            if not os.path.isfile("%s/%s" % (self.path, self._path)):
                logging.critical(
                    "can not locate role %s/%s in role %s/%s" %
                    (self.path, self._path, self.path, self.config))
                sys.exit(1)
                self._path = None
        elif not self._title:
            logging.critical(
                "role must have a 'path' or 'title' attribute in role %s/%s" %
                (self.path, self.config))
            sys.exit(1)
    #end def __init__

    def output(self):
        """
        convert attributs for output
        """
        return self._path
    #end def output
#end class XmlRole


class xml_package(xml_object):
    """ Xml object 'package' class """

    def __init__(self, attributes, path, config):

        #parse config
        self.path = path
        self.config = config

        #Attributes
        self._name = None
        self._version = None
        self._release = None
        self._repository = None

        if not self._validate_attributes(
                'package', attributes,
                ('name', 'version', 'release', 'repository'),
                '%s/%s' % (self.path, self.config)):
            return

        self._name = attributes.get('name')
        self._version = attributes.get('version')
        self._release = attributes.get('release')
        self._repository = attributes.get('repository')

        # Validate attributs
        if not self._name:
            logging.critical(
                "package needs a 'name' attribute in role %s/%s" %
                (self.path, self.config))
            sys.exit(1)
    #end def __init__

    def output(self):
        """ convert attributs for output """

        return (self._name, self._version, self._release, self._repository)
    #end def output
#end class XmlProject


class xml_repository(xml_object):
    """ Xml object 'package' class """

    def __init__(self, attributes, path, config):

        #parse config
        self.path = path
        self.config = config

        #Attributes
        self._name = None
        self._description = None
        self._baseurl = None

        if not self._validate_attributes(
                'repository', attributes,
                ('name', 'description', 'baseurl'),
                '%s/%s' % (self.path, self.config)):
            return

        self._name = attributes.get('name')
        self._description = attributes.get('description')
        self._baseurl = attributes.get('baseurl')

        # Validate attributs
        if not self._name:
            logging.critical(
                "repository needs a 'name' attribute in role %s/%s" %
                (self.path, self.config))
            sys.exit(1)
        if not self._description:
            logging.critical(
                "repository needs a 'description' attribute in role %s/%s" %
                (self.path, self.config))
            sys.exit(1)
        if not self._baseurl:
            logging.critical(
                "repository needs a 'baseurl' attribute in role %s/%s" %
                (self.path, self.config))
            sys.exit(1)
    #end def __init__

    def output(self):
        """ convert attributs for output """

        return {'repoid': self._name,
                'description': self._description,
                'baseurl': self._baseurl}
    #end def output
#end class XmlProject
