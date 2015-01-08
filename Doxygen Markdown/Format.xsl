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


    <!--definition for linebreaks-->
    <xsl:template name="nl">
        <xsl:text>&#xa;</xsl:text>
    </xsl:template>

    <!--definition for a tabulator-->
    <xsl:template name="tab">
        <xsl:text>   </xsl:text>
    </xsl:template>

    <!--definition for the head-->
    <xsl:template name="head">
        <xsl:text>#</xsl:text>
    </xsl:template>

    <!--definition for line-->
    <xsl:template name="hr">
        <xsl:text>***</xsl:text>
        <xsl:call-template name="nl"/>
    </xsl:template>
    
    <!--definition for a blockelement-->
    <xsl:template name="block">
        <xsl:text>&gt; </xsl:text>
    </xsl:template>


    <!--defininition for source code (multiline) with one required parameter (value = source code)-->
    <xsl:template name="multisource">
        <xsl:param name="value" as="xs:string" required="yes"/>
        <xsl:param name="code"/>
        
        <xsl:call-template name="nl"/>
        <xsl:text>```</xsl:text>
        <xsl:value-of select="$code"/>
        <xsl:call-template name="nl"/>
        <xsl:value-of select="$value"/>
        <xsl:text>```</xsl:text>
        <xsl:call-template name="nl"/>
    </xsl:template>


    <!--defininition for source code (singleline) with one required parameter (value = source code)-->
    <xsl:template name="singlesource">
        <xsl:param name="value" as="xs:string" required="yes"/>
        <xsl:text> `</xsl:text>
        <xsl:value-of select="normalize-space(replace($value, '\n', ' '))"/>
        <xsl:text>` </xsl:text>
    </xsl:template>


    <!--definition for link with one required (url = link address) and one optional parameter (text = link description)-->
    <xsl:template name="link">
        <xsl:param name="text" as="xs:string"/>
        <xsl:param name="url" as="xs:string" required="yes"/>
        <xsl:choose>
            <xsl:when test="$text">
                <xsl:value-of select="concat(' [',$text)"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="concat('[', $url)"/>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:value-of select="concat('](', normalize-space($url), ') ')"/>
    </xsl:template>


    <!--definition for blod data with one required parameter (value = data)-->
    <xsl:template name="strong">
        <xsl:param name="value" as="xs:string" required="yes"/>
        <xsl:value-of select="concat(' __', $value, '__ ')"/>
    </xsl:template>


    <!--definition for italic data with one required parameter (value = data)-->
    <xsl:template name="italic">
        <xsl:param name="value" as="xs:string" required="yes"/>
        <xsl:value-of select="concat(' _', $value, '_ ')"/>
    </xsl:template>


    <!--creates the indent for a list element-->
    <xsl:template name="listindent">
        <xsl:param name="indent" select="0" as="xs:integer"/>
        <xsl:for-each select="1 to $indent">
            <xsl:call-template name="tab"/>
        </xsl:for-each>
    </xsl:template>
    
    
    <!--paragraph element-->
    <xsl:template name="paragraph">
        <xsl:param name="query" select="*"/>
        <xsl:param name="blockindent" select="0" as="xs:integer"/>
        
        <xsl:for-each select="1 to $blockindent">
            <xsl:call-template name="block"/>
        </xsl:for-each>
        
        <xsl:if test="$query">
            <xsl:apply-templates select="$query">
                <xsl:with-param name="blockindent" select="$blockindent+1"/>
            </xsl:apply-templates>
        </xsl:if>
    </xsl:template>


    <!--add list entry with one required parameter (value = itemdata) and one optional parameter (item = bulletdata)-->
    <xsl:template name="list">
        <xsl:param name="query" select="*"/>
        <xsl:param name="value"/>
        <xsl:param name="item" as="xs:string" select="'*'"/>
        <xsl:param name="listindent" select="0" as="xs:integer"/>

        <xsl:call-template name="listindent">
            <xsl:with-param name="indent" select="$listindent"/>
        </xsl:call-template>

        <xsl:value-of select="concat($item, ' ', $value)"/>

        <xsl:if test="$query">
            <xsl:apply-templates select="$query">
                <xsl:with-param name="listindent" select="$listindent+1"/>
            </xsl:apply-templates>
        </xsl:if>
        <xsl:call-template name="nl"/>
    </xsl:template>


    <!--template call for creating a section with header and indent.
        Parameter head for the heading text, query for the apply call (optional), 
        description for the line below header (optional) and sectionindent for indent
        of the section, that will passed down to the nodes
    -->
    <xsl:template name="section">
        <xsl:param name="head" required="yes"/>
        <xsl:param name="query" select="*"/>
        <xsl:param name="description"/>
        <xsl:param name="sort"/>
        <xsl:param name="sectionindent" select="1" as="xs:integer"/>

        <!--create the indent, sets header text and description-->
        <xsl:if test="$sectionindent gt 0">
            <xsl:for-each select="1 to $sectionindent">
                <xsl:call-template name="head"/>
            </xsl:for-each>
            <xsl:text> </xsl:text>
        </xsl:if>

        <xsl:value-of select="normalize-space($head)"/>
        <xsl:call-template name="nl"/>

        <xsl:if test="normalize-space($description)">
            <xsl:value-of select="normalize-space($description)"/>
            <xsl:call-template name="nl"/>
        </xsl:if>
        <xsl:call-template name="nl"/>

        <!--create the apply query-->
        <xsl:if test="$query">
            <!--
                <xsl:choose>
                <xsl:when test="$sort">
                <xsl:apply-templates select="$query">
                <xsl:with-param name="indent" select="$indent+1"/>
                <xsl:sort select="*[name()=$sort]"/>
                </xsl:apply-templates>
                </xsl:when>
                <xsl:otherwise>
            -->
            <xsl:apply-templates select="$query">
                <xsl:with-param name="sectionindent" select="$sectionindent+1"/>
            </xsl:apply-templates>
        </xsl:if>

        <xsl:call-template name="nl"/>
    </xsl:template>

</xsl:stylesheet>
