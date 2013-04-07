# -*- coding: utf-8 -*-

# This is a Builder for getting access for a SVN & Git Repositories.
# The builder need the external command line tools for SVN & Git access,
# so they must be installed in the system and accessiable by Scons

import os

#import SCons.Errors
import SCons.Util




# detecting tool function and setting default parameter,
# we use always abspath, because the reporitory can not work
# without an relative path
# @param env environment object
def __detect( env ) :   
    env["REPOSITORY"] = {
    
        "SVN" : {
            
            "RUN"       : "",
            "CHECKOUT"  : "",
            "UPDATE"    : "",
            "COMMIT"    : "",
            
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
            "PARAMETER" : "--git-dir=${SOURCE.abspath}${REPOSITORY['GIT']['DIR']} --work-tree=${SOURCE.abspath}",
            "PULL"      : "${REPOSITORY['GIT']['RUN']} ${REPOSITORY['GIT']['PARAMETER']} pull",
            "PUSH"      : "${REPOSITORY['GIT']['RUN']} ${REPOSITORY['GIT']['PARAMETER']} push",
            "CLONE"     : "${REPOSITORY['GIT']['RUN']} clone $SOURCE ${TARGET.abspath}",
            "COMMIT"    : "${REPOSITORY['GIT']['RUN']} ${REPOSITORY['GIT']['PARAMETER']} add . && ${REPOSITORY['GIT']['RUN']} ${REPOSITORY['GIT']['PARAMETER']} commit -m $TARGET"
            
        }
    
    }



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




# generate function, that adds the builder to the environment
# @env environment object
def generate( env ) :
    __detect(env)

    env["BUILDERS"]["GitClone"]   = SCons.Builder.Builder( action = SCons.Action.Action("${REPOSITORY['GIT']['CLONE']}"),  target_factory = SCons.Node.FS.Dir,  source_factory = SCons.Node.Python.Value,  single_source = True,  PRINT_CMD_LINE_FUNC = __GitCloneMessage )
    env["BUILDERS"]["GitPull"]    = SCons.Builder.Builder( action = SCons.Action.Action("${REPOSITORY['GIT']['PULL']}"),  source_factory = SCons.Node.FS.Dir,  single_source = True,  PRINT_CMD_LINE_FUNC = __GitPullMessage )
    env["BUILDERS"]["GitCommit"]  = SCons.Builder.Builder( action = SCons.Action.Action("${REPOSITORY['GIT']['COMMIT']}"),  source_factory = SCons.Node.FS.Dir,  single_source = True,  PRINT_CMD_LINE_FUNC = __GitCommitMessage )


# existing function of the builder
# @return true
def exists(env) :
    return 1