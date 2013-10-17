constructor
===========

Documentation
--------
For installation instructions and information on the design overview
of the constructor, please read the documentation that is found here 
and on wiki.

Purpose
-------
This utility allow to construct Yum repository with metapackage from any of public/private repositories on the base of xml specifications (roles). Roles describe a set of required packages and repositories from which these packages with dependencies should be downloaded into a local repository. Attributes in xml roles allow to differentiate and versioning service environment.

Support OS:
--------
- RHEL >= 5.0
- CentOS >= 5.0
- Fedora >= 13
- Scientific >= 5.0

Dependences
--------
- python 
- createrepo
- rpm-build
- yum = 3.2.22 (CentOS 5)

Contents
--------

  2) ChangeLog           - Project's changelog.
  3) build-tools.spec    - Spec file for rpm building.
  4) repository          - Example of project repository with xml specs (roles),
                           in roles can/should be described: project, packages, 
                           yum repositories.
  5) src/build.sh        - shell script for project building. Its example 
                           that can be changed for your need.
  6) src/constructor.py  - constructor's main script. It realize base logic 
                           of rpm filding and download
  7) src/gen_spec.py     - constructor's spec generator script. It create project
                           and release spec file need for meta rpm and yum 
                           repository rpm  
  8) src/get_info.py     - constructor's get information script. It's usefull
                           for shell scripts like build.sh and get project 
                           information like project name, type, version, 
                           release etc.
  9) src/modules         - constructor's modules directory


Installing
----------

The scripts from src/ directory  and repository/ can be placed in your $HOME dir 
or where you need. You should edit scripts and set python modules directory.

Running 
-------

you can run sync.sh or you build script with args:
> sync.sh 

Questions?
----------

If you have questions about build-tools, or problems getting things
working, first try searching wiki.

If all else fails, you can email me and I'll try and respond as
soon as I get a chance.

        -- Andrey V. Scopenco (andrey@scopenco.net)