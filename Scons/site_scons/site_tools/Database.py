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
        
     
     
# emitter for database create builder
# @param target target file on the local drive
# @param source URL for download
# @param env environment object        
def __createEmitter( target, source, env ) :
    if len(env.get("connection", "")) == 0 :
        raise SCons.Errors.StopError( "connection definition must be a non-empty string" )

    """
    if "order" in env and len(env.get("order", [])) == 0 :
        raise SCons.Errors.StopError( "order option must be a non-empty list" )

    if "layout" in env and len(env.get("layout", {}).keys()) == 0 :
        raise SCons.Errors.StopError( "layout definition must be a non-emtpy dictionary" )

    if "native" in env and len(env.get("native", [])) == 0 :
        raise SCons.Errors.StopError( "native option must be a non-empty list" )
        
    """
        
    return target, source
    
        
        
# defines the builder of the builder for database creating
# @param target target file on the local drive
# @param source URL for download
# @param env environment object
def __createBuilder( target, source, env ) :
    # create the database connection and set the transaction
    engine      = None
    metadata    = None
    connect     = None
    transaction = None
    
    try :
        engine      = sqlalchemy.create_engine(env["connection"], echo = env.get("DATABASE_VERBOSE", False) )   
        metadata    = sqlalchemy.MetaData()
        connect     = engine.connect()
        transaction = sqlalchemy.sessionmaker(autocommit=False)
    except Exception, e :
        raise SCons.Errors.StopError( e )

    """
    try :
        
        # for Python 2.6 we need an orderd dict structure, so we check the "order" parameter
        order = env.get("order", [])
        if order :
            for i in order :
                if not i in env.get("layout", []) :
                    raise SCons.Errors.StopError( "order key [%s] not in the database definition" % (i) )
                
                __createTable( env, engine, metadata, connect, i, env["layout"][i] )
        
        # for an ordered structure we can iterate of the data
        else :
            for tablename, tabledata in env.get("layout", {}).iteritems() :
                __createTable( env, transaction, transaction, connect, tablename, tabledata )
                
        # run native code
        #for i in env.get("native", []) :
        #    transaction.execute( i )
        
        transaction.commit()
    except Exception, e :
        transaction.rollback()
        raise SCons.Errors.StopError( e )
    """
    connect.close()
    
    
# function that creates all tables in the database
# @param env environment object
# @param engine engine object
# @param metadata metadata object
# @param connect connect object
# @param tablename string with table name
# @param tabledata dict with table data
def __createTable( env, engine, metadata, connect, tablename, tabledata ) :
    # get all columns and add them to table
    tablestructure = []
    for columnname, columndata in (dict((contentname, contentdata) for contentname, contentdata in tabledata.iteritems() if type(contentdata) == type({}) and contentdata.get("kind") == "column")).iteritems() :
        
        # get all parameters 
        param = dict((key, value) for key, value in columndata.iteritems() if not key in ["kind", "type", "foreignkey"])

        # get foreign keys
        if "foreignkey" in columndata and type(columndata["foreignkey"]) == type("") :
            tablestructure.append( sqlalchemy.Column( columnname, columndata["type"], sqlalchemy.ForeignKey(columndata["foreignkey"]), **param ) )
        elif "foreignkey" in columndata and type(columndata["foreignkey"]) == type([]) :
            tablestructure.append( sqlalchemy.Column( columnname, columndata["type"], *[sqlalchemy.ForeignKey(i) for i in columndata["foreignkey"]], **param ) )
        else :
            tablestructure.append( sqlalchemy.Column( columnname, columndata["type"], **param ) )


    # create table structure (and drop optional all tables before)
    if tablestructure :
        sqlalchemy.Table( tablename, metadata, *tablestructure )
        
        if env.get("DATABASE_DROPALL", False) :
            metadata.drop_all( engine )
        metadata.create_all( engine, checkfirst=env.get("DATABASE_CHECKFIRST", True) )
        
        
    # create inserts to the table if the insert field is a list
    if "insert" in tabledata and type(tabledata["insert"]) == type([]) and tabledata["insert"] :
        for i in tabledata["insert"] :
            connect.execute( sqlalchemy.Table( tablename, metadata ).insert(), **i )

                    

    
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
    