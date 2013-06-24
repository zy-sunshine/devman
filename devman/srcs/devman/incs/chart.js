function ColumnChart(chartContainerId,chartId)
{
this.chartHeight = 300;
this.chartWidth = 800;

this.chartBorderStyle = "solid";
this.chartBorderColor = "gray";
this.chartBackground = "#E3EDCD";

this.columnBorderStyle = "solid";
this.columnBorderColor = "#B3B3DC";
this.columnBackground = "#DCDCF4";

this.levelLineColor = "#B9B9B9";
this.levelLineStyle = "dotted";

this.textAlign = "center";
this.textFontSize = "10";
this.textColor = "#000000";

var cols = new Array();
var lines = new Array();
var maxHeight = 0;
var isIe = true;

this.create = function(colHeights,topTexts,bottomTexts,levelLinePoss,levelLineTexts,sortHeights)
{
heightRatio = this.chartHeight*0.6/sortHeights[sortHeights.length-1];
widthRatio = this.chartWidth/sortHeights.length;
this.chartBorderWidth = 1;
this.columnBorderWidth = 1;
this.levelLineThickness = 1;
this.columnWidth = 0.6*widthRatio;
createColumns(colHeights,topTexts,bottomTexts);


if(levelLinePoss != null)
createLevelLines(levelLinePoss,levelLineTexts);

if(document.styleSheets.length == 0)
{
var styleTag = document.createElement("style");
styleTag.setAttribute("type","text/css");
document.getElementsByTagName("head")[0].appendChild(styleTag);
}

var styleSheet = document.styleSheets[0];

var rules = styleSheet.rules;
if(rules == null)
{
rules = styleSheet.cssRules;
isIe = false;
}

var chartClass = chartId + "Class";
if(isIe)
styleSheet.addRule("." + chartClass," ");
else
styleSheet.insertRule("." + chartClass + " {}",rules.length);

var rule = rules[rules.length - 1];
rule.style.position = "relative";
rule.style.margin = "0 auto"
rule.style.background = this.chartBackground;
rule.style.borderWidth = this.chartBorderWidth + "px";
rule.style.borderColor = this.chartBorderColor;
rule.style.borderStyle = this.chartBorderStyle;
var chartWidth = cols.length * (2 * this.columnBorderWidth + this.columnWidth);
if(chartWidth < this.chartWidth)
chartWidth = this.chartWidth;
rule.style.width = this.chartWidth + "px";
rule.style.height = this.chartHeight + 10 + "px";

if(isIe)
styleSheet.addRule("." + chartClass + " div.col"," ");
else
styleSheet.insertRule("." + chartClass + " div.col {}",styleSheet.cssRules.length);
rule = rules[rules.length - 1];
rule.style.position = "absolute";
rule.style.background = this.columnBackground;
rule.style.borderWidth = this.columnBorderWidth + "px";
rule.style.borderColor = this.columnBorderColor;
rule.style.borderStyle = this.columnBorderStyle;
rule.style.width = this.columnWidth + "px";
rule.style.bottom = "0px";

if(isIe)
styleSheet.addRule("." + chartClass + " div.line"," ");
else
styleSheet.insertRule("." + chartClass + " div.line {}",styleSheet.cssRules.length);
rule = rules[rules.length - 1];
rule.style.position = "absolute";
rule.style.borderTopColor = this.levelLineColor;
rule.style.borderTopWidth = this.levelLineThickness + "px";
rule.style.borderTopStyle = this.levelLineStyle;
rule.style.width = (chartWidth -  this.chartBorderWidth) + "px";
rule.style.left = "0px";

if(isIe)
styleSheet.addRule("." + chartClass + " div.text"," ");
else
styleSheet.insertRule("." + chartClass + " div.text {}",styleSheet.cssRules.length);
rule = rules[rules.length - 1];
rule.style.position = "absolute";
rule.style.textAlign = this.textAlign;
rule.style.fontSize = this.textFontSize + "px";
rule.style.color = this.textColor;

var chart = document.createElement("div");
chart.id = chartId;
document.getElementById(chartContainerId).appendChild(chart);
chart.className = chartClass;

var left = 0;
var colWidth = this.columnWidth + 2 * this.columnBorderWidth;
for(i = 0; i < cols.length; i ++)
{
var colHeight = heightRatio*cols[i].height
var col = document.createElement("div");
col.className = "col";
col.style.height = colHeight + "px";
left = i * widthRatio
col.style.left = left + "px";
chart.appendChild(col);

if(cols[i].topText != "")
chart.appendChild(createText(cols[i].topText,left,colHeight + 2,colWidth));   
if(cols[i].bottomText != "")
chart.appendChild(createText(cols[i].bottomText,left,-18,colWidth));           
}

for(i = 0; i < lines.length; i ++)
{
var line = document.createElement("div");
line.className = "line";
line.style.bottom = lines[i].position + "px";
chart.appendChild(line);

if(lines[i].text != "")
chart.appendChild(createText(lines[i].text,-30,lines[i].position - this.textFontSize/2,30));
}
};

function createText(text,left,bottom,width)
{
var txtDiv = document.createElement("div");
txtDiv.innerHTML = text;
txtDiv.className = "text";
txtDiv.style.left = left + "px";
txtDiv.style.bottom = bottom + "px";
if(width != null && width != "")
txtDiv.style.width = width + "px";
return txtDiv;
}

function createColumns(colHeights,topTexts,bottomTexts)
{
var tText = "";
var bText = "";
for(i = 0; i < colHeights.length; i ++)
{
if(topTexts != null && i < topTexts.length && topTexts[i] != null)
tText = topTexts[i];
if(bottomTexts != null && i < bottomTexts.length && bottomTexts[i] != null)
bText = bottomTexts[i];

if(colHeights[i] > maxHeight)
maxHeight = colHeights[i];

cols[i] = new Column(colHeights[i],tText,bText);
}

};

function createLevelLines(poss,texts)
{
var text = "";
for(i = 0; i < poss.length; i ++)
{
if(texts != null)
possHeight = heightRatio*poss[i]
if(possHeight > 300)
continue;
text = texts[i];
lines[i] = new LevelLine(possHeight,text);
}
}

function Column(colHeight,topText,bottomText)
{
this.height = colHeight;
this.topText = topText;
this.bottomText = bottomText;
}

function LevelLine(pos,text)
{
this.position = pos;
this.text = text;
}
}