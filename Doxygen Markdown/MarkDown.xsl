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
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions"
    xmlns:local="localDocumentNamespace">

    <xsl:import href="./Configuration.xsl"/>
    <xsl:import href="./Format.xsl"/>
    <xsl:output method="text" version="1.0" encoding="UTF-8" indent="no" standalone="yes"/>
    <xsl:strip-space elements="*"/>




    <!--=== nodes for main structures ==================================================================================-->

    <xsl:template match="compounddef[@kind='dir']"/>
    <xsl:template match="compounddef[@kind='file']"/>
    <xsl:template match="compounddef[@kind='namespace']"/>
    <xsl:template match="compounddef[@kind='struct']"/>





    <!--layout structure for setting class data-->
    <xsl:template match="compounddef[@kind='class']">
        <xsl:if test="$create_Classes">
            <xsl:result-document href="{local:filename('class', compoundname)}">

                <xsl:variable name="template">
                    <xsl:apply-templates select="templateparamlist" mode="return"/>
                </xsl:variable>

                <xsl:call-template name="section">
                    <xsl:with-param name="head"
                        select="concat(replace(replace($template, '&lt;', '\\&lt;'), '&gt;', '\\&gt;'), ' ', compoundname)"/>
                    <xsl:with-param name="description" select="briefdescription"/>
                </xsl:call-template>

            </xsl:result-document>
        </xsl:if>
    </xsl:template>


    <!--layout setting for a page-->
    <xsl:template match="compounddef[@kind='page']">
        <xsl:if test="$create_Pages">
            <xsl:result-document href="{local:filename('page', title)}">

                <xsl:call-template name="section">
                    <xsl:with-param name="head" select="title"/>
                    <xsl:with-param name="description" select="briefdescription"/>
                </xsl:call-template>

            </xsl:result-document>
        </xsl:if>
    </xsl:template>

    <!--================================================================================================================-->




    <!--=== nodes for header structure =================================================================================-->

    <!--template for matching public member functions-->
    <xsl:template match="sectiondef[@kind='public-func']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="hr"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="sort" select="name"/>
            <xsl:with-param name="query" select="memberdef"/>
            <xsl:with-param name="head" select="$text_PublicFunction"/>
        </xsl:call-template>
    </xsl:template>


    <!--template for matching public static functions-->
    <xsl:template match="sectiondef[@kind='public-static-func']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="hr"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="sort" select="name"/>
            <xsl:with-param name="query" select="memberdef"/>
            <xsl:with-param name="head" select="$text_PublicStaticFunction"/>
        </xsl:call-template>
    </xsl:template>


    <!--template for matching public member functions-->
    <xsl:template match="sectiondef[@kind='public-type']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="hr"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="sort" select="name"/>
            <xsl:with-param name="query" select="memberdef"/>
            <xsl:with-param name="head" select="$text_PublicType"/>
        </xsl:call-template>
    </xsl:template>


    <!--template for matching public attributes-->
    <xsl:template match="sectiondef[@kind='public-attrib']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="hr"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="sort" select="name"/>
            <xsl:with-param name="query" select="memberdef"/>
            <xsl:with-param name="head" select="$text_PublicAttribute"/>
        </xsl:call-template>
    </xsl:template>


    <!--template for matching public static attributes-->
    <xsl:template match="sectiondef[@kind='public-static-attrib']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="hr"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="sort" select="name"/>
            <xsl:with-param name="query" select="memberdef"/>
            <xsl:with-param name="head" select="$text_PublicStaticAttribute"/>
        </xsl:call-template>
    </xsl:template>



    <!--template for matching private functions-->
    <xsl:template match="sectiondef[@kind='private-func']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="hr"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="sort" select="name"/>
            <xsl:with-param name="query" select="memberdef"/>
            <xsl:with-param name="head" select="$text_PrivateFunction"/>
        </xsl:call-template>
    </xsl:template>


    <!--template for matching private static functions-->
    <xsl:template match="sectiondef[@kind='private-static-func']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="hr"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="sort" select="name"/>
            <xsl:with-param name="query" select="memberdef"/>
            <xsl:with-param name="head" select="$text_PrivateStaticFunction"/>
        </xsl:call-template>
    </xsl:template>


    <!--template for matching public member functions-->
    <xsl:template match="sectiondef[@kind='private-type']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="hr"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="sort" select="name"/>
            <xsl:with-param name="query" select="memberdef"/>
            <xsl:with-param name="head" select="$text_PrivateType"/>
        </xsl:call-template>
    </xsl:template>


    <!--template for matching private attributes-->
    <xsl:template match="sectiondef[@kind='private-attrib']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="hr"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="sort" select="name"/>
            <xsl:with-param name="query" select="memberdef"/>
            <xsl:with-param name="head" select="$text_PrivateAttribute"/>
        </xsl:call-template>
    </xsl:template>


    <!--template for matching private static attributes-->
    <xsl:template match="sectiondef[@kind='private-static-attrib']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="hr"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="sort" select="name"/>
            <xsl:with-param name="query" select="memberdef"/>
            <xsl:with-param name="head" select="$text_PrivateStaticAttribute"/>
        </xsl:call-template>
    </xsl:template>



    <!--template for matching friend declaration-->
    <xsl:template match="sectiondef[@kind='friend']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="hr"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="sort" select="name"/>
            <xsl:with-param name="query" select="memberdef"/>
            <xsl:with-param name="head" select="$text_Friend"/>
        </xsl:call-template>
    </xsl:template>



    <xsl:template match="memberdef[@kind='enum']"/>


    <!--typedef doxygen definition-->
    <xsl:template match="memberdef[@kind='typedef']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="head">
                <xsl:call-template name="singlesource">
                    <xsl:with-param name="value" select="concat(type, ' ', name)"/>
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>


    <!--function / methode / friend doxygen definition-->
    <xsl:template match="memberdef[@kind='function'] | memberdef[@kind='friend']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="head">
                <xsl:call-template name="singlesource">
                    <xsl:with-param name="value">
                        <xsl:apply-templates select="templateparamlist" mode="return"/>
                        <xsl:value-of select="concat(' ', type, ' ', name, argsstring)"/>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>
        <xsl:call-template name="hr"/>
    </xsl:template>


    <!--member / variable doxygen definition-->
    <xsl:template match="memberdef[@kind='variable']">
        <xsl:param name="sectionindent"/>

        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="head">
                <xsl:call-template name="singlesource">
                    <xsl:with-param name="value" select="concat(type, ' ', name, ' ', initializer)"
                    />
                </xsl:call-template>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>


    <!--structure of doxygens briefdescription-->
    <xsl:template match="briefdescription">
        <xsl:param name="listindent" as="xs:integer" select="0"/>

        <xsl:if test="normalize-space(.)">
            <xsl:call-template name="nl"/>
            <xsl:call-template name="nl"/>
            <xsl:call-template name="listindent">
                <xsl:with-param name="indent" select="$listindent"/>
            </xsl:call-template>
            <xsl:value-of select="concat(normalize-space(.), ' ')"/>
            <xsl:call-template name="nl"/>
        </xsl:if>
    </xsl:template>


    <!--template for detailed description eg bug / todo / parameter lists-->
    <xsl:template match="detaileddescription">
        <xsl:param name="sectionindent"/>

        <xsl:if test="normalize-space(.)">
            <xsl:call-template name="hr"/>
            <xsl:call-template name="section">
                <xsl:with-param name="sectionindent" select="$sectionindent"/>
                <xsl:with-param name="head" select="$text_DetailedDescription"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!--================================================================================================================-->


    <!--=== nodes for layout of datasets ===============================================================================-->

    <xsl:template match="compounddef/briefdescription"/>

    <xsl:template match="parameternamelist"/>
    <xsl:template match="derivedcompoundref"/>
    <xsl:template match="reimplementedby"/>
    <xsl:template match="compoundname"/>
    <xsl:template match="title"/>

    <!--<xsl:template match="memberdef/detaileddescription"/>-->
    <xsl:template match="memberdef/type"/>
    <xsl:template match="memberdef/argsstring"/>
    <xsl:template match="memberdef/definition"/>
    <xsl:template match="memberdef/param"/>
    <xsl:template match="memberdef/name"/>
    <xsl:template match="memberdef/initializer"/>

    <!--check the kindref attribute and create a link within the wiki-->
    <xsl:template match="references"/>
    <xsl:template match="ref">
        <xsl:value-of select="concat(' ', ., ' ')"/>
    </xsl:template>


    <!--template for para tag, add blank space for correct layout-->
    <xsl:template match="para">
        <xsl:param name="sectionindent"/>

        <xsl:apply-templates>
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
        </xsl:apply-templates>
        <xsl:text> </xsl:text>
    </xsl:template>


    <!--computeroutput template for file definitions - should be a link in the output-->
    <xsl:template match="computeroutput">
        <xsl:call-template name="singlesource">
            <xsl:with-param name="value" select="."/>
        </xsl:call-template>
    </xsl:template>


    <!--seperator for linebreak-->
    <xsl:template match="simplesectsep | simplesect">
        <xsl:apply-templates/>
        <xsl:call-template name="nl"/>
    </xsl:template>


    <!--note description with block element-->
    <xsl:template match="simplesect[@kind='note']">
        <xsl:param name="blockindent" select="1"/>
        <xsl:call-template name="paragraph">
            <xsl:with-param name="blockindent" select="$blockindent"/>
        </xsl:call-template>
        <xsl:call-template name="nl"/>
    </xsl:template>


    <!--function return parameter-->
    <xsl:template match="simplesect[@kind='return']">
        <xsl:param name="listindent" select="0"/>

        <xsl:call-template name="list">
            <xsl:with-param name="listindent" select="$listindent"/>
        </xsl:call-template>
    </xsl:template>


    <!--function parameter (we need the nl, because a linebreak must be added if the detailed description does not create any)-->
    <xsl:template match="parameterlist[@kind='param']">
        <xsl:param name="listindent" select="0"/>

        <xsl:call-template name="nl"/>
        <xsl:for-each select="parameteritem">
            <xsl:call-template name="list">
                <xsl:with-param name="listindent" select="$listindent"/>
                <xsl:with-param name="item" select="concat(position(), '.')"/>
                <xsl:with-param name="value">
                    <xsl:call-template name="singlesource">
                        <xsl:with-param name="value" select="parameternamelist"/>
                    </xsl:call-template>
                </xsl:with-param>
            </xsl:call-template>
        </xsl:for-each>
    </xsl:template>


    <!--todo / bug doxygen structure-->
    <xsl:template match="xreftitle"/>

    <xsl:template match="xrefsect">
        <xsl:param name="sectionindent" select="0"/>

        <xsl:call-template name="nl"/>
        <xsl:call-template name="section">
            <xsl:with-param name="sectionindent" select="$sectionindent"/>
            <xsl:with-param name="head" select="xreftitle"/>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="xrefdescription/para">
        <xsl:call-template name="list">
            <xsl:with-param name="query"/>
            <xsl:with-param name="value">
                <xsl:apply-templates/>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>


    <!--template for template lists (default ignore templatelist otherwise your return mode)-->
    <xsl:template match="templateparamlist"/>
    <xsl:template match="templateparamlist" mode="return">
        <xsl:value-of select="$text_TypenameName"/>
        <xsl:text>&lt;</xsl:text>
        <xsl:for-each select="param">
            <xsl:if test="position() gt 1">
                <xsl:text>,</xsl:text>
            </xsl:if>
            <xsl:apply-templates select="."/>
        </xsl:for-each>
        <xsl:text>&gt;</xsl:text>
    </xsl:template>

    <xsl:template match="templateparamlist/param">
        <xsl:value-of select="normalize-space(concat(replace(type, 'typename', ''), ' ', defname))"/>
        <xsl:apply-templates select="defval"/>
    </xsl:template>

    <xsl:template match="templateparamlist/param/defval">
        <xsl:value-of select="concat('=', .)"/>
    </xsl:template>


    <!--link doxygen definition-->
    <xsl:template match="ulink">
        <xsl:call-template name="link">
            <xsl:with-param name="text" select="."/>
            <xsl:with-param name="url" select="@url"/>
        </xsl:call-template>
    </xsl:template>


    <!--creates an bold text-->
    <xsl:template match="bold">
        <xsl:call-template name="strong">
            <xsl:with-param name="value" select="."/>
        </xsl:call-template>
    </xsl:template>


    <!--creates an italic text-->
    <xsl:template match="emphasis">
        <xsl:call-template name="italic">
            <xsl:with-param name="value" select="."/>
        </xsl:call-template>
    </xsl:template>


    <!--doxygen definition for inline source codes-->
    <xsl:template match="programlisting">
        <xsl:call-template name="multisource">
            <xsl:with-param name="value">
                <xsl:apply-templates/>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template match="codeline">
        <xsl:apply-templates/>
        <xsl:call-template name="nl"/>
    </xsl:template>

    <!--================================================================================================================-->




    <!--=== ignoring and default definitions ===========================================================================-->

    <!--create an internal link within the pages-->
    <xsl:function name="local:internallink">
        <xsl:param name="type" as="xs:string"/>
        <xsl:param name="name" as="xs:string"/>
        <xsl:value-of
            select="replace(local:filename($type, $name), concat('.', $MarkDownFileExtension), '')"
        />
    </xsl:function>


    <!--XSL function for creating the correct filename-->
    <xsl:function name="local:filename">
        <xsl:param name="type" as="xs:string"/>
        <xsl:param name="filename" as="xs:string"/>

        <xsl:choose>
            <xsl:when test="lower-case($type) = 'namespace'">
                <xsl:value-of
                    select="fn:encode-for-uri( concat($fileprefix_Namespace, replace(normalize-space($filename), ' ', '-'), '.', $MarkDownFileExtension))"
                />
            </xsl:when>

            <xsl:when test="lower-case($type) = 'class'">
                <xsl:value-of
                    select="fn:encode-for-uri( concat($fileprefix_Class, replace(normalize-space($filename), ' ', '-'), '.', $MarkDownFileExtension))"
                />
            </xsl:when>

            <xsl:when test="lower-case($type) = 'page'">
                <xsl:value-of
                    select="fn:encode-for-uri( concat($fileprefix_Page, replace(normalize-space($filename), ' ', '-'), '.', $MarkDownFileExtension))"
                />
            </xsl:when>

            <xsl:when test="lower-case($type) = 'directory'">
                <xsl:value-of
                    select="fn:encode-for-uri( concat($fileprefix_Directory, replace(normalize-space($filename), ' ', '-'), '.', $MarkDownFileExtension))"
                />
            </xsl:when>

            <xsl:when test="lower-case($type) = 'file'">
                <xsl:value-of
                    select="fn:encode-for-uri( concat($fileprefix_File, replace(normalize-space($filename), ' ', '-'), '.', $MarkDownFileExtension))"
                />
            </xsl:when>

            <xsl:otherwise>
                <xsl:message terminate="yes">
                    <xsl:value-of
                        select="concat('value [',$type,'] for filename [',$filename,'] creating is unknown')"
                    />
                </xsl:message>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:function>


    <!--default text node handling-->
    <xsl:template match="text()|@*">
        <xsl:value-of select="normalize-space(.)"/>
    </xsl:template>


    <xsl:template match="basecompoundref"/>
    <xsl:template match="inheritancegraph"/>
    <xsl:template match="location"/>
    <xsl:template match="inbodydescription"/>
    <xsl:template match="innerclass"/>
    <xsl:template match="innerfile"/>
    <xsl:template match="referencedby"/>
    <xsl:template match="listofallmembers"/>
    <xsl:template match="collaborationgraph"/>
    <xsl:template match="includes"/>

    <!--================================================================================================================-->

</xsl:stylesheet>
