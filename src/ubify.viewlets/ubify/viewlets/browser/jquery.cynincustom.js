jQuery.fn.log = function (msg) {
    console.log("%s: %o", msg, this);
    return this;
};
jQuery.fn.tagCloud = function(arrTagsForCloud){
    if (!arrTagsForCloud || !arrTagsForCloud.length)
        return new Array();

    var tagcloud_min = arrTagsForCloud[0].count;
    var tagcloud_max = -1;

    jq.each(arrTagsForCloud, function(i, n) {
        tagcloud_max = Math.max(n.count, tagcloud_max);
        tagcloud_min = Math.min(n.count,tagcloud_min);
    });

    var tagcloud_diff = ( tagcloud_max == tagcloud_min ? 1 : (tagcloud_max - tagcloud_min) / (5 - 1) );

    function getNormalizedSize(count) {
        return 1 + (count - tagcloud_min) / tagcloud_diff;
    }

    var arrTagsClasses = new Array();

    for (var i = 0; i < arrTagsForCloud.length; ++i) {
        var tag = arrTagsForCloud[i].tag;
        var tagclassname = 'tagcloudsize' + Math.round(getNormalizedSize(arrTagsForCloud[i].count));
        arrTagsClasses[i] = tagclassname;
    }

    return arrTagsClasses;
}

function limitChars(textid, limit, infodiv)
{
    var text = jq('#'+textid).val();
    var textlength = text.length;
    if(textlength > limit)
    {
        jq('#'+textid).val(text.substr(0,limit));
    }
    text = jq('#'+textid).val();
    textlength = text.length;
    var diff = limit - textlength;
    if (diff > 0)
        jq("#" + infodiv).html(diff);
    else
        jq("#" + infodiv).html("0");
    if (diff < (10/100) * limit)
    {
        jq("#" + infodiv).css("color","red");
    }
    else
    {
        jq("#" + infodiv).css("color","");
    }

}

    function centerloginbox()
    {
        loginboxheight = jq('.loginbox').height()/2;
        windowheight = jq().height()/2;
        logodivheight = jq('.loginboxlogo').height();
        logoimgheight = jq('.loginboxlogo img').height();
        if (logoimgheight < logodivheight)
        {
            jq('.loginboxlogo img').css({position:'relative',top:logodivheight/2 - logoimgheight/2 + 'px'});
        }
        jq('.loginbox').animate(
            {top:(windowheight) - (loginboxheight) + 'px'},500
            );
    }

function MarkSelectedListTags()
{
    jq(".listtag").each(function ()
        {
            if(window.currentselectedtags != undefined)
            {
                for (var i=0; i<currentselectedtags.length; i++)
                {
                    if (jq(this).attr("rel") == currentselectedtags[i])
                    {
                        jq(this).removeAttr("href");
                        jq(this).addClass("listtagselected");
                        jq(this).removeAttr("title");
                    }
                    else
                    {
                        jq(this).attr("href", curloc + delim + "Subject:list=" + jq(this).attr("rel"));
                    }
                }
            }
            else
            {
                jq(this).attr("href", curloc + delim + "Subject:list=" + jq(this).attr("rel"));
            }
        }
    );
}
function issuemessage(type, header, body){
    switch(type.toLowerCase())
    {
        case 'error':
            jq('#kssPortalMessage > dt').html(header);
            jq('#kssPortalMessage > dd').html(body);
            jq('#kssPortalMessage').removeClass('info').addClass('error').show();
            break;
        case 'info':
        default:
            jq('#kssPortalMessage > dt').html(header);
            jq('#kssPortalMessage > dd').html(body);
            jq('#kssPortalMessage').removeClass('error');
            if (! jq('#kssPortalMessage').hasClass('info')){jq('#kssPortalMessage').addClass('info');}
            jq('#kssPortalMessage').show();
            break;
    }
}

function renderComments(targetobjid,renderhtml,data){    
    targetobj = jq('#' + targetobjid);
    jq(renderhtml).find('div.commentBody.exec').removeClass('exec');    
    if (targetobj != undefined){
        var outputhtml = '';
        var temphtml = '';
        var viewtype = 'threadedview';
        if(!data){
            items = commentsdata.items;
            viewtype = commentsdata.view_type;
        }
        else{
            items = data.items;
            viewtype = data.view_type;
        }        
        
        if (items && items.length > 0){
            jq.each(items,function(i,item){
                var indentby = 0;
                indentby = Math.min(item.depth,10) * 10 + 'px';                
                jq(renderhtml).find("div:first").css('margin-left',indentby);
                temphtml = jq(renderhtml).html();
                temphtml = temphtml.replace(/%previd/g,item.prev_id).replace(/%id/g,item.id).replace(/%replyto/g,item.replytoid).replace(/%depth/g,item.depth).replace(/%mdate/g,item.mdate).replace(/%userinfourl/g,item.userinfourl).replace(/%useravatarurl/g,item.useravatarurl).replace(/%userid/g,item.userid).replace(/%permalink/g,item.permalink).replace(/%cookedtext/g,item.replycooked).replace(/%replyurl/g,item.replyurl);
                if (viewtype != 'threadedview'){
                    outputhtml += temphtml;   
                }
                else{
                    prevobjexists = jq('#commenttable' + item.prev_id).length > 0;                    
                    if (prevobjexists){
                        jq(temphtml).insertAfter('#commenttable' + item.prev_id);    
                    }
                    else{
                        jq(targetobj).append(temphtml);
                    }
                }               
            });
        }
        
        if(!data && outputhtml != ''){
            jq(targetobj).append(outputhtml);
        }
        else if(outputhtml != ''){
            if(data.removeallcomments == 'False'){
                if(data.marker_delete && data.marker_delete != ''){
                    jq('#' + data.marker_delete).prevAll().remove();    
                }                
            }
            else{
                jq(targetobj).html('');
            }            
            jq(targetobj).append(outputhtml);        
        }
    }
}
function nyroShowBackground(elts, settings, callback)
{
    elts.bg.css({opacity:.75});
    callback();
}
function nyroHideBackground(elts, settings, callback)
{
    elts.bg.css({opacity:0});
    callback();
}
function nyroShowLoading(elts, settings, callback) {
        elts.loading.show();
        callback();
}

function nyroShowContent(elts, settings, callback) {
        elts.loading.hide();
        elts.contentWrapper.css({
                                    marginTop: settings.marginTop+'px',
                                    marginLeft: settings.marginLeft+'px'
                                })
                                .show();
        callback();
}
function nyroHideContent(elts, settings, callback)
{
    elts.contentWrapper.hide();
    callback();
}

function processComments(data){
    idindex = jq('form[name=frmListerTimeout] #comcynapsecyninfetchindex').val();
    uid = jq('form[name=frmListerTimeout] #comcynapsecyninfetchUID').val();
    if (!idindex){
        id = '';
    }
    if (!uid){
        uid = jq("input[name=comcynapsecynincontextUID]").val();
    }
    if (data.timeoutuid && data.timeoutuid == uid){
        if (data.timeoutcommentcount){
            jq('form[name=frmListerTimeout] #comcynapsecommentcount, form[name=frmDiscussionAddNew] #comcynapsecommentcount' + id).val(data.timeoutcommentcount);
            jq('#discussionlabel').html(data.timeoutcommentcount);
        }
        if (data.timeoutlastcommentid){
            jq('form[name=frmListerTimeout] #comcynapselastcommentid,form[name=frmDiscussionAddNew] #comcynapselastcommentid' + id).val(data.timeoutlastcommentid);                           
        }
        if (data.timeouttimestamp){
            jq('form[name=frmListerTimeout] #comcynapselasttimestamp,form[name=frmDiscussionAddNew] #comcynapselasttimestamp' + id).val(data.timeouttimestamp);
        }
        if (id != ''){
            targetobjid = 'comcynapselistcommentscontainer' + id;    
        }
        else{
            targetobjid = 'comcynapsecyninitemcommentscontainer';
        }
        renderhtml = jq('#dummycommenttable').clone(true);
        if (data.canreply && data.canreply == 'False'){
            jq(renderhtml).find('form[name=reply]').css('display','none');
        }
        else if(data.canreply && data.canreply == 'True'){
            jq(renderhtml).find('form[name=reply]').css('display','inline');
        }
        renderComments(targetobjid,renderhtml,data);
        if(data.xmorecomments && data.xmorecomments != ''){                        
            jq('#listdiscussioncount' + id).html(data.xmorecomments);
            jq('#commentcountspan' + id + ' a').css('display','inline');
        }
        else if(data.xmorecomments && data.xmorecomments == ''){
            jq('#commentcountspan' + id + ' a').css('display','none');
        }
        if(data.shownocomments && data.shownocomments == 'False'){
            jq('.nocommentsyet').css('display','none');
            jq('#commentcountspan' + id).css('display','inline');
        }
        else if(data.shownocomments && data.shownocomments == 'True'){
            jq('.nocommentsyet').css('display','inline');
            jq('#commentcountspan' + id).css('display','none');
        }
    }     
}
jq(window).load(function(){
        centerloginbox();
    });

jq(document).ready(function() {
    //////////////////////////////////////////////////////////////////// Center the login box
        resizeTimer = null;
        jq(window).bind('resize', function()
        {
            if (resizeTimer) clearTimeout(resizeTimer);
            resizeTimer = setTimeout(centerloginbox, 100);
        });
    //////////////////////////////////////////////////////////////////// vertical navigation accordion begin
    jq("#verticalnavigation .accordionheader").click(function()
        {
            jq(this).toggleClass('expanded').next().slideToggle("fast");
        })
        .next().hide();


        if (window.currentaccordion != undefined)
        {
            jq('#verticalnavigation .' + window.currentaccordion).toggleClass('expanded').next().slideDown();
        }
        else
        {
            jq("#verticalnavigation .spaces").toggleClass('expanded').next().slideDown();
        }

//////////////////////////////////////////////////////////////////// vertical navigation accordion end
    /////////////////////////////////////////////Local Scroll Begin
    var location = window.location.href;
    var lasthash = location.lastIndexOf("#");
    if (lasthash > -1)
        location = location.substring(0, lasthash);

    var hashlink = jq("#AddCommentButtonLS").attr("href");
    jq("#AddCommentButtonLS").attr("href",location + hashlink);
    jq("#AddCommentButton").hide();
    jq("#AddCommentButtonLS").show();

    jq(".commentpermalink, a.purehashlink").each(function(i,o)
        {
            o.href=location + '#' + o.name;
        });
    jq("#discussionnamedlink").attr("href",location + "#discussion");
    jq("#rateitnamedlink").attr("href",location + "#rateit")

    jq.localScroll();
    /////////////////////////////////////////////Local Scroll End




/////////////////////////////////Cluetip begin
    jq('.cluetip').bt({activeClass:'cluetipTarget'
                        ,cssClass:'cluetips'
                        ,strokeStyle:'#beb510'
                        ,fill:'rgba(0,0,0,.7)'
                        ,spikeLength:7
                        ,spikeGirth:15
                        ,strokeWidth:0
                        ,cornerRadius:10
                        });
    jq('.navtip').bt({activeClass:'navtipTarget'
                        ,cssClass:'navtips'
                        ,strokeStyle:'#beb510'
                        ,fill:'rgba(0,0,0,.7)'
                        ,spikeLength:7
                        ,spikeGirth:15
                        ,strokeWidth:0
                        ,cornerRadius:10
                        ,closeWhenOthersOpen:true
                        ,positions:'right'});
    jq('.navtipleft').bt({activeClass:'navtipTarget'
                        ,cssClass:'navtips'
                        ,strokeStyle:'#beb510'
                        ,fill:'rgba(0,0,0,.7)'
                        ,spikeLength:7
                        ,spikeGirth:15
                        ,strokeWidth:0
                        ,cornerRadius:10
                        ,closeWhenOthersOpen:true
                        ,positions:'left'});
    jq('.navtipVertical').live('mouseover',function(event){
        event.preventDefault();
        jq(this).bt({
            cssStyles:{width:'auto'}
            ,cssClass:'navtips'
            ,strokeStyle:'#beb510'
            ,fill:'rgba(0,0,0,.7)'
            ,spikeLength:7
            ,spikeGirth:15
            ,strokeWidth:0
            ,cornerRadius:10
            ,closeWhenOthersOpen:true
            ,positions:'top'});
        jq(this).btOn();
    }).live('mouseout',function(event){
        event.preventDefault();        
        jq(this).btOff();
    });
    
    
    if (jq.support.opacity){
    jq('.textfieldtipBottom').bt({
                        cssStyles:{width:'auto'}
                        ,trigger:['focus click', 'blur']
                        ,cssClass:'navtips'
                        ,strokeStyle:'#beb510'
                        ,fill:'rgba(0,0,0,.7)'
                        ,spikeLength:7
                        ,spikeGirth:15
                        ,strokeWidth:0
                        ,cornerRadius:10
                        ,closeWhenOthersOpen:true
                        ,positions:'top'});
    jq('.cluetipnoie').bt({activeClass:'cluetipTarget'
                        ,cssClass:'cluetips'
                        ,strokeStyle:'#beb510'
                        ,fill:'rgba(0,0,0,.7)'
                        ,spikeLength:7
                        ,spikeGirth:15
                        ,strokeWidth:0
                        ,cornerRadius:10
                        });

    }
    else
    {
        jq('.textfieldtipBottom').attr('title',"")
    }
    jq('.calendartip').bt({
                        closeWhenOthersOpen:true
                        ,contentSelector:'jq(jq(this).attr("rel"))'
                        ,trigger:'click'
                        ,activeClass:'avatartipTarget'
                        ,cssClass:'avatartips'
                        ,cssStyles:{'min-height':'48px'}
                        ,strokeStyle:'#000000'
                        ,strokeWidth:0
                        ,fill:'rgba(0,0,0,.6)'
                        ,spikeLength:50
                        ,spikeGirth:30
                        ,centerPointX:.7
                        ,centerPointY:.1
                        ,cornerRadius:10
                        ,width:300
                        ,padding:'1em'
                        });
    jq('.avatarlink').live('click',function(event){
        event.preventDefault();
        jq(this).bt({closeWhenOthersOpen:true
                        ,trigger:'click'
                        ,activeClass:'avatartipTarget'
                        ,cssClass:'avatartips'
                        ,cssStyles:{'min-height':'48px'}
                        ,strokeStyle:'#000000'
                        ,strokeWidth:0
                        ,fill:'rgba(0,0,0,.6)'
                        ,spikeLength:50
                        ,spikeGirth:30
                        ,centerPointX:.7
                        ,centerPointY:.1
                        ,cornerRadius:10
                        ,ajaxPath:["jq(this).attr('rel')"]
                        ,ajaxError: "<div class='bterror'>"+msg_ajax_error+" <em>%error</em>.</div>"
                        ,ajaxLoading: '<div class="btspinner"><center><img src="/spinner-w-48.gif" /></center></div>'
                        ,ajaxCache:false
                        ,width:300
                        ,padding:'1em'
                        });
        jq(this).btOn();
        });    
    jq('.topbarmybuttontip').bt({closeWhenOthersOpen:true
                        ,trigger:'click'
                        ,activeClass:'avatartipTarget'
                        ,cssClass:'avatartips'
                        ,cssStyles:{'min-height':'48px'}
                        ,strokeStyle:'#000000'
                        ,strokeWidth:0
                        ,fill:'rgba(0,0,0,.6)'
                        ,spikeLength:7
                        ,spikeGirth:15
                        ,cornerRadius:10
                        ,ajaxPath:["jq(this).attr('rel')"]
                        ,ajaxError: "<div class='bterror'>"+msg_ajax_error+" <em>%error</em>.</div>"
                        ,ajaxLoading: '<div class="btspinner"><center><img src="/spinner-w-48.gif" /></center></div>'
                        ,ajaxCache:false
                        ,width:320
                        ,padding:'1em'
                        ,positions:'bottom'
                        });
/////////////////////////////////Cluetip end

////////////////////////////////////////// Bigger links begin
    jq(".biggerlink").biggerlink({follow:false});
    jq(".forcelink").biggerlink({follow:true});
////////////////////////////////////////// Bigger links end



/********************** Click Menu Begin **************************************************/
    jq.fn.clickMenu.setDefaults({arrowSrc:'arrow_right.gif',onClick:function(e){
        e.preventDefault();
        var obj = null;
        var n = this.firstChild;
        for ( ; n; n = n.nextSibling )
        {
            if ( n.nodeType == 1 && n.nodeName.toUpperCase() == 'A' )
            {
                obj = n;
                break;
            }
        }
        if (jq(obj).hasClass('nofollow')) return true;
        if (obj) window.location = obj ;
        return false;
    }});

    jq('.applications_menu').clickMenu();
    jq('.addnew_menu').clickMenu();
    jq('.help_menu').clickMenu();
    jq(".help_menu").attr("style","");
    jq(".titlebarmenurow").attr("style","");
    jq(".breadCrumbMenu").clickMenu();
    jq("#portal-breadcrumbs").removeClass("hidden");
/********************** Click Menu End **************************************************/

/////////////////////////////////Status Message begin
    jq('#statusinputtextarea').focus(function(event){
        if (!jq(this).hasClass('exec')){
            jq(this).autoResize({extraSpace:20,animateDuration:0,limit:400}).addClass('exec');
        }
        jq('#comcynapsesmessagetitle').val(jq(this).attr('title'));
        jq("#statusbuttontable").show();
    });
    jq("#comcynapsecynincancelstatusmessageinput").click(function(event){
       event.preventDefault();       
       jq("#statusbuttontable").hide();
       jq('#charleninfo').html("140").css('color','');
       jq('#statusinputtextarea').css("height","20px");
       triggerResetInputLabel(jq('#statusinputtextarea'));
       jq('#comcynapsemessageerror').hide();
    });
    jq(".statusmessageinput").keyup(function(){
        limitChars("statusinputtextarea", 140, "charleninfo");
        });
    jq("input[name=com.cynapse.cynin.statusmessagesubmit]").click(function(event){
        event.preventDefault();
        var smessage = jq.trim(jq("#statusinputtextarea").val());
        if(smessage == '' || smessage == jq("#statusinputtextarea").attr('title')){
            jq('#comcynapsemessageerror').show();
        }
        else{
            jq('#comcynapsemessageerror').hide();
            jq.ajax({
                type:"POST",
                url: 'setstatusmessage',
                data: jq('#comcynapsecyninstatusmessageinputform').serialize(),
                success: function(data){
                    jq('label.statusheaderlabel.hidden').removeClass('hidden');
                    jq('#currentmessagediv').html(data);
                    jq('#comcynapsestatusmessagecommentscount').html('').attr('href','');                    
                    jq("#statusbuttontable").hide();
                    jq('#charleninfo').html("140").css('color','');
                    jq('#statusinputtextarea').css("height","20px");
                    triggerResetInputLabel(jq('#statusinputtextarea'));
                    jq('#comcynapsemessageerror').hide();
                    issuemessage('info',portalmessage_info,smessagesuccess);
                },
                error: function(event){
                    issuemessage('error',portalmessage_error,smessageerror);                    
                }
            });
        }
        });    
/////////////////////////////////Status message end
///////////////////////////////// Portal Status message begin
    jq('.link_closeportalmessage').click(function(event){
        event.preventDefault();
        jq(this).closest('.portalMessage').hide();
        });
///////////////////////////////// Portal Status message end

/////////////////////////////////nyroModal begin
    cyninnyrosettings = {
        showBackground:nyroShowBackground,
        hideBackground:nyroHideBackground,
        showContent:nyroShowContent,
        hideContent:nyroHideContent
        };
    jq.nyroModalSettings(cyninnyrosettings);
    jq('.SelectWikiStartModalDialog').nyroModal({title:'Select wiki start page'});
    jq('.nyroModalnew, .nyroModalWide').nyroModal({minWidth:720,minHeight:450});
    
    jq('.lightbox').nyroModal({type:"gallery",regexImg:'.+image_preview',minHeight:120,minWidth:120});
    jq('.nyroMindmap').nyroModal({minHeight:1024,minWidth:1600});
    jq('.logout').click(function(event){
            event.preventDefault();
            jq.nyroModalManual({content:jq('#logoutconfirm').html(),title:logoutpopup_title,minHeight: 120});        
        });
    jq('.nyroTitled').click(function(event){
        event.preventDefault();
        var href = jq(this).attr('href');
        var basetitle = jq(this).attr('title');
        var bttitle = jq(this).attr('bt-xtitle');
        var thetitle = '';
        if (basetitle == '' && bttitle != '')
        {
            thetitle = bttitle;
        }
        else
        {
            thetitle = basetitle;
        }
        jq.nyroModalManual({title:thetitle,url:href,titleFromIframe:false});
        });
/////////////////////////////////nyroModal End



//////////////////////////////////////////////////////////////////////Filter panel begin    
    if (window.iscalendarview != undefined && ! iscalendarview)
    {
        var usedateFormat = 'MMM d, yy';
        var start = jq("#startDate").val();
        var end = jq("#endDate").val();
        if (start)
        {
                var sFormatted = Date.parse(start).toString(usedateFormat);
        }
        if (end)
        {
                var eFormatted = Date.parse(end).toString(usedateFormat);
        }
        if (sFormatted && eFormatted)
        {
            jq("#rangeDate").val(sFormatted + " - " + eFormatted).removeClass("inputLabelActive");
        }
    }

    String.prototype.endsWith = function(str)
    {return (this.match(str+"$")==str);}
    if (window.arrTagsForCloud != undefined)
        arrTagNameAndClasses = jq("#comcynapsetagsarea").tagCloud(arrTagsForCloud);
    var displaymodifiers = "";
    if (window.selectedmodifiers != undefined){
        for(i=0;i < selectedmodifiers.length;i++){
            displaymodifiers = displaymodifiers + selectedmodifiers[i] + ",";
        }
    }
    if (displaymodifiers.endsWith(',')){
        var lstidxofcomma = displaymodifiers.lastIndexOf(',');
        displaymodifiers = displaymodifiers.substring(0,lstidxofcomma);
    }
    if (jq("#filterpanelModifiers").length > 0){
        jq("#filterpanelModifiers").val(displaymodifiers);
        if (displaymodifiers == ''){
            jq("#filterpanelModifiers").trigger('focus').trigger('blur');
        }
        else{
            jq("#filterpanelModifiers").removeClass('inputLabelActive').addClass('inputLabel');
        }
    }
    jq("#comcynapsetagsareatoggle").ready(function (){
        jq("#comcynapsetagsareatoggle").html(showfilterlabel);
        jq("#filtertagpanelapplybutton").hide();
    });
    jq("#comcynapsetagsarea").ready(function(){
        jq("#comcynapsetagsarea div span a[rel='tag']").each(function(i){
            if(this.rel.toLowerCase() == 'tag'){
                tagcname = arrTagNameAndClasses[i];
                jq(this).addClass(tagcname);
            }
        });
    });
    jq("#comcynapsetagsareatoggle").click(function (event) {
        event.preventDefault();
        if(this.innerHTML.toLowerCase() == hidefilterlabel.toLowerCase()){
            jq("#comcynapsetagsarea").slideUp("fast");
            jq("#filtertagpanelapplybutton").hide();
            this.innerHTML = showfilterlabel;
        }
        else{
            jq("#comcynapsetagsarea").slideDown("fast");
            jq("#filtertagpanelapplybutton").show();
            this.innerHTML = hidefilterlabel;
        }
    });
    jq(".filterpaneltag").click(function (event) {
        event.preventDefault();
        var lenofarray = currentselectedtags.length;
        var clickedvalue = this.innerHTML.replace(/&amp;/g,'&');
        clickedvalue = clickedvalue.replace(/<span.*>.*/g,''); //Remove the span that is there inside the tag now
        tagindexinarray = jq.inArray(clickedvalue,currentselectedtags);
        if( tagindexinarray < 0 & jq(this).attr('rel') == 'tag'){
            currentselectedtags[lenofarray] = clickedvalue;
            jq(this).addClass("filterpaneltagselected");
            jq(".filterpaneltag[rel='dummytag']").removeClass('filterpaneltagselected');
        }
        else if(jq(this).attr('rel') == 'dummytag'){
            if (lenofarray > 0){
                currentselectedtags = jq.makeArray();
                jq('.filterpaneltagselected').removeClass('filterpaneltagselected');
                jq(this).addClass("filterpaneltagselected");
            }
        }
        else{
            currentselectedtags = currentselectedtags.slice(0,tagindexinarray).concat( currentselectedtags.slice(tagindexinarray+1) );
            jq(this).removeClass("filterpaneltagselected");
            if (currentselectedtags.length == 0){
                jq(".filterpaneltag[rel='dummytag']").addClass('filterpaneltagselected');
            }
        }
    });
    jq("#pt_toggle").click(function(event){
        if(!jq(this)[0].checked){
            jq(this)[0].checked = true;
        }
        jq('.typeselectcheckbox').each(function(){
            jq(this)[0].checked = false;
        });
    });
    jq(".typeselectcheckbox").click(function(event){
        if (!jq(this).checked && jq('#pt_toggle').length > 0){
            jq("#pt_toggle")[0].checked = false;
        }
        if(jq("input[name=portal_type:list]:checked").length == 0){
            jq("#pt_toggle")[0].checked = true;
        }
    });
    jq("#filtertagpanelapplybutton").click(function(event){
        event.preventDefault();
        var qparam = '';
        var strURL = '';
        for(i=0;i < currentselectedtags.length; i++)
        {
            var converted = currentselectedtags[i];
            qparam += 'Subject:list=' + encodeURIComponent(converted) + '&';
        }
        idx = currentpageURL.indexOf('?');
        var hasOtherparams = 0;
        var oqparams = "";
        var arrParams = new Array('subject:list','b_start:int','-c','sort_order','sort_on','limit_display:int','portal_type:list','modifiers:list','startdate','enddate','searchabletext');
        if (idx >= 0){
            resturlpart = currentpageURL.substring(idx+1);
            arrPart1 = resturlpart.split("&");
            for (i = 0;i < arrPart1.length; i++){
                arrInner = arrPart1[i].split("=");
                if(arrInner.length > 0){
                    if (jq.inArray(arrInner[0].toLowerCase(),arrParams) == -1){
                        hasOtherparams = 1;
                        oqparams = oqparams + arrPart1[i] + "&";
                    }
                }
            }
        }
        var val_modifiers = jq("#filterpanelModifiers").val();
        val_modifiers = jq.trim(val_modifiers);
        if (val_modifiers != '' && val_modifiers != jq("#filterpanelModifiers").attr('title')){
            var arrmodifiers = val_modifiers.split(',');
            for(i=0;i < arrmodifiers.length;i++){
                if(arrmodifiers[i] != ''){
                    qparam += 'modifiers:list=' + arrmodifiers[i] + "&";
                }
            }
        }
        var ptype_single = jq("input[name=portal_type:list]");
        var iCounter = 0;
        for(i=0;i < ptype_single.length;i++){
            if(ptype_single[i].checked){
                iCounter++;
            }
        }
        if (iCounter != ptype_single.length){
            for(i=0;i < ptype_single.length;i++){
                if(ptype_single[i].checked){
                    qparam += 'portal_type:list=' + ptype_single[i].value + "&";
                }
            }
        }
        if (window.iscalendarview != undefined && ! iscalendarview )
        {
			if (jq("#rangeDate").val() != jq("#rangeDate").attr('title'))
			{
                arrDates = jq("#rangeDate").val().split(" - ");
                if (arrDates && arrDates.length >= 1)
                {
                        spltDateStart = Date.parse(arrDates[0].toString());
                        if (arrDates.length == 1)
                        {
                                if (spltDateStart)
                                {
                                        val_startdate = spltDateStart.toString("yyyy/MM/dd");
                                        val_enddate = spltDateStart.add({days:1}).toString("yyyy/MM/dd");
                                }
                        }
                        else if (arrDates.length == 2)
                        {
                                spltDateEnd = Date.parse(arrDates[1].toString());
                                if ( spltDateStart && spltDateEnd )
                                {
                                        val_startdate = spltDateStart.toString("yyyy/MM/dd");
                                        val_enddate = spltDateEnd.toString("yyyy/MM/dd");
                                }
                        }
                        if (val_startdate && val_enddate)
                        {
                                qparam += "startdate=" + val_startdate + "&" + "enddate=" + val_enddate + "&";
                        }
                }
			}
            var val_searchterm = jq("#filterpanelSearchTerm").val();
            var val_searchtitle = jq("#filterpanelSearchTerm").attr('title');
            val_searchterm = jq.trim(val_searchterm);
            if (val_searchterm != '' && val_searchterm != val_searchtitle){
                qparam += 'SearchableText=' + encodeURIComponent(val_searchterm) + "&";
            }
            var val_sortby = jq("#filterpanelsortby").val();
            if (val_sortby != -1){
                    qparam += 'sort_on=' + val_sortby + "&";
            }
            var val_sortorder = jq("#filterpanelsortorder").val();
            if (val_sortorder != -1){
                    qparam += 'sort_order=' + val_sortorder + "&";
            }
            var val_pagesize = jq("#filterpanelpagesize").val();
            qparam += 'limit_display:int=' + val_pagesize + "&";
        }
		
        if(qparam.length > 0 && idx < 0){
            strURL = currentBaseURL + '?' + qparam;
        }
        else if(qparam.length > 0 && idx >= 0){
            if (hasOtherparams == 1)
                strURL = currentBaseURL + '?' + oqparams + qparam;
            else
                strURL = currentBaseURL + '?' + qparam;
        }
        else if(idx >= 0){
            if (hasOtherparams == 1){
                strURL = currentBaseURL + '?' + oqparams;
            }
            else{
                strURL = currentBaseURL;
            }
        }
        else{
            strURL = currentBaseURL;
        }
        if (strURL.endsWith('&')){
            var lstidx = strURL.lastIndexOf('&');
            strURL = strURL.substring(0,lstidx);
        }
        window.location = strURL;
    });
    jq('.filterpaneltopheader').live('click',function(event){
        event.preventDefault();
        if (!jq(this).hasClass('expanded')){
            jq(this).addClass('expanded');
            jq(this).siblings('.filterpaneltopheader').addClass('expanded');
        }
        var alreadyclicked = jq(this).siblings('.filterpaneltopheader').filter('.opened');        
        if (alreadyclicked){            
            jq('#' + jq(alreadyclicked).attr('rel')).hide();
            jq(alreadyclicked).removeClass('opened');
        }        
        if (jq(this).hasClass('opened')){                        
            jq('#' + jq(this).attr('rel')).hide();
            jq("#filtertagpanelapplybutton").hide();
            jq(this).removeClass('opened');
            jq(this).removeClass('expanded');
            jq(this).siblings('.filterpaneltopheader').removeClass('expanded');
        }
        else{                        
            jq('#' + jq(this).attr('rel')).fadeIn("fast");
            jq("#filtertagpanelapplybutton").show();
            jq(this).addClass('opened');
        }
    });
    jq('#filterpanelModifiers').autocomplete(
        'userssuggest',{
            multiple: true,
            matchContains: true,
            multipleSeparator: ",",
            autoFill: true,
            scroll: true,
            scrollHeight: 300,
            delay:200
        }  
    );
//////////////////////////////////////////////////////////////////////Filter panel end

///////////////////////////////////////////////////////////////////// All updates listing related begin
    curloc = window.location.toString();
    if (curloc.indexOf("?")>-1)
    {
        delim = "&";
    }
    else
    {
        delim = "?";
    }
    
    jq(".link_blogviewlistexpand").click(function(event){
        event.preventDefault();
        var id = jq(this).attr("rel");
        var state = jq(this).attr("kssattr:state");
        jq("#listitemdiscusslinktop" + id).trigger("click");
        if (state == "closed")
            jq(this).attr("kssattr:state","opened");
        else
            jq(this).attr("kssattr:state","closed");
    });
    jq(".comcynapseinlinediscusslink").click(function(event){
        event.preventDefault();
        id = jq(this).attr("rel");
        jq('.documentByLine').removeClass("expanded");
        jq('.documentByLine').removeClass("expanded");
        jq('.listitemtitleheader').removeClass("expanded");
        jq('.listitemdetailrow, .listitemdiscussrow').html("");
 
        if ( jq(this).hasClass("opened"))
        {
            jq('.comcynapseinlinediscusslink').removeClass("opened");
            jq('.comcynapseinlinediscusslink').text("+");
            jq(this).attr('kssattr:state','closed');
            jq('form[name=frmListerTimeout] #comcynapsecyninfetchUID').val('0');
            jq('form[name=frmListerTimeout] #comcynapsecyninfetchindex').val('-1');
            jq('form[name=frmListerTimeout] #comcynapsecommentcount').val('0');
            jq('form[name=frmListerTimeout] #comcynapselasttimestamp').val('0');
            jq('form[name=frmListerTimeout] #comcynapselastcommentid').val('0');
        }
        else
        {
            jq('.comcynapseinlinediscusslink').removeClass("opened");
            jq('.comcynapseinlinediscusslink').attr('kssattr:state','closed');
            jq('.comcynapseinlinediscusslink').text("+");
            jq('#documentByLine' + id).addClass("expanded");
            jq('#listitemtitle' + id).addClass("expanded");
            jq(this).addClass("opened");
            jq(this).text("-");
            var clickeduid = jq(this).attr('kssattr:uid');
            jq(this).attr('kssattr:state','opened');
            jq.ajax({
                url: portal_url + '/itemdetails?uid=' + clickeduid + '&itemindex=' + id,
                cache: false,
                success:function(html){                    
                    jq('#listitemdetail' + id).html(jq(html).filter('div#comcynapseitemdetails').html());
                    jq('#listitemdiscussrow' + id).html(jq(html).filter('div#comcynapseitemcomments').html());
                    data = jq(html).filter('div#comcynapsejsondata').html();
                    renderhtml = jq(html).find('#dummycommenttable').clone(true);
                    targetobjid = 'comcynapselistcommentscontainer' + id;                    
                    renderComments(targetobjid,renderhtml);
                    
                    MarkSelectedListTags();
                    triggerInputLabel();
                    jq('#listitemdiscussrow' + id).focus();
                    jq('#listitemdiscussrow' + id).blur();
                    jq('form[name=frmListerTimeout] #comcynapsecyninfetchUID').val(clickeduid);
                    jq('form[name=frmListerTimeout] #comcynapsecyninfetchindex').val(id);
                    jq('form[name=frmListerTimeout] #comcynapsecommentcount').val(jq('#comcynapsecommentcount' + id).val());
                    jq('form[name=frmListerTimeout] #comcynapselasttimestamp').val(jq('#comcynapselasttimestamp' + id).val());
                    jq('form[name=frmListerTimeout] #comcynapselastcommentid').val(jq('#comcynapselastcommentid' + id).val());
                }
            });
        }
        
        var openeditemindex = jq('#comcynapsecyninfetchindex').val();
        });
    ////list comment refresh
    jq('#comcynapserefreshlistcomments').live("click",function(){
        datastring = jq('form[name=frmListerTimeout]').serialize();                
        jq.post('fetchcommentsforlist',datastring,function(data,textStatus){
            switch(textStatus.toLowerCase()){
                case 'success':                    
                    processComments(data);           
                    break;
            }
            
        },'json');
    });
    jq('#comcynapsehiddencomments').live('click',function(event){
        event.preventDefault();
        datastring = jq('form[name=frmDiscussionAddNew]').serialize();
        jq.post('fetchnewcomments',datastring,function(data,textStatus){            
            switch(textStatus.toLowerCase())
            {
                case 'success':
                    processComments(data);
                    break;
            }
        },'json');
    });
    jq('#togglecommentsview a').live('click',function(event){
        event.preventDefault();
        jq('#togglecommentsview a').removeClass('selected');
        jq(this).addClass('selected');
        viewtype = jq(this).attr('viewtype');        
        uid = jq('form[name=frmDiscussionAddNew] input[name=comcynapsecynincontextUID]').val();        
        datastring = "viewtype=" + viewtype + "&uid=" + uid;
        jq('#comcynapsecyninitemcommentscontainer').hide();
        jq.post('togglecommentsview',datastring,function(data,textStatus){
            switch(textStatus.toLowerCase())
            {
                case 'success':
                    jq('#comcynapsecyninitemcommentscontainer').html('');
                    processComments(data);
                    jq('form[name=frmDiscussionAddNew] #comcynapseviewtype').val(viewtype);
                    break;
            }
        },'json');
        jq('#comcynapsecyninitemcommentscontainer').show();
    });
    jq('input.comcynapsecyninreplycomment').live('click',function(event){
        event.preventDefault();
        inreplytoid = jq(this).attr('rel');
        jq('.inlinereplyform').remove();
        jq('input.comcynapsecyninreplycomment').show();
        jq(".commentbodyta").css('height','auto');
        triggerResetInputLabel(jq(".commentbodyta"));
        jq(".comcynapsecyninlistcommentsubmit,.comcynapsecyninlistcommentcancel,dl.inlineerror").hide();    
        var replydiv = jq('#comcynapsefrmDiscussionAddNew').clone(true);
        var frmaddnew = jq(replydiv).find('form[name=frmDiscussionAddNew]');
        var outerdiv = "<div style='margin-left:10px;' id='replyform" + inreplytoid + "' class='inlinereplyform commenttopcontainer'></div>";
        jq(frmaddnew).wrap(outerdiv);
        var parentdiv = jq(frmaddnew).parent();
        jq(parentdiv).find('div.commentactionbuttonsrow').append('<input type="hidden" name="inreplyto" value="' + inreplytoid + '" />');
        jq(parentdiv).find('#comcynapsecommenterror').hide();
        jq(parentdiv).find('.comcynapsecyninlistcommentcancel').addClass('comcynapsecyninsreplycommentcancel').removeClass('comcynapsecyninlistcommentcancel').css('display','inline').attr('rel',inreplytoid);
        jq(parentdiv).find('.comcynapsecyninlistcommentsubmit').show();        
        jq(parentdiv).appendTo('#commenttable'+inreplytoid);        
        triggerInputLabel();
        jq(parentdiv).find('#taAddNewComment').autoResize({extraSpace:20,animateDuration:0,limit:400}).addClass('exec').removeClass('inputLabelActive').val('').focus();
        jq(this).hide();
    });
    ////Show Hide Post comment detail
    jq(".commentbodyta, #taAddNewComment").live("click",function(){
        jq(this).closest('form').find(".comcynapsecyninlistcommentsubmit, #comcynapsecyninnewcommentsubmit, .comcynapsecyninlistcommentcancel").show();
        jq(this).closest('form').find('input[name=comcynapsenewcommenttitle]').val(this.title);
        if (!jq(this).hasClass('exec')){
            jq(this).autoResize({extraSpace:20,animateDuration:0,limit:400}).addClass('exec');
        }
        jq(this).focus();
        });
    jq(".comcynapsecyninlistcommentcancel").live("click",function(){
        jq(this).closest('form').find(".comcynapsecyninlistcommentsubmit, #comcynapsecyninnewcommentsubmit, .comcynapsecyninlistcommentcancel, dl.inlineerror").hide();
        triggerResetInputLabel(jq(this).closest('form').find(".commentbodyta").css('height','auto'));
        });
    jq(".comcynapsecyninsreplycommentcancel").live("click",function(){
        jq(this).closest('.inlinereplyform').css("display","none").remove();
        jq('#commenttable' + jq(this).attr('rel')).find('input.comcynapsecyninreplycomment').show();        
        });
    
    jq('.comcynapsecyninlistcommentsubmit').live("click",function(event){
        event.preventDefault();
        var itemindex = '';
        itemindex = jq(this).prevAll('input[name=comcynapsecyninitemindex]').val();
        if (itemindex == undefined){
            itemindex = '';
        }
        var closestform = jq(this).closest('form');
        var commenttxtarea = jq(closestform).find('#taAddNewComment'+itemindex);
        var errorholder = jq(closestform).find('#comcynapsecommenterror' + itemindex);
        var valcomment = jq.trim(jq(commenttxtarea).val());
        
        if(valcomment == '' || valcomment.toLowerCase() == jq(commenttxtarea).attr('title').toLowerCase()){
            jq(errorholder).show();
        }
        else{
            jq(errorholder).hide();
            datastring = jq(this).closest('form[name=frmDiscussionAddNew]').serialize();
            jq.post('addnewcomment',datastring,function(data,textStatus){
                switch(textStatus.toLowerCase())
                {
                    case 'success':
                        if (data.view_type && data.view_type != 'listview'){
                            jq(closestform).find('.comcynapsecyninsreplycommentcancel').trigger('click');
                        }
                        processComments(data);
                        jq('#taAddNewComment' + itemindex).css('height','auto');                        
                        triggerResetInputLabel(jq('#taAddNewComment' + itemindex));
                        jq(closestform).find(".comcynapsecyninlistcommentsubmit,.comcynapsecyninlistcommentcancel").hide();                        
                        break;
                }
            },'json');
        }        
    });
///////////////////////////////////////////////////////////////////// All updates listing related end

///////////////////////////////////////////////////////////////////// Ratings begin
    jq(".comcynapseratingbutton").live('mouseover',function(event){
        jq(this).addClass("hover");
        currlabel = jq(".comcynapseratinginputlabel");
        currlabel.html(jq(this).attr("title"));
        });
    jq(".comcynapseratingbutton").live('mouseout',function(event){
        jq(this).removeClass("hover");
        currlabel = jq(".comcynapseratinginputlabel");
        currlabel.html(currlabel.attr("title"));
        });
    jq(".comcynapseratingbutton").live('click',function(event){
        event.preventDefault();
        clickednode = this;
        var itemuid = jq(this).closest('form').find('input[name=itemUID]').val();
        var rate_data = jq('#comcynapsecyninratingform').serialize();
        rate_data = rate_data + '&ratevalue=' + jq(this).val();
        jq.ajax({type: "POST",url: "ratecontent",data: rate_data,
            success: function(data){
                var valncount = '';
                var valpcount = '';
                arrdata = data.split(',');
                var myrating = arrdata[0];
                var totrating = arrdata[1];
                if (arrdata.length > 2){
                    valpcount = arrdata[2];
                }
                if (arrdata.length > 3){
                    valncount = arrdata[3];
                }
                
                jq('#displaytotalscoredetail' + itemuid).html(totrating);
                jq('#displaytotalscorelabel' + itemuid).html(totrating);
                jq(".comcynapseratinginputlabel").html(myrating);
                jq(".comcynapseratinginputlabel").attr('title',myrating);
                if (valpcount > 0){
                    jq('.outerpcount').css('display','').find('.displaypositivecountlabel').html(valpcount);     
                }
                else{
                    jq('.outerpcount').css('display','none');
                }
                if (valncount > 0){
                    jq('.outerncount').css('display','').find('.displaynegativecountlabel').html(valncount);
                }
                else{
                    jq('.outerncount').css('display','none');
                }
                jq(clickednode).addClass('selected');
                jq(clickednode).siblings('.comcynapseratingbutton').removeClass('selected');
            },
            error: function(event){
                issuemessage('error',portalmessage_error,ratingerror);
            }
        });
    });
///////////////////////////////////////////////////////////////////// Ratings end

//////////////////////////////////////////////////////////////////// jq ui tabs begin
    jq("#activityportlet > ul").tabs();

    jq("#statsportlet > ul").tabs();
    jq("#topratedandmostvisitedportlet > ul").tabs();
    jq("#siteupdatesportlet > ul").tabs();

//////////////////////////////////////////////////////////////////// jq ui tabs begin


//////////////////////////////////////////////////////////////////// tags portlet begin
    if (window.tagsportlet_arrTagsForCloud != undefined)
        tagsportlet_arrTagNameAndClasses = jq("#tagsportlet-tagcloud").tagCloud(tagsportlet_arrTagsForCloud);

    jq("#tagsportlet-tagcloud").ready(function(){
        jq("#tagsportlet-tagcloud div span a").each(function(i){
            if(this.rel.toLowerCase() == 'tag'){
                tagcname = tagsportlet_arrTagNameAndClasses[i];
                jq(this).addClass(tagcname);
            }
        });
    });
//////////////////////////////////////////////////////////////////// tags portlet end

//////////////////////////////////////////////////////////////////// form header legend show/hide begin
    jq(".editformheaderlegend").click(function(event){
            jq(this).toggleClass('opened').next().slideToggle("fast");
        });
//////////////////////////////////////////////////////////////////// form header legend show/hide end

/////////////////////////////////////////////////////////////////// Email feedback form begin
    jq("a.sendemailexpand").click(function(){
        jq()
            jq("#emailfeedbackform").slideToggle("slow");
        });
/////////////////////////////////////////////////////////////////// Email feedback form end
////////////////////////////////////////////////////////////////// Member search begin
jq('.usersearchlink').click(function(event){
        event.preventDefault();
        jq('.usersearchform').slideToggle('fast');
        jq(this).toggleClass('opened');
    });
////////////////////////////////////////////////////////////////// Member search end
///////////////////////////////////////////////////////////////// Description Macro begin
    jq("a.descriptiontoggle").click(function(){
        jq("#singleviewdescriptionarea").slideToggle("fast",function(){
            if (jq(this).css("display") == "none")
            {
                //enable hide
                jq("a.descriptiontoggle").removeClass("opened")
                createCookie("showdescriptionmacro",false,365);
            }
            else
            {
                //enable show
                jq("a.descriptiontoggle").addClass("opened")
                createCookie("showdescriptionmacro",true,365);
            }
        });
    });
///////////////////////////////////////////////////////////////// Description Macron end
///////////////////////////////////////////////////////////////// Toggle max width begin
jq('.toggleMaxWidth').click(function(event){
    event.preventDefault();
    var curmax = readCookie("maxwidth");
    var newmax = "";
    if (curmax == "100%")
    {
        newmax = "80em";
    }
    else
    {
        newmax = "100%";
    }
    jq("#page_margins").css("max-width",newmax);
    createCookie("maxwidth",newmax,365);
    });
///////////////////////////////////////////////////////////////// Toggle max width begin
///////////////////////////////////////////////////////////////// Add Discussion
jq("#discussiontextarea").autoResize({extraSpace:0,animateDuration:0,limit:400});
jq('#discussiontextarea, #comcynapsediscussioninputtitle').focus(function(event){
    event.preventDefault();
    jq('#discussionmoreinputholder').show();
    jq('#comcynapsediscussiontitle').val(jq('#discussiontextarea').attr('title'));
    jq('#comcynapsetagstitle').val(jq('#comcynapsediscussiontag').attr('title'));
    if (! jq('#comcynapsespacelocation').hasClass('exec')){
        jq.getJSON("fetchlocationstoaddcontent",cache=false,function(data){
            var optionslist = '';
            jq.each(data.items,function(i,item){                
                if (i == 0){
                    jq('#comcynapsespacelocation').html('');
                }
                var tempdash = lbldash + ' ';
                var dashtitle = '';
                for (i = 0; i < item.depth; i++){
                    dashtitle += tempdash;    
                }
                var itemclass = '';                
                if (item.occ && item.occ != ''){
                    itemclass = item.occ;
                }
                optionslist += "<option class='" + itemclass + "' value='" + item.UID + "'>" + dashtitle + item.title + "</option>";                
            });                        
            if (optionslist != ''){
                jq('#comcynapsespacelocation').append(optionslist);
            }            
            jq('#comcynapsespacelocation').val(jq('#comcynapseadddiscussioncontextuid').val()).addClass('exec');
            if (jq('#comcynapsespacelocation option:selected').attr('class') == 'disabledspaceselection'){
                jq("input[name=com.cynapse.cynin.discussionsubmit]").hide();
                jq('#comcynapsenotallowed').show();
            }
        });
    }    
    });
jq('#comcynapsecynincanceldiscussionmessageinput').live('click',function(event){
    event.preventDefault();
    jq('.discussionsubmitbutton').show();
    jq('#discussionmoreinputholder').hide();
    triggerResetInputLabel(jq('#discussiontextarea'));
    triggerResetInputLabel(jq('#comcynapsediscussioninputtitle'));
    jq('#comcynapseadddiscussioncontextuid').val(jq('#discussiontextarea').attr('kssattr:currentcontextuid'));
    jq('#discussiontextarea').css('height','auto');
    triggerResetInputLabel(jq('#comcynapsediscussiontag'));
    jq('#comcynapsenotallowed').hide();
    jq('#comcynapsespacelocation').removeClass('exec');
    });
jq('.discussionsubmitbutton').click(function(event){
    //setTimeout("jq('#discussiontextarea').blur()",5000);
    event.preventDefault();
    var valdiscussion = jq.trim(jq("#discussiontextarea").val());
    if(jq("#comcynapsediscussioninputtitle").length > 0 && (jq.trim(jq("#comcynapsediscussioninputtitle").val())== '' || jq.trim(jq("#comcynapsediscussioninputtitle").val()) ==  jq("#comcynapsediscussioninputtitle").attr('title') )){
        issuemessage('error', portalmessage_error, discussiontitleempty);
    }
    else if(valdiscussion == '' || valdiscussion == jq("#discussiontextarea").attr('title')){
        issuemessage('error',portalmessage_error,discussionempty);
    }
    else{
        jq('#kssPortalMessage').hide();        
        jq.ajax({
            type: "POST",
            url: "creatediscussion",
            data: jq('#comcynapseadddiscussioninputform').serialize(),
            success: function(data){                
                issuemessage('info',portalmessage_info,discussionsuccess.replace(/%link/g,data));
                jq('#discussiontextarea').css('height','auto');
                triggerResetInputLabel(jq('#comcynapsediscussioninputtitle'));
                triggerResetInputLabel(jq('#discussiontextarea'));
                triggerResetInputLabel(jq('#comcynapsediscussiontag'));
                jq('#discussionmoreinputholder').css('display','none');
            },
            error: function(event){
                issuemessage('error',portalmessage_error,discussionerror);                    
            }
        });
    }
    });
jq('#comcynapsespacelocation').change(function(event){
        if (jq('#comcynapsespacelocation option:selected').attr('class') != 'disabledspaceselection'){            
            jq("input[name=com.cynapse.cynin.discussionsubmit]").show();
            jq('#comcynapseadddiscussioncontextuid').val(jq(this).val());
            jq('#comcynapsenotallowed').hide();
        }
        else{
            jq("input[name=com.cynapse.cynin.discussionsubmit]").hide();
            jq('#comcynapsenotallowed').show();
        }
    });
jq('.tagshint,#comcynapsediscussiontag').autocomplete(
    'tagssuggest',{
        multiple: true,
        matchContains: true,
        multipleSeparator: ",",
        scroll: true,
        scrollHeight: 300,
        delay:200
    }  
);
jq('.listitemrowcontainer, .blogiteminfopanel').mouseover(function(event){
    var id = jq(this).attr('rel');
    jq('#listitemdiscusslinktop' + id).addClass('hover');
    });
jq('.listitemrowcontainer, .blogiteminfopanel').mouseout(function(event){
    var id = jq(this).attr('rel');
    jq('#listitemdiscusslinktop' + id).removeClass('hover');
});
///////////////////////////////////////////////////////////////// Add Discussion
jq('.defaultappview').change(function(event){
    jq('.allowedappviews').attr('disabled','');
    var allowedviewobj = jq('.allowedappviews').parent().find('#allowed_' + jq(this).attr('id'));
    jq(allowedviewobj).attr('disabled','disabled');
    if (jq('input[name=appview_allowedtoggle]:checked').length == 0){
        jq(allowedviewobj).attr('checked','true');
    }
});
jq('.allowedappviews').click(function(event){
    if (!jq(this).checked && jq('#appview_allowedtoggle').length > 0){
        jq("#appview_allowedtoggle")[0].checked = false;
        jq("input[name=hiddenallselected]").val('0');
        jq(jq('.allowedappviews').parent().find('#allowed_' + jq('.defaultappview:checked').attr('id'))).attr('checked','true');
    }
    if(jq("input[name=allowedAppView:list]:checked").length == 0){
        jq("#appview_allowedtoggle")[0].checked = true;
        jq("input[name=hiddenallselected]").val('1');
    } 
});
jq("#appview_allowedtoggle").click(function(event){
    if(!jq(this)[0].checked){        
        jq("input[name=hiddenallselected]").val('0');
        jq('.allowedappviews').each(function(){
            jq(this)[0].checked = false;
            if (jq(jq(this)[0]).attr('disabled') == true){
                jq(this)[0].checked = true;
            }
        });
    }
    else{
        jq("input[name=hiddenallselected]").val('1');
        jq('.allowedappviews').each(function(){
            jq(this)[0].checked = false;
        });
    }
});

jq('#kss-spinner').bind("ajaxSend", function(){
   $(this).show();
 }).bind("ajaxComplete", function(){
   $(this).hide();
 });

});
