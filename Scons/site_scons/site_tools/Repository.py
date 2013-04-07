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
    pass


# creates the output message
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __message( s, target, source, env ) : 
    pass


# generate function, that adds the builder to the environment
# @env environment object
def generate( env ) :
    __detect(env)


# existing function of the builder
# @return true
def exists(env) :
    return 1