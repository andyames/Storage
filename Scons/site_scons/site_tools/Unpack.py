# -*- coding: utf-8 -*-

# The Unpack Builder can be used for unpacking archives (eg Zip, TGZ, BZ, ... ).
# The emitter of the Builder reads the archive data and creates a returning file list
# the builder extract the archive. The environment variable stores a dictionary "UNPACK"
# for setting different extractions:
# {
#   SUFFIX => defines a list with file suffixes, which should be handled with this extractor
#   EXTRACTFLAGS => a string parameter for the RUN command for extracting the data
#   EXTRACTCMD => full extract command of the builder
#   RUN => the main program which will be started (if the parameter is empty, the extractor will be ignored)
#   LISTCMD => the listing command for the emitter
#   LISTFLAGS => the string options for the RUN command for showing a list of files
#   LISTEXTRACTOR => a optional Python function, that is called on each output line of the
#                    LISTCMD for extracting file & dir names, the function need two parameters (first line number,
#                    second line content) and must return a string with the file / dir path (other value types
#                    will be ignored)
# }
# The file which is handled by the first suffix match of the extractor, the extractor list can be append for other files.
# The order of the extractor dictionary creates the listing & extractor command eg file extension .tar.gz should be
# before .gz, because the tar.gz is extract in one shoot


import subprocess

import SCons.Errors
import SCons.Util


# extractor function for Tar output
# @param count number of returning lines
# @param no number of the output line
# @param i line content
def __fileextractor_nix_tar( count, no, i ) :
    return i.split()[-1]

# extractor function for GZip output,
# ignore the first line
# @param count number of returning lines
# @param no number of the output line
# @param i line content
def __fileextractor_nix_gzip( count, no, i ) :
    if no == 0 :
        return None
    return i.split()[-1]

# extractor function for Unzip output,
# ignore the first & last two lines
# @param count number of returning lines
# @param no number of the output line
# @param i line content
def __fileextractor_nix_unzip( count, no, i ) :
    if no < 3 or no >= count - 2 :
        return None
    return i.split()[-1]


# detecting tool function and
# setting default parameter
# @param env environment object
def __detect( env ) :
    toolset = { 
        "TARGZ" : {
            "SUFFIX"         : [".tar.gz", ".tgz", ".tar.gzip"],
            "EXTRACTSUFFIX"  : "",
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "${UNPACK['TARGZ']['RUN']} ${UNPACK['TARGZ']['EXTRACTFLAGS']} $SOURCE ${UNPACK['TARGZ']['EXTRACTSUFFIX']}",
            "RUN"            : "",
            "LISTCMD"        : "${UNPACK['TARGZ']['RUN']} ${UNPACK['TARGZ']['LISTFLAGS']} $SOURCE",
            "LISTFLAGS"      : "",
            "LISTEXTRACTOR"  : None
        },

        "TARBZ" : {
            "SUFFIX"         : [".tar.bz", ".tbz", ".tar.bz2", ".tar.bzip2", ".tar.bzip"],
            "EXTRACTSUFFIX"  : "",
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "${UNPACK['TARBZ']['RUN']} ${UNPACK['TARBZ']['EXTRACTFLAGS']} $SOURCE ${UNPACK['TARBZ']['EXTRACTSUFFIX']}",
            "RUN"            : "",
            "LISTCMD"        : "${UNPACK['TARBZ']['RUN']} ${UNPACK['TARBZ']['LISTFLAGS']} $SOURCE",
            "LISTFLAGS"      : "",
            "LISTEXTRACTOR"  : None
        },

        "BZIP" : {
            "SUFFIX"         : [".bz", "bzip", ".bz2", ".bzip2"],
            "EXTRACTSUFFIX"  : "",
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "${UNPACK['BZIP']['RUN']} ${UNPACK['BZIP']['EXTRACTFLAGS']} $SOURCE ${UNPACK['BZIP']['EXTRACTSUFFIX']}",
            "RUN"            : "",
            "LISTCMD"        : "${UNPACK['BZIP']['RUN']} ${UNPACK['BZIP']['LISTFLAGS']} $SOURCE",
            "LISTFLAGS"      : "",
            "LISTEXTRACTOR"  : None
        },

        "GZIP" : {
            "SUFFIX"         : [".gz", ".gzip"],
            "EXTRACTSUFFIX"  : "",
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "${UNPACK['GZIP']['RUN']} ${UNPACK['GZIP']['EXTRACTFLAGS']} $SOURCE ${UNPACK['GZIP']['EXTRACTSUFFIX']}",
            "RUN"            : "",
            "LISTCMD"        : "${UNPACK['GZIP']['RUN']} ${UNPACK['GZIP']['LISTFLAGS']} $SOURCE",
            "LISTFLAGS"      : "",
            "LISTEXTRACTOR"  : None
        },

        "TAR" : {
            "SUFFIX"         : [".tar"],
            "EXTRACTSUFFIX"  : "",
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "${UNPACK['TAR']['RUN']} ${UNPACK['TAR']['EXTRACTFLAGS']} $SOURCE ${UNPACK['TAR']['EXTRACTSUFFIX']}",
            "RUN"            : "",
            "LISTCMD"        : "${UNPACK['TAR']['RUN']} ${UNPACK['TAR']['LISTFLAGS']} $SOURCE",
            "LISTFLAGS"      : "",
            "LISTEXTRACTOR"  : None
        },

        "ZIP" : {
            "SUFFIX"         : [".zip"],
            "EXTRACTSUFFIX"  : "",
            "EXTRACTFLAGS"   : "",
            "EXTRACTCMD"     : "${UNPACK['ZIP']['RUN']} ${UNPACK['ZIP']['EXTRACTFLAGS']} $SOURCE ${UNPACK['ZIP']['EXTRACTSUFFIX']}",
            "RUN"            : "",
            "LISTCMD"        : "${UNPACK['ZIP']['RUN']} ${UNPACK['ZIP']['LISTFLAGS']} $SOURCE",
            "LISTFLAGS"      : "",
            "LISTEXTRACTOR"  : None
        }
    }

    #if env["PLATFORM"] <> "darwin" and "win" in env["PLATFORM"] :
    #    pass

    # read the tools on *nix systems and sets the default parameters
    if env["PLATFORM"] in ["darwin", "linux"] :

        toolset["ZIP"]["RUN"]             = __NonExist2Val(env.WhereIs("unzip"), "")
        toolset["TAR"]["LISTEXTRACTOR"]   = __fileextractor_nix_unzip
        toolset["TAR"]["LISTFLAGS"]       = "-l"
        toolset["ZIP"]["EXTRACTFLAGS"]    = "-oqq"

        toolset["TAR"]["RUN"]             = __NonExist2Val(env.WhereIs("tar"), "")
        toolset["TAR"]["LISTEXTRACTOR"]   = __fileextractor_nix_tar
        toolset["TAR"]["LISTFLAGS"]       = "tvf"
        toolset["TAR"]["EXTRACTFLAGS"]    = "xf"

        toolset["BZIP"]["RUN"]            = __NonExist2Val(env.WhereIs("bzip2"), "")
        toolset["BZIP"]["EXTRACTFLAGS"]   = "-df"

        toolset["GZIP"]["RUN"]            = __NonExist2Val(env.WhereIs("gzip"), "")
        toolset["GZIP"]["LISTEXTRACTOR"]  = __fileextractor_nix_gzip
        toolset["GZIP"]["LISTFLAGS"]      = "-l"
        toolset["GZIP"]["EXTRACTFLAGS"]   = "-df"

        toolset["TARGZ"]["RUN"]           = toolset["TAR"]["RUN"] 
        toolset["TARGZ"]["LISTEXTRACTOR"] = __fileextractor_nix_tar
        toolset["TARGZ"]["EXTRACTFLAGS"]  = "xfz"
        toolset["TARGZ"]["LISTFLAGS"]     = "tvfz"

        toolset["TARBZ"]["RUN"]           = toolset["TAR"]["RUN"] 
        toolset["TARBZ"]["LISTEXTRACTOR"] = __fileextractor_nix_tar
        toolset["TARBZ"]["EXTRACTFLAGS"]  = "xfj"
        toolset["TARBZ"]["LISTFLAGS"]     = "tvfj"

    else :
        raise SCons.Errors.StopError("Unpack tool detection on this platform [%s] unkown" % (env["PLATFORM"]))

    env.Replace(UNPACK = toolset)


# function for replacing a None
# type value to a fixed value
# @param val input value
# @param empty replacing value
# @return input value or empty value
def __NonExist2Val( val, empty ) :
    if not val :
        return empty
    return val


# returns the extractor item for handling the source file
# @param source input source file
# @param env environment object
# @return extractor entry or None on non existing
def __getExtractor( source, env ) :
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

        if not SCons.Util.is_String(extractor["EXTRACTFLAGS"]) :
            raise SCons.Errors.StopError("extract flags of the unpack builder for [%s] archives is not a string" % (unpackername))
        if not SCons.Util.is_String(extractor["EXTRACTCMD"]) :
            raise SCons.Errors.StopError("extract command of the unpack builder for [%s] archives is not a string" % (unpackername))


        # check the source file suffix and if the first is found, run the list command        
        if not SCons.Util.is_List(extractor["SUFFIX"]) :
            raise SCons.Errors.StopError("suffix list of the unpack builder for [%s] archives is not a list" % (unpackername))

        for suffix in extractor["SUFFIX"] :
            if str(source[0]).lower()[-len(suffix):] == suffix.lower() :
                return extractor

    return None 


# creates the extracter output message
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __message( s, target, source, env ) : 
    print "extract [%s] ..." % (source[0])


# action function for extracting of the data
# @param target target packed file
# @param source extracted files
# @env environment object
def __action( target, source, env ) :
    extractor = __getExtractor(source, env)
    if not extractor :
        raise SCons.Errors.StopError( "can not find any extractor value for the source file [%s]" % (source[0]) )
    
    # if the extract command is empty, we create an error
    if len(extractor["EXTRACTCMD"]) == 0 :
        raise SCons.Errors.StopError( "the extractor command for the source file [%s] is empty" % (source[0]) )

    # build it now
    handle = subprocess.Popen( env.subst(extractor["EXTRACTCMD"], source=source, target=target), shell=True )
    if handle.wait() <> 0 :
        raise SCons.Errors.BuildError( "error running extractor on the source [%s]" % (source)  )



# emitter function for getting the files
# within the archive
# @param target target packed file
# @param source extracted files
# @env environment object
def __emitter( target, source, env ) :
    extractor = __getExtractor(source, env)
    if not extractor :
        raise SCons.Errors.StopError( "can not find any extractor value for the source file [%s]" % (source[0]) )

    # we do a little trick, because the Download compiler create an empty file, so we
    # return direct the target file / we return it also, if the does not exists a LISTCMD
    if source[0].get_size() == 0 or len(extractor["LISTCMD"]) == 0 :
        return target, source
           
    # create the list command and run it in a subprocess and pipes the output to a variable
    cmd    = subprocess.Popen( env.subst(extractor["LISTCMD"], source=source), shell=True, stdout=subprocess.PIPE )
    target = cmd.stdout.readlines()
    cmd.communicate()
    if cmd.returncode <> 0 :
        raise SCons.Errors.StopError("error on running list command of the source file [%s]" % (source[0]) )

    # if the returning output exists and the listseperator is a callable structure
    # we run it for each line of the output and if the return of the callable is
    # a string we push it back to the target list
    try :
        if callable(extractor["LISTEXTRACTOR"]) :
            target = filter( lambda s : SCons.Util.is_String(s), [ extractor["LISTEXTRACTOR"]( len(target), no, i) for no, i in enumerate(target) ] )
    except Exception, e :
        raise SCons.Errors.StopError( "%s" % (e) )
    
    return target, source




# generate function, that adds the builder to the environment,
# the value "DOWNLOAD_USEFILENAME" replaces the target name with
# the filename of the URL
# @env environment object
def generate( env ) :
    __detect(env)

    # the target_factory must be a "Entry", because the target list can be files and dirs, so we can not specified the targetfactory explicite 
    env["BUILDERS"]["Unpack"] = SCons.Builder.Builder( action = __action,  emitter = __emitter,  target_factory = SCons.Node.FS.Entry,  source_factory = SCons.Node.FS.File,  PRINT_CMD_LINE_FUNC = __message )


# existing function of the builder
# @return true
def exists(env) :
    return 1