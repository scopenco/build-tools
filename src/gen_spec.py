#!/usr/bin/env python
# (c) 2009 Andrey V. Scopenco andrey@scopenco.net
# $Id$
# create project and release spec

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
                    help="set project xml file")
    geng.add_option("-x", "--xml_path", dest='xmldir',
		    default=os.getcwd(), help="Path to xml roles directory")
    geng.add_option("-s", "--spec_template", dest='spec_template',
		    help="set spec template file")
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
    if not options.spec_template:
        logging.critical('spec template file is required.')
        sys.exit(1)
    if not os.path.isfile("%s" % options.spec_template):
        logging.critical('%s does not exit.' % options.spec_template)
        sys.exit(1)

    projects        = []      # project desc
    packages        = []      # list of packages
    roles           = []      # list of roles
    repositories    = []      # list of repos

    cli.get_xml_tags(options.config, options.xmldir, projects, packages, roles, repositories)

    logging.debug("project %s" % projects[0])
    logging.debug("packages %s" % packages)

    # get package version and release
    projects[0]['requires_packages'] = ''
    for p in packages:
	# append name
	pa = p[0]
	# append version and release
	if p[1]:
	    projects[0]['requires_packages'] = projects[0]['requires_packages'] + 'Requires: %s >= %s\n' % (pa, p[1])
	else:
	    projects[0]['requires_packages'] = projects[0]['requires_packages'] + 'Requires: %s\n' % pa

    F = open('%s' % options.spec_template)
    TEMPLATE = F.read()
    try:
	print TEMPLATE % projects[0]
    except KeyError, e:
	logging.critical('attr %s not found in project attributes' % e)
	sys.exit(1)

#end def main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("aborted at user request")
        sys.exit(1)
