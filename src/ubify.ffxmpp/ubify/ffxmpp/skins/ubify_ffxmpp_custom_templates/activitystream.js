$(window).load(function(){
    doresize();
});

function doresize()
{
    $("#activitystreamitems").height(
        $(window).height() 
        - $("#sitelogoholder").height() 
        - $("#activitystreamlabelholder").height()
        - 14
    );

}


        $(window).bind('resize', function(){doresize()});
