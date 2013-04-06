# -*- coding: utf-8 -*-

# The Unpack Builder can be used for unpacking archives (eg Zip, TGZ, BZ, ... ).
# The emitter of the Builder reads the archive data and creates a returning file list
# the builder extract the archive. The environment variable stores a dictionary "UNPACK"
# for setting different extractions:
# {
#	SUFFIX => defines a list with file suffixes, which should be handled with this extractor
#	EXTRACTFLAGS => a string parameter for the RUN command for extracting the data
#   EXTRACTCMD => full extract command of the builder
#   RUN => the main program which will be started
#   LISTCMD => the listing command for the emitter
#   LISTFLAGS => the string options for the RUN command for showing a list of files
#   LISTEXTRACTOR => a optional Python function, that is called on each output line of the
#                    LISTCMD for extracting file & dir names, the function need one parameter
#                    and must return a string with the file / dir path (other value types will be ignored)
#}


import subprocess

import SCons.Errors
import SCons.Util


# function for replacing a None
# type value to a fixed value
# @param val input value
# @param empty replacing value
# @return input value or empty value
def __NonExist2Val( val, empty ) :
    if not val :
        return empty
    return val


def __fileextractor_nix( i ) :
    return i.split()[-1]


# detecting tool function and
# setting default parameter
# @param env environment object
def __detecttools( env ) :
    toolset = { 
        "TAR" : {
            "SUFFIX" 	     : [".tar"],
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "",
            "RUN"            : "",
            "LISTCMD"        : "",
            "LISTFLAGS"      : "",
            "LISTEXTRACTOR"  : None
        },

        "TARGZ" : {
            "SUFFIX" 	     : [".tar.gz", ".tgz", ".tar.gzip"],
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "",
            "RUN"            : "",
            "LISTCMD"        : "${UNPACK['TARGZ']['RUN']} ${UNPACK['TARGZ']['LISTFLAGS']} $SOURCE",
            "LISTFLAGS"      : "tvfz",
            "LISTEXTRACTOR"  : None
        },

        "TARBZ" : {
            "SUFFIX" 	     : [".tar.bz", ".tbz", ".tar.bz2", ".tar.bzip2", ".tar.bzip"],
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "",
            "RUN"            : "",
            "LISTCMD"        : "",
            "LISTFLAGS"      : "",
            "LISTEXTRACTOR"  : None
        },

        "BZIP" : {
            "SUFFIX"         : [".bz", "bzip", ".bz2", ".bzip2"],
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "",
            "RUN"            : "",
            "LISTCMD"        : "",
            "LISTFLAGS"      : "",
            "LISTEXTRACTOR"  : None
        },

        "GZIP" : {
            "SUFFIX"         : [".gz", ".gzip"],
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "",
            "RUN"            : "",
            "LISTCMD"        : "",
            "LISTFLAGS"      : "",
            "LISTEXTRACTOR"  : None
        },

        "ZIP" : {
            "SUFFIX"         : [".zip"],
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "",
            "RUN"            : "",
            "LISTCMD"        : "",
            "LISTFLAGS"      : "",
            "LISTEXTRACTOR"  : None
        }
    }

    if env["PLATFORM"] <> "darwin" and "win" in env["PLATFORM"] :
        pass
    elif env["PLATFORM"] in ["darwin", "linux"] :
        # env.Detect([.....]) or 'gtar'
        toolset["TAR"]["RUN"]             = __NonExist2Val(env.WhereIs("tar"), "")
        toolset["BZIP"]["RUN"]            = __NonExist2Val(env.WhereIs("bzip2"), "")
        toolset["GZIP"]["RUN"]            = __NonExist2Val(env.WhereIs("gzip"), "")
        toolset["ZIP"]["RUN"]             = __NonExist2Val(env.WhereIs("unzip"), "")

        toolset["TARGZ"]["RUN"]           = toolset["TAR"]["RUN"] 
        toolset["TARGZ"]["LISTEXTRACTOR"] = __fileextractor_nix 

        toolset["TARBZ"]["RUN"]           = toolset["TAR"]["RUN"] 

    else :
        raise SCons.Errors.StopError("Unpack tool detection on this platform [%s] unkown" % (env["PLATFORM"]))

    env.Replace(UNPACK = toolset)


# creates the extracter output message
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __message( s, target, source, env ) : 
    print "extract [%s] to [%s] ..." % (source[0], target[0])


# action function for extracting of the data
# @param target target packed file
# @param source extracted files
# @env environment object
def __action( target, source, env ) :
    pass


# emitter function for getting the files
# within the archive
# @param target target packed file
# @param source extracted files
# @env environment object
def __emitter( target, source, env ) :
    target = []
    
    # we check each unpacker and get the correct
    # list command first, run the command and
    # replace the target filelist with the list values
    for unpackername, extractor in env["UNPACK"].iteritems() :

        # if the run command not set, we continue the extractor search, otherwise we check the extractor parameters
        if not SCons.Util.is_String(extractor["RUN"]) :
            raise SCons.Errors.StopError("list command of the unpack builder for [%s] archives is not a string" % (unpackername))
        if not len(extractor["RUN"]) :
            continue

        if not SCons.Util.is_String(extractor["LISTFLAGS"]) :
            raise SCons.Errors.StopError("list flags of the unpack builder for [%s] archives is not a string" % (unpackername))
        if not SCons.Util.is_String(extractor["LISTCMD"]) :
            raise SCons.Errors.StopError("list command of the unpack builder for [%s] archives is not a string" % (unpackername))
        if not SCons.Util.is_List(extractor["SUFFIX"]) :
            raise SCons.Errors.StopError("suffix list of the unpack builder for [%s] archives is not a list" % (unpackername))
        
        # check the source file suffix and if the first is found, run the list command        
        for suffix in extractor["SUFFIX"] :
            if str(source[0]).lower()[-len(suffix):] == suffix.lower() :
                
 
                cmd    = subprocess.Popen( env.subst(extractor["LISTCMD"], source=source), shell=True, stdout=subprocess.PIPE )
                target = cmd.stdout.readlines()
                cmd.communicate()
                if cmd.returncode <> 0 :
                    raise SCons.Errors.StopError("error on running list command of the unpacker [%s]" % (unpackername))

                # if the returning output exists and the listseperator is a callable structure
                # we run it for each line of the output and if the return of the callable is
                # a string we push it back to the target list, the callable function get the 
                # output line
                try :
                    if callable(extractor["LISTEXTRACTOR"]) :
                        target = filter( lambda s : SCons.Util.is_String(s), [ extractor["LISTEXTRACTOR"](v) for v in target ] )
                except Exception, e :
                    raise SCons.Errors.StopError( "%s" % (e) )

                return target, source

    raise SCons.Errors.StopError( "can not find any unpack value for the source file [%s]" % (source[0]) )




# generate function, that adds the builder to the environment,
# the value "DOWNLOAD_USEFILENAME" replaces the target name with
# the filename of the URL
# @env environment object
def generate( env ) :
    __detecttools(env)

    # the target_factory must be a "Entry", because the target list can be files and dirs, so we can not specified the targetfactory explicite 
    env["BUILDERS"]["Unpack"] = SCons.Builder.Builder( action = __action,  emitter = __emitter,  target_factory = SCons.Node.FS.Entry,  source_factory = SCons.Node.FS.File,  PRINT_CMD_LINE_FUNC = __message )

    #print env.Dump()

# existing function of the builder
# @return true
def exists(env) :
    return 1