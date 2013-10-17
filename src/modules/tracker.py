#!/usr/bin/env python
# (c) 2009 Andrey V. Scopenco andrey@scopenco.net
# $Id$
# yum tracking module
# used in search deps process

import yum
import logging
import sys

class tracker(yum.YumBase):
    """ class used to check dependences"""

    def __init__(self):
        yum.YumBase.__init__(self)

        self.deps = {}
        self.unprocessed = {}
    #end def __init__

    def provide_pkg(self, req):
        """ find the best pkg for dependence"""

        best = None
        (r, f, v) = req

        satisfiers = []
        try:
            for po in self.whatProvides(r, f, v):
                # if req always in dep dict then use it
                if po.pkgtup in self.unprocessed.keys():
                    logging.debug('matched %s to require for %s' % (po, req[0]))
                    self.deps[req] = po
                    return po
                if po not in satisfiers:
                    satisfiers.append(po)
        except yum.Errors.NoMoreMirrorsRepoError, e:
            logging.critical(e)
            sys.exit(1)

        if satisfiers:
            # if req not in dep list, calc the best and add to deps
            logging.debug('available dep(s) %s to require for %s' % (' '.join([str(n) for n in satisfiers]), req[0]))
            best = self.bestPackagesFromList(satisfiers)[0]
            logging.debug('select dep %s to require for %s' % (best, req[0]))
            self.deps[req] = best
            return best
        return None
    #end def provide_pkg

    def findDeps(self, pkg):
        """ find dependences for pkgs"""

        unresolved = []

        logging.debug(getattr('===> %s <' % pkg, 'ljust')(88,'='))
        reqs = pkg.returnPrco('requires')
        provs = pkg.returnPrco('provides')

        for req in reqs:
            if req[0].startswith('rpmlib(') or req[0].startswith('config('):
                continue
            if req in provs:
                continue

            # check if req always processed
            dep = self.deps.get(req, None)
            if dep is None:
                # find best pkg for dep
                dep = self.provide_pkg(req)
		if dep is None:
		# if cant find dep do error
		    logging.critical("unresolvable dependency %s in %s"	% (req[0], pkg))
		    sys.exit(1)

            if dep not in unresolved:
#	        logging.info("dep %s" % str(dep))
                if dep.pkgtup not in self.unprocessed.keys():
                    logging.info("adding %s for %s, required by %s" % (dep, req[0], pkg))
                    unresolved.append(dep)
                else:
                    logging.debug("always processed %s for %s, required by %s" % (dep, req[0], pkg))

        return unresolved
    #end def findDeps
