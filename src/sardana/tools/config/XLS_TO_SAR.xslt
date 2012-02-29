<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:wb="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
    <xsl:output method="xml" indent="yes"/> 

    <xsl:template match="/">
        <xsl:apply-templates select="wb:Workbook" />
    </xsl:template>
    
    <xsl:template match="wb:Workbook">
        <xsl:variable name="SarCode">
            <xsl:value-of select="ss:Worksheet[@ss:Name='Global']/ss:Table/ss:Row[1]/ss:Cell[2]/ss:Data"/>
        </xsl:variable>
        <xsl:variable name="SarName">
            <xsl:value-of select="ss:Worksheet[@ss:Name='Global']/ss:Table/ss:Row[2]/ss:Cell[2]/ss:Data"/>
        </xsl:variable>
        <xsl:variable name="SarDesc">
            <xsl:value-of select="ss:Worksheet[@ss:Name='Global']/ss:Table/ss:Row[3]/ss:Cell[2]/ss:Data"/>
        </xsl:variable>
        <xsl:element name="Sardana">
            <xsl:attribute name="name">
                <xsl:value-of select="$SarCode"/>
            </xsl:attribute>
            <xsl:attribute name="longName">
                <xsl:value-of select="$SarName"/>
            </xsl:attribute>
            <Description><xsl:value-of select="$SarDesc"/></Description>
            <xsl:apply-templates select="ss:Worksheet"/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="ss:Worksheet[@ss:Name='Servers']">
        <xsl:for-each select="ss:Table/ss:Row">
            <xsl:variable name="serverType">
                <xsl:value-of select="ss:Cell[1]/ss:Data"/>
            </xsl:variable>
            <xsl:if test="$serverType != 'Type'">
                
                <xsl:variable name="tangoHost">
                    <xsl:value-of select="ss:Cell[2]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="serverName">
                    <xsl:value-of select="ss:Cell[3]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="desc">
                    <xsl:value-of select="ss:Cell[4]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="name">
                    <xsl:value-of select="ss:Cell[5]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="deviceName">
                    <xsl:value-of select="ss:Cell[6]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="path">
                    <xsl:value-of select="ss:Cell[7]/ss:Data"/>
                </xsl:variable>
                
                <!-- Server element -->
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

                    <!-- Element -->
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
                        
                        <!-- Particular for each server -->
                        <xsl:choose>
                            <xsl:when test="$serverType = 'Pool'">
                                <xsl:element name="Property">
                                    <xsl:attribute name="name">PoolPath</xsl:attribute>
                                    <xsl:call-template name="Set-Property">
                                        <xsl:with-param name="list">
                                            <xsl:value-of select="$path"/>
                                        </xsl:with-param>
                                        <xsl:with-param name="delimiter">:</xsl:with-param>
                                        <xsl:with-param name="tag">Item</xsl:with-param>
                                    </xsl:call-template>
                                </xsl:element>
                                <xsl:element name="Property">
                                    <xsl:attribute name="name">Version</xsl:attribute>
                                    <xsl:call-template name="Set-Property">
                                        <xsl:with-param name="list">0.3.0
                                        </xsl:with-param>
                                        <xsl:with-param name="delimiter">:</xsl:with-param>
                                        <xsl:with-param name="tag">Item</xsl:with-param>
                                    </xsl:call-template>
                                </xsl:element>
                                <xsl:call-template name="Set-Pool">
                                    <xsl:with-param name="poolDeviceName">
                                        <xsl:value-of select="$deviceName"/>
                                    </xsl:with-param>
                                </xsl:call-template>
                            </xsl:when>
                            <xsl:when test="$serverType = 'MacroServer'">
                                <xsl:variable name="pools">
                                    <xsl:value-of select="ss:Cell[8]/ss:Data"/>
                                </xsl:variable>
                                <xsl:element name="Property">
                                    <xsl:attribute name="name">MacroPath</xsl:attribute>
                                    <xsl:call-template name="Set-Property">
                                        <xsl:with-param name="list">
                                            <xsl:value-of select="$path"/>
                                        </xsl:with-param>
                                        <xsl:with-param name="delimiter">:</xsl:with-param>
                                        <xsl:with-param name="tag">Item</xsl:with-param>
                                    </xsl:call-template>
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
                
                    
                    <!-- Particular for each server -->
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

    <xsl:template match="ss:Worksheet[@ss:Name='Global']"/>
    <xsl:template match="ss:Worksheet[@ss:Name='Motors']"/>
    <xsl:template match="ss:Worksheet[@ss:Name='IORegisters']"/>
    <xsl:template match="ss:Worksheet[@ss:Name='Channels']"/>
    <xsl:template match="ss:Worksheet[@ss:Name='CommunicationChannels']"/>
    <xsl:template match="ss:Worksheet[@ss:Name='Doors']"/>
    <xsl:template match="ss:Worksheet[@ss:Name='Controllers']"/>
    <xsl:template match="ss:Worksheet[@ss:Name='Parameters']"/>
    <xsl:template match="ss:Worksheet[@ss:Name='Acquisition']"/>
    
    <xsl:template name="Set-Pool">
        <xsl:param name="poolDeviceName"/>
        <!-- Find controllers -->
        <xsl:call-template name="Set-Pool-Controllers">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
        </xsl:call-template>
        <!-- Find measurement groups -->
        <xsl:call-template name="Set-Pool-MeasurementGroups">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
        </xsl:call-template>
        
    </xsl:template>
   
    <xsl:template name="Set-Pool-MeasurementGroups">
        <xsl:param name="poolDeviceName"/>

        <xsl:for-each select="/wb:Workbook/ss:Worksheet[@ss:Name='Acquisition']/ss:Table/ss:Row">
            <xsl:variable name="currentPool">
                <xsl:value-of select="ss:Cell[2]/ss:Data"/>
            </xsl:variable>
            <xsl:if test="$currentPool = $poolDeviceName">

                <xsl:variable name="mgName">
                    <xsl:value-of select="ss:Cell[3]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="mgDeviceName">
                    <xsl:value-of select="ss:Cell[4]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="mgElements">
                    <xsl:value-of select="ss:Cell[5]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="mgDescription">
                    <xsl:value-of select="ss:Cell[6]/ss:Data"/>
                </xsl:variable>
                <MeasurementGroup name="{$mgName}" deviceName="{$mgDeviceName}">
                    <xsl:call-template name="Set-MeasurementGroupElements">
                        <xsl:with-param name="list">
                            <xsl:value-of select="$mgElements"/>
                        </xsl:with-param>
                        <xsl:with-param name="delimiter">;</xsl:with-param>
                    </xsl:call-template>
                    <xsl:element name="Description">
                        <xsl:value-of select="$mgDescription"/>
                    </xsl:element>
                </MeasurementGroup>
            </xsl:if>
        </xsl:for-each>
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

    <xsl:template name="Set-Pool-Ctrl-IORegisters">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:call-template name="Set-Pool-Ctrl-Elements">
            <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
            <xsl:with-param name="ctrlName" select="$ctrlName"/>
            <xsl:with-param name="sheet">IORegisters</xsl:with-param>
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
    
    <xsl:template name="Set-Pool-Ctrl-Elements">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="ctrlName"/>
        <xsl:param name="sheet"/>
        
        <xsl:for-each select="/wb:Workbook/ss:Worksheet[@ss:Name=$sheet]/ss:Table/ss:Row">
            <xsl:variable name="pool">
                <xsl:value-of select="ss:Cell[2]/ss:Data"/>
            </xsl:variable>
            <xsl:variable name="ctrl">
                <xsl:value-of select="ss:Cell[3]/ss:Data"/>
            </xsl:variable>
            <xsl:variable name="type">
                <xsl:value-of select="ss:Cell[1]/ss:Data"/>
            </xsl:variable>
            <xsl:if test="$pool = $poolDeviceName and $ctrl = $ctrlName">
                <xsl:variable name="name">
                    <xsl:value-of select="ss:Cell[4]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="deviceName">
                    <xsl:value-of select="ss:Cell[5]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="axis">
                    <xsl:value-of select="ss:Cell[6]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="desc">
                    <xsl:value-of select="ss:Cell[7]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="attributes">
                    <xsl:value-of select="ss:Cell[8]/ss:Data"/>
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
                    <xsl:element name="Description">
                        <xsl:value-of select="$desc"/>
                    </xsl:element>
                    <xsl:call-template name="Set-Attributes">
                        <xsl:with-param name="list">
                            <xsl:value-of select="$attributes"/>
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
    
    <xsl:template name="Set-Pool-Controllers">
        <xsl:param name="poolDeviceName"/>
        
        <xsl:for-each select="/wb:Workbook/ss:Worksheet[@ss:Name='Controllers']/ss:Table/ss:Row">
            <xsl:variable name="ctrlPool">
                <xsl:value-of select="ss:Cell[2]/ss:Data"/>
            </xsl:variable>
            <xsl:if test="$ctrlPool = $poolDeviceName">
            
                <xsl:variable name="ctrlType">
                    <xsl:value-of select="ss:Cell[1]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="ctrlName">
                    <xsl:value-of select="ss:Cell[3]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="ctrlLib">
                    <xsl:value-of select="ss:Cell[4]/ss:Data"/>
                </xsl:variable>                
                <xsl:variable name="ctrlClass">
                    <xsl:value-of select="ss:Cell[5]/ss:Data"/>
                </xsl:variable>

                <Controller type="{$ctrlType}" name="{$ctrlName}"
                            lib="{$ctrlLib}"   class="{$ctrlClass}">
                    <!-- Properties are the 6th column if the Cell tag does not have the Index != 6.
                         If it does it means that the Properties column is empty and it refers to the next non empty column-->
                    <xsl:if test="not(ss:Cell[6][@ss:Index]) or ss:Cell[6][@ss:Index]='6'">
                        <xsl:call-template name="Set-CtrlProperty">
                            <xsl:with-param name="list">
                                <xsl:value-of select="ss:Cell[6]/ss:Data"/>
                            </xsl:with-param>
                            <xsl:with-param name="delimiter">;</xsl:with-param>
                            <xsl:with-param name="separator">:</xsl:with-param>
                        </xsl:call-template>
                    </xsl:if>
                    
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
                            <xsl:call-template name="Set-Property">
                                <xsl:with-param name="list">
                                    <xsl:choose>
                                        <xsl:when test="ss:Cell[@ss:Index='7']">
                                            <xsl:value-of select="ss:Cell[@ss:Index='7']/ss:Data"/>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="ss:Cell[7]/ss:Data"/>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:with-param>
                                <xsl:with-param name="delimiter">;</xsl:with-param>
                                <xsl:with-param name="tag">Motor</xsl:with-param>
                            </xsl:call-template>
                            <xsl:call-template name="Set-Pool-Ctrl-PseudoMotors">
                                <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
                                <xsl:with-param name="ctrlName" select="$ctrlName"/>
                            </xsl:call-template>
                        </xsl:when>
                        <xsl:when test="$ctrlType = 'PseudoCounter'">
                            <xsl:call-template name="Set-Property">
                                <xsl:with-param name="list">
                                    <xsl:choose>
                                        <xsl:when test="ss:Cell[@ss:Index='7']">
                                            <xsl:value-of select="ss:Cell[@ss:Index='7']/ss:Data"/>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:value-of select="ss:Cell[7]/ss:Data"/>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:with-param>
                                <xsl:with-param name="delimiter">;</xsl:with-param>
                                <xsl:with-param name="tag">Channel</xsl:with-param>
                            </xsl:call-template>
                            <xsl:call-template name="Set-Pool-Ctrl-PseudoCounters">
                                <xsl:with-param name="poolDeviceName" select="$poolDeviceName"/>
                                <xsl:with-param name="ctrlName" select="$ctrlName"/>
                            </xsl:call-template>
                        </xsl:when>
                    </xsl:choose>
                </Controller>
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
        <xsl:for-each select="/wb:Workbook/ss:Worksheet[@ss:Name='Doors']/ss:Table/ss:Row">
            <xsl:variable name="doorServer">
                <xsl:value-of select="ss:Cell[1]/ss:Data"/>
            </xsl:variable>
            <xsl:variable name="doorMacroServer">
                <xsl:value-of select="ss:Cell[2]/ss:Data"/>
            </xsl:variable>
            <xsl:if test="$doorServer = $serverName and $doorMacroServer = $deviceName">
                <xsl:variable name="desc">
                    <xsl:value-of select="ss:Cell[3]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="name">
                    <xsl:value-of select="ss:Cell[4]/ss:Data"/>
                </xsl:variable>
                <xsl:variable name="deviceName">
                    <xsl:value-of select="ss:Cell[5]/ss:Data"/>
                </xsl:variable>
            
                <xsl:element name="Door">
                    <xsl:attribute name="name"><xsl:value-of select="$name"/></xsl:attribute>
                    <xsl:attribute name="deviceName"><xsl:value-of select="$deviceName"/></xsl:attribute>
                    <xsl:element name="Description"><xsl:value-of select="$desc"/></xsl:element>
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
                <!--
                <xsl:call-template name="Set-Attribute-Config">
                    <xsl:with-param name="poolDeviceName">
                        <xsl:value-of select="$poolDeviceName"/>
                    </xsl:with-param>
                    <xsl:with-param name="devAlias">
                        <xsl:value-of select="$devAlias"/>
                    </xsl:with-param>
                    <xsl:with-param name="attrName">
                        <xsl:value-of select="$attrname"/>
                    </xsl:with-param>
                </xsl:call-template>
                -->
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
    
    <xsl:template name="Set-Attributes-Config">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="devAlias"/>
        <xsl:for-each select="/wb:Workbook/ss:Worksheet[@ss:Name='Parameters']/ss:Table/ss:Row">
            <xsl:variable name="currPool">
                <xsl:value-of select="ss:Cell[1]/ss:Data"/>
            </xsl:variable>
            <xsl:variable name="currDev">
                <xsl:value-of select="ss:Cell[2]/ss:Data"/>
            </xsl:variable>
        
            <xsl:if test="$currPool = $poolDeviceName and $currDev = $devAlias">
                <xsl:element name="Attribute">
                    <xsl:attribute name="name" >
                        <xsl:value-of select="ss:Cell[3]/ss:Data"/>
                    </xsl:attribute>
                    <xsl:element name="Configuration">
                        <xsl:element name="Display">
                            <xsl:attribute name="label" >
                                <xsl:value-of select="ss:Cell[4]/ss:Data"/>
                            </xsl:attribute>
                            <xsl:attribute name="format" >
                                <xsl:value-of select="ss:Cell[5]/ss:Data"/>
                            </xsl:attribute>
                        </xsl:element>
                        <xsl:element name="Units">
                            <xsl:attribute name="unit" >
                                <xsl:value-of select="ss:Cell[12]/ss:Data"/>
                            </xsl:attribute>
                            <xsl:attribute name="display_unit" >
                                <xsl:value-of select="ss:Cell[12]/ss:Data"/>
                            </xsl:attribute>
                        </xsl:element>
                        <xsl:element name="Range">
                            <xsl:attribute name="min" >
                                <xsl:value-of select="ss:Cell[6]/ss:Data"/>
                            </xsl:attribute>
                            <xsl:attribute name="max" >
                                <xsl:value-of select="ss:Cell[11]/ss:Data"/>
                            </xsl:attribute>
                        </xsl:element>
                        <xsl:element name="Alarms">
                            <xsl:attribute name="min_alarm" >
                                <xsl:value-of select="ss:Cell[7]/ss:Data"/>
                            </xsl:attribute>
                            <xsl:attribute name="min_warning" >
                                <xsl:value-of select="ss:Cell[8]/ss:Data"/>
                            </xsl:attribute>
                            <xsl:attribute name="max_warning" >
                                <xsl:value-of select="ss:Cell[9]/ss:Data"/>
                            </xsl:attribute>
                            <xsl:attribute name="max_alarm" >
                                <xsl:value-of select="ss:Cell[10]/ss:Data"/>
                            </xsl:attribute>
                        </xsl:element>
                    </xsl:element>
                    <xsl:if test="ss:Cell[13]/ss:Data != '-1'">
                        <xsl:element name="Polling">
                            <xsl:attribute name="polled" >True</xsl:attribute>
                            <xsl:attribute name="period" >
                                <xsl:value-of select="ss:Cell[13]/ss:Data"/>
                            </xsl:attribute>
                        </xsl:element>
                    </xsl:if>
                    <xsl:if test="ss:Cell[14]/ss:Data != 'Automatic'">
                        <xsl:element name="Events">
                            <xsl:element name="ChangeEvent">
                                <xsl:choose> 
                                    <xsl:when test="contains(ss:Cell[14]/ss:Data, '%')">
                                        <xsl:attribute name="relative">
                                            <xsl:value-of select="ss:Cell[14]/ss:Data"/>
                                        </xsl:attribute>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:attribute name="absolute">
                                            <xsl:value-of select="ss:Cell[14]/ss:Data"/>
                                        </xsl:attribute>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:element>
                        </xsl:element>
                    </xsl:if>
                    <xsl:element name="Description">
                        <xsl:value-of select="ss:Cell[15]/ss:Data"/>
                    </xsl:element>
                </xsl:element>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

    <xsl:template name="Set-Attribute-Config">
        <xsl:param name="poolDeviceName"/>
        <xsl:param name="devAlias"/>
        <xsl:param name="attrName"/>
        <xsl:for-each select="/wb:Workbook/ss:Worksheet[@ss:Name='Parameters']/ss:Table/ss:Row">
            <xsl:variable name="currPool">
                <xsl:value-of select="ss:Cell[1]/ss:Data"/>
            </xsl:variable>
            <xsl:variable name="currDev">
                <xsl:value-of select="ss:Cell[2]/ss:Data"/>
            </xsl:variable>
            <xsl:variable name="currAttr">
                <xsl:value-of select="ss:Cell[3]/ss:Data"/>
            </xsl:variable>
        
            <xsl:if test="$currPool = $poolDeviceName and $currDev = $devAlias and $currAttr = $attrName">
                <xsl:element name="Configuration">
                    <xsl:element name="Display">
                        <xsl:attribute name="label" >
                            <xsl:value-of select="ss:Cell[4]/ss:Data"/>
                        </xsl:attribute>
                        <xsl:attribute name="format" >
                            <xsl:value-of select="ss:Cell[5]/ss:Data"/>
                        </xsl:attribute>
                    </xsl:element>
                    <xsl:element name="Units">
                        <xsl:attribute name="unit" >
                            <xsl:value-of select="ss:Cell[12]/ss:Data"/>
                        </xsl:attribute>
                        <xsl:attribute name="display_unit" >
                            <xsl:value-of select="ss:Cell[12]/ss:Data"/>
                        </xsl:attribute>
                    </xsl:element>
                    <xsl:element name="Range">
                        <xsl:attribute name="min" >
                            <xsl:value-of select="ss:Cell[6]/ss:Data"/>
                        </xsl:attribute>
                        <xsl:attribute name="max" >
                            <xsl:value-of select="ss:Cell[11]/ss:Data"/>
                        </xsl:attribute>
                    </xsl:element>
                    <xsl:element name="Alarms">
                        <xsl:attribute name="min_alarm" >
                            <xsl:value-of select="ss:Cell[7]/ss:Data"/>
                        </xsl:attribute>
                        <xsl:attribute name="min_warning" >
                            <xsl:value-of select="ss:Cell[8]/ss:Data"/>
                        </xsl:attribute>
                        <xsl:attribute name="max_warning" >
                            <xsl:value-of select="ss:Cell[9]/ss:Data"/>
                        </xsl:attribute>
                        <xsl:attribute name="max_alarm" >
                            <xsl:value-of select="ss:Cell[10]/ss:Data"/>
                        </xsl:attribute>
                    </xsl:element>
                    <xsl:element name="Description">
                        <xsl:value-of select="ss:Cell[13]/ss:Data"/>
                    </xsl:element>
                </xsl:element>
                <xsl:if test="ss:Cell[14]/ss:Data">
                    <xsl:element name="Polling">
                        <xsl:attribute name="polled" >True</xsl:attribute>
                        <xsl:attribute name="period" >
                            <xsl:value-of select="ss:Cell[14]/ss:Data"/>
                        </xsl:attribute>
                    </xsl:element>
                </xsl:if>
            </xsl:if>
        </xsl:for-each>
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
        
        <xsl:element name="{$tag}"><xsl:value-of select="$first"/></xsl:element>
        
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
    
</xsl:stylesheet>
