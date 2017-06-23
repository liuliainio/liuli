/**
 * Placeholder
 */
function dismissRelatedLookupPopup(win, chosenId) {
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);

    // TODO: do our own logic here
    if(name.substring(0,7) == "subject") {
        window.open("/admin/utilities/subjectapplication/" + chosenId + "/?_popup=1", "subjectapp", "width=800, height=500, resizable=yes, scrollbars=yes, top=100, left=50");
    } else if(name.substring(0,7) == "version" ) {
        window.open("/admin/utilities/popappversion/" + chosenId + "/?_popup=1", "subversion", "width=800, height=500, top=100, left=50, resizable=yes, scrollbars=yes");
    } else {
        //elem is null when click popup window's save button
        if(elem){
            if(elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
                elem.value += ',' + chosenId;
            } else {
                if (name.indexOf('id_apps') != -1) {
                    document.getElementById(name).value = chosenId;
                } else {
                    var input = document.getElementById(name);
                    input.value = chosenId;
                    if (chosenId == "" | chosenId == undefined | chosenId == null) {
                        input.nextElementSibling.nextElementSibling.children[0].textContent = '';
                    } else {
                        var xmlhttp;
                        var display_href = input.nextElementSibling.nextElementSibling;
                        if (window.XMLHttpRequest) {
                            xmlhttp = new XMLHttpRequest();
                        } else {
                            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
                        }
                        xmlhttp.onreadystatechange=function() {
                            if (xmlhttp.readyState==4 && xmlhttp.status==200 && xmlhttp.responseText) {
                                display_href.children[0].textContent = xmlhttp.responseText.replace(/"/g, '');
                                var href_value = display_href.getAttribute('href').replace(/\/(\d+|obj_id_placeholder)\//, '/' + chosenId + '/');
                                display_href.setAttribute('href', href_value);
                            }
                        }
                        xmlhttp.open("GET", '../../../get_related_lookup_info?cls_name=' + display_href.getAttribute('cls_name') + '&v=' + chosenId, true);
                        xmlhttp.send();
                    }
                }
            }
        }
    }
    win.close();
}
