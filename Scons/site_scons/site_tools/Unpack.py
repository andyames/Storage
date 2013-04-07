# -*- coding: utf-8 -*-

# The Unpack Builder can be used for unpacking archives (eg Zip, TGZ, BZ, ... ).
# The emitter of the Builder reads the archive data and creates a returning file list
# the builder extract the archive. The environment variable stores a dictionary "UNPACK"
# for set different extractions (subdict "EXTRACTOR"):
# {
#   PRIORITY      => a value for setting the extractor order (lower numbers = extractor is used earlier)
#   SUFFIX        => defines a list with file suffixes, which should be handled with this extractor
#   EXTRACTSUFFIX => suffix of the extract command
#   EXTRACTFLAGS  => a string parameter for the RUN command for extracting the data
#   EXTRACTCMD    => full extract command of the builder
#   RUN           => the main program which will be started (if the parameter is empty, the extractor will be ignored)
#   LISTCMD       => the listing command for the emitter
#   LISTFLAGS     => the string options for the RUN command for showing a list of files
#   LISTSUFFIX    => suffix of the list command
#   LISTEXTRACTOR => a optional Python function, that is called on each output line of the
#                    LISTCMD for extracting file & dir names, the function need two parameters (first line number,
#                    second line content) and must return a string with the file / dir path (other value types
#                    will be ignored)
# }
# Other options in the UNPACK dictionary are:
#   VIWEXTRACTOUTPUT=> shows the output messages of the extraction command (default False)
# The file which is handled by the first suffix match of the extractor, the extractor list can be append for other files.
# The order of the extractor dictionary creates the listing & extractor command eg file extension .tar.gz should be
# before .gz, because the tar.gz is extract in one shoot


import subprocess, os

import SCons.Errors, SCons.Warnings
import SCons.Util


# enables Scons warning for this builder
SCons.Warnings.enableWarningClass(SCons.Warnings.Warning)


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
    
# extractor function for 7-Zip (double packed files eg .tar.gz)
# @param count number of returning lines
# @param no number of the output line
# @param i line content
def __fileextractor_win_7zip_double( count, no, i ) :
    item = i.split()
    if len(item) == 6 and item[-1].lower() <> "folders" and item[-3].lower() <> "files" and item[-1].lower() <> "Name" :
        return item[-1]
    return None
    
# extractor function for 7-Zip (single packed files eg .tar)
# @param count number of returning lines
# @param no number of the output line
# @param i line content
def __fileextractor_win_7zip_single( count, no, i ) :
    item = i.split()
    if len(item) == 7 and item[-1].lower() <> "Name" :
        return item[-1]
    return None




# detecting tool function and
# setting default parameter
# @param env environment object
def __detect( env ) :
    toolset = { 
        "VIWEXTRACTOUTPUT" : False,
        "EXTRACTOR" : { 
            "TARGZ" : {
                "PRIORITY"       : 0,
                "SUFFIX"         : [".tar.gz", ".tgz", ".tar.gzip"],
                "EXTRACTSUFFIX"  : "",
                "EXTRACTFLAGS"   : "",
                "EXTRACTCMD"     : "${UNPACK['EXTRACTOR']['TARGZ']['RUN']} ${UNPACK['EXTRACTOR']['TARGZ']['EXTRACTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['TARGZ']['EXTRACTSUFFIX']}",
                "RUN"            : "",
                "LISTCMD"        : "${UNPACK['EXTRACTOR']['TARGZ']['RUN']} ${UNPACK['EXTRACTOR']['TARGZ']['LISTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['TARGZ']['LISTSUFFIX']}",
                "LISTSUFFIX"     : "",
                "LISTFLAGS"      : "",
                "LISTEXTRACTOR"  : None
            },

            "TARBZ" : {
                "PRIORITY"       : 0,
                "SUFFIX"         : [".tar.bz", ".tbz", ".tar.bz2", ".tar.bzip2", ".tar.bzip"],
                "EXTRACTSUFFIX"  : "",
                "EXTRACTFLAGS"   : "",
                "EXTRACTCMD"     : "${UNPACK['EXTRACTOR']['TARBZ']['RUN']} ${UNPACK['EXTRACTOR']['TARBZ']['EXTRACTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['TARBZ']['EXTRACTSUFFIX']}",
                "RUN"            : "",
                "LISTCMD"        : "${UNPACK['EXTRACTOR']['TARBZ']['RUN']} ${UNPACK['EXTRACTOR']['TARBZ']['LISTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['TARBZ']['LISTSUFFIX']}",
                "LISTSUFFIX"     : "",
                "LISTFLAGS"      : "",
                "LISTEXTRACTOR"  : None
            },

            "BZIP" : {
                "PRIORITY"       : 1,
                "SUFFIX"         : [".bz", "bzip", ".bz2", ".bzip2"],
                "EXTRACTSUFFIX"  : "",
                "EXTRACTFLAGS"   : "",
                "EXTRACTCMD"     : "${UNPACK['EXTRACTOR']['BZIP']['RUN']} ${UNPACK['EXTRACTOR']['BZIP']['EXTRACTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['BZIP']['EXTRACTSUFFIX']}",
                "RUN"            : "",
                "LISTCMD"        : "${UNPACK['EXTRACTOR']['BZIP']['RUN']} ${UNPACK['EXTRACTOR']['BZIP']['LISTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['BZIP']['LISTSUFFIX']}",
                "LISTSUFFIX"     : "",
                "LISTFLAGS"      : "",
                "LISTEXTRACTOR"  : None
            },

            "GZIP" : {
                "PRIORITY"       : 1,
                "SUFFIX"         : [".gz", ".gzip"],
                "EXTRACTSUFFIX"  : "",
                "EXTRACTFLAGS"   : "",
                "EXTRACTCMD"     : "${UNPACK['GZIP']['RUN']} ${UNPACK['GZIP']['EXTRACTFLAGS']} $SOURCE ${UNPACK['GZIP']['EXTRACTSUFFIX']}",
                "RUN"            : "",
                "LISTCMD"        : "${UNPACK['GZIP']['RUN']} ${UNPACK['GZIP']['LISTFLAGS']} $SOURCE ${UNPACK['GZIP']['LISTSUFFIX']}",
                "LISTSUFFIX"     : "",
                "LISTFLAGS"      : "",
                "LISTEXTRACTOR"  : None
            },

            "TAR" : {
                "PRIORITY"       : 1,
                "SUFFIX"         : [".tar"],
                "EXTRACTSUFFIX"  : "",
                "EXTRACTFLAGS"   : "",
                "EXTRACTCMD"     : "${UNPACK['EXTRACTOR']['TAR']['RUN']} ${UNPACK['EXTRACTOR']['TAR']['EXTRACTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['TAR']['EXTRACTSUFFIX']}",
                "RUN"            : "",
                "LISTCMD"        : "${UNPACK['EXTRACTOR']['TAR']['RUN']} ${UNPACK['EXTRACTOR']['TAR']['LISTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['TAR']['LISTSUFFIX']}",
                "LISTSUFFIX"     : "",
                "LISTFLAGS"      : "",
                "LISTEXTRACTOR"  : None
            },

            "ZIP" : {
                "PRIORITY"       : 1,
                "SUFFIX"         : [".zip"],
                "EXTRACTSUFFIX"  : "",
                "EXTRACTFLAGS"   : "",
                "EXTRACTCMD"     : "${UNPACK['EXTRACTOR']['ZIP']['RUN']} ${UNPACK['EXTRACTOR']['ZIP']['EXTRACTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['ZIP']['EXTRACTSUFFIX']}",
                "RUN"            : "",
                "LISTCMD"        : "${UNPACK['EXTRACTOR']['ZIP']['RUN']} ${UNPACK['EXTRACTOR']['ZIP']['LISTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['ZIP']['LISTSUFFIX']}",
                "LISTSUFFIX"     : "",
                "LISTFLAGS"      : "",
                "LISTEXTRACTOR"  : None
            }
        }
    }

    # read tools for Windows system (order of check: 7-zip, Winrar, Winzip)
    if env["PLATFORM"] <> "darwin" and "win" in env["PLATFORM"] :
        
        if env.WhereIs("7z") :
            toolset["EXTRACTOR"]["TARGZ"]["RUN"]           = "7z"
            toolset["EXTRACTOR"]["TARGZ"]["LISTEXTRACTOR"] = __fileextractor_win_7zip_double
            toolset["EXTRACTOR"]["TARGZ"]["LISTFLAGS"]     = "x"
            toolset["EXTRACTOR"]["TARGZ"]["LISTSUFFIX"]    = "-so -y | ${UNPACK['EXTRACTOR']['TARGZ']['RUN']} l -sii -ttar -y -so"
            toolset["EXTRACTOR"]["TARGZ"]["EXTRACTFLAGS"]  = "x"
            toolset["EXTRACTOR"]["TARGZ"]["EXTRACTSUFFIX"] = "-so -y | ${UNPACK['EXTRACTOR']['TARGZ']['RUN']} x -sii -ttar -y -oc:."
            
            toolset["EXTRACTOR"]["TARBZ"]["RUN"]           = "7z"
            toolset["EXTRACTOR"]["TARBZ"]["LISTEXTRACTOR"] = __fileextractor_win_7zip_double
            toolset["EXTRACTOR"]["TARBZ"]["LISTFLAGS"]     = "x"
            toolset["EXTRACTOR"]["TARBZ"]["LISTSUFFIX"]    = "-so -y | ${UNPACK['EXTRACTOR']['TARGZ']['RUN']} l -sii -ttar -y -so"
            toolset["EXTRACTOR"]["TARBZ"]["EXTRACTFLAGS"]  = "x"
            toolset["EXTRACTOR"]["TARBZ"]["EXTRACTSUFFIX"] = "-so -y | ${UNPACK['EXTRACTOR']['TARGZ']['RUN']} x -sii -ttar -y -oc:."
            
            toolset["EXTRACTOR"]["ZIP"]["RUN"]             = "7z"
            toolset["EXTRACTOR"]["ZIP"]["LISTEXTRACTOR"]   = __fileextractor_win_7zip_double
            toolset["EXTRACTOR"]["ZIP"]["LISTFLAGS"]       = "l"
            toolset["EXTRACTOR"]["ZIP"]["LISTSUFFIX"]      = "-y -so"
            toolset["EXTRACTOR"]["ZIP"]["EXTRACTFLAGS"]    = "x"
            toolset["EXTRACTOR"]["ZIP"]["EXTRACTSUFFIX"]   = "-y -oc:."
            
            toolset["EXTRACTOR"]["TAR"]["RUN"]             = "7z"
            toolset["EXTRACTOR"]["TAR"]["LISTEXTRACTOR"]   = __fileextractor_win_7zip_single
            toolset["EXTRACTOR"]["TAR"]["LISTFLAGS"]       = "l"
            toolset["EXTRACTOR"]["TAR"]["LISTSUFFIX"]      = "-y -ttar -so"
            toolset["EXTRACTOR"]["TAR"]["EXTRACTFLAGS"]    = "x"
            toolset["EXTRACTOR"]["TAR"]["EXTRACTSUFFIX"]   = "-y -ttar -oc:."
        
    # read the tools on *nix systems and sets the default parameters
    elif env["PLATFORM"] in ["darwin", "linux", "posix"] :

        if env.WhereIs("unzip") :
            toolset["EXTRACTOR"]["ZIP"]["RUN"]             = "unzip"
            toolset["EXTRACTOR"]["TAR"]["LISTEXTRACTOR"]   = __fileextractor_nix_unzip
            toolset["EXTRACTOR"]["TAR"]["LISTFLAGS"]       = "-l"
            toolset["EXTRACTOR"]["ZIP"]["EXTRACTFLAGS"]    = "-oqq"

        if env.WhereIs("tar") :
            toolset["EXTRACTOR"]["TAR"]["RUN"]             = "tar"
            toolset["EXTRACTOR"]["TAR"]["LISTEXTRACTOR"]   = __fileextractor_nix_tar
            toolset["EXTRACTOR"]["TAR"]["LISTFLAGS"]       = "tvf"
            toolset["EXTRACTOR"]["TAR"]["EXTRACTFLAGS"]    = "xf"

            toolset["EXTRACTOR"]["TARGZ"]["RUN"]           = "tar"
            toolset["EXTRACTOR"]["TARGZ"]["LISTEXTRACTOR"] = __fileextractor_nix_tar
            toolset["EXTRACTOR"]["TARGZ"]["EXTRACTFLAGS"]  = "xfz"
            toolset["EXTRACTOR"]["TARGZ"]["LISTFLAGS"]     = "tvfz"

            toolset["EXTRACTOR"]["TARBZ"]["RUN"]           = "tar"
            toolset["EXTRACTOR"]["TARBZ"]["LISTEXTRACTOR"] = __fileextractor_nix_tar
            toolset["EXTRACTOR"]["TARBZ"]["EXTRACTFLAGS"]  = "xfj"
            toolset["EXTRACTOR"]["TARBZ"]["LISTFLAGS"]     = "tvfj"
            
        if env.WhereIs("bzip2") :
            toolset["EXTRACTOR"]["BZIP"]["RUN"]            = "bzip2"
            toolset["EXTRACTOR"]["BZIP"]["EXTRACTFLAGS"]   = "-df"

        if env.WhereIs("gzip") :
            toolset["EXTRACTOR"]["GZIP"]["RUN"]            = "gzip"
            toolset["EXTRACTOR"]["GZIP"]["LISTEXTRACTOR"]  = __fileextractor_nix_gzip
            toolset["EXTRACTOR"]["GZIP"]["LISTFLAGS"]      = "-l"
            toolset["EXTRACTOR"]["GZIP"]["EXTRACTFLAGS"]   = "-df"

    else :
        raise SCons.Errors.StopError("Unpack tool detection on this platform [%s] unkown" % (env["PLATFORM"]))
    
    env.Replace(UNPACK = toolset)


# returns the extractor item for handling the source file
# @param source input source file
# @param env environment object
# @return extractor entry or None on non existing
def __getExtractor( source, env ) :
    # we check each unpacker and get the correc  list command first, run the command and
    # replace the target filelist with the list values, we sorte the extractors by their priority
    for unpackername, extractor in sorted(env["UNPACK"]["EXTRACTOR"].iteritems(), key = lambda (k,v) : (v["PRIORITY"],k)):
        
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

    # build it now (we need the shell, because some programs need it)
    handle = None
    cmd    = env.subst(extractor["EXTRACTCMD"], source=source, target=target)
    
    if env["UNPACK"]["VIWEXTRACTOUTPUT"] :
        handle  = subprocess.Popen( cmd, shell=True )
    else :
        devnull = open(os.devnull, "wb")
        handle  = subprocess.Popen( cmd, shell=True, stdout=devnull )
    
    if handle.wait() <> 0 :
        raise SCons.Errors.BuildError( "error running extractor [%s] on the source [%s]" % (cmd, source[0])  )

        
# emitter function for getting the files
# within the archive
# @param target target packed file
# @param source extracted files
# @env environment object
def __emitter( target, source, env ) :
    extractor = __getExtractor(source, env)
    if not extractor :
        raise SCons.Errors.StopError( "can not find any extractor value for the source file [%s]" % (source[0]) )

    # we do a little trick, because eg the download builder creates an empty file, so we
    # return direct the target file / we return it also, if the does not exists a LISTCMD
    if source[0].get_size() == 0 or len(extractor["LISTCMD"]) == 0 :
        return target, source
           
    # create the list command and run it in a subprocess and pipes the output to a variable,
    # we need the shell for reading data from the stdout
    cmd    = env.subst(extractor["LISTCMD"], source=source, target=target)
    handle = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE )
    target = handle.stdout.readlines()
    handle.communicate()
    if handle.returncode <> 0 :
        raise SCons.Errors.StopError("error on running list command [%s] of the source file [%s]" % (cmd, source[0]) ) 
    
    # if the returning output exists and the listseperator is a callable structure
    # we run it for each line of the output and if the return of the callable is
    # a string we push it back to the target list
    try :
        if callable(extractor["LISTEXTRACTOR"]) :
            target = filter( lambda s : SCons.Util.is_String(s), [ extractor["LISTEXTRACTOR"]( len(target), no, i) for no, i in enumerate(target) ] )
    except Exception, e :
        raise SCons.Errors.StopError( "%s" % (e) )
    
    # the line removes duplicated names - we need this line, otherwise an cyclic dependency error will occured,
    # because the list process can create redundant data (an archive file can not store redundant content in a filepath)
    target = list(set(target))
    if not target :
        SCons.Warnings.warn(SCons.Warnings.Warning, "emitter file list on target [%s] is empty, please check your extractor list function [%s]" % (source[0], cmd) ) 
    
    return target, source




# generate function, that adds the builder to the environment
# @env environment object
def generate( env ) :
    __detect(env)

    # the target_factory must be a "Entry", because the target list can be files and dirs, so we can not specified the targetfactory explicite 
    env["BUILDERS"]["Unpack"] = SCons.Builder.Builder( action = __action,  emitter = __emitter,  target_factory = SCons.Node.FS.Entry,  source_factory = SCons.Node.FS.File,  PRINT_CMD_LINE_FUNC = __message )


# existing function of the builder
# @return true
def exists(env) :
    return 1