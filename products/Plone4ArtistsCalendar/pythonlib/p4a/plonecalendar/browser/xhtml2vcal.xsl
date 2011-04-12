<?xml version="1.0"?>
<xsl:stylesheet 
 xmlns:xsl ="http://www.w3.org/1999/XSL/Transform"
 xmlns:uri ="http://www.w3.org/2000/07/uri43/uri.xsl?template="
 xmlns:datetime ="http://suda.co.uk/projects/X2V/datetime.xsl?template="
 version="1.0"
>

<!-- i have saved the file locally to conserve bandwidth, always check for updateds -->
<xsl:import href="uri.xsl" />
<xsl:import href="datetime.xsl" />

<xsl:output
  encoding="UTF-8"
  indent="no"
  media-type="text/calendar"
  method="text"
/>
<!--
brian suda
brian@suda.co.uk
http://suda.co.uk/

XHTML-2-iCal
Version 0.8.1
2006-07-10

Copyright 2005 Brian Suda
This work is relicensed under The W3C Open Source License
http://www.w3.org/Consortium/Legal/copyright-software-19980720


NOTES:
Until the hCal spec has been finalised this is a work in progress.
I'm not an XSLT expert, so there are no guarantees to quality of this code!

-->
<xsl:param name="Prodid">-//suda.co.uk//X2V 0.8 (BETA)//EN</xsl:param>
<xsl:param name="Source">(Best Practice: should be URL that this was ripped from)</xsl:param>
<xsl:param name="Anchor" />

<xsl:param name="Debug" select="0"/>

<xsl:variable name="lcase" select='"abcdefghijklmnopqrstuvwxyz"'/>
<xsl:variable name="ucase" select='"ABCDEFGHIJKLMNOPQRSTUVWXYZ"'/>
<xsl:variable name="digit" select='"01234567890"'/>
<xsl:variable name="alpha" select='concat($lcase, $ucase)'/>
<xsl:param name="Encoding" >UTF-8</xsl:param>
<xsl:variable name="nl"><xsl:text>
</xsl:text></xsl:variable>
<xsl:variable name="tb"><xsl:text>	</xsl:text></xsl:variable>


<xsl:template match="/">
	<xsl:text>BEGIN:VCALENDAR</xsl:text>
	<xsl:text>&#x0A;PRODID:</xsl:text><xsl:value-of select="$Prodid"/>
	<xsl:text>&#x0A;X-ORIGINAL-URL:</xsl:text><xsl:value-of select="normalize-space($Source)"/>
	<xsl:text>&#x0A;X-WR-CALNAME:</xsl:text>
	<xsl:call-template name="escapeText">
		<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(//*[name() = 'title'])" /></xsl:with-param>
	</xsl:call-template>
	<xsl:text>&#x0A;VERSION:2.0</xsl:text>
	<xsl:text>&#x0A;METHOD:PUBLISH</xsl:text>	
	<xsl:apply-templates select="//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ',normalize-space(@class),' '),' vevent ')]"/>
	<xsl:text>&#x0A;END:VCALENDAR</xsl:text>
</xsl:template>

<!-- Add more templates as they are needed-->
<xsl:template match="*[contains(concat(' ',normalize-space(@class),' '),' vevent ')]">
	<xsl:if test="not($Anchor) or @id = $Anchor">
		<xsl:text>&#x0A;BEGIN:VEVENT</xsl:text>
		<!-- check for header="" and extract that data -->
		<xsl:if test="@headers">
			<xsl:call-template name="extract-ids">
				<xsl:with-param name="text-string"><xsl:value-of select="@headers"/></xsl:with-param>
			</xsl:call-template>
		</xsl:if>
		
		<xsl:if test=".//*[ancestor-or-self::*[name() = 'del'] = false()] and .//*[descendant-or-self::*[name() = 'object' or name() = 'a'] = true() and contains(normalize-space(@data),'#')]">
			<xsl:for-each select=".//*[descendant-or-self::*[name() = 'object' or name() = 'a'] = true() and contains(normalize-space(@data),'#') and contains(concat(' ',normalize-space(@class),' '),' include ')]">
				<xsl:variable name="header-id"><xsl:value-of select="substring-after(@data,'#')"/></xsl:variable>
				<xsl:for-each select="//*[@id=$header-id]">
					<xsl:call-template name="veventProperties"/>
				</xsl:for-each>
			</xsl:for-each>
		</xsl:if> 		
	
		<xsl:call-template name="veventProperties"/>
		<xsl:text>&#x0A;END:VEVENT&#x0A;</xsl:text>
	</xsl:if>
</xsl:template>

<!-- Add more templates as they are needed-->
<xsl:template match="*[contains(concat(' ',normalize-space(@class),' '),' vfreebusy ')]">
	<xsl:if test="not($Anchor) or @id = $Anchor">
		<xsl:text>&#x0A;BEGIN:VFREEBUSY</xsl:text>
		<!-- check for header="" and extract that data -->
		<xsl:if test="@headers">
			<xsl:call-template name="extract-ids">
				<xsl:with-param name="text-string"><xsl:value-of select="@headers"/></xsl:with-param>
			</xsl:call-template>
		</xsl:if>
		
		<xsl:if test=".//*[ancestor-or-self::*[name() = 'del'] = false()] and .//*[descendant-or-self::*[name() = 'object'] = true() and contains(normalize-space(@data),'#')]">
			<xsl:for-each select=".//*[descendant-or-self::*[name() = 'object'] = true() and contains(normalize-space(@data),'#') and contains(concat(' ',normalize-space(@class),' '),' include ')]">
				<xsl:variable name="header-id"><xsl:value-of select="substring-after(@data,'#')"/></xsl:variable>
				<xsl:for-each select="//*[@id=$header-id]">
					<xsl:call-template name="vfreebusyProperties"/>
				</xsl:for-each>
			</xsl:for-each>
		</xsl:if> 		
	
		<xsl:call-template name="vfreebusyProperties"/>
		<xsl:text>&#x0A;END:VFREEBUSY&#x0A;</xsl:text>
	</xsl:if>
</xsl:template>

<xsl:template name="vfreebusyProperties">
	<xsl:call-template name="textPropLang">
		<xsl:with-param name="label">CONTACT</xsl:with-param>
		<xsl:with-param name="class">contact</xsl:with-param>
	</xsl:call-template>
	
	<xsl:variable name="duration-val">
	  <xsl:call-template name="textProp">
	    <xsl:with-param name="class">duration</xsl:with-param>
	  </xsl:call-template>
	</xsl:variable>
	<xsl:if test="not($duration-val = '')">
	    <xsl:text>&#x0A;DURATION;CHARSET=</xsl:text><xsl:value-of select="$Encoding"/>
	    <xsl:text>:</xsl:text>
		<xsl:value-of select="translate(normalize-space($duration-val),$lcase,$ucase)"/>
	</xsl:if>

	<xsl:call-template name="dateProp">
		<xsl:with-param name="label">DTSTART</xsl:with-param>
		<xsl:with-param name="class">dtstart</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="dateProp">
		<xsl:with-param name="label">DTEND</xsl:with-param>
		<xsl:with-param name="class">dtend</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="dateProp">
		<xsl:with-param name="label">DTSTAMP</xsl:with-param>
		<xsl:with-param name="class">dtstamp</xsl:with-param>
	</xsl:call-template>
	
	<xsl:call-template name="textProp">
		<xsl:with-param name="label">UID</xsl:with-param>
		<xsl:with-param name="class">uid</xsl:with-param>
	</xsl:call-template>

	<xsl:apply-templates select=".//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ',normalize-space(@class),' '),' url ')]" mode="url"/>

	<xsl:call-template name="personProp">
		<xsl:with-param name="label">ATTENDEE</xsl:with-param>
		<xsl:with-param name="class">attendee</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="personProp">
		<xsl:with-param name="label">ORGANIZER</xsl:with-param>
		<xsl:with-param name="class">organizer</xsl:with-param>
	</xsl:call-template>
	
	<xsl:call-template name="textPropLang">
		<xsl:with-param name="label">COMMENT</xsl:with-param>
		<xsl:with-param name="class">comment</xsl:with-param>
	</xsl:call-template>
	
	<!-- freebusy -->
	<!-- rstatus -->

</xsl:template>

<xsl:template name="veventProperties">
	<xsl:call-template name="textProp">
		<xsl:with-param name="label">CLASS</xsl:with-param>
		<xsl:with-param name="class">class</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="textProp">
		<xsl:with-param name="label">UID</xsl:with-param>
		<xsl:with-param name="class">uid</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="textPropLang">
		<xsl:with-param name="label">COMMENT</xsl:with-param>
		<xsl:with-param name="class">comment</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="textPropLang">
		<xsl:with-param name="label">DESCRIPTION</xsl:with-param>
		<xsl:with-param name="class">description</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="textPropLang">
		<xsl:with-param name="label">LOCATION</xsl:with-param>
		<xsl:with-param name="class">location</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="textPropLang">
		<xsl:with-param name="label">SUMMARY</xsl:with-param>
		<xsl:with-param name="class">summary</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="textPropLang">
		<xsl:with-param name="label">CONTACT</xsl:with-param>
		<xsl:with-param name="class">contact</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="textProp">
		<xsl:with-param name="label">SEQUENCE</xsl:with-param>
		<xsl:with-param name="class">sequence</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="textProp">
		<xsl:with-param name="label">PRIORITY</xsl:with-param>
		<xsl:with-param name="class">priority</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="textProp">
		<xsl:with-param name="label">STATUS</xsl:with-param>
		<xsl:with-param name="class">status</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="textProp">
		<xsl:with-param name="label">TRANSP</xsl:with-param>
		<xsl:with-param name="class">transp</xsl:with-param>
	</xsl:call-template>
	
	<xsl:variable name="duration-val">
	  <xsl:call-template name="textProp">
	    <xsl:with-param name="class">duration</xsl:with-param>
	  </xsl:call-template>
	</xsl:variable>
	<xsl:if test="not($duration-val = '')">
	    <xsl:text>&#x0A;DURATION;CHARSET=</xsl:text><xsl:value-of select="$Encoding"/>
	    <xsl:text>:</xsl:text>
		<xsl:value-of select="translate(normalize-space($duration-val),$lcase,$ucase)"/>
	</xsl:if>

	<xsl:call-template name="dateProp">
		<xsl:with-param name="label">DTSTART</xsl:with-param>
		<xsl:with-param name="class">dtstart</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="dateProp">
		<xsl:with-param name="label">DTEND</xsl:with-param>
		<xsl:with-param name="class">dtend</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="dateProp">
		<xsl:with-param name="label">DTSTAMP</xsl:with-param>
		<xsl:with-param name="class">dtstamp</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="dateProp">
		<xsl:with-param name="label">LAST-MODIFIED</xsl:with-param>
		<xsl:with-param name="class">last-modified</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="dateProp">
		<xsl:with-param name="label">CREATED</xsl:with-param>
		<xsl:with-param name="class">created</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="dateProp">
		<xsl:with-param name="label">RECURRENCE-ID</xsl:with-param>
		<xsl:with-param name="class">recurrence-id</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="personProp">
		<xsl:with-param name="label">ATTENDEE</xsl:with-param>
		<xsl:with-param name="class">attendee</xsl:with-param>
	</xsl:call-template>

	<xsl:call-template name="personProp">
		<xsl:with-param name="label">ORGANIZER</xsl:with-param>
		<xsl:with-param name="class">organizer</xsl:with-param>
	</xsl:call-template>
	
	<xsl:call-template name="multiTextPropLang">
		<xsl:with-param name="label">CATEGORIES</xsl:with-param>
		<xsl:with-param name="class">category</xsl:with-param>
	</xsl:call-template>
	

	<!-- These are all unique: custom templates -->
	<xsl:apply-templates select=".//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ',normalize-space(@class),' '),' related-to ')]" mode="related-to"/>
	<xsl:apply-templates select=".//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ',normalize-space(@class),' '),' attach ')]" mode="attach"/>
	<xsl:apply-templates select=".//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ',normalize-space(@class),' '),' url ')]" mode="url"/>
	<xsl:apply-templates select=".//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ',normalize-space(@class),' '),' rdate ')]" mode="rdate"/>
	<xsl:apply-templates select=".//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ',normalize-space(@class),' '),' exdate ')]" mode="exdate"/>

	<!-- <xsl:apply-templates select=".//*[contains(concat(' ',normalize-space(@class),' '),' geo ')]" mode="geo"/>  -->
	<!-- <xsl:apply-templates select=".//*[contains(concat(' ',normalize-space(@class),' '),' resources ')]" mode="resources"/> -->
	<!-- <xsl:apply-templates select=".//*[contains(concat(' ',normalize-space(@class),' '),' status ')]" mode="status"/> -->
	<!-- <xsl:apply-templates select=".//*[contains(concat(' ',normalize-space(@class),' '),' transp ')]" mode="transp"/> -->

	<!-- UNWRITTEN TEMPLATES -->
	<!--
		
	@@ - all the RRULE stuff!
	
	-->
</xsl:template>

<!-- Date property -->
<xsl:template name="dateProp">
	<xsl:param name="label" />
	<xsl:param name="class" />
	
	<xsl:for-each select="descendant-or-self::*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ', @class, ' '),concat(' ', $class, ' '))]">
        <xsl:text>&#x0A;</xsl:text>
		<xsl:value-of select="$label" />
		<!-- TZID needs work! -->
		<xsl:apply-templates select="*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ',@class,' '),' tzid ')]" mode="tzid"/>
        <xsl:text>:</xsl:text>

		<xsl:choose>
			<xsl:when test="@longdesc != ''">
				<xsl:call-template name="datetime:utc-time-converter">
					<xsl:with-param name="time-string"><xsl:value-of select="normalize-space(@longdesc)" /></xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:when test="@alt != ''">
				<xsl:call-template name="datetime:utc-time-converter">
					<xsl:with-param name="time-string"><xsl:value-of select="normalize-space(@alt)" /></xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:when test="@title != ''">
				<xsl:call-template name="datetime:utc-time-converter">
					<xsl:with-param name="time-string"><xsl:value-of select="normalize-space(@title)" /></xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:call-template name="datetime:utc-time-converter">
					<xsl:with-param name="time-string"><xsl:value-of select="normalize-space(.)" /></xsl:with-param>
				</xsl:call-template>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:for-each>
</xsl:template>

<!-- TEXT PROPERTY without LANGUAGE -->
<xsl:template name="textProp">
	<xsl:param name="label" />
	<xsl:param name="class" />
		
	<xsl:for-each select=".//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ', @class, ' '),concat(' ', $class, ' '))]">
	<xsl:if test="position() = 1">
	  <xsl:if test="$label">
	    <xsl:text>&#x0A;</xsl:text>
	    <xsl:value-of select="$label" />
	    <xsl:text>;CHARSET=</xsl:text><xsl:value-of select="$Encoding"/>
	    <xsl:text>:</xsl:text>
	  </xsl:if>
		<xsl:choose>
			<xsl:when test='local-name(.) = "ol" or local-name(.) = "ul"'>
				<xsl:for-each select="*">
					<xsl:if test="not(position()=1)">
						<xsl:text>,</xsl:text>
					</xsl:if>
					<xsl:choose>
						<xsl:when test=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
							<xsl:for-each select=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
								<xsl:variable name="textFormatted">
								<xsl:apply-templates select="." mode="unFormatText" />
								</xsl:variable>
								<xsl:value-of select="normalize-space($textFormatted)"/>
							</xsl:for-each>
						</xsl:when>
						<xsl:otherwise>
							<xsl:variable name="textFormatted">
							<xsl:apply-templates select="." mode="unFormatText" />
							</xsl:variable>
							<xsl:value-of select="normalize-space($textFormatted)"/>
						</xsl:otherwise>
					</xsl:choose>		
				</xsl:for-each>
			</xsl:when>
			<xsl:when test='local-name(.) = "abbr" and @title'>
				<xsl:variable name="textFormatted">
				<xsl:apply-templates select="@title" mode="unFormatText" />
				</xsl:variable>
				<xsl:value-of select="normalize-space($textFormatted)"/>
			</xsl:when>			
			<xsl:when test='@alt and (local-name(.) = "img" or local-name(.) = "area")'>
				<xsl:variable name="textFormatted">
				<xsl:apply-templates select="@alt" mode="unFormatText" />
				</xsl:variable>
				<xsl:value-of select="normalize-space($textFormatted)"/>
			</xsl:when>
			<xsl:when test=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
				<xsl:for-each select=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
					<xsl:variable name="textFormatted">
					<xsl:apply-templates select="." mode="unFormatText" />
					</xsl:variable>
					<xsl:value-of select="normalize-space($textFormatted)"/>
				</xsl:for-each>
			</xsl:when>
			<xsl:otherwise>
				<xsl:variable name="textFormatted">
				<xsl:apply-templates select="." mode="unFormatText" />
				</xsl:variable>
				<xsl:value-of select="normalize-space($textFormatted)"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:if>
	</xsl:for-each>
</xsl:template>

<!-- TEXT PROPERTY with LANGUAGE -->
<xsl:template name="textPropLang">
	<xsl:param name="label" />
	<xsl:param name="class" />

	<xsl:for-each select=".//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ', @class, ' '),concat(' ', $class, ' '))]">

	<xsl:if test="position() = 1">

        <xsl:text>&#x0A;</xsl:text>
		<xsl:value-of select="$label" />
    	<xsl:call-template name="lang" />
		<xsl:text>;CHARSET=</xsl:text><xsl:value-of select="$Encoding"/>
        <xsl:text>:</xsl:text>
		<xsl:choose>
			<xsl:when test='local-name(.) = "ol" or local-name(.) = "ul"'>
				<xsl:for-each select="*">
					<xsl:if test="not(position()=1)">
						<xsl:text>,</xsl:text>
					</xsl:if>
					<xsl:choose>
						<xsl:when test=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
							<xsl:for-each select=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
								<xsl:variable name="textFormatted">
								<xsl:apply-templates select="." mode="unFormatText" />
								</xsl:variable>
								<xsl:value-of select="normalize-space($textFormatted)"/>
							</xsl:for-each>
						</xsl:when>
						<xsl:otherwise>
							<xsl:variable name="textFormatted">
							<xsl:apply-templates select="." mode="unFormatText" />
							</xsl:variable>
							<xsl:value-of select="normalize-space($textFormatted)"/>
						</xsl:otherwise>
					</xsl:choose>		
				</xsl:for-each>
			</xsl:when>
			<xsl:when test='local-name(.) = "abbr" and @title'>
				<xsl:variable name="textFormatted">
				<xsl:apply-templates select="@title" mode="unFormatText" />
				</xsl:variable>
				<xsl:value-of select="normalize-space($textFormatted)"/>
			</xsl:when>
			<xsl:when test='@alt and (local-name(.) = "img" or local-name(.) = "area")'>
				<xsl:variable name="textFormatted">
				<xsl:apply-templates select="@alt" mode="unFormatText" />
				</xsl:variable>
				<xsl:value-of select="normalize-space($textFormatted)"/>
			</xsl:when>
			<xsl:when test=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
				<xsl:for-each select=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
					<xsl:variable name="textFormatted">
					<xsl:apply-templates select="." mode="unFormatText" />
					</xsl:variable>
					<xsl:value-of select="normalize-space($textFormatted)"/>						
				</xsl:for-each>
			</xsl:when>
			<xsl:otherwise>
				<xsl:variable name="textFormatted">
				<xsl:apply-templates select="." mode="unFormatText" />
				</xsl:variable>
				<xsl:value-of select="normalize-space($textFormatted)"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:if>
	</xsl:for-each>
</xsl:template>

<!-- Person Property (Attendee / Organizer) -->
<xsl:template name="personProp">
	<xsl:param name="label" />
	<xsl:param name="class" />

	<xsl:for-each select=".//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ', @class, ' '),concat(' ', $class, ' '))]">
    <!-- @@ "the first descendant element with that class should take
         effect, any others being ignored." -->
        <xsl:text>&#x0A;</xsl:text>
		<xsl:value-of select="$label" />
    	<xsl:call-template name="lang" />
        <xsl:text>;</xsl:text>
		
		
		<!-- @@ get all the possible parameters -->
		<xsl:text>MAILTO:</xsl:text>
		<xsl:choose>
			<xsl:when test="@href != ''">
				<xsl:call-template name="escapeText">
					<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(substring-after(@href,':'))" /></xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:when test="@longdesc != ''">
				<xsl:call-template name="escapeText">
					<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@longdesc)" /></xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:when test="@alt != ''">
				<xsl:call-template name="escapeText">
					<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@alt)" /></xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:when test="@title != ''">
				<xsl:call-template name="escapeText">
					<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@title)" /></xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:call-template name="escapeText">
					<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(.)" /></xsl:with-param>
				</xsl:call-template>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:for-each>
</xsl:template>


<!-- working templates -->
<xsl:template match="*[contains(@class,'tzid')]" mode="tzid">
<xsl:text>;TZID=</xsl:text>
<xsl:choose>
	<xsl:when test="@longdesc != ''">
		<xsl:call-template name="escapeText">
			<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@longdesc)" /></xsl:with-param>
		</xsl:call-template>
	</xsl:when>
	<xsl:when test="@alt != ''">
		<xsl:call-template name="escapeText">
			<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@alt)" /></xsl:with-param>
		</xsl:call-template>
	</xsl:when>
	<xsl:when test="@title != ''">
		<xsl:call-template name="escapeText">
			<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@title)" /></xsl:with-param>
		</xsl:call-template>
	</xsl:when>
	<xsl:otherwise>
		<xsl:call-template name="escapeText">
			<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(.)" /></xsl:with-param>
		</xsl:call-template>
	</xsl:otherwise>
</xsl:choose>
</xsl:template>

<!-- RDATE property -->
<xsl:template match="*[contains(@class,'rdate')]" mode="rdate">
<xsl:text>
RDATE</xsl:text>
<xsl:apply-templates select="*[contains(concat(' ',@class,' '),' tzid ')]" mode="tzid"/>
<xsl:choose>
	<xsl:when test="name()='ol'">
		<xsl:if test="contains(.,'/') = true()">
			<xsl:text>;VALUE=PERIOD</xsl:text>
		</xsl:if>
		<xsl:text>:</xsl:text>
		<xsl:for-each select="*">
			<xsl:if test="not(position()=1)">
				<xsl:text>,</xsl:text>
			</xsl:if>
			<xsl:call-template name="datetime:utc-time-converter">
				<xsl:with-param name="time-string"><xsl:value-of select="normalize-space(substring-before(.,'/'))" /></xsl:with-param>
			</xsl:call-template>
			<xsl:text>/</xsl:text>
			<xsl:call-template name="datetime:utc-time-converter">
				<xsl:with-param name="time-string"><xsl:value-of select="normalize-space(substring-after(.,'/'))" /></xsl:with-param>
			</xsl:call-template>
		</xsl:for-each>
	</xsl:when>
	<xsl:when test="name()='ul'">
		<xsl:if test="contains(.,'/') = true()">
			<xsl:text>;VALUE=PERIOD</xsl:text>
		</xsl:if>
		<xsl:text>:</xsl:text>
		<xsl:for-each select="*">
			<xsl:if test="not(position()=1)">
				<xsl:text>,</xsl:text>
			</xsl:if>
			<xsl:call-template name="datetime:utc-time-converter">
				<xsl:with-param name="time-string"><xsl:value-of select="normalize-space(substring-before(.,'/'))" /></xsl:with-param>
			</xsl:call-template>
			<xsl:text>/</xsl:text>
			<xsl:call-template name="datetime:utc-time-converter">
				<xsl:with-param name="time-string"><xsl:value-of select="normalize-space(substring-after(.,'/'))" /></xsl:with-param>
			</xsl:call-template>
		</xsl:for-each>
	</xsl:when>
	<xsl:otherwise>
		<xsl:choose>
			<xsl:when test="@longdesc != ''">
				<xsl:if test="contains(@longdesc,'/') = true()">
					<xsl:text>;VALUE=PERIOD</xsl:text>
				</xsl:if>
				<xsl:text>:</xsl:text>
					<xsl:call-template name="datetime:rdate-comma-utc">
						<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@longdesc)" /></xsl:with-param>
					</xsl:call-template>
			</xsl:when>
			<xsl:when test="@alt != ''">
				<xsl:if test="contains(@alt,'/') = true()">
					<xsl:text>;VALUE=PERIOD</xsl:text>
				</xsl:if>
				<xsl:text>:</xsl:text>
					<xsl:call-template name="datetime:rdate-comma-utc">
						<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@alt)" /></xsl:with-param>
					</xsl:call-template>
			</xsl:when>
			<xsl:when test="@title != ''">
				<xsl:if test="contains(@title,'/') = true()">
					<xsl:text>;VALUE=PERIOD</xsl:text>
				</xsl:if>
				<xsl:text>:</xsl:text>
					<xsl:call-template name="datetime:rdate-comma-utc">
						<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@title)" /></xsl:with-param>
					</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:if test="contains(.,'/') = true()">
					<xsl:text>;VALUE=PERIOD</xsl:text>
				</xsl:if>
				<xsl:text>:</xsl:text>
					<xsl:call-template name="datetime:rdate-comma-utc">
						<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(.)" /></xsl:with-param>
					</xsl:call-template>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:otherwise>
</xsl:choose>
</xsl:template>

<!-- EXRULE property -->
<xsl:template match="*[contains(@class,'exrule')]" mode="exrule">
<xsl:text>
EXRULE</xsl:text>
<xsl:apply-templates select="*[contains(concat(' ',@class,' '),' tzid ')]" mode="tzid"/>
<xsl:text>:</xsl:text>
<xsl:choose>
	<xsl:when test="name()='ol'">
		<xsl:for-each select="*">
			<xsl:if test="not(position()=1)">
				<xsl:text>,</xsl:text>
			</xsl:if>
			<xsl:call-template name="escapeText">
				<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(.)" /></xsl:with-param>
			</xsl:call-template>
		</xsl:for-each>
	</xsl:when>
	<xsl:when test="name()='ul'">
		<xsl:for-each select="*">
			<xsl:if test="not(position()=1)">
				<xsl:text>,</xsl:text>
			</xsl:if>
			<xsl:call-template name="escapeText">
				<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(.)" /></xsl:with-param>
			</xsl:call-template>
		</xsl:for-each>
	</xsl:when>
	<xsl:otherwise>
		<xsl:choose>
			<xsl:when test="@longdesc != ''">
				<xsl:value-of select="normalize-space(@longdesc)" />
			</xsl:when>
			<xsl:when test="@alt != ''">
				<xsl:value-of select="normalize-space(@alt)" />
			</xsl:when>
			<xsl:when test="@title != ''">
				<xsl:value-of select="normalize-space(@title)" />
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="normalize-space(.)" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:otherwise>
</xsl:choose>
</xsl:template>


<!-- TEXT PROPERTY with LANGUAGE -->
<xsl:template name="multiTextPropLang">
	<xsl:param name="label" />
	<xsl:param name="class" />

	<xsl:if test=".//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ', @class, ' '),concat(' ', $class, ' '))]">
		<xsl:text>&#x0A;</xsl:text>
		<xsl:value-of select="$label" />
		<!-- this lang needs to be looked at! -->
		<xsl:call-template name="lang" />
		<xsl:text>;CHARSET=</xsl:text><xsl:value-of select="$Encoding"/>
	    <xsl:text>:</xsl:text>
	</xsl:if>
	
	<xsl:for-each select=".//*[ancestor-or-self::*[name() = 'del'] = false() and contains(concat(' ', @class, ' '),concat(' ', $class, ' '))]">
		<xsl:choose>
			<xsl:when test='local-name(.) = "ol" or local-name(.) = "ul"'>
				<xsl:for-each select="*">
					<xsl:if test="not(position()=1)">
						<xsl:text>,</xsl:text>
					</xsl:if>
					<xsl:choose>
						<xsl:when test=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
							<xsl:for-each select=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
								<xsl:variable name="textFormatted">
								<xsl:apply-templates select="." mode="unFormatText" />
								</xsl:variable>
								<xsl:value-of select="normalize-space($textFormatted)"/>
							</xsl:for-each>
						</xsl:when>
						<xsl:otherwise>
							<xsl:variable name="textFormatted">
							<xsl:apply-templates select="." mode="unFormatText" />
							</xsl:variable>
							<xsl:value-of select="normalize-space($textFormatted)"/>
						</xsl:otherwise>
					</xsl:choose>		
				</xsl:for-each>
			</xsl:when>
			<xsl:when test='local-name(.) = "abbr" and @title'>
				<xsl:variable name="textFormatted">
				<xsl:apply-templates select="@title" mode="unFormatText" />
				</xsl:variable>
				<xsl:value-of select="normalize-space($textFormatted)"/>
			</xsl:when>
			<xsl:when test='@alt and (local-name(.) = "img" or local-name(.) = "area")'>
				<xsl:variable name="textFormatted">
				<xsl:apply-templates select="@alt" mode="unFormatText" />
				</xsl:variable>
				<xsl:value-of select="normalize-space($textFormatted)"/>
			</xsl:when>
			<xsl:when test=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
				<xsl:for-each select=".//*[contains(concat(' ', normalize-space(@class), ' '),' value ')]">
					<xsl:variable name="textFormatted">
					<xsl:apply-templates select="." mode="unFormatText" />
					</xsl:variable>
					<xsl:value-of select="normalize-space($textFormatted)"/>
				</xsl:for-each>
			</xsl:when>
			<xsl:otherwise>
				<xsl:variable name="textFormatted">
				<xsl:apply-templates select="." mode="unFormatText" />
				</xsl:variable>
				<xsl:value-of select="normalize-space($textFormatted)"/>
			</xsl:otherwise>
		</xsl:choose>	
		<xsl:if test="not(position()=last())">
			<xsl:text>,</xsl:text>
		</xsl:if>
	</xsl:for-each>
</xsl:template>

<!-- RELATED-TO property -->
<xsl:template match="*[contains(@class,'related-to')]" mode="related-to">
<xsl:text>
RELATED-TO</xsl:text>
<xsl:if test="@rel != ''">
<xsl:text>;</xsl:text><xsl:value-of select="@rel"/>
</xsl:if>
<xsl:text>:</xsl:text>
<xsl:choose>
	<xsl:when test="@longdesc != ''">
		<xsl:call-template name="escapeText">
			<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@longdesc)" /></xsl:with-param>
		</xsl:call-template>
	</xsl:when>
	<xsl:when test="@alt != ''">
		<xsl:call-template name="escapeText">
			<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@alt)" /></xsl:with-param>
		</xsl:call-template>
	</xsl:when>
	<xsl:when test="@title != ''">
		<xsl:call-template name="escapeText">
			<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@title)" /></xsl:with-param>
		</xsl:call-template>
	</xsl:when>
	<xsl:otherwise>
		<xsl:call-template name="escapeText">
			<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(.)" /></xsl:with-param>
		</xsl:call-template>
	</xsl:otherwise>
</xsl:choose>
</xsl:template>

<!-- URL property -->
<xsl:template match="*[contains(@class,'url')]" mode="url">
<xsl:text>
URL</xsl:text>
<xsl:choose>
	<xsl:when test="@href != ''">
			<xsl:choose>
			<xsl:when test="substring-before(@href,':') = true()">
				<xsl:text>:</xsl:text>
				<xsl:value-of select="@href" />
			</xsl:when>
			<xsl:when test="@href != ''">
				<xsl:text>:</xsl:text>
				<!-- convert to absolute url -->
				<xsl:call-template name="uri:expand">
					<xsl:with-param name="base"><xsl:value-of select="$Source" /></xsl:with-param>
					<xsl:with-param name="there"><xsl:value-of select="@href"/></xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:text>:</xsl:text>
				<xsl:value-of select="normalize-space(.)"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:when>
	<xsl:when test="@longdesc != ''">
			<xsl:choose>
			<xsl:when test="substring-before(@longdesc,':') = true()">
				<xsl:text>:</xsl:text>
				<xsl:value-of select="@href" />
			</xsl:when>
			<xsl:when test="@longdesc != ''">
				<xsl:text>:</xsl:text>
				<!-- convert to absolute url -->
				<xsl:call-template name="uri:expand">
					<xsl:with-param name="base" ><xsl:value-of select="$Source" /></xsl:with-param>
					<xsl:with-param name="there" ><xsl:value-of select="@longdesc" /></xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:text>:</xsl:text>
				<xsl:value-of select="normalize-space(.)"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:when>
	<xsl:when test="@alt != ''">
		<xsl:call-template name="escapeText">
			<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@alt)" /></xsl:with-param>
		</xsl:call-template>
	</xsl:when>
	<xsl:when test="@title != ''">
		<xsl:call-template name="escapeText">
			<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(@title)" /></xsl:with-param>
		</xsl:call-template>
	</xsl:when>
	<xsl:otherwise>
		<xsl:call-template name="escapeText">
			<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(.)" /></xsl:with-param>
		</xsl:call-template>
	</xsl:otherwise>
</xsl:choose>
</xsl:template>

<!-- ATTACH property -->
<xsl:template match="*[contains(@class,'attach')]" mode="attach">
<xsl:text>
ATTACH</xsl:text>

<xsl:choose>
	<xsl:when test="@href != ''">
		<xsl:if test="@type">
			<xsl:text>;FMTTYPE=</xsl:text><xsl:value-of select="@type"/>
		</xsl:if>
		<xsl:choose>
			<xsl:when test="substring-before(@href,':') = 'http'">
				<xsl:text>:</xsl:text><xsl:value-of select="@href" />
			</xsl:when>
			<xsl:when test="substring-before(@href,':') = 'data'">
				<xsl:text>;ENCODING=BASE64;VALUE=BINARY:</xsl:text><xsl:value-of select="substring-after(@src,',')"/>
			</xsl:when>
			<xsl:when test="@href != ''">
				<!-- probably need to make this absolute ONLY if no other protocol -->
				<xsl:text>:</xsl:text>
				<xsl:value-of select="@href"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:text>:</xsl:text><xsl:value-of select="normalize-space(.)"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:when>
	<xsl:when test="@src != ''">
		<xsl:choose>
			<xsl:when test="substring-before(@src,':') = 'http'">
				<xsl:text>:</xsl:text><xsl:value-of select="@src" />
			</xsl:when>
			<xsl:when test="substring-before(@src,':') = 'data'">
				<xsl:text>ENCODING=BASE64;VALUE=BINARY:</xsl:text><xsl:value-of select="substring-after(@src,',')"/>
			</xsl:when>
			<xsl:when test="@src != ''">
				<xsl:text>;VALUE=</xsl:text>
				<!-- convert to absolute url -->
				<xsl:call-template name="uri:expand">
					<xsl:with-param name="base" ><xsl:value-of select="$Source"/></xsl:with-param>
					<xsl:with-param name="there" ><xsl:value-of select="@src"/></xsl:with-param>
				</xsl:call-template>
				</xsl:when>
			<xsl:otherwise>
				<xsl:text>:</xsl:text><xsl:value-of select="normalize-space(.)"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:when>
	<xsl:otherwise>
		<xsl:text>:</xsl:text><xsl:value-of select="normalize-space(.)" />
	</xsl:otherwise>
</xsl:choose>
</xsl:template>

<!-- UID property-->
<!--
<xsl:template match="@id" mode="uid">
<xsl:text>
UID:</xsl:text>
<xsl:call-template name="escapeText">
	<xsl:with-param name="text-string"><xsl:value-of select="normalize-space(.)" /></xsl:with-param>
</xsl:call-template>
</xsl:template>
-->

<!-- recursive function to escape text -->
<xsl:template name="escapeText">
	<xsl:param name="text-string"></xsl:param>
	<xsl:variable name="nl">&#x0A;</xsl:variable>
	<xsl:choose>
		<xsl:when test="substring($text-string,2) = true()">
			<xsl:choose>
				<xsl:when test="substring($text-string,1,1) = '\'">
					<xsl:text>\\</xsl:text>
					<xsl:call-template name="escapeText">
						<xsl:with-param name="text-string"><xsl:value-of select="substring($text-string,2)"/></xsl:with-param>
					</xsl:call-template>
				</xsl:when>
				<xsl:when test="substring($text-string,1,1) = ','">
					<xsl:text>\,</xsl:text>
					<xsl:call-template name="escapeText">
						<xsl:with-param name="text-string"><xsl:value-of select="substring($text-string,2)"/></xsl:with-param>
					</xsl:call-template>
				</xsl:when>
				<xsl:when test="substring($text-string,1,1) = ';'">
					<xsl:text>\;</xsl:text>
					<xsl:call-template name="escapeText">
						<xsl:with-param name="text-string"><xsl:value-of select="substring($text-string,2)"/></xsl:with-param>
					</xsl:call-template>
				</xsl:when>
				<!-- New Line -->
				<!--
				<xsl:when test="substring($text-string,1,1) = $nl">
					<xsl:text>\n</xsl:text>
					<xsl:call-template name="escapeText">
						<xsl:with-param name="text-string"><xsl:value-of select="substring($text-string,2)"/></xsl:with-param>
					</xsl:call-template>
				</xsl:when>
				-->
				<xsl:otherwise>
					<xsl:value-of select="substring($text-string,1,1)"/>
					<xsl:call-template name="escapeText">
						<xsl:with-param name="text-string"><xsl:value-of select="substring($text-string,2)"/></xsl:with-param>
					</xsl:call-template>
				</xsl:otherwise>				
			</xsl:choose>
		</xsl:when>
		<xsl:otherwise>
			<xsl:value-of select="$text-string"/>			
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>

<!-- Get the language for an property -->
<xsl:template name="lang">
	<xsl:variable name="langElt" select='ancestor-or-self::*[@xml:lang or @lang]' />
	<xsl:if test="$langElt">
		<xsl:variable name="lang">
			<xsl:choose>
				<xsl:when test="$langElt[last()]/@xml:lang">
					<xsl:value-of select="normalize-space($langElt[last()]/@xml:lang)" />
				</xsl:when>
				<xsl:when test="$langElt[last()]/@lang">
					<xsl:value-of select="normalize-space($langElt[last()]/@lang)" />
				</xsl:when>
				<xsl:otherwise>
					<xsl:message>where id lang and xml:lang go?!?!?</xsl:message>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>
		<xsl:text>;LANGUAGE=</xsl:text>
		<xsl:value-of select="$lang" />
	</xsl:if>
</xsl:template>

<!-- recursive function to extract headers="id id id" -->
<xsl:template name="extract-ids">
<xsl:param name="text-string"/>
<xsl:choose>
	<xsl:when test="substring-before($text-string,' ') = true()">
		<xsl:call-template name="get-header">
			<xsl:with-param name="header-id"><xsl:value-of select="substring-before($text-string,' ')"/></xsl:with-param>
		</xsl:call-template>
		<xsl:call-template name="extract-ids">
			<xsl:with-param name="text-string"><xsl:value-of select="substring-after($text-string,' ')"/></xsl:with-param>
		</xsl:call-template>
	</xsl:when>
	<xsl:otherwise>
		<xsl:call-template name="get-header">
			<xsl:with-param name="header-id"><xsl:value-of select="$text-string"/></xsl:with-param>
		</xsl:call-template>
	</xsl:otherwise>
</xsl:choose>
</xsl:template>

<xsl:template name="get-header">
	<!-- problem here! need to pass the tag WITH the id, not decendants -->
	<xsl:param name="header-id"/>
	<xsl:for-each select="//*[@id=$header-id]">
		<xsl:call-template name="veventProperties">
	<!--		<xsl:with-param name="Anchor"><xsl:value-of select="$header-id"/></xsl:with-param> -->
		</xsl:call-template>
	</xsl:for-each>
</xsl:template>

<!-- recursive function to give plain text some equivalent HTML formatting -->
<xsl:template match="*" mode="unFormatText">
	<xsl:for-each select="node()">
		<xsl:choose>

			<xsl:when test="name() = 'p'">
				<xsl:apply-templates select="." mode="unFormatText"/>
				<xsl:text>\n\n</xsl:text>
			</xsl:when>
			<xsl:when test="name() = 'del'"></xsl:when>
			
			<xsl:when test="name() = 'div'">
				<xsl:apply-templates select="." mode="unFormatText"/>
				<xsl:text>\n</xsl:text>
			</xsl:when>
			<xsl:when test="name() = 'dl' or name() = 'dt' or name() = 'dd'">
				<xsl:apply-templates select="." mode="unFormatText"/>
				<xsl:text>\n</xsl:text>
			</xsl:when>
			<xsl:when test="name() = 'q'">
				<xsl:text>“</xsl:text>
				<xsl:apply-templates select="." mode="unFormatText"/>
				<xsl:text>”</xsl:text>
				<xsl:text>\n</xsl:text>
			</xsl:when>
			<xsl:when test="name() = 'sup'">
				<xsl:text>[</xsl:text>
				<xsl:apply-templates select="." mode="unFormatText"/>
				<xsl:text>]</xsl:text>
			</xsl:when>
			<xsl:when test="name() = 'sub'">
				<xsl:text>(</xsl:text>
				<xsl:apply-templates select="." mode="unFormatText"/>
				<xsl:text>)</xsl:text>
			</xsl:when>
			<xsl:when test="name() = 'ul' or name() = 'ol'">
				<xsl:apply-templates select="." mode="unFormatText"/>
				<xsl:text>\n</xsl:text>
			</xsl:when>
			<xsl:when test="name() = 'li'">
				<xsl:choose>
					<xsl:when test="name(..) = 'ol'">
						<xsl:number format="1. " />
						<xsl:apply-templates select="." mode="unFormatText"/>
						<xsl:text>\n</xsl:text>
					</xsl:when> 
					<xsl:otherwise> 
						<xsl:text>* </xsl:text>
						<xsl:apply-templates select="." mode="unFormatText"/>
						<xsl:text>\n</xsl:text>
					</xsl:otherwise> 
				</xsl:choose>
			</xsl:when>
			<xsl:when test="name() = 'pre'">
				<xsl:call-template name="escapeText">
					<xsl:with-param name="text-string">
						<xsl:value-of select="."/>
					</xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:when test="name() = 'br'">
				<xsl:text>\n</xsl:text>
			</xsl:when>
			<xsl:when test="name() = 'h1' or name() = 'h2' or name() = 'h3' or name() = 'h4' or name() = 'h5' or name() = 'h6'">
				<xsl:apply-templates select="." mode="unFormatText"/>				
				<xsl:text>\n</xsl:text>
			</xsl:when>
			<xsl:when test="descendant::*">
				<xsl:apply-templates select="." mode="unFormatText"/>
			</xsl:when>
			<xsl:when test="text()">
				<xsl:call-template name="normalize-spacing">
					<xsl:with-param name="text-string">
						<xsl:call-template name="escapeText">
							<xsl:with-param name="text-string">
								<xsl:value-of select="."/>
							</xsl:with-param>
						</xsl:call-template>
					</xsl:with-param>
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>				
				<xsl:choose>
					<!--
					<xsl:when test="normalize-space(.) = '' and not(contains(.,' '))"><xsl:text>^</xsl:text></xsl:when>-->
					<xsl:when test="contains(.,' ') and normalize-space(.) = ''">
						
						<xsl:text> </xsl:text>
					</xsl:when>
					<xsl:when test="substring(.,1,1) = $tb or substring(.,1,1) = ' '">
						<xsl:text> </xsl:text>
						<xsl:choose>
							<xsl:when test="substring(.,string-length(.),1) = $tb or substring(.,string-length(.),1) = ' '">
								<xsl:value-of select="normalize-space(.)"/>
								<xsl:text> </xsl:text>	
							</xsl:when>	
							<xsl:otherwise>
								<xsl:value-of select="normalize-space(.)"/>
							</xsl:otherwise>						
						</xsl:choose>
					</xsl:when>
					<xsl:when test="substring(.,string-length(.),1) = $tb or substring(.,string-length(.),1) = ' '">
						<xsl:value-of select="normalize-space(.)"/>
						<xsl:text> </xsl:text>
					</xsl:when>
					<xsl:otherwise>
						
						<!--
						<xsl:call-template name="normalize-spacing">
							<xsl:with-param name="text-string">
						-->
								<xsl:call-template name="escapeText">
									<xsl:with-param name="text-string">
										<xsl:value-of select="translate(translate(.,$tb,' '),$nl,' ')"/>
									</xsl:with-param>
								</xsl:call-template>
						<!--
							</xsl:with-param>
						</xsl:call-template>
					-->
					</xsl:otherwise>
				</xsl:choose>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:for-each>

</xsl:template>

<!-- recursive function to normalize-spacing in text -->
<xsl:template name="normalize-spacing">
	<xsl:param name="text-string"></xsl:param>
	<xsl:param name="colapse-spacing">1</xsl:param>
	<xsl:choose>
		<xsl:when test="substring($text-string,2) = true()">
			<xsl:choose>
				<xsl:when test="$colapse-spacing = '1'">
					<xsl:choose>
						<xsl:when test="substring($text-string,1,1) = ' ' or substring($text-string,1,1) = '$tb' or substring($text-string,1,1) = '$cr' or substring($text-string,1,1) = '$nl'">
							<xsl:text> </xsl:text>
							<xsl:call-template name="normalize-spacing">
								<xsl:with-param name="text-string"><xsl:value-of select="substring($text-string,2)"/></xsl:with-param>
								<xsl:with-param name="colapse-spacing">1</xsl:with-param>
							</xsl:call-template>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="normalize-space(substring($text-string,1,1))"/>
							<xsl:call-template name="normalize-spacing">
								<xsl:with-param name="text-string"><xsl:value-of select="substring($text-string,2)"/></xsl:with-param>
								<xsl:with-param name="colapse-spacing">0</xsl:with-param>
							</xsl:call-template>							
						</xsl:otherwise>
					</xsl:choose>
				</xsl:when>
				<xsl:otherwise>
					<xsl:choose>
						<xsl:when test="substring($text-string,1,1) = ' ' or substring($text-string,1,1) = '$tb' or substring($text-string,1,1) = '$cr' or substring($text-string,1,1) = '$nl'">
							<xsl:text> </xsl:text>
							<xsl:call-template name="normalize-spacing">
								<xsl:with-param name="text-string"><xsl:value-of select="substring($text-string,2)"/></xsl:with-param>
								<xsl:with-param name="colapse-spacing">1</xsl:with-param>
							</xsl:call-template>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="normalize-space(substring($text-string,1,1))"/>
							<xsl:call-template name="normalize-spacing">
								<xsl:with-param name="text-string"><xsl:value-of select="substring($text-string,2)"/></xsl:with-param>
								<xsl:with-param name="colapse-spacing">0</xsl:with-param>
							</xsl:call-template>							
						</xsl:otherwise>
					</xsl:choose>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:when>		
			
		<xsl:otherwise>
			<xsl:choose>
				<xsl:when test="$colapse-spacing = '1'">
					<xsl:value-of select="normalize-space($text-string)"/>			
				</xsl:when>
				<xsl:when test="substring($text-string,1,1) = ' '">
					<xsl:text> </xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="normalize-space($text-string)"/>			
				</xsl:otherwise>
			</xsl:choose>
		</xsl:otherwise>		
	</xsl:choose>

</xsl:template>

<!-- don't pass text thru -->
<xsl:template match="text()"></xsl:template>
</xsl:stylesheet>
