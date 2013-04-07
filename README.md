Storage
=======

Repository for different scripts and testing calls, each subdirectory on the root is an independend script directory.
I don't create for each directory an own repository, because these scripts are small and not full projects with data.

The following subdirectories store:

* __Doxygen Markdown__ XSLT files for transforming [Doxygen](http://www.doxygen.org) XML documentation into [MarkDown](http://daringfireball.net/projects/markdown) syntax. The transformation can be run by the [Scons](http://www.scons.org) script, that uses [Saxon (HE)](http://saxon.sourceforge.net/) for the XSL transformation
* __Irrlicht__ a [Scons](http://www.scons.org) build scripts for the 3D graphic engine [Irrlicht](http://irrlicht.sourceforge.net/)
* __Scons__ directory for creating [Scons](http://www.scons.org) builder. The ```SConstruct``` file in the directory stores the example / testing code and the subdirectory ```site_scons/site_tools``` stores the builder scripts.
