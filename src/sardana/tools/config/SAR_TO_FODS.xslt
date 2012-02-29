<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
    <xsl:output method="xml" indent="yes"/>
    
    <xsl:template match="/Sardana">
        <office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                         xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
                         xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                         xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                         xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
                         xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
                         xmlns:xlink="http://www.w3.org/1999/xlink"
                         xmlns:dc="http://purl.org/dc/elements/1.1/"
                         xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
                         xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
                         xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
                         xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
                         xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
                         xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
                         xmlns:math="http://www.w3.org/1998/Math/MathML"
                         xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
                         xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
                         xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"
                         xmlns:ooo="http://openoffice.org/2004/office"
                         xmlns:ooow="http://openoffice.org/2004/writer"
                         xmlns:oooc="http://openoffice.org/2004/calc"
                         xmlns:dom="http://www.w3.org/2001/xml-events"
                         xmlns:xforms="http://www.w3.org/2002/xforms"
                         xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xmlns:rpt="http://openoffice.org/2005/report"
                         xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2"
                         xmlns:rdfa="http://docs.oasis-open.org/opendocument/meta/rdfa#"
                         xmlns:field="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:field:1.0"
                         xmlns:formx="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0"
                         office:version="1.2"
                         office:mimetype="application/vnd.oasis.opendocument.spreadsheet">
            <office:styles>
                <style:default-style style:family="table-cell">
                    <style:table-cell-properties style:decimal-places="2"/>
                    <style:paragraph-properties style:tab-stop-distance="0.5in"/>
                    <style:text-properties fo:font-size="8pt"
                                           style:font-name="Liberation Sans" fo:language="en" fo:country="US"
                                           style:font-size-asian="8pt"
                                           style:font-name-asian="DejaVu Sans"
                                           style:language-asian="zxx"
                                           style:country-asian="none"
                                           style:font-size-complex="8pt"
                                           style:font-name-complex="DejaVu Sans"
                                           style:language-complex="zxx"
                                           style:country-complex="none"/>
                </style:default-style>
                <style:style style:name="Default" style:family="table-cell"/>
            </office:styles>
            <office:automatic-styles>
                <style:style style:name="globalcol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="5in"/>
                </style:style>
                <style:style style:name="typecol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="1.2in"/>
                </style:style>
                <style:style style:name="servcol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="1.1in"/>
                </style:style>
                <style:style style:name="poolcol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="1.2in"/>
                </style:style>
                <style:style style:name="mscol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="1.2in"/>
                </style:style>
                <style:style style:name="ctrlcol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="2.2in"/>
                </style:style>
                <style:style style:name="namecol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="2in"/>
                </style:style>
                <style:style style:name="smallnamecol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="1.2in"/>
                </style:style>
                <style:style style:name="devnamecol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="1.6in"/>
                </style:style>
                <style:style style:name="axiscol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="0.4in"/>
                </style:style>
                <style:style style:name="desccol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="1.5in"/>
                </style:style>
                <style:style style:name="attrcol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="2in"/>
                </style:style>
                <style:style style:name="pathcol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="3in"/>
                </style:style>
                <style:style style:name="hostcol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="1.2in"/>
                </style:style>
                <style:style style:name="confcol" style:family="table-column">
                    <style:table-column-properties fo:break-before="auto" style:column-width="1in"/>
                </style:style>

                <style:style style:name="row1" style:family="table-row">
                    <style:table-row-properties style:row-height="0.1445in" fo:break-before="auto"
                                                style:use-optimal-row-height="true"/>
                </style:style>
                
                <style:style style:name="header1" style:family="table-cell" style:parent-style-name="Default">
                    <style:text-properties fo:font-size="8pt"
                                           fo:font-style="italic"
                                           fo:font-weight="bold"
                                           style:font-size-asian="8pt"
                                           style:font-style-asian="italic"
                                           style:font-weight-asian="bold"
                                           style:font-size-complex="8pt"
                                           style:font-style-complex="italic"
                                           style:font-weight-complex="bold"/>
                </style:style>
                <style:style style:name="cell1" style:family="table-cell" style:parent-style-name="Default">
                    <style:text-properties fo:font-size="8pt" style:font-size-asian="8pt" style:font-size-complex="8pt"/>
                </style:style>
            </office:automatic-styles>
            <office:body>
                <office:spreadsheet>
                    <xsl:call-template name="Set-Global"/>
                    <xsl:call-template name="Set-Servers"/>
                    <xsl:call-template name="Set-Doors"/>
                    <xsl:call-template name="Set-Controllers"/>
                    <xsl:call-template name="Set-Motors"/>
                    <xsl:call-template name="Set-IORegisters"/>
                    <xsl:call-template name="Set-Channels"/>
                    <xsl:call-template name="Set-CommunicationChannels"/>
                    <xsl:call-template name="Set-MeasurementGroups"/>
                    <xsl:call-template name="Set-Parameters"/>
                </office:spreadsheet>
            </office:body>
        </office:document>
    </xsl:template>

    <xsl:template name="Set-Parameters">
        <table:table table:name="Parameters" table:default-cell-style-name="Default">
            <table:table-column table:style-name="poolcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="confcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="desccol"    table:default-cell-style-name="cell1"/>
            <table:table-row table:style-name="row1">
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Pool</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Element</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Parameter</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Label</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Format</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Min Value</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Min Alarm</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Min Warning</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Max Warning</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Max Alarm</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Max Value</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Unit</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Polling Period</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Change Event</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Description</text:p>
                </table:table-cell>
            </table:table-row>
        
            <xsl:for-each select="PoolServer/Pool">
                <xsl:variable name="pool"><xsl:value-of select="@deviceName"/></xsl:variable>
                <xsl:for-each select="Controller">
                    <xsl:for-each select="Motor">
                        <xsl:variable name="element"><xsl:value-of select="@name"/></xsl:variable>
                        <xsl:for-each select="Attribute[Configuration]">
                            <table:table-row table:style-name="row1">
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="$pool"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="$element"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="@name"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="Configuration/Display/@label"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="Configuration/Display/@format"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="Configuration/Range/@min"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="Configuration/Alarms/@min_alarm"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="Configuration/Alarms/@min_warning"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="Configuration/Alarms/@max_warning"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="Configuration/Alarms/@max_alarm"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="Configuration/Range/@max"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="Configuration/Units/@unit"/></text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p>
                                        <xsl:choose>
                                            <xsl:when test="Polling/@polled = 'True' or Polling/@polled = 'Yes'">
                                                <xsl:value-of select="Polling/@period"/>
                                            </xsl:when>
                                            <xsl:otherwise>-1</xsl:otherwise>
                                        </xsl:choose>
                                    </text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p>
                                        <xsl:choose>
                                            <xsl:when test="Events/ChangeEvent/@absolute">
                                                <xsl:value-of select="Events/ChangeEvent/@absolute"/>
                                            </xsl:when>
                                            <xsl:when test="Events/ChangeEvent/@relative">
                                                <xsl:value-of select="Events/ChangeEvent/@relative"/>
                                            </xsl:when>
                                            <xsl:otherwise></xsl:otherwise>
                                        </xsl:choose>
                                    </text:p>
                                </table:table-cell>
                                <table:table-cell office:value-type="string" table:style-name="cell1">
                                    <text:p><xsl:value-of select="Description"/></text:p>
                                </table:table-cell>
                            </table:table-row>
                        </xsl:for-each>
                    </xsl:for-each>
                </xsl:for-each>
            </xsl:for-each>
        </table:table>
    </xsl:template>
        
    <xsl:template name="Set-MeasurementGroups">
        <table:table table:name="Acquisition" table:default-cell-style-name="Default">
            <table:table-column table:style-name="typecol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="poolcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="namecol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="devnamecol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="attrcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="desccol"    table:default-cell-style-name="cell1"/>
            <table:table-row table:style-name="row1">
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Type</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Pool</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Name</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>DeviceName</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Channels</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Description</text:p>
                </table:table-cell>
            </table:table-row>
            
            <xsl:for-each select="PoolServer/Pool">
                <xsl:variable name="pool"><xsl:value-of select="@deviceName"/></xsl:variable>
                <xsl:for-each select="MeasurementGroup">
                    <table:table-row table:style-name="row1">
                        <table:table-cell office:value-type="string">
                            <text:p>MeasurementGroup</text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="$pool"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="@name"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="@deviceName"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <xsl:for-each select="ChannelRef">
                                <text:p><xsl:value-of select="@name"/></text:p>
                            </xsl:for-each>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="Description"/></text:p>
                        </table:table-cell>
                    </table:table-row>
                </xsl:for-each>
            </xsl:for-each>
        </table:table>
     </xsl:template>

    <xsl:template name="Set-CommunicationChannels">
        <table:table table:name="CommunicationChannels" table:default-cell-style-name="Default">
            <xsl:call-template name="Set-Element-Header"/>
            
            <xsl:for-each select="PoolServer/Pool">
                <xsl:variable name="pool"><xsl:value-of select="@deviceName"/></xsl:variable>
                <xsl:for-each select="Controller[@type = 'Communication']">
                    <xsl:for-each select="CommunicationChannel">
                        <xsl:call-template name="Set-Element">
                            <xsl:with-param name="pool"><xsl:value-of select="$pool"/></xsl:with-param>
                            <xsl:with-param name="ctrl"><xsl:value-of select="@name"/></xsl:with-param>
                            <xsl:with-param name="type">CommunicationChannel</xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                </xsl:for-each>
            </xsl:for-each>
        </table:table>
     </xsl:template>
     
    <xsl:template name="Set-Channels">
        <table:table table:name="Channels">
            <xsl:call-template name="Set-Element-Header"/>
            
            <xsl:for-each select="PoolServer/Pool">
                <xsl:variable name="pool"><xsl:value-of select="@deviceName"/></xsl:variable>
                <xsl:for-each select="Controller[@type = 'CounterTimer']">
                    <xsl:for-each select="CounterTimer">
                        <xsl:call-template name="Set-Element">
                            <xsl:with-param name="pool"><xsl:value-of select="$pool"/></xsl:with-param>
                            <xsl:with-param name="ctrl"><xsl:value-of select="@name"/></xsl:with-param>
                            <xsl:with-param name="type">CounterTimer</xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                </xsl:for-each>
                
                <xsl:for-each select="Controller[@type = 'ZeroDExpChannel']">
                    <xsl:for-each select="ZeroDExpChannel">
                        <xsl:call-template name="Set-Element">
                            <xsl:with-param name="pool"><xsl:value-of select="$pool"/></xsl:with-param>
                            <xsl:with-param name="ctrl"><xsl:value-of select="@name"/></xsl:with-param>
                            <xsl:with-param name="type">ZeroDExpChannel</xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                </xsl:for-each>

                <xsl:for-each select="Controller[@type = 'OneDExpChannel']">
                    <xsl:for-each select="OneDExpChannel">
                        <xsl:call-template name="Set-Element">
                            <xsl:with-param name="pool"><xsl:value-of select="$pool"/></xsl:with-param>
                            <xsl:with-param name="ctrl"><xsl:value-of select="@name"/></xsl:with-param>
                            <xsl:with-param name="type">OneDExpChannel</xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                </xsl:for-each>

                <xsl:for-each select="Controller[@type = 'TwoDExpChannel']">
                    <xsl:for-each select="TwoDExpChannel">
                        <xsl:call-template name="Set-Element">
                            <xsl:with-param name="pool"><xsl:value-of select="$pool"/></xsl:with-param>
                            <xsl:with-param name="ctrl"><xsl:value-of select="@name"/></xsl:with-param>
                            <xsl:with-param name="type">TwoDExpChannel</xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                </xsl:for-each>

                <xsl:for-each select="Controller[@type = 'PseudoCounter']">
                    <xsl:for-each select="PseudoCounter">
                        <xsl:call-template name="Set-Element">
                            <xsl:with-param name="pool"><xsl:value-of select="$pool"/></xsl:with-param>
                            <xsl:with-param name="ctrl"><xsl:value-of select="@name"/></xsl:with-param>
                            <xsl:with-param name="type">PseudoCounter</xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                </xsl:for-each>

            </xsl:for-each>
        </table:table>
    </xsl:template>
    
    <xsl:template name="Set-IORegisters">
        <table:table table:name="IORegisters" table:default-cell-style-name="Default">
            <xsl:call-template name="Set-Element-Header"/>
            
            <xsl:for-each select="PoolServer/Pool">
                <xsl:variable name="pool"><xsl:value-of select="@deviceName"/></xsl:variable>
                <xsl:for-each select="Controller[@type = 'IORegister']">
                    <xsl:for-each select="IORegister">
                        <xsl:call-template name="Set-Element">
                            <xsl:with-param name="pool"><xsl:value-of select="$pool"/></xsl:with-param>
                            <xsl:with-param name="ctrl"><xsl:value-of select="@name"/></xsl:with-param>
                            <xsl:with-param name="type">IORegister</xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                </xsl:for-each>
            </xsl:for-each>
        </table:table>
     </xsl:template>

    <xsl:template name="Set-Motors">
        <table:table table:name="Motors" table:default-cell-style-name="Default">
            <xsl:call-template name="Set-Element-Header"/>
            
            <xsl:for-each select="PoolServer/Pool">
                <xsl:variable name="pool"><xsl:value-of select="@deviceName"/></xsl:variable>
                <xsl:for-each select="Controller[@type = 'Motor']">
                    <xsl:for-each select="Motor">
                        <xsl:call-template name="Set-Element">
                            <xsl:with-param name="pool"><xsl:value-of select="$pool"/></xsl:with-param>
                            <xsl:with-param name="ctrl"><xsl:value-of select="@name"/></xsl:with-param>
                            <xsl:with-param name="type">Motor</xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                </xsl:for-each>
            </xsl:for-each>
        </table:table>
     </xsl:template>
     
    <xsl:template name="Set-Controllers">
        <table:table table:name="Controllers" table:default-cell-style-name="Default">
            <table:table-column table:style-name="typecol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="poolcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="namecol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="namecol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="namecol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="attrcol"    table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="attrcol"    table:default-cell-style-name="cell1"/>
            <table:table-row table:style-name="row1">
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Type</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Pool</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Name</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>File</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Class</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Properties</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Elements</text:p>
                </table:table-cell>
            </table:table-row>

            <xsl:for-each select="PoolServer/Pool">
                <xsl:variable name="pool"><xsl:value-of select="@deviceName"/></xsl:variable>
                <xsl:for-each select="Controller">
                    <table:table-row table:style-name="row1">
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="@type"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="$pool"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="@name"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="@lib"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="@class"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <xsl:for-each select="Property">
                                <text:p><xsl:value-of select="@name"/>:<xsl:value-of select="Item"/></text:p>
                            </xsl:for-each>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <xsl:choose>
                                <xsl:when test="@type = 'PseudoMotor'">
                                    <xsl:for-each select="Motor">
                                        <text:p><xsl:value-of select="."/></text:p>
                                    </xsl:for-each>
                                </xsl:when>
                                <xsl:when test="@type = 'PseudoCounter'">
                                    <xsl:for-each select="Channel">
                                        <text:p><xsl:value-of select="."/></text:p>
                                    </xsl:for-each>
                                </xsl:when>
                                <xsl:otherwise>
                                    <text:p></text:p>
                                </xsl:otherwise>
                            </xsl:choose>
                        </table:table-cell>
                    </table:table-row>
                </xsl:for-each>
            </xsl:for-each>
        </table:table>
    </xsl:template>
    
    <xsl:template name="Set-Doors">
        <table:table table:name="Doors" table:default-cell-style-name="Default">
            <table:table-column table:style-name="servcol" table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="mscol"   table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="desccol" table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="namecol" table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="devnamecol"  table:default-cell-style-name="cell1"/>
            <table:table-row table:style-name="row1">
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Server</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>MacroServer</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Description</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Name</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Tango Name</text:p>
                </table:table-cell>
            </table:table-row>
            <table:table-row table:style-name="row1">
                <xsl:for-each select="MacroServerServer">
                    <xsl:variable name="server"><xsl:value-of select="@serverName"/></xsl:variable>
                    <xsl:variable name="ms"><xsl:value-of select="MacroServer/@deviceName"/></xsl:variable>
                    <xsl:for-each select="Door">
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="$server"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="$ms"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="Description"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="@name"/></text:p>
                        </table:table-cell>
                        <table:table-cell office:value-type="string">
                            <text:p><xsl:value-of select="@deviceName"/></text:p>
                        </table:table-cell>
                    </xsl:for-each>
                </xsl:for-each>
            </table:table-row>
        </table:table>
    </xsl:template>
    
    <xsl:template name="Set-Servers">
        <table:table table:name="Servers" table:default-cell-style-name="Default">
            <table:table-column table:style-name="typecol"  table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="hostcol"  table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="servcol"  table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="desccol"  table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="smallnamecol"  table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="devnamecol"  table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="pathcol"  table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="attrcol"  table:default-cell-style-name="cell1"/>
            <table:table-row table:style-name="row1">
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Type</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Host</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Server</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Description</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Name</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Tango Name</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Path</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>Pools</text:p>
                </table:table-cell>
            </table:table-row>
        
            <xsl:for-each select="PoolServer">
                <table:table-row table:style-name="row1">
                    <table:table-cell office:value-type="string">
                        <text:p>Pool</text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <text:p><xsl:value-of select="@tangoHost"/></text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <text:p><xsl:value-of select="@serverName"/></text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <text:p><xsl:value-of select="Description"/></text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <text:p><xsl:value-of select="Pool/@name"/></text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <text:p><xsl:value-of select="Pool/@deviceName"/></text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <xsl:for-each select="Pool/Property[@name='PoolPath']/Item">
                            <text:p><xsl:value-of select="."/></text:p>
                        </xsl:for-each>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <text:p></text:p>
                    </table:table-cell>
                </table:table-row>
            </xsl:for-each>
            
            <xsl:for-each select="MacroServerServer">
                <table:table-row table:style-name="row1">
                    <table:table-cell office:value-type="string">
                        <text:p>Pool</text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <text:p><xsl:value-of select="@tangoHost"/></text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <text:p><xsl:value-of select="@serverName"/></text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <text:p><xsl:value-of select="Description"/></text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <text:p><xsl:value-of select="MacroServer/@name"/></text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <text:p><xsl:value-of select="MacroServer/@deviceName"/></text:p>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <xsl:for-each select="MacroServer/Property[@name='MacroPath']/Item">
                            <text:p><xsl:value-of select="."/></text:p>
                        </xsl:for-each>
                    </table:table-cell>
                    <table:table-cell office:value-type="string">
                        <xsl:for-each select="MacroServer/Property[@name='PoolNames']/Item">
                            <text:p><xsl:value-of select="."/></text:p>
                        </xsl:for-each>
                    </table:table-cell>
                </table:table-row>
            </xsl:for-each>
            
        </table:table>
    </xsl:template>
    
    <xsl:template name="Set-Global">
        <table:table table:name="Global" table:default-cell-style-name="Default">
            <table:table-column table:default-cell-style-name="cell1"/>
            <table:table-column table:style-name="globalcol" table:default-cell-style-name="cell1"/>
            <table:table-row table:style-name="row1">
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>code</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string">
                    <text:p><xsl:value-of select="@name"/></text:p>
                </table:table-cell>
            </table:table-row>
            <table:table-row table:style-name="row1">
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>name</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string">
                    <text:p><xsl:value-of select="@longName"/></text:p>
                </table:table-cell>
            </table:table-row>
            <table:table-row table:style-name="row1">
                <table:table-cell office:value-type="string" table:style-name="header1">
                    <text:p>description</text:p>
                </table:table-cell>
                <table:table-cell office:value-type="string">
                    <text:p><xsl:value-of select="Description"/></text:p>
                </table:table-cell>
            </table:table-row>
        </table:table>
    </xsl:template>
    
    <xsl:template name="Set-Element">
        <xsl:param name="type"/>
        <xsl:param name="pool"/>
        <xsl:param name="ctrl"/>
        <table:table-row table:style-name="row1">
            <table:table-cell office:value-type="string">
                <text:p><xsl:value-of select="$type"/></text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string">
                <text:p><xsl:value-of select="$pool"/></text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string">
                <text:p><xsl:value-of select="$ctrl"/></text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string">
                <text:p><xsl:value-of select="@name"/></text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string">
                <text:p><xsl:value-of select="@deviceName"/></text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string">
                <text:p><xsl:value-of select="@axis"/></text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string">
                <text:p><xsl:value-of select="Description"/></text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string">
                <xsl:for-each select="Attribute">
                    <xsl:if test="Value">
                        <text:p><xsl:value-of select="@name"/>:<xsl:value-of select="Value"/></text:p>
                    </xsl:if>
                </xsl:for-each>
            </table:table-cell>
        </table:table-row>
    </xsl:template>
    
    <xsl:template name="Set-Element-Header">
        <table:table-column table:style-name="typecol"    table:default-cell-style-name="cell1"/>
        <table:table-column table:style-name="poolcol"    table:default-cell-style-name="cell1"/>
        <table:table-column table:style-name="ctrlcol"    table:default-cell-style-name="cell1"/>
        <table:table-column table:style-name="namecol"    table:default-cell-style-name="cell1"/>
        <table:table-column table:style-name="devnamecol" table:default-cell-style-name="cell1"/>
        <table:table-column table:style-name="axiscol"    table:default-cell-style-name="cell1"/>
        <table:table-column table:style-name="desccol"    table:default-cell-style-name="cell1"/>
        <table:table-column table:style-name="attrcol"    table:default-cell-style-name="cell1"/>
        <table:table-row table:style-name="row1">
            <table:table-cell office:value-type="string" table:style-name="header1">
                <text:p>Type</text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string" table:style-name="header1">
                <text:p>Pool</text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string" table:style-name="header1">
                <text:p>Controller</text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string" table:style-name="header1">
                <text:p>Name</text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string" table:style-name="header1">
                <text:p>DeviceName</text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string" table:style-name="header1">
                <text:p>Axis</text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string" table:style-name="header1">
                <text:p>Description</text:p>
            </table:table-cell>
            <table:table-cell office:value-type="string" table:style-name="header1">
                <text:p>Attributes</text:p>
            </table:table-cell>
        </table:table-row>
    </xsl:template>
</xsl:stylesheet>