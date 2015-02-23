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



# This is a Builder for getting access for a SVN & Git Repositories.
# The builder need the external command line tools for SVN & Git access,
# so they must be installed in the system and accessiable by Scons

import subprocess, os
import SCons.Builder, SCons.Node, SCons.Errors, SCons.Script



# creates the output message for Git Clone
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __GitCloneMessage( s, target, source, env ) : 
    print "Git clone [%s] into [%s] ..." % (source[0], target[0])
    
# creates the output message for Git Pull
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __GitPullMessage( s, target, source, env ) :
    print "Git pull [%s] ..." % (source[0])
    
# creates the output message for Git Commit
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __GitCommitMessage( s, target, source, env ) : 
    print "Git commit with message [%s] ..." % (target[0])

# emitter for the Git clone call for setting
# the clean option
# @param target target file on the local drive
# @param source URL for download
# @env environment object
def __GitCloneEmitter( target, source, env ) :
    env.Clean( target, target[0] )
    return target, source
        
        

# creates the output message for SVN checkout
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __SVNCheckoutMessage( s, target, source, env ) : 
    print "SVN Checkout [%s] into [%s] ..." % (source[0], target[0])
    
# creates the output message for SVN update
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __SVNUpdateMessage( s, target, source, env ) : 
    print "SVN Update [%s] ..." % (source[0])
    
# creates the output message for SVN update
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __SVNCommitMessage( s, target, source, env ) : 
    print "SVN Commit [%s] ..." % (source[0])

# emitter for the SVN checkout call for setting
# the clean option
# @param target target file on the local drive
# @param source URL for download
# @env environment object
def __SVNCheckoutEmitter( target, source, env ) :
    env.Clean( target, target[0] )
    return target, source



# global emitter, that maps a source to a source
# without dependency cycle and always-build option
# @param target target file on the local drive
# @param source URL for download
# @env environment object
def __mapemitter( target, source, env ) :
    SCons.Script.Ignore(source, source)
    SCons.Script.AlwaysBuild(source)
    return source, source
        


# generate function, that adds the builder to the environment
# @env environment object
def generate( env ) :
    # setup environment variables
    env["REPOSITORY"] = {
    
        # we need some syntax data for calling the SVN client
        # RUN       => path to the command-line svn client
        # CHECKOUT  => checkout command
        # UPDATE    => update command
        # COMMIT    => command for commit
        "SVN" : {
            
            "RUN"       : "svn",
            "CHECKOUT"  : "${REPOSITORY['SVN']['RUN']} checkout $SOURCE ${TARGET.abspath}",
            "UPDATE"    : "${REPOSITORY['SVN']['RUN']} update $SOURCE",
            "COMMIT"    : "${REPOSITORY['SVN']['RUN']} add $SOURCE"+os.path.sep+"* --force && ${REPOSITORY['SVN']['RUN']} commit $SOURCE -m $TARGET"
        },
        
        # we need the working & git dir, but for correct path seperation we store a path seperator and the Git-dir in a variable
        # DIR       => stores relativ to the work-tree the .git directory
        # RUN       => path to the command-line git client
        # PARAMETER => parameter, that is added on each git call
        # PULL      => command for pull request
        # PUSH      => command for push request
        # CLONE     => command for cloning
        # COMMIT    => command for commit
        "GIT" : {
            "DIR"       : os.path.sep + ".git",
            "RUN"       : "git",
            "PARAMETER" : "--git-dir=$SOURCE${REPOSITORY['GIT']['DIR']}",
            "PULL"      : "${REPOSITORY['GIT']['RUN']} ${REPOSITORY['GIT']['PARAMETER']} pull",
            "PUSH"      : "${REPOSITORY['GIT']['RUN']} ${REPOSITORY['GIT']['PARAMETER']} push",
            "CLONE"     : "${REPOSITORY['GIT']['RUN']} clone $SOURCE ${TARGET.abspath}",
            "COMMIT"    : "${REPOSITORY['GIT']['RUN']} ${REPOSITORY['GIT']['PARAMETER']} add . && ${REPOSITORY['GIT']['RUN']} ${REPOSITORY['GIT']['PARAMETER']} commit -m $TARGET"
        }
    
    }

    # add for each "general" command an own builder
    env["BUILDERS"]["GitClone"]    = SCons.Builder.Builder( action = SCons.Action.Action("${REPOSITORY['GIT']['CLONE']}"),   emitter = __GitCloneEmitter,     source_factory = SCons.Node.Python.Value,  target_factory = SCons.Node.FS.Dir,    single_source = True,  PRINT_CMD_LINE_FUNC = __GitCloneMessage )
    env["BUILDERS"]["GitPull"]     = SCons.Builder.Builder( action = SCons.Action.Action("${REPOSITORY['GIT']['PULL']}"),    emitter = __mapemitter,          source_factory = SCons.Node.FS.Dir,        target_factory = SCons.Node.FS.Dir,    single_source = True,  PRINT_CMD_LINE_FUNC = __GitPullMessage )
    env["BUILDERS"]["GitCommit"]   = SCons.Builder.Builder( action = SCons.Action.Action("${REPOSITORY['GIT']['COMMIT']}"),  emitter = __mapemitter,          source_factory = SCons.Node.FS.Dir,        target_factory = SCons.Node.FS.Dir,    single_source = True,  PRINT_CMD_LINE_FUNC = __GitCommitMessage )

    env["BUILDERS"]["SVNCheckout"] = SCons.Builder.Builder( action = SCons.Action.Action("${REPOSITORY['SVN']['CHECKOUT']}"),  emitter = __SVNCheckoutEmitter,  source_factory = SCons.Node.Python.Value,  target_factory = SCons.Node.FS.Dir,  single_source = True,  PRINT_CMD_LINE_FUNC = __SVNCheckoutMessage )
    env["BUILDERS"]["SVNUpdate"]   = SCons.Builder.Builder( action = SCons.Action.Action("${REPOSITORY['SVN']['UPDATE']}"),    emitter = __mapemitter,          source_factory = SCons.Node.FS.Dir,        target_factory = SCons.Node.FS.Dir,  single_source = True,  PRINT_CMD_LINE_FUNC = __SVNUpdateMessage )
    env["BUILDERS"]["SVNCommit"]   = SCons.Builder.Builder( action = SCons.Action.Action("${REPOSITORY['SVN']['COMMIT']}"),    emitter = __mapemitter,          source_factory = SCons.Node.FS.Dir,        target_factory = SCons.Node.FS.Dir,  single_source = True,  PRINT_CMD_LINE_FUNC = __SVNCommitMessage )


# existing function of the builder
# @param env environment object
# @return true
def exists(env) :
    return 1
