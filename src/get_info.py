#!/usr/bin/env python
# (c) 2009 Andrey V. Scopenco andrey@scopenco.net
# $Id$
# get name type vendor version release 
# usefull for shell scripts to get project data

import os
import sys
from optparse import OptionParser
import logging
import xml.sax

sys.path.insert(0, 'modules')

import cli
import xmlparser

def main():
    # get options
    p = OptionParser(description='get info about selected project',
                    prog='get_info.py',
                    usage='%prog --config CONFIG [options]')
    p.add_option("-c", "--config", type="string", dest="config",
                    action="callback", callback=cli.check_before_store,
                    help="Project xml file")
    p.add_option("-x", "--xml_path", type="string", dest='xmldir',
        default=os.getcwd(), help="Path to xml roles directory")
    p.add_option("-a", "--attribute", dest='attribute',
        help="show project attribute")
    p.add_option("-d", "--debug", action="store_true", dest="debug",
                    help="Print debugging information")
    options, arguments = p.parse_args()

    # setup logging
    if options.debug:
        LEVEL = logging.DEBUG
    else:
        LEVEL = logging.INFO
    logging.basicConfig(format='%(asctime)s: %(message)s', level=LEVEL)

    # check os compat
    if cli.check_os_version():
        logging.critical('OS not supported. Please install build-tools on CentOS 5.')
        sys.exit(1)

    # check mandatory options
    if not options.config:
        logging.critical('project xml is required.')
        sys.exit(1)
    if not os.path.isdir(options.xmldir):
        logging.critical('%s does not exit.' % options.xmldir)
        sys.exit(1)
    if not os.path.isfile("%s/%s" % (options.xmldir, options.config)):
        logging.critical('%s/%s does not exit.' % (options.xmldir, options.config))
        sys.exit(1)

    projects        = []      # project desc
    packages        = []      # list of packages
    roles           = []      # list of roles
    repositories    = []      # list of repos

    cli.get_xml_tags(options.config, options.xmldir, projects, packages, roles, repositories)

    if options.attribute:
        if options.attribute in projects[0].keys():
            print projects[0][options.attribute]
        else:
            logging.critical('attribute %s not found' % options.attribute)
            sys.exit(1)
    else:
        logging.critical('attribute is not defined')
        sys.exit(1)
#end def main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("aborted at user request")
        sys.exit(1)
