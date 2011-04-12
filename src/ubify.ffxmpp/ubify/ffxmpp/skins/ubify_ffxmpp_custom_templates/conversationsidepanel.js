$(window).load(function(){
    doresize();
});

function doresize()
{
    $("#conversationsidepanelitems").height(
        $(window).height() 
        - $("#cspFullName").height()
        - $("#infotipstatusmessageholder").height()
        - $("#recentitemslabelholder").height()
        - 10
    );

}


        $(window).bind('resize', function(){doresize()});
