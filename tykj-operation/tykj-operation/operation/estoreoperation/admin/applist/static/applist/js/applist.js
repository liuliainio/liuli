/**
 * Placeholder
 */
function dismissRelatedLookupPopup(win, chosenId) {
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);

    // TODO: do our own logic here
    if(name.substring(0,7) == "subject") {
        window.open("/admin/editorial/subjectapplication/" + chosenId + "/?_popup=1", "subjectapp", "width=800, height=500,resizable=yes,scrollbars=yes, top=100, left=50");
    } else if(name.substring(0,7) == "version" ) {
        window.open("/admin/utilities/popappversion/" + chosenId + "/?_popup=1", "subversion", "width=800, height=500, top=100, left=50,resizable=yes,scrollbars=yes");
    } else {
        //elem is null when click popup window's save button
        if(elem) {
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
var packages = null;
window.addEventListener('load',function(){
    var action = $('.action-counter');
    if(action.length>0){
        action.after('<br/><input type="text" id="addAppList" style="width:160px;margin:0 10px 0 5px;" placeHolder="请在此处粘贴您要增加的榜单" /><span class="addList" onclick="getPreview();">导入榜单</span><object id="flashProxy" style="width:131px;height:34px;margin-bottom:-13px" type="application/x-shockwave-flash" data="/static/admin_tools/flash/out.swf"></object>');
    }else{
        $('#changelist-form').append('<div class="actions"><input type="text" id="addAppList" style="width:160px;margin-right:8px;" placeholder="请在此处粘贴您要增加的榜单"><span class="addList" onclick="getPreview()">导入榜单</span><object id="flashProxy" style="width:131px;height:34px;margin-bottom:-13px" type="application/x-shockwave-flash" data="/static/admin_tools/flash/out.swf"></object></div>');
    }
    getPackageName();
    $('body').append('<div class="previewImport_out" id="preview_in_area"><div class="PI_title">导入榜单</div><div class="PI_subtitle" id="PIT_exist">当前平台存在项：</div><div class="PIE_area" id="pie_area"><table><tr><th>应用名</th><th>包名</th><th>序号</th><th>已存在序号</th><th>是否覆盖</th></tr></table></div><span class="PI_btn" style="margin-left: 175px;" onclick="inputApplist()">确定</span><span class="PI_btn" onclick="$(\'#preview_in_area\').css(\'display\',\'none\')">取消</span></div>');
});

function outPutStateOk(){
    alert('已经导出到剪贴版，请在完成同步前不要复制任何数据。');
}

function getPackageName(){
    var trs = $('#result_list tr'),id_list=[];
    for(var i=trs.length-1;i>0;i--){
        id_list.push(trs[i].getElementsByTagName('th')[0].getElementsByTagName('a')[0].innerHTML);
    }
    $.getJSON('../../get_package_name', {app_list: JSON.stringify(id_list)}, function(reData){
        if(reData){
            packages = reData;
        }
    });
}
function outPutApplist(){
    var secItem = $('#result_list tr.selected'),len=secItem.length,outJson={};
    if(len==0){
        alert('您还没有选中任何要导出的项！');
        return 'null';
    }
        //getFlash('flashProxy').writeClipboard('this is for test!');
    //outJson.list_name = appListName;
    outJson.app_list = []
    if(Object.prototype.toString.call(packages)!='[object Object]'){
        alert('导出失败，无法获取要导出项详情，请稍候再试或重新刷新页面再试！');
        return undefined;
    }
    for(var i=0;i<len;i++){
        outJson.app_list[i]=packages[secItem[i].getElementsByTagName('th')[0].getElementsByTagName('a')[0].innerHTML];
    }
    outJson.type="applist";
    return JSON.stringify(outJson);
    //console.log(JSON.stringify(outJson));
}
function getPreview(){
   var inputBox = $('#addAppList')[0],inJson=inputBox.value,request_len;
        if(!inJson){
                alert('请先输入要导入的榜单！');
                return ;
        }
        try{
        inJson = JSON.parse(inJson);
    }catch(err){
        inJson = '';
    }
    g_attachs={list_method:'AppListItem'}
    inJson.method = "preview";
    if(inJson&&inJson.type=='applist'){
        var methodList=[{name:'首页推荐',method:'CategoryRecommendApp'},{name:'装机必备',method:'BootApp'},{name:'必备应用',method:'PreparedApp'},{name:'榜单管理',method:'TopApp'}];
        if(appListName=='天翼酷玩'){
            alert('当前榜单暂不支持导入！');
            return ;
        }
        inputBox.value='正在导入……';
        inJson.list_name = appListName;
        inJson.list_method = 'AppListItem';
        for(var i=0,len=methodList.length;i<len;i++){
            if(appListName.indexOf(methodList[i].name)!=-1){
                g_attachs.list_method = inJson.list_method = methodList[i].method;
                break;
            }
        }
        if(inJson.list_method=='CategoryRecommendApp'){
                var tmpArr = appListName.split('-'),transArr=[{name:'最新',key:10},{name:'最热',key:11},{name:'最适合',key:12},{name:'首发',key:13}];
                if(tmpArr.length==2){
                    for(i=0,len=transArr.length;i<len;i++){
                        if(tmpArr[1].indexOf(transArr[i].name)!=-1){
                                g_attachs.listType = inJson.listType = transArr[i].key;
                                break;
                        }
                    }
                }
        }
        if(inJson.list_method=='TopApp'){
                var tmpArr = appListName.split('-');
                //transArr=[{name:'应用',key:11},{name:'影音',key:12},{name:'游戏',key:13},{name:'阅读',key:14}];
                if(tmpArr.length==2&&tmpArr[1]){
                        g_attachs.listKind = inJson.listKind = tmpArr[1];
                }
        }
        $.getJSON('../../sync_applist_add',{add_list:JSON.stringify(inJson)},function(redata){
                                inputBox.value='';
                                try{
                                        reData = typeof(redata) =='object'?redata:JSON.parse(redata);
                                }catch(err){
                                        alert('操作出错，请稍候重试！'+err);
                                        return ;
                                }
                                if(reData.exist){
                                         exist_app=reData.exist;
                                        var tmp=[],tmpObj,j=0;
                                        for(var i in exist_app){
                                                tmpObj = exist_app[i];
                                                if(tmpObj.package_name){
                                                        j++;
                                                        tmp.push('<tr '+(tmpObj.order?"repeat":"")+'  id="'+i+'"><td>'+tmpObj.name+'</td><td>'+tmpObj.package_name+'</td><td class="new_order"><input type="text" value="'+j+'" /></td><td>'+(tmpObj.order?tmpObj.order:"不存在")+'</td><td><input type="checkbox" '+(tmpObj.order?"":"style='display:none'")+' onchange="if(this.checked){this.parentNode.parentNode.setAttribute(\'reset\',\'\');}else{$(this).parent().parent().removeAttr(\'reset\')}"/></td></tr>');
                                                }
                                        }
                                        $('#pie_area table').html('<tr><th>应用名</th><th>包名</th><th>序号</th><th>已存在序号</th><th>是否覆盖</th>');
                                        $('#pie_area table').append(tmp.join(''));
                                        $('#preview_in_area').css('display','block');
                                }
                                else{
                                        alert('导入榜单项在当前平台不存在！');
                                }
        });
    }else{
        inputBox.value='';
        alert('导入数据错误，请重新输入！');
    }
}
function inputApplist(){
    //var appListName =appListName;
    var all_tr = $('#pie_area').find('tr'),tmptr,add_list=g_attachs,inputBox = $('#addAppList')[0],insert_len=0;
    add_list.add_app_list=[];
    add_list.update_app_list=[];
    for(var i=1,len=all_tr.length;i<len;i++){
        tmptr = all_tr[i];
        if(tmptr.attributes['repeat']){
            if(tmptr.attributes['reset']){
                add_list.update_app_list.push({id:tmptr.id,order:all_tr[i].getElementsByTagName('input')[0].value});
                insert_len++;
            }
        }else{
            add_list.add_app_list.push({id:tmptr.id,order:all_tr[i].getElementsByTagName('input')[0].value});
            insert_len++;
        }
    }
    if(insert_len ==0){
        return ;
    }
    inputBox.value='正在导入……';
    add_list.list_name = appListName;
        add_list.method = 'add';
        add_list.insert = insert_len;
            $.getJSON('../../sync_applist_add',{add_list:JSON.stringify(add_list)},function(redata){
            inputBox.value='';
                if(redata.length>0){
                        alert('导入成功!');
                        $('#preview_in_area').css('display','none');
                        location.reload();

                }else{
                        alert('导入失败！请重试');
                }
            });
}
