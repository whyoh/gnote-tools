<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyz--'" />
<xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ/:'" />

	<!-- start with an identity - should be able to remove this eventually -->
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()"/>
		</xsl:copy>
	</xsl:template>
	
	<!-- skip the first line of text - it should be a repeat of the title -->
	<xsl:template match="*[local-name() = 'note-content' and namespace-uri() = 'http://beatniksoftware.com/tomboy']/text()[1]">
      <xsl:value-of select="substring-after(., '&#xA;')" />
		<xsl:apply-templates select="@*|node()"/>
	</xsl:template>

	<!-- construct the HTML page with title, styles and a heading -->
   <xsl:template match="/*[local-name() = 'note' and namespace-uri() = 'http://beatniksoftware.com/tomboy']">
   <html>
   <head>
   <title><xsl:value-of select="/*[local-name() = 'note' and namespace-uri() = 'http://beatniksoftware.com/tomboy']/*[local-name() = 'title' and namespace-uri() = 'http://beatniksoftware.com/tomboy']"/> - notes</title>
    <style>
    	body {
    		margin: 20px 100px;
    		font-family: sans-serif;
    		background: lightgrey;
    		color: #333;
    		white-space: pre-line;
    	}
    	h1 {
    		font-weight: normal;
    		margin-bottom: 0;
    	}
    	.item {
    		color: #444;
    		background: white;
    		padding: 20px;
    		margin-bottom: 10px;
    	}
    	.small {
    		font-size: 75%;
    	}
    	.large {
    		font-size: 125%;
    	}
    	.huge {
    		font-size: 150%;
    	}
    	.monospace {
    		font-family: monospace;
    	}
    	.highlight {
    		background: yellow;
    	}
    	a.broken {
    		color: red;
    	}
    	a.internal {
    		color: #26e;
    	}
    	.field {
    		color: #888;
    		font-size: 75%;
    		font-style: italic;
			text-align: right;
    	}
    	.fieldname {
    		font-weight: bold;
    		margin-right: 5px;
    	}
    	ul.field {
    		margin: 6px 0;
    	}
    	li.tag {
    		display: inline;
    		margin-left: 3px;
    		padding: 3px 7px;
    		border: 2px solid yellow;
    		background: orange;
    		border-radius: 8px;
    		box-shadow: 0 1px 2px grey;
    	}
    </style>
   </head><body>
	<xsl:apply-templates select="*"/>
	</body></html>
   </xsl:template>

	<xsl:template match="*[local-name() = 'title' and namespace-uri() = 'http://beatniksoftware.com/tomboy']">
	   <h1><xsl:value-of select="."/></h1> 
	</xsl:template>

	<!-- skip the text element (and its attributes) -->
	<xsl:template match="*[local-name() = 'text' and namespace-uri() = 'http://beatniksoftware.com/tomboy']">
		<xsl:apply-templates select="*"/>
	</xsl:template>

	<!-- put the content in a div but drop this element's attributes -->
	<xsl:template match="*[local-name() = 'note-content' and namespace-uri() = 'http://beatniksoftware.com/tomboy']">
		<div class="item"><xsl:apply-templates select="node()"/></div>
	</xsl:template>

	<!-- deal with links and formatting -->
	<xsl:template match="*[namespace-uri() = 'http://beatniksoftware.com/tomboy/link']">
		<a><xsl:attribute name='href'><xsl:choose><xsl:when test='local-name() != "url"'><xsl:value-of select='concat(translate(., $uppercase, $lowercase), ".xml")'/></xsl:when><xsl:otherwise><xsl:value-of select='.'/></xsl:otherwise></xsl:choose></xsl:attribute><xsl:attribute name='class'><xsl:value-of select='local-name()'/></xsl:attribute><xsl:apply-templates select="@*|node()"/></a>
	</xsl:template>

	<xsl:template match="*[(local-name() = 'bold' or local-name() = 'italic' or local-name() = 'strikethrough') and namespace-uri() = 'http://beatniksoftware.com/tomboy']">
		<xsl:element name='{substring(local-name(), 1, 1)}'><xsl:apply-templates select="@*|node()"/></xsl:element>
	</xsl:template>

	<xsl:template match="*[namespace-uri() = 'http://beatniksoftware.com/tomboy/size' or (local-name() = 'monospace' or local-name() = 'highlight') and namespace-uri() = 'http://beatniksoftware.com/tomboy']">
		<span><xsl:attribute name='class'><xsl:value-of select='local-name()'/></xsl:attribute><xsl:apply-templates select="@*|node()"/></span>
	</xsl:template>

	<xsl:template match="*[local-name() = 'list']">
		<ul><xsl:apply-templates select="@*|node()"/></ul>
	</xsl:template>

	<xsl:template match="*[local-name() = 'list-item']">
		<li><xsl:apply-templates select="@*|node()"/></li>
	</xsl:template>

	<!-- note metadata - FIXME would be nice to replace this with an 'everything else' match, put them all in a div and have a show/hide button for it -->
	<xsl:template match="*[(local-name() = 'last-change-date' or local-name() = 'create-date') and namespace-uri() = 'http://beatniksoftware.com/tomboy']">
		<div class='field'><span class='fieldname'><xsl:value-of select='local-name()'/></span><xsl:value-of select='.'/></div>
	</xsl:template>

	<xsl:template match="*[(local-name() = 'last-metadata-change-date' or local-name() = 'cursor-position' or local-name() = 'selection-bound-position' or local-name() = 'width' or local-name() = 'height' or local-name() = 'x' or local-name() = 'y' or local-name() = 'open-on-startup') and namespace-uri() = 'http://beatniksoftware.com/tomboy']">
	</xsl:template>

	<xsl:template match="*[local-name() = 'tags' and namespace-uri() = 'http://beatniksoftware.com/tomboy']">
		<ul class='field'><xsl:apply-templates select="@*|node()"/></ul>
	</xsl:template>

	<xsl:template match="*[local-name() = 'tag' and namespace-uri() = 'http://beatniksoftware.com/tomboy']">
		<li class='tag'><xsl:value-of select='.'/></li>
	</xsl:template>

</xsl:transform>
