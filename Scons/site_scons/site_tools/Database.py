# -*- coding: utf-8 -*-

# the Database builder can create and/or update any
# database which is supported by Pythons Database API
# http://wiki.python.org/moin/DatabaseProgramming/
# The database is describe in a XML document

import SCons.Builder, SCons.Node, SCons.Errors



# creates the creating message
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __createMessage( s, target, source, env ) :
    print "create database [%s] from [%s] ..." % (source[0], target[0])
    
# creates the update message
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __updateMessage( s, target, source, env ) :
    print "update database [%s] from [%s] ..." % (source[0], target[0])
        
        
        
# defines the builder of the builder for database creating
# @param target target file on the local drive
# @param source URL for download
# @env environment object
def __createBuilder( target, source, env ) :
    return target, source
    
# defines the builder of the builder for database updating
# @param target target file on the local drive
# @param source URL for download
# @env environment object
def __updateBuilder( target, source, env ) :
    return target, source
    
    
    
    
# generate function, that adds the builder to the environment
# @env environment object
def generate( env ) :
    env["BUILDERS"]["DatabaseCreate"] = SCons.Builder.Builder( action = __createBuilder,  source_factory = SCons.Node.FS.File,  target_factory = SCons.Node.Python.Value,   single_source = True,  PRINT_CMD_LINE_FUNC = __createMessage )
    env["BUILDERS"]["DatabaseUpdate"] = SCons.Builder.Builder( action = __updateBuilder,  source_factory = SCons.Node.FS.File,  target_factory = SCons.Node.Python.Value,   single_source = True,  PRINT_CMD_LINE_FUNC = __updateMessage )
    
# existing function of the builder
# @param env environment object
# @return true
def exists(env) :
    return 1
    