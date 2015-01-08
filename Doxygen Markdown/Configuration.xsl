<!--
############################################################################
# GPL License                                                              #
#                                                                          #
# This file is part of the Doxygen Markdown Converter                      #
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
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
    xmlns:xs="http://www.w3.org/2001/XMLSchema">


    <!--text data for headlines (don't use linebreaks within the variable content)-->
    <xsl:variable name="text_PublicType" as="xs:string">Public Types</xsl:variable>
    <xsl:variable name="text_PublicFunction" as="xs:string">Public Member Methods</xsl:variable>
    <xsl:variable name="text_PublicStaticFunction" as="xs:string">Static Public Member Methods</xsl:variable>
    <xsl:variable name="text_PublicAttribute" as="xs:string">Public Attributes</xsl:variable>
    <xsl:variable name="text_PublicStaticAttribute" as="xs:string">Static Public Attributes</xsl:variable>

    <xsl:variable name="text_PrivateType" as="xs:string">Private Types</xsl:variable>
    <xsl:variable name="text_PrivateFunction" as="xs:string">Private Member Methods</xsl:variable>
    <xsl:variable name="text_PrivateStaticFunction" as="xs:string">Static Private Member Methods</xsl:variable>
    <xsl:variable name="text_PrivateAttribute" as="xs:string">Private Attributes</xsl:variable>
    <xsl:variable name="text_PrivateStaticAttribute" as="xs:string">Static Private Attributes</xsl:variable>
    
    <xsl:variable name="text_Friend" as="xs:string">Friends</xsl:variable>
    <xsl:variable name="text_DetailedDescription" as="xs:string">Detailed Description</xsl:variable>
    
    <xsl:variable name="text_TypenameName">typename</xsl:variable>
    
    
    <!--boolean flags, which parts are created-->
    <xsl:variable name="create_Classes" as="xs:boolean">true</xsl:variable>
    <xsl:variable name="create_Pages" as="xs:boolean">true</xsl:variable>
    <xsl:variable name="create_Namespaces" as="xs:boolean">true</xsl:variable>
    <xsl:variable name="create_Files" as="xs:boolean">true</xsl:variable>
    <xsl:variable name="create_Directory" as="xs:boolean">true</xsl:variable>
    
    
    <!--prefix for filenames (don't forget spaces at the end of the prefix / GitHub spaces must be changed to -)-->
    <xsl:variable name="MarkDownFileExtension" as="xs:string">md</xsl:variable>
    
    <xsl:variable name="fileprefix_Class" as="xs:string">Class-</xsl:variable>
    <xsl:variable name="fileprefix_Page" as="xs:string">Page-</xsl:variable>
    <xsl:variable name="fileprefix_Namespace" as="xs:string">Namespace-</xsl:variable>
    <xsl:variable name="fileprefix_File" as="xs:string">File-</xsl:variable>
    <xsl:variable name="fileprefix_Directory" as="xs:string">Directory-</xsl:variable>
    
    
</xsl:stylesheet>
