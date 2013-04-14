# -*- coding: utf-8 -*-

# the Database builder can create and/or update any
# database which is supported by http://www.sqlalchemy.org/ .
# The builder is a wrapper around the SQLAlchemy interface,
# so SQLAlchemy and the database driver must be also installed,
# they are not part of the builder

import sqlalchemy
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
#def __updateMessage( s, target, source, env ) :
#    print "update database [%s] from [%s] ..." % (source[0], target[0])
        
        
        
def __createEmitter( target, source, env ) :
    if not "connection" in env or type(env["connection"]) <> type("") or len(env["connection"]) == 0:
        raise SCons.Errors.StopError( "connection definition must be a non-empty string" )

    if not "layout" in env or  type(env["layout"]) <> type({}) or len(env["layout"].keys()) == 0:
        raise SCons.Errors.StopError( "layout definition must be a non-empty dictionary" )
        
    return target, source
    
        
        
# defines the builder of the builder for database creating
# @param target target file on the local drive
# @param source URL for download
# @env environment object
def __createBuilder( target, source, env ) :
    # create the database connection
    try :
    
        db = sqlalchemy.create_engine(env["connection"], echo = env.get("DATABASE_VERBOSE", False) )
        metadata = sqlalchemy.MetaData()
        
        for tablename, fields in env["layout"].iteritems() :
            sqlalchemy.Table( tablename, metadata, *[
                sqlalchemy.Column(fieldname, fieldvalue["type"], **dict((k,v) for k,v in fieldvalue.iteritems() if k <> "type")) if type(fieldvalue) == type({}) else sqlalchemy.Column(fieldname, fieldvalue) for fieldname, fieldvalue in fields.iteritems()
            ])
       
        metadata.create_all( db, checkfirst=env.get("DATABASE_CHECKFIRST", True) )
    except Exception, e :
        raise SCons.Errors.StopError( e )
        

    
# defines the builder of the builder for database updating
# @param target target file on the local drive
# @param source URL for download
# @env environment object
#def __updateBuilder( target, source, env ) :
#    return target, source
    
    
    
    
# generate function, that adds the builder to the environment
# @env environment object
def generate( env ) :
    
    env["BUILDERS"]["DatabaseCreate"] = SCons.Builder.Builder( action = __createBuilder,  emitter = __createEmitter,  source_factory = SCons.Node.Python.Value,  target_factory = SCons.Node.Python.Value,  single_source = True,  PRINT_CMD_LINE_FUNC = __createMessage )
    #env["BUILDERS"]["DatabaseUpdate"] = SCons.Builder.Builder( action = __updateBuilder,  source_factory = SCons.Node.Python.Value,  target_factory = SCons.Node.Python.Value,  single_source = True,  PRINT_CMD_LINE_FUNC = __updateMessage )
    
# existing function of the builder
# @param env environment object
# @return true
def exists(env) :
    return 1
    