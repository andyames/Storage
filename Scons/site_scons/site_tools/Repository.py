# -*- coding: utf-8 -*-

# This is a Builder for getting access for a SVN & Git Repositories.
# The builder need the external command line tools for SVN & Git access,
# so they must be installed in the system and accessiable by Scons


import SCons.Errors
import SCons.Util




# detecting tool function and
# setting default parameter
# @param env environment object
def __detect( env ) :
    env["GITPARAMETER"] = ""
    env["SVNPARAMETER"] = ""
    
    env["REPOSITORY"] = {
    
        "SVN" : {
            
            "RUN"       : "",
            "PULL"      : "",
            "PUSH"      : "",
            "COMMIT"    : "",
            
        },
        
        "GIT" : {
            
            "RUN"       : "git",
            "PULL"      : "${REPOSITORY['GIT']['RUN']} $GITPARAMETER --work-tree=$TARGET pull",
            "PUSH"      : "${REPOSITORY['GIT']['RUN']} $GITPARAMETER --work-tree=$TARGET push",
            "CLONE"     : "${REPOSITORY['GIT']['RUN']} $GITPARAMETER clone $SOURCE $TARGET",
            "COMMIT"    : "${REPOSITORY['GIT']['RUN']} $GITPARAMETER --work-tree=$SOURCE add . && ${REPOSITORY['GIT']['RUN']} $GITPARAMETER --work-tree=$SOURCE commit -m $TARGET"
            
        }
    
    }

    pass


# creates the output message
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __GitCloneMessage( s, target, source, env ) : 
    print "Git clone [%s] into [%s] ..." % (source[0], target[0])


# generate function, that adds the builder to the environment
# @env environment object
def generate( env ) :
    __detect(env)

    env["BUILDERS"]["GitClone"] = SCons.Builder.Builder( action = SCons.Action.Action("${REPOSITORY['GIT']['CLONE']}"),  target_factory = SCons.Node.FS.Dir,  source_factory = SCons.Node.Python.Value,  PRINT_CMD_LINE_FUNC = __GitCloneMessage )
    env["BUILDERS"]["GitPull"] = SCons.Builder.Builder( action = SCons.Action.Action("${REPOSITORY['GIT']['PULL']}"),  target_factory = SCons.Node.Python.Value,  source_factory = SCons.Node.FS.Dir,  PRINT_CMD_LINE_FUNC = __GitCloneMessage )


# existing function of the builder
# @return true
def exists(env) :
    return 1