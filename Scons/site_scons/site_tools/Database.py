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
    # create the database connection and set the transaction
    try :
        engine   = sqlalchemy.create_engine(env["connection"], echo = env.get("DATABASE_VERBOSE", False) )   
        metadata = sqlalchemy.MetaData()
        connect  = engine.connect()
        

        for tablename, tabledata in env["layout"].iteritems() :

            tablestructure = []
            
            # get all columns and add them to table
            for columnname, columndata in (dict((contentname, contentdata) for contentname, contentdata in tabledata.iteritems() if type(contentdata) == type({}) and contentdata.get("kind") == "column")).iteritems() :
                tablestructure.append( sqlalchemy.Column( columnname, columndata["type"], **dict((key, value) for key, value in columndata.iteritems() if not key in ["kind", "type"] ) ) )

            # create table structure
            if tablestructure :
                sqlalchemy.Table( tablename, metadata, *tablestructure )
                metadata.create_all( engine, checkfirst=env.get("DATABASE_CHECKFIRST", True) )
                
                
            # create inserts to the table if the insert field is a list
            if "insert" in tabledata and type(tabledata["insert"]) == type([]) and tabledata["insert"] :
                for i in tabledata["insert"] :
                    connect.execute( sqlalchemy.Table( tablename, metadata ).insert(), **i )

        
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
    