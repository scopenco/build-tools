build-tools
===========

Documentation
--------
For installation instructions and information on the design overview
of the build-tools scripts, please read the documentation that is found here 
and on wiki.

Purpose
-------
This utility allow to construct Yum repository with metapackage from any of public/private repositories on the base of xml specifications (roles). Roles describe a set of required packages and repositories from which these packages with dependencies should be downloaded into a local repository. Attributes in xml roles allow to differentiate and versioning service environment in DevOps.

Support OS:
--------
- RHEL >= 5.0
- CentOS >= 5.0
- Fedora >= 13
- Scientific >= 5.0

Dependences
--------
- python >= 2.4.3
- createrepo
- rpm-build
- yum = 3.2.22 (CentOS 5)

Contents
--------

- **ChangeLog**           - Project's changelog.
- **build-tools.spec**    - Spec file for rpm building.
- **repository**          - Example of project repository with xml specs (roles),
                            in roles can/should be described: project, packages, 
                            yum repositories.
- **src/build.sh**        - shell script for project building. Its example 
                            that can be changed for your need.
- **src/constructor.py**  - constructor's main script. It realize base logic 
                            of rpm filding and download
- **src/gen_spec.py**     - constructor's spec generator script. It create project
                            and release spec file need for meta rpm and yum 
                            repository rpm  
- **src/get_info.py**     - constructor's get information script. It's usefull
                            for shell scripts like build.sh and get project 
                            information like project name, type, version, 
                            release etc.
- **src/modules**         - constructor's modules directory


Installing
----------

1. The scripts from src/ directory  and repository/ can be placed in your $HOME dir 
or where you need. You should edit scripts and set python modules directory.
1. Install build-tools from yum repo http://createrepo.com.
1. Use chef-kitchen and deploy cookbook https://github.com/scopenco/chef-build-tools for build creation.

Running 
-------

you can run example build scripts:
```bash
# build-el5.sh
# build-el6.sh
```

Detailed example in wiki.

Questions?
----------

If you have questions about build-tools, or problems getting things
working, first try searching wiki.

If all else fails, you can email me and I'll try and respond as
soon as I get a chance.

        -- Andrey V. Scopenco (andrey@scopenco.net)
