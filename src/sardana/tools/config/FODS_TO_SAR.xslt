<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
 xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
 xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
    <xsl:output method="xml" indent="yes"/> 

    <xsl:template match="/">
        <xsl:apply-templates select="/office:document/office:body/office:spreadsheet" />
    </xsl:template>
    
    <xsl:template match="/office:document/office:body/office:spreadsheet">
        <xsl:variable name="SarCode">
            <xsl:value-of select="table:table[@table:name='Global']/table:table-row[1]/table:table-cell[2]/text:p"/>
        </xsl:variable>
        <xsl:variable name="SarName">
            <xsl:value-of select="table:table[@table:name='Global']/table:table-row[2]/table:table-cell[2]/text:p"/>
        </xsl:variable>
        <xsl:variable name="SarDesc">
            <xsl:value-of select="table:table[@table:name='Global']/table:table-row[3]/table:table-cell[2]/text:p"/>
        </xsl:variable>
        <xsl:element name="Sardana">
            <xsl:attribute name="name">
                <xsl:value-of select="$SarCode"/>
            </xsl:attribute>
            <xsl:attribute name="longName">
                <xsl:value-of select="$SarName"/>
            </xsl:attribute>
            <Description><xsl:value-of select="$SarDesc"/></Description>
            <xsl:apply-templates select="table:table"/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="table:table[@table:name='Global']"/>
    <xsl:template match="table:table[@table:name='Motors']"/>
    <xsl:template match="table:table[@table:name='IORegisters']"/>
    <xsl:template match="table:table[@table:name='Channels']"/>
    <xsl:template match="table:table[@table:name='CommunicationChannels']"/>
    <xsl:template match="table:table[@table:name='Doors']"/>
    <xsl:template match="table:table[@table:name='Controllers']"/>
    <xsl:template match="table:table[@table:name='Parameters']"/>
    <xsl:template match="table:table[@table:name='Acquisition']"/>
    <xsl:template match="table:table[@table:name='Instruments']"/>

    <xsl:template match="table:table[@table:name='Servers']">
        <xsl:for-each select="table:table-row">
            <xsl:variable name="serverType">
                <xsl:value-of select="table:table-cell[1]/text:p"/>
            </xsl:variable>
            <xsl:if test="string-length($serverType) and $serverType != 'Type'">
                <xsl:variable name="tangoHost">
                    <xsl:value-of select="table:table-cell[2]/text:p"/>
                </xsl:variable>
                <xsl:variable name="serverName">
                    <xsl:value-of select="table:table-cell[3]/text:p"/>
                </xsl:variable>
                <xsl:variable name="desc">
                    <xsl:value-of select="table:table-cell[4]/text:p"/>
                </xsl:variable>
                <xsl:variable name="name">
                    <xsl:value-of select="table:table-cell[5]/text:p"/>
                </xsl:variable>
                <xsl:variable name="deviceName">
                    <xsl:value-of select="table:table-cell[6]/text:p"/>
                </xsl:variable>
                
                <xsl:element name="{$serverType}Server">
                    <xsl:if test="string-length($tangoHost)">
                        <xsl:attribute name="tangoHost">
                            <xsl:value-of select="$tangoHost"/>
                        </xsl:attribute>
                    </xsl:if>
                    <xsl:attribute name="serverName">
                        <xsl:value-of select="$serverName"/>
                    </xsl:attribute>
                    <xsl:element name="Description">
                        <xsl:value-of select="$desc"/>
                    </xsl:element>

                    <xsl:element name="{$serverType}">
                        <xsl:attribute name="name">
                            <xsl:value-of select="$name"/>
                        </xsl:attribute>
                        <xsl:attribute name="deviceName">
                            <xsl:value-of select="$deviceName"/>
                        </xsl:attribute>
                        <xsl:element name="Description">
                            <xsl:value-of select="$desc"/>
                        </xsl:element>
                    
                    <xsl:choose>
                        <xsl:when test="$serverType = 'Pool'">
                            <xsl:element name="Property">
                                <xsl:attribute name="name">PoolPath</xsl:attribute>
                                <xsl:for-each select="table:table-cell[7]/text:p">
                                    <xsl:call-template name="Set-Property">
                                        <xsl:with-param name="list">
                                            <xsl:value-of select="."/>
                                        </xsl:with-param>
                                        <xsl:with-param name="delimiter">:</xsl:with-param>
                                        <xsl:with-param name="tag">Item</xsl:with-param>
                                    </xsl:call-template>
                                </xsl:for-each>
                            </xsl:element>
                            
                            <xsl:element name="Property">
                                <xsl:attribute name="name">Version</xsl:attribute>
                                <xsl:element name="Item">0.3.0</xsl:element>
                            </xsl:element>
                            
                            <xsl:call-template name="Set-Pool">
                                <xsl:with-param name="poolDeviceName">
                                    <xsl:value-of select="$deviceName"/>
                                </xsl:with-param>
                            </xsl:call-template>
                            
                        </xsl:when>
                        
                        <xsl:when test="$serverType = 'MacroServer'">
                            <xsl:variable name="pools">
                                <xsl:value-of select="table:table-cell[8]/text:p"/>
                            </xsl:variable>

                            <xsl:element name="Property">
                                <xsl:attribute name="name">MacroPath</xsl:attribute>
                                <xsl:for-each select="table:table-cell[7]/text:p">
                                    <xsl:call-template name="Set-Property">
                                        <xsl:with-param name="list">
                                            <xsl:value-of select="."/>
                                        </xsl:with-param>
                                        <xsl:with-param name="delimiter">:</xsl:with-param>
                                        <xsl:with-param name="tag">Item</xsl:with-param>
                                    </xsl:call-template>
                                </xsl:for-each>
                            </xsl:element>

                            <xsl:call-template name="Set-MacroServer">
                                <xsl:with-param name="serverName">
                                    <xsl:value-of select="$serverName"/>
                                </xsl:with-param>
                                <xsl:with-param name="deviceName">
                                    <xsl:value-of select="$deviceName"/>
                                </xsl:with-param>
                                <xsl:with-param name="pools">
                                    <xsl:value-of select="$pools"/>
                                </xsl:with-param>
                            </xsl:call-template>
                        </xsl:when>
                        
                    </xsl:choose>
                    
                </xsl:element>
                
                <xsl:choose>
                    <xsl:when test="$serverType = 'MacroServer'">
                        <xsl:call-template name="Set-MacroServer-Doors">
                            <xsl:with-param name="serverName" select="$serverName">
                                <xsl:value-of select="$serverName"/>
                            </xsl:with-param>
                            <xsl:with-param name="deviceName" select="$deviceName">
                                <xsl:value-of select="$deviceName"/>
                            </xsl:with-param>
                        </xsl:call-template>
                    </xsl:when>
                </xsl:choose>
                
            </xsl:element>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <xsl:template name="Set-MacroServer">
        <xsl:param name="serverName"/>
        <xsl:param name="deviceName"/>
        <xsl:param name="pools"/>
        <xsl:element name="Property">
            <xsl:attribute name="name">PoolNames</xsl:attribute>
            <xsl:call-template name="Set-Property">
                <xsl:with-param name="list">
                    <xsl:value-of select="$pools"/>
                </xsl:with-param>
                <xsl:with-param name="delimiter">;</xsl:with-param>
                <xsl:with-param name="tag">Item</xsl:with-param>
            </xsl:call-template>
        </xsl:element>
    </xsl:template>
    
    <xsl:template name="Set-MacroServer-Doors">
        <xsl:param name="serverName"/>
        <xsl:param name="deviceName"/>
        <xsl:for-each select="/office:document/office:body/office:spreadsheet/table:table[@table:name='Doors']/table:table-row">
            <xsl:variable name="doorServer">
                <xsl:value-of select="table:table-cell[1]/text:p"/>
            </xsl:variable>
            <xsl:variable name="doorMacroServer">
                <xsl:value-of select="table:table-cell[2]/text:p"/>
            </xsl:variable>
            <xsl:if test="$doorServer = $serverName and $doorMacroServer = $deviceName">
                <xsl:variable name="desc">
                    <xsl:value-of select="table:table-cell[3]/text:p"/>
                </xsl:variable>
                <xsl:variable name="name">
                    <xsl:value-of select="table:table-cell[4]/text:p"/>
                </xsl:variable>
                <xsl:variable name="deviceName">
                    <xsl:value-of select="table:table-cell[5]/text:p"/>
                </xsl:variable>
            
                <xsl:element name="Door">
                    <xsl:attribute name="name"><xsl:value-of select="$name"/></xsl:attribute>
                    <xsl:attribute name="deviceName"><xsl:value-of select="$deviceName"/></xsl:attribute>
                    <xsl:element name="Description"><xsl:value-of select="$desc"/></xsl:element>
                </xsl:element>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <xsl:template name="Set-Pool">
        <xsl:param name="poolDeviceName"/>

        <xsl:call-template name="Set-Pool-Instruments">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
        </xsl:call-template>

        <!-- Find controllers -->        
        <xsl:call-template name="Set-Pool-Controllers">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
        </xsl:call-template>
        
        <!-- Find measurement groups -->
        <xsl:call-template name="Set-Pool-MeasurementGroups">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
        </xsl:call-template>
    </xsl:template>

    <xsl:template name="Set-Pool-Ctrl-IORegisters">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:call-template name="Set-Pool-Ctrl-Elements">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
            <xsl:with-param name="ctrlName" select="$ctrlName"/>
            <xsl:with-param name="sheet">IORegisters</xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    
    <xsl:template name="Set-Pool-Ctrl-Motors">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:call-template name="Set-Pool-Ctrl-Elements">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
            <xsl:with-param name="ctrlName" select="$ctrlName"/>
            <xsl:with-param name="sheet">Motors</xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template name="Set-Pool-Ctrl-PseudoMotors">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:call-template name="Set-Pool-Ctrl-Motors">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
            <xsl:with-param name="ctrlName" select="$ctrlName"/>
        </xsl:call-template>
    </xsl:template>
    
    <xsl:template name="Set-Pool-Ctrl-Counters">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:call-template name="Set-Pool-Ctrl-Elements">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
            <xsl:with-param name="ctrlName" select="$ctrlName"/>
            <xsl:with-param name="sheet">Channels</xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    
    <xsl:template name="Set-Pool-Ctrl-0D">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:call-template name="Set-Pool-Ctrl-Elements">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
            <xsl:with-param name="ctrlName" select="$ctrlName"/>
            <xsl:with-param name="sheet">Channels</xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template name="Set-Pool-Ctrl-1D">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:call-template name="Set-Pool-Ctrl-Elements">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
            <xsl:with-param name="ctrlName" select="$ctrlName"/>
            <xsl:with-param name="sheet">Channels</xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template name="Set-Pool-Ctrl-2D">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:call-template name="Set-Pool-Ctrl-Elements">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
            <xsl:with-param name="ctrlName" select="$ctrlName"/>
            <xsl:with-param name="sheet">Channels</xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template name="Set-Pool-Ctrl-Communication">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:call-template name="Set-Pool-Ctrl-Elements">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
            <xsl:with-param name="ctrlName" select="$ctrlName"/>
            <xsl:with-param name="sheet">CommunicationChannels</xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    
    <xsl:template name="Set-Pool-Ctrl-PseudoCounters">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:call-template name="Set-Pool-Ctrl-Elements">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
            <xsl:with-param name="ctrlName" select="$ctrlName"/>
            <xsl:with-param name="sheet">Channels</xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <xsl:template name="Set-Pool-Instruments">
        <xsl:param name="poolDeviceName"/>

        <xsl:for-each select="/office:document/office:body/office:spreadsheet/table:table[@table:name='Instruments']/table:table-row">
            <xsl:variable name="instrumentPool">
                <xsl:value-of select="table:table-cell[2]/text:p"/>
            </xsl:variable>
            <xsl:if test="$instrumentPool = $poolDeviceName">
                
                <xsl:variable name="instrumentName">
                    <xsl:value-of select="table:table-cell[3]/text:p"/>
                </xsl:variable>
                <xsl:variable name="instrumentClass">
                    <xsl:value-of select="table:table-cell[4]/text:p"/>
                </xsl:variable>
                <Instrument name="{$instrumentName}" class="{$instrumentClass}" />
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <xsl:template name="Set-Pool-Controllers">
        <xsl:param name="poolDeviceName"/>

        <xsl:for-each select="/office:document/office:body/office:spreadsheet/table:table[@table:name='Controllers']/table:table-row">
            <xsl:variable name="ctrlPool">
                <xsl:value-of select="table:table-cell[2]/text:p"/>
            </xsl:variable>
            <xsl:if test="$ctrlPool = $poolDeviceName">
            
                <xsl:variable name="ctrlType">
                    <xsl:value-of select="table:table-cell[1]/text:p"/>
                </xsl:variable>
                <xsl:variable name="ctrlName">
                    <xsl:value-of select="table:table-cell[3]/text:p"/>
                </xsl:variable>
                <xsl:variable name="ctrlLib">
                    <xsl:value-of select="table:table-cell[4]/text:p"/>
                </xsl:variable>
                <xsl:variable name="ctrlClass">
                    <xsl:value-of select="table:table-cell[5]/text:p"/>
                </xsl:variable>

                <Controller type="{$ctrlType}" name="{$ctrlName}"
                            lib="{$ctrlLib}"   class="{$ctrlClass}">
                    <xsl:for-each select="table:table-cell[6]/text:p">
                        <xsl:call-template name="Set-CtrlProperty">
                            <xsl:with-param name="list">
                                <xsl:value-of select="."/>
                            </xsl:with-param>
                            <xsl:with-param name="delimiter">;</xsl:with-param>
                            <xsl:with-param name="separator">:</xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                    
                    <xsl:choose>
                        <xsl:when test="$ctrlType = 'Motor'">
                            <xsl:call-template name="Set-Pool-Ctrl-Motors">
                                <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
                                <xsl:with-param name="ctrlName" select="$ctrlName"/>
                            </xsl:call-template>
                        </xsl:when>
                        
                        <xsl:when test="$ctrlType = 'IORegister'">
                            <xsl:call-template name="Set-Pool-Ctrl-IORegisters">
                                <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
                                <xsl:with-param name="ctrlName" select="$ctrlName"/>
                            </xsl:call-template>
                        </xsl:when>
                        <xsl:when test="$ctrlType = 'CounterTimer'">
                            <xsl:call-template name="Set-Pool-Ctrl-Counters">
                                <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
                                <xsl:with-param name="ctrlName" select="$ctrlName"/>
                            </xsl:call-template>
                        </xsl:when>
                        <xsl:when test="$ctrlType = 'ZeroDExpChannel'">
                            <xsl:call-template name="Set-Pool-Ctrl-0D">
                                <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
                                <xsl:with-param name="ctrlName" select="$ctrlName"/>
                            </xsl:call-template>
                        </xsl:when>
                        <xsl:when test="$ctrlType = 'OneDExpChannel'">
                            <xsl:call-template name="Set-Pool-Ctrl-1D">
                                <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
                                <xsl:with-param name="ctrlName" select="$ctrlName"/>
                            </xsl:call-template>
                        </xsl:when>
                        <xsl:when test="$ctrlType = 'TwoDExpChannel'">
                            <xsl:call-template name="Set-Pool-Ctrl-2D">
                                <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
                                <xsl:with-param name="ctrlName" select="$ctrlName"/>
                            </xsl:call-template>
                        </xsl:when>
                        <xsl:when test="$ctrlType = 'Communication'">
                            <xsl:call-template name="Set-Pool-Ctrl-Communication">
                                <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
                                <xsl:with-param name="ctrlName" select="$ctrlName"/>
                            </xsl:call-template>
                        </xsl:when>
                        <xsl:when test="$ctrlType = 'PseudoMotor'">
                            <xsl:for-each select="table:table-cell[7]/text:p">
                                <xsl:call-template name="Set-Property">
                                    <xsl:with-param name="list">
                                        <xsl:value-of select="."/>
                                    </xsl:with-param>
                                    <xsl:with-param name="delimiter">;</xsl:with-param>
                                    <xsl:with-param name="tag">Motor</xsl:with-param>
                                </xsl:call-template>
                            </xsl:for-each>
                            <xsl:call-template name="Set-Pool-Ctrl-PseudoMotors">
                                <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
                                <xsl:with-param name="ctrlName" select="$ctrlName"/>
                            </xsl:call-template>
                        </xsl:when>
                        <xsl:when test="$ctrlType = 'PseudoCounter'">
                            <xsl:call-template name="Set-Property">
                                <xsl:with-param name="list">
                                    <xsl:value-of select="table:table-cell[7]/text:p"/>
                                </xsl:with-param>
                                <xsl:with-param name="delimiter">;</xsl:with-param>
                                <xsl:with-param name="tag">Channel</xsl:with-param>
                            </xsl:call-template>
                            <xsl:call-template name="Set-Pool-Ctrl-PseudoCounters">
                                <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
                                <xsl:with-param name="ctrlName" select="$ctrlName"/>
                            </xsl:call-template>
                        </xsl:when>
                        
                        <xsl:otherwise></xsl:otherwise>
                    </xsl:choose>
                </Controller>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <xsl:template name="Set-Pool-Ctrl-Elements">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:param name="sheet"/>
        <xsl:for-each select="/office:document/office:body/office:spreadsheet/table:table[@table:name=$sheet]/table:table-row">
            <xsl:variable name="pool">
                <xsl:value-of select="table:table-cell[2]/text:p"/>
            </xsl:variable>

            <xsl:variable name="ctrl">
                <xsl:value-of select="table:table-cell[3]/text:p"/>
            </xsl:variable>
            <xsl:variable name="type">
                <xsl:value-of select="table:table-cell[1]/text:p"/>
            </xsl:variable>
            <xsl:if test="$pool = $poolDeviceName and $ctrl = $ctrlName">
                <xsl:variable name="name">
                    <xsl:value-of select="table:table-cell[4]/text:p"/>
                </xsl:variable>
                <xsl:variable name="deviceName">
                    <xsl:value-of select="table:table-cell[5]/text:p"/>
                </xsl:variable>
                <xsl:variable name="axis">
                    <xsl:value-of select="table:table-cell[6]/text:p"/>
                </xsl:variable>
                <xsl:variable name="instrument">
                    <xsl:value-of select="table:table-cell[7]/text:p"/>
                </xsl:variable>
                <xsl:variable name="desc">
                    <xsl:value-of select="table:table-cell[8]/text:p"/>
                </xsl:variable>
                
                <xsl:element name="{$type}">
                    <xsl:attribute name="name">
                        <xsl:value-of select="$name"/>
                    </xsl:attribute>
                    <xsl:attribute name="deviceName">
                        <xsl:choose>
                            <xsl:when test="string-length(normalize-space($deviceName))">
                                <xsl:value-of select="$deviceName"/>
                            </xsl:when>
                            <xsl:otherwise>Automatic</xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                    <xsl:attribute name="axis">
                        <xsl:value-of select="$axis"/>
                    </xsl:attribute>
                    <xsl:if test="$instrument != 'None'">
                        <xsl:element name="InstrumentRef">
                            <xsl:value-of select="$instrument"/>
                        </xsl:element>
                    </xsl:if>
                    <xsl:if test="string-length($desc)">
                        <xsl:element name="Description">
                            <xsl:value-of select="$desc"/>
                        </xsl:element>
                    </xsl:if>
                    <xsl:for-each select="table:table-cell[9]/text:p">
                        <xsl:call-template name="Set-Attributes">
                            <xsl:with-param name="list">
                                <xsl:value-of select="."/>
                            </xsl:with-param>
                            <xsl:with-param name="delimiter">;</xsl:with-param>
                            <xsl:with-param name="separator">:</xsl:with-param>
                            <xsl:with-param name="poolDeviceName">
                                <xsl:value-of select="$poolDeviceName"/>
                            </xsl:with-param>
                            <xsl:with-param name="devAlias">
                                <xsl:value-of select="$name"/>
                            </xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                    <xsl:call-template name="Set-Attributes-Config">
                        <xsl:with-param name="poolDeviceName">
                            <xsl:value-of select="$poolDeviceName"/>
                        </xsl:with-param>
                        <xsl:with-param name="devAlias">
                            <xsl:value-of select="$name"/>
                        </xsl:with-param>
                    </xsl:call-template>
                </xsl:element>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>
    
    <xsl:template name="Set-Pool-MeasurementGroups">
        <xsl:param name="poolDeviceName"/>
        <xsl:for-each select="/office:document/office:body/office:spreadsheet/table:table[@table:name='Acquisition']/table:table-row">
            <xsl:variable name="currentPool">
                <xsl:value-of select="table:table-cell[2]/text:p"/>
            </xsl:variable>
            <xsl:if test="$currentPool = $poolDeviceName">
                <xsl:variable name="mgName">
                    <xsl:value-of select="table:table-cell[3]/text:p"/>
                </xsl:variable>
                <xsl:variable name="mgDeviceName">
                    <xsl:value-of select="table:table-cell[4]/text:p"/>
                </xsl:variable>
                <xsl:variable name="mgElements">
                    <xsl:value-of select="table:table-cell[5]/text:p"/>
                </xsl:variable>
                <xsl:variable name="mgDescription">
                    <xsl:value-of select="table:table-cell[6]/text:p"/>
                </xsl:variable>
                <xsl:element name="MeasurementGroup">
                    <xsl:attribute name="name"><xsl:value-of select="$mgName"/></xsl:attribute>
                    <xsl:attribute name="deviceName"><xsl:value-of select="$mgDeviceName"/></xsl:attribute>
                    <xsl:for-each select="table:table-cell[5]/text:p">
                        <xsl:call-template name="Set-MeasurementGroupElements">
                            <xsl:with-param name="list">
                                <xsl:value-of select="."/>
                            </xsl:with-param>
                            <xsl:with-param name="delimiter">;</xsl:with-param>
                        </xsl:call-template>
                    </xsl:for-each>
                    <xsl:element name="Description">
                        <xsl:value-of select="$mgDescription"/>
                    </xsl:element>
                </xsl:element>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>
    
    <xsl:template name="Set-MeasurementGroupElements">
        <xsl:param name="list"/>
        <xsl:param name="delimiter"/>
        <xsl:variable name="newlist">
            <xsl:choose>
                <xsl:when test="contains($list, $delimiter)">
                    <xsl:value-of select="normalize-space($list)"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="concat(normalize-space($list), $delimiter)"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:variable name="first" select="substring-before($newlist, $delimiter)"/>
        <xsl:variable name="remaining" select="substring-after($newlist, $delimiter)"/>
        
         <xsl:element name="ChannelRef">
            <xsl:attribute name="name" >
                <xsl:value-of select="$first"/>
            </xsl:attribute>
        </xsl:element>
        
        <xsl:if test="$remaining">
            <xsl:call-template name="Set-MeasurementGroupElements">
                <xsl:with-param name="list" select="$remaining"/>
                <xsl:with-param name="delimiter">
                    <xsl:value-of select="$delimiter"/>
                </xsl:with-param>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <xsl:template name="Set-CtrlProperty">
        <xsl:param name="list"/>
        <xsl:param name="delimiter"/>
        <xsl:param name="separator"/>
        <xsl:variable name="newlist">
            <xsl:choose>
                <xsl:when test="contains($list, $delimiter)">
                    <xsl:value-of select="normalize-space($list)"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:if test="string-length(normalize-space($list))">
                        <xsl:value-of select="concat(normalize-space($list), $delimiter)"/>
                    </xsl:if>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:if test="string-length($newlist)">
            <xsl:variable name="first" select="substring-before($newlist, $delimiter)"/>
            <xsl:variable name="remaining" select="substring-after($newlist, $delimiter)"/>

            <xsl:variable name="propname" select="substring-before($first, $separator)"/>
            <xsl:variable name="propval" select="substring-after($first, $separator)"/>
            
            <xsl:element name="Property">
                <xsl:attribute name="name">
                    <xsl:value-of select="$propname"/>
                </xsl:attribute>
                <xsl:element name="Item">
                    <xsl:value-of select="$propval"/>
                </xsl:element>
            </xsl:element>
            
            <xsl:if test="$remaining">
                <xsl:call-template name="Set-CtrlProperty">
                    <xsl:with-param name="list" select="$remaining"/>
                    <xsl:with-param name="delimiter" select="$delimiter"/>
                    <xsl:with-param name="separator" select="$separator"/>
                </xsl:call-template>
            </xsl:if>
        </xsl:if>
    </xsl:template>
    
    <xsl:template name="Set-Property">
        <xsl:param name="list"/>
        <xsl:param name="delimiter"/>
        <xsl:param name="tag"/>
        <xsl:variable name="newlist">
            <xsl:choose>
                <xsl:when test="contains($list, $delimiter)">
                    <xsl:value-of select="normalize-space($list)"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="concat(normalize-space($list), $delimiter)"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:variable name="first" select="substring-before($newlist, $delimiter)"/>
        <xsl:variable name="remaining" select="substring-after($newlist, $delimiter)"/>
        
        <xsl:if test="$first">
            <xsl:element name="{$tag}"><xsl:value-of select="$first"/></xsl:element>
        </xsl:if>
        <xsl:if test="$remaining">
            <xsl:call-template name="Set-Property">
                <xsl:with-param name="list" select="$remaining"/>
                <xsl:with-param name="delimiter">
                    <xsl:value-of select="$delimiter"/>
                </xsl:with-param>
                <xsl:with-param name="tag" select="$tag"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>
    
    <xsl:template name="Set-Attributes-Config">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="devAlias"/>
        <xsl:for-each select="/office:document/office:body/office:spreadsheet/table:table[@table:name='Parameters']/table:table-row">
            <xsl:variable name="currPool">
                <xsl:value-of select="table:table-cell[1]/text:p"/>
            </xsl:variable>
            <xsl:variable name="currDev">
                <xsl:value-of select="table:table-cell[2]/text:p"/>
            </xsl:variable>
        
            <xsl:if test="$currPool = $poolDeviceName and $currDev = $devAlias">
                <xsl:element name="Attribute">
                    <xsl:attribute name="name" >
                        <xsl:value-of select="table:table-cell[3]/text:p"/>
                    </xsl:attribute>
                    <xsl:element name="Configuration">
                        <xsl:element name="Display">
                            <xsl:attribute name="label" >
                                <xsl:value-of select="table:table-cell[4]/text:p"/>
                            </xsl:attribute>
                            <xsl:attribute name="format" >
                                <xsl:value-of select="table:table-cell[5]/text:p"/>
                            </xsl:attribute>
                        </xsl:element>
                        <xsl:element name="Units">
                            <xsl:attribute name="unit" >
                                <xsl:value-of select="table:table-cell[12]/text:p"/>
                            </xsl:attribute>
                            <xsl:attribute name="display_unit" >
                                <xsl:value-of select="table:table-cell[12]/text:p"/>
                            </xsl:attribute>
                        </xsl:element>
                        <xsl:element name="Range">
                            <xsl:attribute name="min" >
                                <xsl:value-of select="table:table-cell[6]/text:p"/>
                            </xsl:attribute>
                            <xsl:attribute name="max" >
                                <xsl:value-of select="table:table-cell[11]/text:p"/>
                            </xsl:attribute>
                        </xsl:element>
                        <xsl:element name="Alarms">
                            <xsl:attribute name="min_alarm" >
                                <xsl:value-of select="table:table-cell[7]/text:p"/>
                            </xsl:attribute>
                            <xsl:attribute name="min_warning" >
                                <xsl:value-of select="table:table-cell[8]/text:p"/>
                            </xsl:attribute>
                            <xsl:attribute name="max_warning" >
                                <xsl:value-of select="table:table-cell[9]/text:p"/>
                            </xsl:attribute>
                            <xsl:attribute name="max_alarm" >
                                <xsl:value-of select="table:table-cell[10]/text:p"/>
                            </xsl:attribute>
                        </xsl:element>
                    </xsl:element>
                    <xsl:if test="table:table-cell[13]/text:p != '-1'">
                        <xsl:element name="Polling">
                            <xsl:attribute name="polled" >True</xsl:attribute>
                            <xsl:attribute name="period" >
                                <xsl:value-of select="table:table-cell[13]/text:p"/>
                            </xsl:attribute>
                        </xsl:element>
                    </xsl:if>
                    <xsl:if test="table:table-cell[14]/text:p != 'Automatic'">
                        <xsl:element name="Events">
                            <xsl:element name="ChangeEvent">
                                <xsl:choose> 
                                    <xsl:when test="contains(table:table-cell[14]/text:p, '%')">
                                        <xsl:attribute name="relative">
                                            <xsl:value-of select="table:table-cell[14]/text:p"/>
                                        </xsl:attribute>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:attribute name="absolute">
                                            <xsl:value-of select="table:table-cell[14]/text:p"/>
                                        </xsl:attribute>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:element>
                        </xsl:element>
                    </xsl:if>
                    <xsl:element name="Description">
                        <xsl:value-of select="table:table-cell[15]/text:p"/>
                    </xsl:element>
                </xsl:element>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <xsl:template name="Set-Attributes">
        <xsl:param name="list"/>
        <xsl:param name="delimiter"/>
        <xsl:param name="separator"/>
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="devAlias"/>
        <xsl:variable name="newlist">
            <xsl:choose>
                <xsl:when test="contains($list, $delimiter)">
                    <xsl:value-of select="normalize-space($list)"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:if test="string-length(normalize-space($list))">
                        <xsl:value-of select="concat(normalize-space($list), $delimiter)"/>
                    </xsl:if>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:if test="string-length($newlist)">
            <xsl:variable name="first" select="substring-before($newlist, $delimiter)"/>
            <xsl:variable name="remaining" select="substring-after($newlist, $delimiter)"/>

            <xsl:variable name="attrname" select="substring-before($first, $separator)"/>
            <xsl:variable name="attrval" select="substring-after($first, $separator)"/>
            
            <xsl:element name="Attribute">
                <xsl:attribute name="name">
                    <xsl:value-of select="$attrname"/>
                </xsl:attribute>
                <xsl:element name="Value">
                    <xsl:value-of select="$attrval"/>
                </xsl:element>
            </xsl:element>
            
            <xsl:if test="$remaining">
                <xsl:call-template name="Set-Attributes">
                    <xsl:with-param name="list" select="$remaining"/>
                    <xsl:with-param name="delimiter" select="$delimiter"/>
                    <xsl:with-param name="separator" select="$separator"/>
                </xsl:call-template>
            </xsl:if>
        </xsl:if>
    </xsl:template>
    
</xsl:stylesheet>
