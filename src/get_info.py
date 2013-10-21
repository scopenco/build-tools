#!/usr/bin/env python
# (c) 2009 Andrey V. Scopenco andrey@scopenco.net
# $Id$
# get name type vendor version release 
# usefull for shell scripts to get project data

import os
import sys
import optparse
import logging
import xml.sax

sys.path.insert(0, 'modules')

import cli
import xmlparser

def parse_args():
    """ Parse command args """

    usage = "%prog --config CONFIG [options]"
    version = "%prog 1.0"
    parser = cli.EncodedOptionParser(usage=usage, version=version,
                                    formatter=cli.HelpFormatter())

    geng = optparse.OptionGroup(parser, "General Options")
    geng.add_option("-c", "--config", type="string", dest="config",
                    action="callback", callback=cli.check_before_store,
                    help="project xml file")
    geng.add_option("-x", "--xml_path", dest='xmldir',
        default=os.getcwd(), help="Path to xml roles directory")
    geng.add_option("-a", "--attribute", dest='attribute',
        help="show project attribute")
    parser.add_option_group(geng)

    misc = optparse.OptionGroup(parser, "Miscellaneous Options")
    misc.add_option("-d", "--debug", action="store_true", dest="debug",
                    help="Print debugging information")
    parser.add_option_group(misc)

    (options, dummy) = parser.parse_args()
    return options
#end def parse_args

def main():
    options = parse_args()
    cli.setup_logging("project", options.debug)

    # check os compat
    if not cli.check_os_version:                                                                                                                                                               
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
