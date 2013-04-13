# -*- coding: utf-8 -*-

# the InstallAll builder extends the Scons default Install builder with
# the linked libraries. The builder copies the target into a directory
# and checks the LIBS and copy them also into the target directory.
# Additional libs can be manual added or ignored.


import SCons.Builder, SCons.Node, SCons.Errors



# creates the install output message
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __message( s, target, source, env ) :
    for i in source :
        print "install [%s] to [%s] ..." % (i, target[0])
        
        
# defines the emitter of the builder, for
# creating the correct dependencies and library
# prefixes
# @param target target file on the local drive
# @param source URL for download
# @env environment object
def __emitter( target, source, env ) :
    return target, source
    
    
    
    
# generate function, that adds the builder to the environment
# @env environment object
def generate( env ) :
    env["BUILDERS"]["InstallAll"] = SCons.Builder.Builder( action = "",  emitter = __emitter,  target_factory = SCons.Node.FS.Dir,  single_source = False,  PRINT_CMD_LINE_FUNC = __message )
    
# existing function of the builder
# @param env environment object
# @return true
def exists(env) :
    return 1
    