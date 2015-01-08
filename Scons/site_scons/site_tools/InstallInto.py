# -*- coding: utf-8 -*-

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



# the InstallInto-Builder can store a list of sources into the target dir
# for each source a subdirectory can be list and non-existing directory
# will be created


import os, shutil
import SCons.Builder, SCons.Node, SCons.Errors


# creates the downloading output message
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __message( s, target, source, env ) :
    for s,t in zip(source, target) :
        print "install file [%s] to [%s] ..." % (s, t)


# the action function, which copies the files and creates
# the target directories if needed
# @param target list of target files
# @param source list of source files
# @@param env environment object
def __action( target, source, env ) :
    try :
        for s,t in zip(source, target) :

            tdir = os.path.dirname(str(t))
            if not os.path.exists(tdir) :
                os.makedirs(tdir)

            shutil.copy(str(s), str(t))
    except Exception, e :
        raise SCons.Errors.StopError( "%s" % (e) )


# defines the emitter of the builder
# @param target target directory
# @param source list of input files
# @param env environment object
def __emitter( target, source, env ) :
    if type(env["INSTALLATIONDIRS"]) == type("") :
        env["INSTALLATIONDIRS"] = [env["INSTALLATIONDIRS"]]
    if type(env["INSTALLATIONDIRS"]) <> type([]) :
        raise SCons.Errors.StopError( "installation dirs environment parameter must be a list" )

    ret = []
    for i,s in enumerate(source) :
        if i < len(env["INSTALLATIONDIRS"]) :
            ret.append( os.path.join( str(target[0]), env["INSTALLATIONDIRS"][i], os.path.basename(str(s)) ) )
        else :
            ret.append( os.path.join( str(target[0]), os.path.basename(str(s)) ) )

    return ret, source


# generate function, that adds the builder to the environment,
# the value "INSTALLATIONDIRS" is a list of subdirectories
# of the target directory
# @param env environment object
def generate( env ) :
    env["BUILDERS"]["InstallInto"] = SCons.Builder.Builder( action = __action,  emitter = __emitter, source_factory = SCons.Node.FS.File, target_factory = SCons.Node.FS.Dir, PRINT_CMD_LINE_FUNC = __message )
    env.Replace(INSTALLATIONDIRS =  [] )


# existing function of the builder
# @param env environment object
# @return true
def exists(env) :
    return 1
