# -*- coding: utf-8 -*-

# -- Dual Licence ----------------------------------------------------------

############################################################################
# GPL License                                                              #
#                                                                          #
# This file is a SCons (http://www.scons.org/) builder                     #
# Copyright (c) 2012-14, Philipp Kraus, <philipp.kraus@flashpixx.de>       #
# This program is free software: you can redistribute it and/or modify     #
# it under the terms of the GNU General Public License as                  #
# published by the Free Software Foundation, either version 3 of the       #
# License, or (at your option) any later version.                          #
#                                                                          #
# This program is distributed in the hope that it will be useful,          #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with this program. If not, see <http://www.gnu.org/licenses/>.     #
############################################################################

# --------------------------------------------------------------------------

############################################################################
# BSD 3-Clause License                                                     #
#                                                                          #
# This file is a SCons (http://www.scons.org/) builder                     #
# Copyright (c) 2012-14, Philipp Kraus, <philipp.kraus@flashpixx.de>       #
# All rights reserved.                                                     #
#                                                                          #
# Redistribution and use in source and binary forms, with or without       #
# modification, are permitted provided that the following conditions are   #
# met:                                                                     #
#                                                                          #
# 1. Redistributions of source code must retain the above copyright        #
# notice, this list of conditions and the following disclaimer.            #
#                                                                          #
# 2. Redistributions in binary form must reproduce the above copyright     #
# notice, this list of conditions and the following disclaimer in the      #
# documentation and/or other materials provided with the distribution.     #
#                                                                          #
# 3. Neither the name of the copyright holder nor the names of its         #
# contributors may be used to endorse or promote products derived from     #
# this software without specific prior written permission.                 #
#                                                                          #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS      #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT        #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A  #
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT       #
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,   #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED #
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR   #
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF   #
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING     #
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS       #
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.             #
############################################################################



# The Unpack Builder can be used for unpacking archives (eg Zip, TGZ, BZ, ... ).
# The emitter of the Builder reads the archive data and creates a returning file list
# the builder extract the archive. The environment variable stores a dictionary "UNPACK"
# for set different extractions (subdict "EXTRACTOR"):
# {
#   PRIORITY         => a value for setting the extractor order (lower numbers = extractor is used earlier)
#   SUFFIX           => defines a list with file suffixes, which should be handled with this extractor
#   EXTRACTSUFFIX    => suffix of the extract command
#   EXTRACTFLAGS     => a string parameter for the RUN command for extracting the data
#   EXTRACTCMD       => full extract command of the builder
#   RUN              => the main program which will be started (if the parameter is empty, the extractor will be ignored)
#   LISTCMD          => the listing command for the emitter
#   LISTFLAGS        => the string options for the RUN command for showing a list of files
#   LISTSUFFIX       => suffix of the list command
#   LISTEXTRACTOR    => a optional Python function, that is called on each output line of the
#                       LISTCMD for extracting file & dir names, the function need two parameters (first line number,
#                       second line content) and must return a string with the file / dir path (other value types
#                       will be ignored)
# }
# Other options in the UNPACK dictionary are:
#   STOPONEMPTYFILE  => bool variable for stoping if the file has empty size (default True)
#   VIWEXTRACTOUTPUT => shows the output messages of the extraction command (default False)
#   EXTRACTDIR       => path in that the data will be extracted (default #)
#
# The file which is handled by the first suffix match of the extractor, the extractor list can be append for other files.
# The order of the extractor dictionary creates the listing & extractor command eg file extension .tar.gz should be
# before .gz, because the tar.gz is extract in one shoot.
#
# Under *nix system these tools are supported: tar, bzip2, gzip, unzip
# Under Windows only 7-Zip (http://www.7-zip.org/) is supported


import subprocess, os

import SCons.Errors, SCons.Warnings
import SCons.Util


# enables Scons warning for this builder
class UnpackWarning(SCons.Warnings.Warning) :
    pass
    
SCons.Warnings.enableWarningClass(UnpackWarning)



# extractor function for Tar output
# @param env environment object
# @param count number of returning lines
# @param no number of the output line
# @param i line content
def __fileextractor_nix_tar( env, count, no, i ) :
    return i.split()[-1]

# extractor function for GZip output,
# ignore the first line
# @param env environment object
# @param count number of returning lines
# @param no number of the output line
# @param i line content
def __fileextractor_nix_gzip( env, count, no, i ) :
    if no == 0 :
        return None
    return i.split()[-1]

# extractor function for Unzip output,
# ignore the first & last two lines
# @param env environment object
# @param count number of returning lines
# @param no number of the output line
# @param i line content
def __fileextractor_nix_unzip( env, count, no, i ) :
    if no < 3 or no >= count - 2 :
        return None
    return i.split()[-1]
    
# extractor function for 7-Zip
# @param env environment object
# @param count number of returning lines
# @param no number of the output line
# @param i line content
def __fileextractor_win_7zip( env, count, no, i ) :
    item = i.split()
    if no > 8 and no < count - 2 :
        return item[-1]
    return None



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
            raise SCons.Errors.StopError("run command of the unpack builder for [%s] archives is not set - can not extract files" % (unpackername))
 
        
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

    # we do a little trick, because in some cases we do not have got a physical
    # file (eg we download a packed archive), so we don't get a list or knows
    # the targets. On physical files we can do this with the LISTCMD, but on
    # non-physical files we hope the user knows the target files, so we inject
    # this knowledge into the return target.
    if env.has_key("UNPACKLIST") :
        if not SCons.Util.is_List(env["UNPACKLIST"]) and not SCons.Util.is_String(env["UNPACKLIST"]) :
            raise SCons.Errors.StopError( "manual target list of [%s] must be a string or list" % (source[0]) )
        if not env["UNPACKLIST"] :
            raise SCons.Errors.StopError( "manual target list of [%s] need not be empty" % (source[0]) )
        return env["UNPACKLIST"], source
    
        
    # we check if the source file exists, because we would like to read the data
    if not source[0].exists() :
        raise SCons.Errors.StopError( "source file [%s] must be exist" % (source[0]) )
           
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
            target = filter( lambda s : SCons.Util.is_String(s), [ extractor["LISTEXTRACTOR"]( env, len(target), no, i) for no, i in enumerate(target) ] )
    except Exception, e :
        raise SCons.Errors.StopError( "%s" % (e) )
    
    # the line removes duplicated names - we need this line, otherwise an cyclic dependency error will occured,
    # because the list process can create redundant data (an archive file can not store redundant content in a filepath)
    target = [i.strip() for i in list(set(target))]
    if not target :
        SCons.Warnings.warn(UnpackWarning, "emitter file list on target [%s] is empty, please check your extractor list function [%s]" % (source[0], cmd) ) 
    
    # we append the extractdir to each target if is not absolut
    if env["UNPACK"]["EXTRACTDIR"] <> "." :
        target = [i if os.path.isabs(i) else os.path.join(env["UNPACK"]["EXTRACTDIR"], i) for i in target]
    
    return target, source




# generate function, that adds the builder to the environment
# @env environment object
def generate( env ) :
    # setup environment variable
    toolset = { 
        "STOPONEMPTYFILE"  : True,
        "VIWEXTRACTOUTPUT" : False,
        "EXTRACTDIR"       : os.curdir,
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
                "EXTRACTCMD"     : "${UNPACK['EXTRACTOR']['GZIP']['RUN']} ${UNPACK['EXTRACTOR']['GZIP']['EXTRACTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['GZIP']['EXTRACTSUFFIX']}",
                "RUN"            : "",
                "LISTCMD"        : "${UNPACK['EXTRACTOR']['GZIP']['RUN']} ${UNPACK['EXTRACTOR']['GZIP']['LISTFLAGS']} $SOURCE ${UNPACK['EXTRACTOR']['GZIP']['LISTSUFFIX']}",
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

    # read tools for Windows system
    if env["PLATFORM"] <> "darwin" and "win" in env["PLATFORM"] :
        
        if env.WhereIs("7z") :
            toolset["EXTRACTOR"]["TARGZ"]["RUN"]           = "7z"
            toolset["EXTRACTOR"]["TARGZ"]["LISTEXTRACTOR"] = __fileextractor_win_7zip
            toolset["EXTRACTOR"]["TARGZ"]["LISTFLAGS"]     = "x"
            toolset["EXTRACTOR"]["TARGZ"]["LISTSUFFIX"]    = "-so -y | ${UNPACK['EXTRACTOR']['TARGZ']['RUN']} l -sii -ttar -y -so"
            toolset["EXTRACTOR"]["TARGZ"]["EXTRACTFLAGS"]  = "x"
            toolset["EXTRACTOR"]["TARGZ"]["EXTRACTSUFFIX"] = "-so -y | ${UNPACK['EXTRACTOR']['TARGZ']['RUN']} x -sii -ttar -y -oc:${UNPACK['EXTRACTDIR']}"
            
            toolset["EXTRACTOR"]["TARBZ"]["RUN"]           = "7z"
            toolset["EXTRACTOR"]["TARBZ"]["LISTEXTRACTOR"] = __fileextractor_win_7zip
            toolset["EXTRACTOR"]["TARBZ"]["LISTFLAGS"]     = "x"
            toolset["EXTRACTOR"]["TARBZ"]["LISTSUFFIX"]    = "-so -y | ${UNPACK['EXTRACTOR']['TARGZ']['RUN']} l -sii -ttar -y -so"
            toolset["EXTRACTOR"]["TARBZ"]["EXTRACTFLAGS"]  = "x"
            toolset["EXTRACTOR"]["TARBZ"]["EXTRACTSUFFIX"] = "-so -y | ${UNPACK['EXTRACTOR']['TARGZ']['RUN']} x -sii -ttar -y -oc:${UNPACK['EXTRACTDIR']}"
            
            toolset["EXTRACTOR"]["BZIP"]["RUN"]            = "7z"
            toolset["EXTRACTOR"]["BZIP"]["LISTEXTRACTOR"]  = __fileextractor_win_7zip
            toolset["EXTRACTOR"]["BZIP"]["LISTFLAGS"]      = "l"
            toolset["EXTRACTOR"]["BZIP"]["LISTSUFFIX"]     = "-y -so"
            toolset["EXTRACTOR"]["BZIP"]["EXTRACTFLAGS"]   = "x"
            toolset["EXTRACTOR"]["BZIP"]["EXTRACTSUFFIX"]  = "-y -oc:${UNPACK['EXTRACTDIR']}"
            
            toolset["EXTRACTOR"]["GZIP"]["RUN"]            = "7z"
            toolset["EXTRACTOR"]["GZIP"]["LISTEXTRACTOR"]  = __fileextractor_win_7zip
            toolset["EXTRACTOR"]["GZIP"]["LISTFLAGS"]      = "l"
            toolset["EXTRACTOR"]["GZIP"]["LISTSUFFIX"]     = "-y -so"
            toolset["EXTRACTOR"]["GZIP"]["EXTRACTFLAGS"]   = "x"
            toolset["EXTRACTOR"]["GZIP"]["EXTRACTSUFFIX"]  = "-y -oc:${UNPACK['EXTRACTDIR']}"
            
            toolset["EXTRACTOR"]["ZIP"]["RUN"]             = "7z"
            toolset["EXTRACTOR"]["ZIP"]["LISTEXTRACTOR"]   = __fileextractor_win_7zip
            toolset["EXTRACTOR"]["ZIP"]["LISTFLAGS"]       = "l"
            toolset["EXTRACTOR"]["ZIP"]["LISTSUFFIX"]      = "-y -so"
            toolset["EXTRACTOR"]["ZIP"]["EXTRACTFLAGS"]    = "x"
            toolset["EXTRACTOR"]["ZIP"]["EXTRACTSUFFIX"]   = "-y -oc:${UNPACK['EXTRACTDIR']}"
            
            toolset["EXTRACTOR"]["TAR"]["RUN"]             = "7z"
            toolset["EXTRACTOR"]["TAR"]["LISTEXTRACTOR"]   = __fileextractor_win_7zip
            toolset["EXTRACTOR"]["TAR"]["LISTFLAGS"]       = "l"
            toolset["EXTRACTOR"]["TAR"]["LISTSUFFIX"]      = "-y -ttar -so"
            toolset["EXTRACTOR"]["TAR"]["EXTRACTFLAGS"]    = "x"
            toolset["EXTRACTOR"]["TAR"]["EXTRACTSUFFIX"]   = "-y -ttar -oc:${UNPACK['EXTRACTDIR']}"
            
        # here can add some other Windows tools, that can handle the archive files
        # but I don't know which ones can handle all file types

        
        
    # read the tools on *nix systems and sets the default parameters
    elif env["PLATFORM"] in ["darwin", "linux", "posix"] :
        
        if env.WhereIs("unzip") :
            toolset["EXTRACTOR"]["ZIP"]["RUN"]             = "unzip"
            toolset["EXTRACTOR"]["ZIP"]["LISTEXTRACTOR"]   = __fileextractor_nix_unzip
            toolset["EXTRACTOR"]["ZIP"]["LISTFLAGS"]       = "-l"
            toolset["EXTRACTOR"]["ZIP"]["EXTRACTFLAGS"]    = "-oqq"
            toolset["EXTRACTOR"]["ZIP"]["EXTRACTSUFFIX"]   = "-d ${UNPACK['EXTRACTDIR']}"
        
        if env.WhereIs("tar") :
            toolset["EXTRACTOR"]["TAR"]["RUN"]             = "tar"
            toolset["EXTRACTOR"]["TAR"]["LISTEXTRACTOR"]   = __fileextractor_nix_tar
            toolset["EXTRACTOR"]["TAR"]["LISTFLAGS"]       = "tvf"
            toolset["EXTRACTOR"]["TAR"]["EXTRACTFLAGS"]    = "xf"
            toolset["EXTRACTOR"]["TAR"]["EXTRACTSUFFIX"]   = "-C ${UNPACK['EXTRACTDIR']}"

            toolset["EXTRACTOR"]["TARGZ"]["RUN"]           = "tar"
            toolset["EXTRACTOR"]["TARGZ"]["LISTEXTRACTOR"] = __fileextractor_nix_tar
            toolset["EXTRACTOR"]["TARGZ"]["EXTRACTFLAGS"]  = "xfz"
            toolset["EXTRACTOR"]["TARGZ"]["LISTFLAGS"]     = "tvfz"
            toolset["EXTRACTOR"]["TARGZ"]["EXTRACTSUFFIX"] = "-C ${UNPACK['EXTRACTDIR']}"

            toolset["EXTRACTOR"]["TARBZ"]["RUN"]           = "tar"
            toolset["EXTRACTOR"]["TARBZ"]["LISTEXTRACTOR"] = __fileextractor_nix_tar
            toolset["EXTRACTOR"]["TARBZ"]["EXTRACTFLAGS"]  = "xfj"
            toolset["EXTRACTOR"]["TARBZ"]["LISTFLAGS"]     = "tvfj"
            toolset["EXTRACTOR"]["TARBZ"]["EXTRACTSUFFIX"] = "-C ${UNPACK['EXTRACTDIR']}"
        
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
    
    # the target_factory must be a "Entry", because the target list can be files and dirs, so we can not specified the targetfactory explicite 
    env.Replace(UNPACK = toolset)
    env["BUILDERS"]["Unpack"] = SCons.Builder.Builder( action = __action,  emitter = __emitter,  target_factory = SCons.Node.FS.Entry,  source_factory = SCons.Node.FS.File,  single_source = True,  PRINT_CMD_LINE_FUNC = __message )


# existing function of the builder
# @param env environment object
# @return true
def exists(env) :
    return 1
