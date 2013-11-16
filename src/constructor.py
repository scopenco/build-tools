#!/usr/bin/env python
# (c) 2009 Andrey V. Scopenco andrey@scopenco.net
# $Id$
# create repository on the base of xml specs

import os
import sys
import optparse
import logging
import rpmUtils.arch
import yum
from urlparse import urljoin
from shutil import copy2

sys.path.insert(0, 'modules')

import cli
import tracker 

def parse_args():
    """ Parse command args """

    usage = "%prog --config CONFIG [options]"
    version = "%prog 1.0"
    parser = cli.EncodedOptionParser(usage=usage, version=version,
                                    formatter=cli.HelpFormatter())

    geng = optparse.OptionGroup(parser, "General Options")
    geng.add_option("-c", "--config", type="string", dest="config",
                    action="callback", callback=cli.check_before_store,
                    help="Project xml file")
    geng.add_option("-p", "--download_path", type="string", dest='destdir',
        default=os.getcwd(), help="Path to download directory")
    geng.add_option("-x", "--xml_path", type="string", dest='xmldir',
        default=os.getcwd(), help="Path to xml roles directory")
    geng.add_option("-a", "--arch", type="string", default=None,
        action="callback", callback=cli.check_before_store,
        help='Check as if running the specified arch (default: current arch)')
    geng.add_option("-u", "--urls", default=False, action="store_true", 
        help="Just list urls of what would be downloaded, don't download")
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

    # setup logging
    if options.debug:
	LEVEL = logging.DEBUG
    else:
	LEVEL = logging.INFO
    logging.basicConfig(format='%(asctime)s: %(message)s', level=LEVEL)
    logging.info('running...')

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


    logging.debug(options)

    project         = []      # project desc
    packages        = []      # list of packages
    roles           = []      # list of roles
    repositories    = []      # list of repos

    if not options.urls:
        logging.info('project %s' % options.config)

    # get xml data
    cli.get_xml_tags(options.config, options.xmldir, project, packages, roles, repositories)

    if not options.urls:
        logging.info('create destination download directory %s' % options.destdir)

    # create destination download dir 
    if not os.path.exists(options.destdir) and not options.urls:
        try:
            os.makedirs(options.destdir)
        except OSError, e:
            logging.critical("cannot create destination dir %s" % options.destdir)
            sys.exit(1)

    if not os.access(options.destdir, os.W_OK) and not options.urls:
        logging.critical("cannot write to  destination dir %s" % options.destdir)
        sys.exit(1)

    track = tracker.tracker()

    # init yum configuration
    track.doConfigSetup(debuglevel=0, init_plugins=False) # init yum, without plugins

    # get list of arch
    if options.arch:
        archlist = rpmUtils.arch.getArchList(options.arch)
    else:
        archlist = rpmUtils.arch.getArchList()
    logging.debug("archlist %s" % archlist)

    # create cachedir
    cachedir = yum.misc.getCacheDir()
    logging.debug('yum cachedir %s' % cachedir)
    if cachedir is None:
        logging.critical("could not make cachedir, exiting")
        sys.exit(1)

    # set up cache dir
    track.repos.setCacheDir(cachedir)

    # disable all local repos
    for repo in track.repos.repos.values():
        logging.debug("disable local repository %s" % repo)
        repo.disable()

    # enable project repos
    try:
        for repo in repositories:
            repoid = repo['repoid']
            repopath = repo['baseurl']
            if repo['baseurl'][0] == '/':
                baseurl = 'file://' + repopath
            else:
                baseurl = repopath

            repopath = os.path.normpath(repopath)
            newrepo = yum.yumRepo.YumRepository(repoid)
            newrepo.name = repopath
            newrepo.baseurl = baseurl
            newrepo.basecachedir = cachedir
            newrepo.metadata_expire = 0
            newrepo.timestamp_check = False
            track.repos.add(newrepo)
            track.repos.enableRepo(newrepo.id)
            if not options.urls:
                logging.info("repository %s, %s" % (repoid,repopath))
            else:
                logging.debug("enable project repository %s, %s" % (repoid,repopath))

    except yum.Errors.DuplicateRepoError, e:
        logging.critical(e)
        sys.exit(1)

    # setup repos
    try:
        track.doRepoSetup()
    except yum.Errors.RepoError, e:
        logging.critical("could not setup repositories: %s" % (e))
        sys.exit(1)

    # get xml data from repos
    if not options.urls:
        logging.info("setting up package sacks")
    track._getSacks(archlist=archlist)

    final_pkgs = {}
    pkg_list = []
    repoid_list = []

    # get list of enabled repos
    # need for checking repos in package attrs
    for repoid in track.repos.listEnabled():
        repoid_list.append(repoid.id)
 
    logging.debug("enabled repos %s" % repoid_list)

    # get package downloads
    for p in packages:
        # append name
        pa = p[0]
        # append version and release
        if p[1]:
            pa = "%s-%s" % (pa, p[1])
            if p[2]:
                pa = "%s-%s" % (pa, p[2])
        
        # check package repo in project repos
        repoid = p[3]

        if repoid:
            if repoid not in repoid_list:
                logging.critical("could not find repository %s for package %s" % (repoid, pa))
                sys.exit(1)

            package_list = track.pkgSack.returnPackages(repoid=repoid)
        else:
            package_list = track.pkgSack.returnPackages()

        exactmatch, matched, unmatched = yum.packages.parsePackages(package_list, [pa])
        logging.debug("exactmatch %s" % ' '.join([str(s) for s in exactmatch]))
        if unmatched:
            logging.critical("package %s not found" % pa)
            sys.exit(1)

        exactmatch = track.bestPackagesFromList(exactmatch)
        if len(exactmatch) == 2:
            if exactmatch[0].pkgtup[0].endswith('-devel') and exactmatch[1].pkgtup[0].endswith('-devel'):
                exactmatch = exactmatch[0:1]

        if not options.urls:
            if repoid:
                logging.info("found package(s) %s in repository %s" % (' '.join([str(n) for n in exactmatch]), repoid))
            else:
                logging.info("found package(s) %s" % ' '.join([str(n) for n in exactmatch]))
        else:
            if repoid:
                logging.debug("found package(s) %s in repository %s" % (' '.join([str(n) for n in exactmatch]), repoid))
            else:
                logging.debug("found package(s) %s" % ' '.join([str(n) for n in exactmatch]))

        pkg_list.extend(exactmatch)
        pkg_list.extend(matched)

    # check if packages are set
    if len(pkg_list) == 0:
        logging.critical("no packages found")
        sys.exit(1)

    # search dependencies
    for po in pkg_list:
        track.unprocessed[po.pkgtup] = po

    while cli.more_to_check(track.unprocessed):
        for pkgtup in track.unprocessed.keys():
            # if always processed then continue from next package
            if track.unprocessed[pkgtup] is None:
                continue

            po = track.unprocessed[pkgtup]
            final_pkgs[po.pkgtup] = po

            deps_list = track.findDeps(po)
            # deps found, set None for while loop
            track.unprocessed[po.pkgtup] = None

            for dep in deps_list:
                if not track.unprocessed.has_key(dep.pkgtup):
                    track.unprocessed[dep.pkgtup] = dep

    # get final list with newest versions
    download_list = final_pkgs.values()

    # sort download list
    download_list.sort(cli.sortPkgObj)

    # counter
    i = 0
    maxi = len(download_list)

    # list or download packages
    for pkg in download_list:
        i += 1
        # counter usefull for viewing download status
        repo = track.repos.getRepo(pkg.repoid)
        logging.debug("repository: %s" % repo)
        remote = pkg.returnSimple('relativepath')
        logging.debug("remote: %s" % remote)
        local = os.path.basename(remote)
        local = os.path.join(options.destdir, local)
        logging.debug("local: %s" % local)
        if (os.path.exists(local) and os.path.getsize(local) == int(pkg.returnSimple('packagesize'))):
            logging.info("%s (%s/%s) already exists and appears to be complete" % (local, i, maxi))
            continue

        url = urljoin(repo.urls[0],remote)
        logging.debug('url: %s' % url)
        if options.urls:
            print '%s' % url
            continue

        # Disable cache otherwise things won't download
        repo.cache = 0
        logging.info('Downloading %s (%s) (%s/%s)' % (os.path.basename(remote), repo, i, maxi))
        pkg.localpath = local # Hack: to set the localpath to what we want.
	try:
	    path = repo.getPackage(pkg)
	except yum.Errors.NoMoreMirrorsRepoError:
	    logging.critical("No more mirrors, exit.")
	    sys.exit(1)

        if not os.path.exists(local) or not os.path.samefile(path, local):
            copy2(path, local)
#end del main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.critical("aborted at user request")
        sys.exit(1)
