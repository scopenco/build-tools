#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
This module is a set of funcs and classes with cli destination
Andrey Skopenko @ 2010
'''

import sys
import os
import logging
import xml.sax
import xmlparser
import platform

def check_before_store(option, opt_str, value, parser):
    '''callback to store args from cmd'''

    if len(value) == 0:
        raise OptionValueError, "%s option requires an argument" % opt_str
    setattr(parser.values, option.dest, value)
#end def check_before_store

def check_before_append(option, opt_str, value, parser):
    '''callback to append args from cmd'''

    if len(value) == 0:
        raise OptionValueError, "%s option requires an argument" % opt_str
    parser.values.ensure_value(option.dest, []).append(value)
#end class check_before_append

def get_xml_tags(config, path, projects, packages, roles, repositories):
    '''parse project xml files and create packages, role, repositories lists'''

    # check role exist
    if not os.path.isfile("%s/%s" % (path, config)):
        logging.critical('%s/%s does not exit.' % (path, config))
        sys.exit(1)

    logging.debug("parse role %s/%s" % (path, config))
    # init handler with role. That need for troubleshooting package dups and roles dups
    handler = xmlparser.xml_handler(path, config)
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)

    try:
        parser.parse("%s/%s" % (path, config))
    except xml.sax.SAXException, e:
        logging.critical(e)
        sys.exit(1)

    for project in handler.projects:
        if project in projects:
           logging.critical("project dublicate '%s' in role %s/%s" % (project, path, config))
           sys.exit(1)
        else:
           logging.debug("project '%s'" % str(project))
           projects.append(project)

    for package in handler.packages:
        if package in packages:
           logging.critical("package dublicate '%s' in role %s/%s" % (package[0], path, config))
           sys.exit(1)
        else:
           logging.debug("package '%s'" % str(package))
           packages.append(package)

    for repo in handler.repositories:
        if repo in repositories:
            logging.critical("repository dublicate '%s' in role %s/%s" % (repo, path, config))
            sys.exit(1)
        else:
            logging.debug("repository '%s'" % str(repo))
            repositories.append(repo)

    for role in handler.roles:
        if role in roles:
            logging.critical("role dublicate '%s' in role %s/%s" % (role, path, config))
            sys.exit(1)
        else:
            logging.debug("role '%s'" % role)
            roles.append(role)
            get_xml_tags(role, path, projects, packages, roles, repositories)
#end def get_xml_tags

def more_to_check(unprocessed_pkgs):
    for pkg in unprocessed_pkgs.keys():
        if unprocessed_pkgs[pkg] is not None:
            return True

    return False
#end def more_to_check

# for yum 2.4.X compat
def sortPkgObj(pkg1 ,pkg2):
    '''sort a list of yum package objects by name'''

    if pkg1.name > pkg2.name:
        return 1
    elif pkg1.name == pkg2.name:
        return 0
    else:
        return -1
#end def sortPkgObj

def check_os_version():
    '''Check OS platform'''

    os_vars = platform.dist()
    if 'redhat' == os_vars[0] and '5' == os_vars[1].split('.')[0]:
        return 0

    return 1
# end def check_os_version

if __name__ == "__main__":
     print __doc__
