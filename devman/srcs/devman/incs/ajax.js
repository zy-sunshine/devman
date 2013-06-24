function changeday(){
	window.location=document.getElementById("daylist").value;	
}
function gopage(total){
	var curlurl = document.URL
	var urllist = curlurl.split('?');
	var pagestr = document.getElementById("page").value
	var page = parseInt(pagestr);	
	if (isNaN(page)){
		page = 1;
	}else{
		if(page>total){
			page = total;
		}else if(page<1){
		    page = 1;
		}
	}
	if(location.search.indexOf('page')>-1){
		var page_start_index = curlurl.indexOf('page');
		var page_end_string = curlurl.substring(page_start_index, curlurl.length)
		if(page_end_string.indexOf(";")>-1){
			page_end_index = page_start_index + curlurl.substring(page_start_index, curlurl.length).indexOf(";");
		}else{
			page_end_index = curlurl.length
		}
		window.location.href = curlurl.substring(0, page_start_index) + 'page='+ page + curlurl.substring(page_end_index, curlurl.length);
	}else{
		if (urllist.length == 1){
			window.location.href = curlurl + '?page='+page;
		
		}else{
			window.location.href = curlurl + ';page='+page;		
		}
	}
}
function clickpage(page){
	var curlurl = document.URL
	var urllist = curlurl.split('?');
	if(location.search.indexOf('page')>-1){
		var page_start_index = curlurl.indexOf('page');
		var page_end_string = curlurl.substring(page_start_index, curlurl.length)
		if(page_end_string.indexOf(";")>-1){
			page_end_index = page_start_index + curlurl.substring(page_start_index, curlurl.length).indexOf(";");
		}else{
			page_end_index = curlurl.length;
		}
		window.location.href = curlurl.substring(0, page_start_index) + 'page='+ page + curlurl.substring(page_end_index, curlurl.length);
	}else{
		if (urllist.length == 1){
			window.location.href = curlurl + '?page='+page;
		
		}else{
			window.location.href = curlurl + ';page='+page;		
		}
	}
}

function setColor(){
        document.getElementById("BUG_STATUS").style.backgroundColor='white';
}

function setEdited(id,baseurl,edited){
	var trs = document.getElementById(id).elements;
	for(var i=3;i<trs.length;i++){
		if(i != (parseInt(edited.substring(1,edited.length-1))+3))
		trs[i].readOnly = false;		
	}
}

function setSaved(id,baseurl){
	var form = document.getElementById(id);
	form.action = baseurl+'/editaction/'+id;
	form.submit();
}

function unSaved(id){
	var form = document.getElementById(id);
	form.submitBtn.disabled = false
}

function setDeleted(id,baseurl){
	var form = document.getElementById(id);
        form.action = baseurl+'/delaction/'+id;
	form.submit();	
}

function checkEmpty(){
        if(document.getElementById("BUG_TITLE").value ==""){
            alert("empty title is not allowed");
            return false;
        }
        return true;
}

function parentSelect(parent,related){
	var selIndex = 0
	var partag = parent[parent.selectedIndex].value.split('_')[1];
	parent[parent.selectedIndex].style.color = "menutext"; 
	for(var i=0;i < related.length;i++) {		
		subtag = related[i].value.split('_')[0];
		if( partag == subtag){
			related[i].disabled = false
			related[i].style.color = "menutext"; 
			selIndex = i
		}else{
			related[i].disabled = true
			related[i].style.color = "graytext"; 
		}		
	}
	related.selectedIndex  = selIndex
}

function subSelect(sub,related){
	var selIndex = 0	
	var subtag = sub[sub.selectedIndex].value.split('_')[0];
	for(var i=0;i < sub.length;i++){
		sub[i].style.color = "graytext";	
	}
	sub[sub.selectedIndex].style.color = "menutext"; 
	for(var i=0;i < related.length;i++) {		
		partag = related[i].value.split('_')[1];
		if( partag == subtag){
//			related[i].disabled = false
//			related[i].style.color = "menutext"; 
			selIndex = i
		}else{
//			related[i].disabled = true
//			related[i].style.color = "graytext"; 
		}		
	}
	related.selectedIndex  = selIndex;
}

function chgColor(select){
	select.style.background = select[select.selectedIndex].style.background;
}

window.onload = function(){
	if(document.getElementById('filters')!=null){
		url = document.URL.replace(/%20/g, " ");
		document.getElementById('filters').value = url;
	}
	if(document.getElementById('module')==null){
		document.getElementById('attr').value = '';
	}else{
		if(location.search.indexOf('?')>-1){
			var params = location.search.split(';')
			var project_index = params[0].indexOf('=') + 1
			var module_index = params[1].indexOf('=') + 1
			document.getElementById('module').value = params[1].substring(module_index,params[1].length)
			if(location.search.indexOf(';attr')>-1){
				var attr_index = params[2].indexOf('=') + 1
				document.getElementById('attr').value = params[2].substring(attr_index,params[2].length)	
			}
		}
	}	
}

function getModuleParams(project,url){
	var module = document.getElementById('module').value;
	window.location.href = url+'?project='+project+';module='+module+';attr=';	
}

function chgAttrsParams(project, url){
	var module = document.getElementById('module').value;
	var attr = document.getElementById('attr').value;
	var params = document.URL.split('?')[1];	
	window.location.href = url+'?project='+project+';module='+module+';attr='+attr;
}

function saveModuleParams(project, url){
	var form = document.getElementById('myModuleForm');
	var module = document.getElementById('module').value;
	var attr = document.getElementById('attr').value;
	form.action = url+'/proj/params/saveaction'+'?project='+project+';module='+module+';attr='+attr;
	form.submit();
}

function editProjDetail(url){
	var cururl = url+'/task/projplan/details/edit?'
	var params = document.URL.split('?')[1];
	window.location.href = cururl + params;
}

function saveProjDetail(url){
	var form = document.getElementById('myProjForm');
	var cururl = url+'/task/projplan/details/save?'
	var params = document.URL.split('?')[1];
	form.action = cururl + params;
	form.submit();
}

function sortTable(value){
	if (value == 'link'){
		return;
	}
	var curlurl = document.URL
	var urllist = curlurl.split('?');
	if(location.search.indexOf('sort')>-1){
		var column_index = curlurl.indexOf('sort');
		var type_index = curlurl.indexOf('orderby')+'orderby'.length+1;
		var orderby = curlurl.substring(type_index, type_index+1)
		if (location.search.indexOf(value)>-1 ){
			if(parseInt(orderby)==0){
				orderby = 1;
			}else{
				orderby = 0;
			}
		}else{
			orderby = 0;
		}
		window.location.href = curlurl.substring(0, column_index)+ 'sort='+ value + ';orderby='+orderby;		
	}else{
		if (urllist.length == 1){
			window.location.href = curlurl + '?sort='+value + ';orderby=0';
		
		}else{
			window.location.href = curlurl + ';sort='+value + ';orderby=0';		
		}		
	}		
}

function checkAll(){
	var selTag = document.getElementsByName('selTag'); 
	var elems = document.list.elements;
	for(var i=0; i< elems.length; i++){
		if(elems[i].type=='checkbox'){
			if(!elems[i].checked&&selTag[0].checked){
				elems[i].checked = true;
			}
			if(elems[i].checked&&!selTag[0].checked){
				elems[i].checked = false;
			}
		}
	}
   
}

function viewAxure(url){
	var isIe=(document.all)?true:false;
	if(isIe) {
		var linka = document.createElement('a');
		linka.href=url;
		document.body.appendChild(linka);
		linka.click();
	}else {
		window.location = url;
	}
}

function showResolution(selhtml){
	selvalue = selhtml.value;
	if(selvalue=='resolved'){
		document.getElementsByName('resolutions')[0].style.display = '';	
	}else{
		document.getElementsByName('resolutions')[0].style.display = 'none';	
	}
	
}

function chgProject(project){

	var curlurl = document.URL.split('?')[0];
	if(document.URL.indexOf('index=')==-1){
		window.location.href = curlurl+'?project='+project;
	}else{
		window.location.href = curlurl+'?project='+project+';index=WikiStart'

	}	
}

function goParamsRows(rows){
	var curlurl = document.URL
	var urllist = curlurl.split('?');
	if(location.search.indexOf('rows')>-1){
		var rows_start_index = curlurl.indexOf('rows');
		var rows_end_string = curlurl.substring(rows_start_index, curlurl.length)
		if(rows_end_string.indexOf(";")>-1){
			rows_end_index = rows_start_index + curlurl.substring(rows_start_index, curlurl.length).indexOf(";");
		}else{
			rows_end_index = curlurl.length
		}
		window.location.href = curlurl.substring(0, rows_start_index) + 'rows='+ rows + curlurl.substring(rows_end_index, curlurl.length);
	}else{
		if (urllist.length == 1){
			window.location.href = curlurl + '?rows='+rows;
		
		}else{
			window.location.href = curlurl + ';rows='+rows;		
		}
	}	
}

