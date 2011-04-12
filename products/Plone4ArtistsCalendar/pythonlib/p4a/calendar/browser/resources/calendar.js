
var popups = new Array();

function events_popup(datestr) {
    winid = 'p4acalendar-allevents-'+datestr;
    if (document.getElementById(winid) != null) {
        popup = popups[datestr];
        if (popup == null)
            popup = new PopupWindow(winid);
        //popup.offsetY = 35;
        popup.autoHide();
        popup.showPopup('p4acalendar-day-'+datestr);
    }
}
