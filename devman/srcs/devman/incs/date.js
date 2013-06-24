function HS_DateAdd(interval,number,date){
    number = parseInt(number);
    if (typeof(date)=="string"){var date = new Date(date.split("-")[0],date.split("-")[1],date.split("-")[2])}
    if (typeof(date)=="object"){var date = date}
    switch(interval){
    case "y":return new Date(date.getFullYear()+number,date.getMonth(),date.getDate()); break;
    case "m":return new Date(date.getFullYear(),date.getMonth()+number,checkDate(date.getFullYear(),date.getMonth()+number,date.getDate())); break;
    case "d":return new Date(date.getFullYear(),date.getMonth(),date.getDate()+number); break;
    case "w":return new Date(date.getFullYear(),date.getMonth(),7*number+date.getDate()); break;
    }
}
function checkDate(year,month,date){
    var enddate = ["31","28","31","30","31","30","31","31","30","31","30","31"];
    var returnDate = "";
    if (year%4==0){enddate[1]="29"}
    if (date>enddate[month]){returnDate = enddate[month]}else{returnDate = date}
    return returnDate;
}

function WeekDay(date){
    var theDate;
    if (typeof(date)=="string"){theDate = new Date(date.split("-")[0],date.split("-")[1],date.split("-")[2]);}
    if (typeof(date)=="object"){theDate = date}
    return theDate.getDay();
}
function HS_calender(){
    var lis = "";
    var now;
    if (typeof(arguments[0])=="string"){
        selectDate = arguments[0].split("-");
        var year = selectDate[0];
        var month = parseInt(selectDate[1])-1+"";
        var date = selectDate[2];
        now = new Date(year,month,date);
    }else if (typeof(arguments[0])=="object"){
        now = arguments[0];
    }
    var lastMonthEndDate = HS_DateAdd("d","-1",now.getFullYear()+"-"+now.getMonth()+"-01").getDate();
    var lastMonthDate = WeekDay(now.getFullYear()+"-"+now.getMonth()+"-01");
    var thisMonthLastDate = HS_DateAdd("d","-1",now.getFullYear()+"-"+(parseInt(now.getMonth())+1).toString()+"-01");
    var thisMonthEndDate = thisMonthLastDate.getDate();
    var thisMonthEndDay = thisMonthLastDate.getDay();
    var todayObj = new Date();
    today = todayObj.getFullYear()+"-"+todayObj.getMonth()+"-"+todayObj.getDate();
   
    for (i=0; i<lastMonthDate; i++){  // Last Month's Date
        lis = "<li class='lastMonthDate'>"+lastMonthEndDate+"</li>" + lis;
        lastMonthEndDate--;
    }
    for (i=1; i<=thisMonthEndDate; i++){ // Current Month's Date

        if(today == now.getFullYear()+"-"+now.getMonth()+"-"+i){
            var todayString = now.getFullYear()+"-"+(parseInt(now.getMonth())+1).toString()+"-"+i;
            lis += "<li><a href=javascript:void(0) class='today' onclick='_selectThisDay(this)' title='"+now.getFullYear()+"-"+(parseInt(now.getMonth())+1)+"-"+i+"'>"+i+"</a></li>";
        }else{
            lis += "<li><a href=javascript:void(0) onclick='_selectThisDay(this)' title='"+now.getFullYear()+"-"+(parseInt(now.getMonth())+1)+"-"+i+"'>"+i+"</a></li>";
        }
       
    }
    var j=1;
    for (i=thisMonthEndDay; i<6; i++){  // Next Month's Date
        lis += "<li class='nextMonthDate'>"+j+"</li>";
        j++;
    }

    var CalenderTitle = "<a href='javascript:void(0)' class='NextMonth' onclick=HS_calender(HS_DateAdd('m',1,'"+now.getFullYear()+"-"+now.getMonth()+"-"+now.getDate()+"'),this) title='Next Month'>&raquo;</a>";
    CalenderTitle += "<a href='javascript:void(0)' class='LastMonth' onclick=HS_calender(HS_DateAdd('m',-1,'"+now.getFullYear()+"-"+now.getMonth()+"-"+now.getDate()+"'),this) title='Previous Month'>&laquo;</a>";
    CalenderTitle += "<span class='selectThisYear'><a href='javascript:void(0)' onclick='CalenderselectYear(this)' title='Click here to select other year' >"+now.getFullYear()+"</a></span> -- <span class='selectThisMonth'><a href='javascript:void(0)' onclick='CalenderselectMonth(this)' title='Click here to select other month'>"+(parseInt(now.getMonth())+1).toString()+"</a></span>";

    if (arguments.length>1){
        arguments[1].parentNode.parentNode.getElementsByTagName("ul")[1].innerHTML = lis;
        arguments[1].parentNode.innerHTML = CalenderTitle;

    }else{
        var CalenderBox = "<div class='calender'><div class='calenderTitle'>"+CalenderTitle+"</div><div class='calenderBody'><ul class='day'><li>Sun</li><li>Mon</li><li>Tue</li><li>Wed</li><li>Thu</li><li>Fri</li><li>Sat</li></ul><ul class='date' id='thisMonthDate'>"+lis+"</ul></div><div class='calenderBottom'><a href='javascript:void(0)' class='closeCalender' onclick='closeCalender(this)'>Close</a><span><span><a href=javascript:void(0) onclick='_selectThisDay(this)' title='"+todayString+"'>Today</a></span></span></div></div>";
        return CalenderBox;
    }
}
function _selectThisDay(d){
    var boxObj = d.parentNode.parentNode.parentNode.parentNode.parentNode;
        boxObj.targetObj.value = d.title;
        boxObj.parentNode.removeChild(boxObj);
}
function closeCalender(d){
    var boxObj = d.parentNode.parentNode.parentNode;
        boxObj.parentNode.removeChild(boxObj);
}

function CalenderselectYear(obj){
        var opt = "";
        var thisYear = obj.innerHTML;
        for (i=1970; i<=2020; i++){
            if (i==thisYear){
                opt += "<option value="+i+" selected>"+i+"</option>";
            }else{
                opt += "<option value="+i+">"+i+"</option>";
            }
        }
        opt = "<select onblur='selectThisYear(this)' onchange='selectThisYear(this)' style='font-size:11px'>"+opt+"</select>";
        obj.parentNode.innerHTML = opt;
}

function selectThisYear(obj){
    HS_calender(obj.value+"-"+obj.parentNode.parentNode.getElementsByTagName("span")[1].getElementsByTagName("a")[0].innerHTML+"-1",obj.parentNode);
}

function CalenderselectMonth(obj){
        var opt = "";
        var thisMonth = obj.innerHTML;
        for (i=1; i<=12; i++){
            if (i==thisMonth){
                opt += "<option value="+i+" selected>"+i+"</option>";
            }else{
                opt += "<option value="+i+">"+i+"</option>";
            }
        }
        opt = "<select onblur='selectThisMonth(this)' onchange='selectThisMonth(this)' style='font-size:11px'>"+opt+"</select>";
        obj.parentNode.innerHTML = opt;
}
function selectThisMonth(obj){
    HS_calender(obj.parentNode.parentNode.getElementsByTagName("span")[0].getElementsByTagName("a")[0].innerHTML+"-"+obj.value+"-1",obj.parentNode);
}
function HS_setDate(inputObj){
    var calenderObj = document.createElement("span");
    calenderObj.innerHTML = HS_calender(new Date());
    calenderObj.style.position = "absolute";
    calenderObj.targetObj = inputObj;
    inputObj.parentNode.insertBefore(calenderObj,inputObj.nextSibling);
}
