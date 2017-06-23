/**
 * get cookie
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Placeholder
 */
function dismissRelatedLookupPopup(win, chosenId) {
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);

    // TODO: do our own logic here
    if(name.substring(0, 6) == "insert") {
        var inserted_order = $(elem).attr("inserted_order");
        var isYes = confirm("Are you sure you want to insert App with ID:" + chosenId + " ?");
        if(isYes) {
            $.post('insert', {
                'id': chosenId,
                'order': inserted_order,
                csrfmiddlewaretoken: getCookie("csrftoken"),
            }, function(data) {
                if (data == 'success') {
                    window.location.reload();
                } else {
                    alert('Insert app failed.');
                }
            })
        }
    } else if(name.substring(0, 7) == "version" ) {
        window.open("/admin/utilities/popappversion/" + chosenId + "/?_popup=1", "subversion", "width=1022, height=500,top=100,left=50,resizable=yes,scrollbars=yes");
    }
    win.close();
}

