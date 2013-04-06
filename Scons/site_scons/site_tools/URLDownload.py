# -*- coding: utf-8 -*-

# the URLDownload-Builder can be download any data from an URL into a target file
# and can replace the target file name with the URL filename (the setting variable
# within the environment object is a boolean type with the name "URLDOWNLOAD_USEURLFILENAM", 
# default setting replaces the target name with the URL filename)


import urllib2
import urlparse

import SCons.Builder
import SCons.Node
import SCons.Errors



# creates the downloading output message
# @param s original message
# @param target target name
# @param source source name
# @param env environment object
def __message( s, target, source, env ) : 
    print "downloading [%s] to [%s] ..." % (source[0], target[0])


# the download function, which reads the data from the URL
# and writes it down to the file
# @param target target file on the local drive
# @param source URL for download
# @env environment object
def __action( target, source, env ) :
    try :
        stream = urllib2.urlopen( str(source[0]) )
        file   = open( str(target[0]), "wb" )
        file.write(stream.read())
        file.close()
        stream.close()
    except Exception, e :
        raise SCons.Errors.StopError( e )


# defines the emitter of the builder
# @param target target file on the local drive
# @param source URL for download
# @env environment object
def __emitter( target, source, env ) :
    # we need a temporary file, because the dependency graph
    # of Scons need a physical existing file (here should be
    # a pseudo file a nice way)
    target[0].prepare()

    if not env.get("URLDOWNLOAD_USEURLFILENAME", False) :
        return target, source

    try :
        url = urlparse.urlparse( str(source[0]) )
    except Exception, e :
        raise SCons.Errors.StopError( e )

    return url.path.split("/")[-1], source




# generate function, that adds the builder to the environment,
# the value "DOWNLOAD_USEFILENAME" replaces the target name with
# the filename of the URL
# @env environment object
def generate( env ) :
    env["BUILDERS"]["URLDownload"] = SCons.Builder.Builder( action = __action,  emitter = __emitter,  target_factory = SCons.Node.FS.File,  source_factory = SCons.Node.Python.Value,  PRINT_CMD_LINE_FUNC = __message )
    env.Replace(URLDOWNLOAD_USEURLFILENAME =  True )

# existing function of the builder
# @return true
def exists(env) :
    return 1


