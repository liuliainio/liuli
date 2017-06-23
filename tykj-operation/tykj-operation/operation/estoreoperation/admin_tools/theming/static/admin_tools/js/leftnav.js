function popTarget(id)
{
    txtNode = document.getElementById(id);
    if(txtNode)
    {
        url = txtNode.value;
        window.open(url);
    }
    else
    {
        alert('alert false');
    }
}

function addEvent(dom,type,func,other){
    if(!type||!func){
        return;
    }
    other = other?other:false;
    dom.addEventListener(type,func,other);
}

function extra_confirm(){
    var need_confirm=$('.needConfirm'),confirm_log,dom_arr=[],target_dom,math_sign=['+','-','*'],enable_break=true;
    if(need_confirm.length>0){
        (function(){
            var method = arguments[0],tmp,randoms=[];
            confirm_log=!method?'没有指定运行类型！':confirm_log;
            switch(method){
                case 'init':
                    $('body').append('<div id="uConfirmBox" style="display:none;position:fixed;left:0;top:0;width:157px;z-index:1000;margin-left:50%;margin-top:10%;border:1px solid #ccc;border-radius:4px;padding-bottom:40px;background-color:white;"><div style=" background-color:#dff4ff;padding:10px;font-size:14px;"><span id="confirmInfo">您确定要这么做么？</span></div><div style=" vertical-align:middle;height:24px;margin-top:5px;"><span style=" margin-left:10px;display:inline-block;vertical-align:middle;">请计算：</span><span id="question" style=" display:inline-block;margin:0 5px 0 0;vertical-align:middle;">99+99</span>=<input id="answer" type="text" onfocus="this.style.borderColor=\'\'" style=" width:20px;float:right;height:16px;margin-right:2px;"></div><span id="sure" style=" display:inline-block;position:absolute;border:1px solid #ccc;border-radius:3px;padding:3px 8px;background:#f9f9f9;background:-webkit-gradient(linear,0 0,0 bottom,from(#f9f9f9),to(#E6E6E6));bottom:0;margin-bottom:5px;margin-left:11px;cursor:pointer;">确定</span><span id="cancle" style=" right:0;display:inline-block;position:absolute;border:1px solid #ccc;border-radius:3px;padding:3px 8px;background:#f9f9f9;background:-webkit-gradient(linear,0 0,0 bottom,from(#f9f9f9),to(#E6E6E6));bottom:0;margin-bottom:5px;margin-right:10px;cursor:pointer;">取消</span></div>');
                    tmp = arguments.callee.bind(this,'show');
                    need_confirm.each(function(){
                        addEvent(this.parentNode,'click',function(e){
                            var extra_com,node=e.target,class_name = node.className;
                            if(!/needConfirm/.test(class_name)){
                                return ;
                            }
                            extra_com = /\bextra_com/.test(class_name)?node.getAttribute('extra_common'):'true';
                            if(enable_break&&eval(extra_com)){
                                e.preventDefault();
                                e.stopPropagation();
                                tmp(e.target);
                            }else{
                                enable_break=true;
                            }
                            return;
                        }, true);
                    });
                    dom_arr = $('#uConfirmBox,#uConfirmBox #question,#uConfirmBox #answer,#uConfirmBox #confirmInfo');//confirmBox questionPlace answerPlace infoPlace
                    addEvent(dom_arr[0],'click',arguments.callee.bind(this,'verification'));
                break;
                case 'show':
                    target_dom=arguments[1];
                    if(!target_dom){
                        return ;
                    }
                    tmp = target_dom.getAttribute('info');
                    if(tmp){
                        dom_arr[1].innerHTML = tmp;
                    }
                    randoms=[Math.random(),Math.random()].sort();
                    dom_arr[2].innerHTML = Math.floor(randoms[1]*10)+math_sign[Math.floor(randoms[0]*10%3)]+Math.floor(randoms[0]*10);
                    dom_arr[0].style.display='block';
                break;
                case 'verification':
                    switch(arguments[1].target.id){
                        case 'sure':
                            var tmpValue = dom_arr[3].value;
                            if(!tmpValue||parseInt(tmpValue)!=eval(dom_arr[2].innerText)){
                                dom_arr[3].style.borderColor='red';
                                return ;
                            }
                            if(target_dom){
                                enable_break = false;
                                target_dom.click();
                                target_dom = null;
                            }
                            dom_arr[3].value = "";
                        break;
                        case 'cancle':
                        break;
                        default:
                        return ;
                    }
                    dom_arr[0].style.display='none';
                break;
                default:
                break;
            }
            return ;
        })('init');
    }
}

function push_method(){
    switch(arguments[0]){
        case 'init':
            var tmp_trs = $('#result_list').find('tr'),sync_btn = $('.sync_btn'),len=tmp_trs.length,tmp_tr,tmp_sync,tmp_status,tmp_value;
            tmp_trs.each(function(i){this.id='push_'+i});
            if(len>1){
                for(var i=1;i<len;i++){
                    tmp_tr = $(tmp_trs[i]);
                    tmp_sync = tmp_tr.find('td').last()[0].innerHTML;
                    tmp_status = tmp_tr.find('#id_form-'+(i-1)+'-status');
                    tmp_value = tmp_status[0].value;
                    if(tmp_value=='0'||(tmp_value==1&&tmp_sync=='需要同步')){
                        tmp_status.find('option').last().remove();
                        disable_change.push('push_'+i);
                    }
                }
            }
            sync_btn.each(function(){
                this.className=this.className+' needConfirm extra_com';
                $(this).attr({'info':'您选中将要同步项中存在有正式发布的push消息，请您确认已经预发布且验证不存在问题！','extra_common':'push_method("verify",e)'});
            });
        break;
        case 'verify':
            var select_tr=$("#result_list .selected"),need_confirm=false;
            if(select_tr.length==0){
                if(arguments[1]){
                    arguments[1].preventDefault();
                    arguments[1].stopPropagation();
                }
                alert('请先选择要同步项！');
                return false;
            }
            select_tr.each(function(){if(this.id&&disable_change.indexOf(this.id)==-1){
                need_confirm=true;
            }});
            return need_confirm;
        break;
        default:
        break;
    }
}

function sync_to_line(){
    var cancle_flag = false,procesLen=100,sync_log,dom_arr,is_sent,ajax_parameters,receive_data,total_item=0,left_item=0,error_times=0;
    (function(){
        var tmp;
        is_sent = false;
        sync_log=!arguments[0]?'没有传入调用类型！':sync_log;
        ajax_parameters=ajax_parameters?ajax_parameters:{
            url:window.location.href.replace(/\?.*/,'')+'syncto',
            data:{},
            timeout:180000,
            success:arguments.callee.bind(this,'repeat'),
            error:arguments.callee.bind(this,'error')
        };
        switch(arguments[0]){
            case 'start':
                tmp = $('.procesCover,#proflag,#showNum,#cancle_btn');
                if(tmp.length!=3){
                    $('#content').append('<div class="procesCover"><div id="processing" class="process">同步进度:<span class="proflagout"><span id="proflag" class="proflag"></span></span><span id="showNum" class="showNum">loading…</span><span class="cancleBtn" id="cancle_btn" >取消</span></div></div>');
                    tmp = $('.procesCover,#proflag,#showNum,#cancle_btn');
                }else{
                    tmp[0].style.display='block';
                }
                dom_arr=tmp;
                dom_arr[3].addEventListener('click',arguments.callee.bind(this,'cancle'));
                ajax_parameters.data={'first':'true'};
                is_sent = true;
            break;
            case 'repeat':
                if(cancle_flag){
                    return ;
                }
                receive_data = arguments[1];
                if(typeof receive_data ==='string'){
                    try{
                        receive_data = JSON.parse(receive_data);
                    }catch(err){
                        receive_data = '';
                    }
                }
                if(receive_data.all === undefined) {
                    sync_log='网络错误，服务器无响应！';
                }else{
                    if(receive_data.suc === undefined){
                        ajax_parameters.data={};
                        left_item = total_item = receive_data.all;
                        is_sent = Boolean(total_item);
                        sync_log=is_sent?'':'没有可同步的项!';
                    }else{
                        error_times = 0;
                        left_item = receive_data.all - receive_data.suc;
                        tmp = receive_data.suc==0&&receive_data.err==left_item;
                        is_sent = tmp?false:true;
                        sync_log = tmp?['成功同步',total_item-left_item,'项,同步失败',left_item,'项'].join(''):!left_item?['全部同步成功，共',total_item,'项'].join(''):sync_log;
                        dom_arr[1].style.width = procesLen * (total_item - left_item) / total_item + 'px';
                    }
                    dom_arr[2].innerHTML = left_item + '/' + total_item;
                }
            break;
            case 'error':
                error_times++;
                is_sent = error_times<4?true:false;
                sync_log = !is_sent?(total_item&&total_item!=left_item?['成功同步',total_item-left_item,'项，同步失败',left_item,'项'].join():'无法进行同步，请稍候重试！'):sync_log;
            break;
            case 'stop':
                dom_arr[0].style.display='none';
                dom_arr[1].style.width = 0;
                dom_arr[2].innerHTML='loading…';
                alert(sync_log);
                if(total_item-left_item){
                    window.location.reload();
                }
                left_item = total_item = 0;
                return ;
            break;
            case 'cancle':
                if(confirm('同步还未完成，已经同步项无法撤销，您确定要取消吗？')){
                    cancle_flag = true;
                    sync_log = ['成功同步',total_item-left_item,'项未同步',left_item,'项！'].join('');
                }else{
                    return ;
                }
            break;
            default:
            return ;
        }
        if(is_sent){
            $.ajax(ajax_parameters);
        }else{
            arguments.callee.bind(this,'stop')();
        }
        //console.log(sync_log);
        return ;
    })('start');
    return ;
}

function changeSortDefault(){
    var sort_th = $('#result_list thead tr th a'),ths,exclude='',version_order=-1,ths = $('#result_list thead tr th');
    if(ths.length == 0){
        return;
    }
    if(ths[0].innerText.replace(/\s/g,'')==='展开详情'){
        [].shift.apply(ths);
    }
    if(/\?.*o=(\d+)/.test(location.href)){
        exclude = ths[RegExp.$1].children[0].innerText;
    }
    if(sort_th.length>0){
        sort_th.each(function(){
            if(exclude&&this.innerText == exclude){
                return ;
            }
            this.href=this.href.replace(/ot=asc/,'ot=desc');
            this.parentNode.className='sorted ascending';
        });
    }
    // for search bar
    ths.each(function(i){
        if(this.innerText.replace(/\s/g,'')=='版本'){
            version_order = i;
            return false;
        }
        return true;
    });
    
    var search_node = $('#changelist-search div');
    if(version_order !=-1){  // 若当前列表存在版本，则搜索结果强制按版本列排序
        order_node = search_node.find('input[name="ot"],input[name="o"]');
        if(order_node.length==2){
            order_node[0].value='desc';
            order_node[1].value = version_order;
        }
        else{
            search_node.append('<input type="hidden" name="ot" value="desc"/><input type="hidden" name="o" value="'+version_order+'">');
        }
    }
/*
    if(document.getElementById('searchFilter'))
    {
          search_node.append('<input type="hidden" name="published__exact" value="1" />');
    }
*/
}

function change_action(){
    var action_div = $('.actions'), selectall_input = $('#action-toggle'),is_empty = selectall_input.length==0,top_prepend=[],bottom_pend=[],tmp;
    if(action_div.length == 1 && !is_empty){
        var submit_btn = $('.actions .button'),action_select = $('.actions select[name="action"]'),action_options,option_order={},options=[];
        if(action_select.length==1&&submit_btn.length==1){
            tmp = '<input type="checkbox" class="selectall" />全选';
            bottom_pend.push(tmp);
            top_prepend.push(tmp);
            action_select[0].selectedIndex = 1;
            action_options = action_select.find('option');
            action_options.each(function(i){
                var tmp_value = this.value,tmp_match;
                if(typeof tmp_value=='string'&&(tmp_match=tmp_value.match(/sync|delete/))){
                    option_order[tmp_match]=i;
                    options.push({type:tmp_match[0],text:this.innerText});
                }
            });
            if(options.length==0){
                return ;
            }
            submit_btn.hide();
            tmp = options[1]?'<button class="'+options[0].type+'_btn">'+options[0].text+'</button><button class="'+options[1].type+'_btn">'+options[1].text+'</button>':'<button class="'+options[0].type+'_btn">'+options[0].text+'</button>';
            top_prepend.push(tmp);
            bottom_pend.push(tmp);
            action_div.prepend(top_prepend.join(''));
            $('#changelist-footbar').prepend('<div class="actions bottomact">'+bottom_pend.join('')+'</div>');
            $('.actions').bind('click',function(e){
                var target = e.target,match,class_name;
                if(target.getAttribute('name')=='index'){
                    return ;
                }
                class_name = target.className;
                if(target&&class_name){
                    switch(match=class_name.match(/selectall|sync|delete/)[0]){
                        case 'selectall':
                            selectall_input.click();
                        break;
                        case 'sync':
                        case 'delete':
                            action_select[0].selectedIndex=option_order[match];
                            submit_btn.click();
                        break;
                        default:
                        break;
                    }
                }
                return ;
            });
        }
    }
}

function event_bind(){
    $('.vForeignKeyRawIdAdminField.customForeignKey').change(function() {
        var value = $(this).val();
        if (value == "" | value == undefined) {
            $(this).next().next().find('strong').text('');
        } else {
            var display_href = $(this).next().next();
            $.getJSON('../../../get_related_lookup_info?cls_name=' + display_href.attr('cls_name') + '&v=' + value, function(data) {
                if (data == "" || data == undefined) {
                    alert("请输入正确的ID.");
                } else if (data == "not_reviewed_app") {
                    alert("请输入已审核的应用.");
                } else {
                    display_href.find('strong').text(data);
                    var href_value = display_href.attr('href').replace(/\/(\d+|obj_id_placeholder)\//, '/' + value + '/');
                    display_href.attr('href', href_value);
                }
            })
        }
    });

    $(".vIntegerField").keydown(function(event) {
        // Allow: backspace, delete, tab, escape, and enter
        if ( event.keyCode == 46 || event.keyCode == 8 || event.keyCode == 9 || event.keyCode == 27 || event.keyCode == 13 ||
             // Allow: Ctrl+A
            (event.keyCode == 65 && event.ctrlKey === true) ||
             // Allow: home, end, left, right
            (event.keyCode >= 35 && event.keyCode <= 39)) {
                 // let it happen, don't do anything
                 return;
        } else {
            // Ensure that it is a number and stop the keypress
            if (event.shiftKey || (event.keyCode < 48 || event.keyCode > 57) && (event.keyCode < 96 || event.keyCode > 105 )) {
                event.preventDefault();
            }
        }
    });
    jQuery('#leftnav h3, #changelist-filter h3').click(function() {
        if(jQuery(this).hasClass('open')) {
            jQuery(this).removeClass('open');
            jQuery(this).addClass('close');
            jQuery(this).next().slideUp('fast');
        } else if(jQuery(this).hasClass('close')) {
            jQuery(this).removeClass('close');
            jQuery(this).addClass('open');
            jQuery(this).next().slideDown('fast');
        } else if (jQuery(this).hasClass('no-child')) {
            return true;
        } return false;
    });
    jQuery('input[name=source]').change(function() {
        if ($(this).attr('checked') == true) {
            var orig_value = $(this).val().split('|')[0];
            $(this).val(orig_value + '|' + $(this).parent().next().val() + '|' + $(this).parent().next().next().val());
        }
    })
    jQuery('.version_operator').change(function() {
        var checkbox = $(this).prev().children();
        if (checkbox.attr('checked') == true) {
            var orig_value = checkbox.val().split('|')[0];
            checkbox.val(orig_value + '|' + $(this).val() + '|' + $(this).next().val());
        }
    })
    jQuery('.version_value').change(function() {
        var checkbox = $(this).prev().prev().children();
        if (checkbox.attr('checked') == true) {
            var orig_value = checkbox.val().split('|')[0];
            checkbox.val(orig_value + '|' + $(this).prev().val() + '|' + $(this).val());
        }
    })
}

function label_in_turn(){ // 应用标签的交互
    var parent_node, 
    all_tags, // 用于保存所有标签名称，因为在页面里边不同标签在变量里边用其数组id记录,保存的时候需要转换回来
    tag_arr=[], 
    select_arr=[], // 用于存储页面上标签的状态 其结构可在监听事件里打断点查看
    sec_tag_doms=[], // 二级标签元素暂存，由于可能存在多个一级标签存在二级标签，所以在生成一级标签的时候同时生成二级提高效率；
    tag_str;
    (function(){
        var self,method,array_item,array_index,returns,select_method,sec_tags,tag_obj,label_input;

        method = arguments[0];
        self=arguments.callee;
        switch(method[0]){
            case 'init': // 初始化 隐藏input 请求api组织所有的标签选项
                parent_node = $('.form-row.label');
                if(parent_node.length!=1){
                    return ;
                }
                parent_node.css('overflow','visible');
                label_input = parent_node.find('#id_label');
                label_input.parent().hide();
                tag_str = label_input.val();
                if(tag_str){
                    tag_str = JSON.parse(tag_str); 
                    self(['decode_string']); // 转换数据格式
                }
                $.getJSON('/get_app_labels',function(reData){
                    if(Object.prototype.toString.call(reData)==='[object Array]'){
                        all_tags = reData;
                        html_array = all_tags.map(self.bind(this,['build_html','one_tag']));
                        parent_node.append(html_array.join('')); //插入页面中，让浏览器渲染
                        if(tag_str){
                            self(['init_set']);  // 如果有上次修改的记录则初始化标签
                        }
                        $('.tags').bind('click',self.bind(this,['action'])); //绑定事件
                        $('form').bind('submit',function(){
                            label_input.val(self.bind(this,['encode_string'])); // 保存时再转换回来
                        });
                    }
                });
            break;
            case 'build_html':  // 构建应用标签html
                array_item = arguments[1];
                array_index = arguments[2];
                returns='';
                switch(method[1]){
                    case 'transfer_init':
                        /*当数据格式更换时，在此处添加格式转换*/
                    break;
                    case 'one_tag': 
                        if(array_item&&array_item.key){  
                            select_arr[array_index]={name:array_item.name,key:array_item.key,one_tag:'',sec_tag:{}}; // 初始化用于页面里暂存数据的变量
                            returns='<div class="tags" id="'+array_index+'">'+array_item.name+':<span class="first_tag" ><span class="tag_tit" >请选择标签</span><ul class="tag_list '+array_item.select_mode+'" ><li class="tag_item default" id="default">默认不选择</li>'+array_item.tags.map(self.bind(this,['build_html','one_tag_item'])).join('')+'</ul></span><span class="sec_tag" id="sec_tag">'+sec_tag_doms.join('')+'</span></div>';// 生成单个应用标签包含一级，二级
                            sec_tag_doms = [];
                            return returns;
                        }
                    break;
                    case 'one_tag_item': // 生成一级选项
                        if(Object.prototype.toString.call(array_item)==='[object Array]'){// 包含二级的一级标签 生成二级，并在select_arr 中留下相应的记录
                            select_method = array_item[0];
                            sec_tag_name = array_item[1];
                            sec_tags = array_item[2]; //是否有二级标记
                            sec_tags=sec_tags?sec_tags:[]; //
                            returns = '<li class="tag_item'+(sec_tags.length?' sec':'')+'" id='+array_index+'>'+sec_tag_name+'</li>'; // 有两级的一级标签结构
                            sec_tag_doms.push('<span id="tag_'+array_index+'" class="'+select_method+'">'+sec_tag_name+':'+sec_tags.map(self.bind(this,['build_html','sec_tag_item'])).join('')+'</span>'); //生成二级标签列表，并存在sec_tag_doms里
                            select_arr[select_arr.length-1].sec_tag[array_index]=sec_tags.map(
                                function(item){
                                    if(/无隐私/.test(item))
                                    {
                                        return{name:item,select:false};
                                    }
                                    return{name:item,select:true};
                            });//设置二级标签初始状态为已选 
                        }else{
                            returns =  array_item?'<li class="tag_item" id='+array_index+'>'+array_item+'</li>':'';// 不包含二级的一级标签简单处理
                        }
                        return returns;
                    break;
                    case 'sec_tag_item': // 生成二级选项
                        sec_tag_str = ''
                        if(typeof(array_item) =='string')
                        {
                            if(/无隐私/.test(array_item))
                            {
                                sec_tag_str = '<span class="sec_item privacy" id='+array_index+'>'+array_item+'</span>';
                            }
                            else
                            {
                                sec_tag_str = '<span class="sec_item on" id='+array_index+'>'+array_item+'</span>';
                            }
                        }
                        return sec_tag_str;
                    break;
                    default:
                    break;
                }
                return '';
            break;
            case 'action':
                var current_item, // 区分不同类的标签，因为所有页面上显示的标签共用一个事件监听
                target_item, // 当前被点击的元素
                tag_node, // 用于保存当前标签的标题及下拉列表，用于交互使用
                match, // 用于标识当前是一级还是二级标签
                current_class, // 当前被点击地元素的类名
                p_id, // 当前操作的标签的id
                one_id, // 当前操作的标签所属一级标签的id
                is_multi, // 一级标签默认单选，此用来标明一级为多选
                is_single; // 二级标签默认多选，此用来标明二级为单选，（暂时未用到）
                e = arguments[1];
                current_item = e.currentTarget;
                tag_node=$(current_item).find('.tag_tit,.tag_list');
                if(tag_node.length<2){ // 页面html结构不完整退出交互
                    return ;
                }
                target_item = e.target;
                is_multi = /multi/.test(tag_node[1].className);
                current_class = target_item.className;
                p_id = current_item.id;
                match = current_class.match(/tag_tit|tag_item|sec_item/);
                switch(match&&match[0]){
                    case 'tag_tit': // 点击标签title 二种情况，一为未展开列表，则民开列表，二若已展开列表则隐藏列表，并更新是多选的一级标签的title
                        var tmp_disp = tag_node[1].style.display;
                        tag_node[1].style.display=tmp_disp=='block'?'none':'block';
                        if(is_multi&&tmp_disp==='block'){
                            var tmp_one_tag;
                            tmp_one_tag = [].map.call($(tag_node[1]).find('.selected'),function(){
                                return arguments[0].innerText;
                            });
                            tag_node[0].innerHTML = tmp_one_tag&&tmp_one_tag.length?tmp_one_tag.join():'请选择标签';
                        }
                    break;
                    case 'tag_item': // 点击的是一级标签
                        one_id = target_item.id;
                        if(is_multi){
                            if(/default/.test(current_class))
                            {
                                select_arr[p_id].one_tag = ''
                                $(tag_node[1]).find('.tag_item').removeClass('selected');
                                target_item.className = current_class+' selected';
                                tag_node[0].innerHTML = target_item.innerText;
                                tag_node[1].style.display='none';
                                $(current_item).find('.sec_tag >span').each(function(){this.style.display= 'none';});
                            }
                            else if(/selected/.test(current_class))// 多选一级存成一个数组
                            { 
                                target_item.className = current_class.replace(/ selected/,''); // 去掉已选
                                select_arr[p_id].one_tag = select_arr[p_id].one_tag.replace(new RegExp(','+one_id+',','g'),''); // 去除slect_arr里的记录
                                if(/sec/.test(current_class))
                                {
                                    $(current_item).find('#tag_'+one_id).hide();  // 若二级标签所属的一级标签没有选中则隐藏
                                }
                            }else
                            {
                                target_item.className = current_class+' selected';
                                select_arr[p_id].one_tag+=','+one_id+','  // 添加select_arr里的记录
                                if(/sec/.test(current_class))
                                {
                                    $(current_item).find('#tag_'+one_id).show();  
                                }
                            }
                            $(tag_node[1]).find('#default').removeClass('selected');
                        }else{  
                            select_arr[p_id].one_tag=one_id ; // 单选一级直接存id 
                            tag_node[0].innerHTML = target_item.innerText;
                            $(tag_node[1]).find('.tag_item').removeClass('selected');
                            target_item.className += ' selected';
                            tag_node[1].style.display='none';
                            $(current_item).find('.sec_tag >span').each(function(){this.style.display= 'none';}); // 单选每次清除二级标签的显示
                            if(/sec/.test(current_class)){
                                $(current_item).find('#tag_'+one_id).show();
                            }
                        }
                    break;
                    case 'sec_item': // 点击的是二级标签 默认是多选
                        sec_id = target_item.id;
                        one_id = target_item.parentNode.id.replace('tag_','');
                        is_single = /single/.test(target_item.parentNode.className);
                        is_select = /on/.test(current_class);
                        if(is_single){  //二级标签如果单选，去除所有已选标记
                            $(current_item).find('.sec_tag >span .sec_item').removeClass('on');
                        }else{
                            if(is_select){
                                if($(target_item.parentNode).find('.sec_item.on').length==1){
                                    alert('二级标签必须选中一项！');
                                    return ;
                                }
                            }
                        }
                        // 交替变化已选未选
                        if(is_select){
                            target_item.className = current_class.replace(/ on/,'');
                            select_arr[p_id]['sec_tag'][one_id][sec_id]['select']=false;
                        }else{
                            target_item_name = target_item.innerText;
                            if(/无隐私/.test(target_item_name))
                            {
                                $(current_item).find('.sec_tag >span .sec_item').removeClass('on');
                                //clear select_arr selected value and prevent from posting extra info to server
                                select_arr[p_id]['sec_tag'][one_id].map(function(v,i){
                                    v['select'] = false;
                                    return v;
                                });
                            }
                            else
                            {
                                var privacy = $(current_item).find('.sec_tag >span .privacy');
                                if(privacy.length > 0)
                                {
                                    privacy.removeClass('on');
                                    var privacy_len = select_arr[p_id]['sec_tag'][one_id].length;
                                    select_arr[p_id]['sec_tag'][one_id][privacy_len-1]['select']=false;
                                }
                            }
                            target_item.className = current_class+' on';
                            select_arr[p_id]['sec_tag'][one_id][sec_id]['select']=true;
                        }
                    break;
                    default:
                    break;
                }
            break;
            case 'init_set': // 初始化标签 一是初始化显示状态，二是初始化记录变量
                var tags,tmp_html;
                tags = $('.tags');
                tags.each(function(){
                    var current_tag,tag_id,jqery_dom,one_tag_pos={},item,sec_tags;
                    tag_id = this.id;
                    current_tag	= tag_arr[tag_id]; // 上次的记录
                    jqery_dom = $(this);
                        tmp_html = current_tag.one_tag.join();
                    jqery_dom.find('.tag_tit').html(tmp_html?tmp_html:'请选择标签');
                    jqery_dom.find('.tag_list li').each(function(){
                        if(current_tag.one_tag.indexOf(this.innerText.replace(/\s/g,''))!=-1){  // 初始化一级的选中状态
                            this.className+=' selected';
                        }
                    });
                    select_arr[tag_id].one_tag = current_tag.one_tag.map(function(){  // 初始化select_arr结构
                        var one_tag_name = arguments[0],tag_pos;
                        tag_pos= all_tags[tag_id].tags.indexOf(one_tag_name);  // 将名称转化为id
                        tag_pos==-1?all_tags[tag_id].tags.every(function(){ // 若没找到id,则认为是包含二级，包含二级的一级标签是一个数组，查找数组
                            var array_item=arguments[0];
                            if(Object.prototype.toString.call(array_item)==='[object Array]'&&array_item.indexOf(one_tag_name)!=-1){
                                tag_pos = arguments[1];
                            }
                            return true;
                        }):'';
                        if(tag_pos!=undefined&&tag_pos!=-1){
                            one_tag_pos[one_tag_name] = tag_pos;
                            return ','+tag_pos+',';
                        }else{
                            return '';
                        }
                    }).join('');
                    for(item in current_tag.sec_tag){  //初始化二级标签的参数
                        sec_tags = current_tag.sec_tag[item];
                        if(current_tag.sec_tag.hasOwnProperty(item)){
                            jqery_dom.find('#tag_'+one_tag_pos[item]+',#tag_'+one_tag_pos[item]+' >span').each(function(){
                                if(/tag_/.test(this.id)){
                                    this.style.display='inline-block';
                                    return true;
                                }
                                sec_tag_name_test = this.innerText.replace(/\s/g,'');
                                if(sec_tags.indexOf(sec_tag_name_test)==-1)
                                {
                                    this.className = this.className.replace(/on/ig,'');
                                    select_arr[tag_id]['sec_tag'][one_tag_pos[item]][this.id]['select']=false;
                                }
                                else if(/无隐私/.test(sec_tag_name_test))
                                {
                                    this.className = this.className + ' on';
                                    select_arr[tag_id]['sec_tag'][one_tag_pos[item]][this.id]['select']= true;
                                }
                            });
                        }
                    }
                });
            break;
            case 'encode_string': //将select_arr转成数据库里保存的结构
                tag_obj={};
                select_arr.map(function(){
                    var tag_item= arguments[0],tag_index=arguments[1],all_sec_tag={};
                    tag_obj[tag_item.key]={
                        name:tag_item.name
                    }
                    try{
                        tag_obj[tag_item.key].tag=tag_item.one_tag.match(/\d+/g).map(function(){
                            var tmp_tag,tmp_sec=[],one_tag=arguments[0];
                            tmp_tag = all_tags[tag_index]['tags'][one_tag];
                            if(Object.prototype.toString.call(tmp_tag)==='[object Array]'){
                                tag_item.sec_tag[one_tag].map(function(){
                                    var tmp_sec_tag=arguments[0];
                                    if(tmp_sec_tag.select){
                                        tmp_sec.push(tmp_sec_tag.name);
                                    }
                                    return ''
                                });
                                all_sec_tag[tmp_tag[1]] = tmp_sec;
                                tmp_tag = tmp_tag[1];
                            }
                            return tmp_tag;
                        })
                    }catch(err){
                        tag_obj[tag_item.key].tag=[];
                    }
                    tag_obj[tag_item.key].sub_tag=all_sec_tag;
                    return '';
                });
                //console.log(JSON.stringify(tag_obj));
                return JSON.stringify(tag_obj);
            break;
            case 'decode_string':  // 转化数据库里存储的数据格式
                for(var i in tag_str){  
                    tag_arr.push({key:i,name:tag_str[i].name,one_tag:tag_str[i].tag,sec_tag:tag_str[i].sub_tag});
                }
            break;
            default:
            break;
        }
    })(['init']);
}

window.addEventListener('load', function(){
    event_bind();
    $('#leftnav h3').click();
    var tmp = $('#leftnav .active');
    if(tmp.length==0){
       $('#leftnav h3')[0].click();
       $('#leftnav h3')[1].click();
    }else{
       tmp.parent().prev().click();
       tmp.parent().prev().parent().prev().click();
    }

    changeSortDefault();
    change_action();
    try{
        label_in_turn();
        if(need_push_method){
            push_method('init');
        }
    }catch(err){

    }
    /*others*/
    /* image preview */
    var tmp2 = $('.icon_path .file-upload>a'), tmp3 = $('#uploadsmallimg'), tmp4 = $('#imgpreview'), tmpApplist = $('#id_app_list'), tmp_unique_token = $('#id_unique_token');
    if(tmpApplist.length > 0) {
        tmpApplist[0].disabled = true;
        $('form').bind('submit',function(){
            $(this).find(':input').removeAttr('disabled');
        });
    }
    if(tmp_unique_token.length > 0) {
        if (tmp_unique_token.val() != "" && tmp_unique_token.val() != undefined) {
            tmp_unique_token[0].disabled = true;
        }
        $('form').bind('submit',function(){
            $(this).find(':input').removeAttr('disabled');
        });
    }
    if(tmp2.length!=0&&tmp3.length!=0&&tmp2.attr('href')){
        tmp4[0].src = tmp3[0].src = tmp2[0].href;
        tmp3.mouseover(function(){tmp4.css('display', 'block')});
        tmp3.mouseout(function(){tmp4.css('display', 'none')});
    }else if(tmp3.length!=0){
         tmp2 = $('.icon_path>div>p:nth-child(2)');
        if(tmp2.length){
           tmp3[0].src = 'http://estoredwnld7.189store.com/' + tmp2.text();
        }
    }
    tmp_save_btn = $('#list_save_btn');
    if(tmp_save_btn.length==1){
       $('.top_toolbar').prepend('<input type="submit" name="_save" class="default" value="保存" onclick="$(\'#list_save_btn\').click();" />')
    }else{
       $('.object-tools').addClass('toR')
    }

    /* set changelist filter h3 innerText */
    $('#changelist-filter h3').each(function(){
        var text = $(this).next().find('li.selected').text().replace(/\s/g,"");
        if(text!='所有'){
            this.innerText = text;
        }
    });
    $('.vForeignKeyRawIdAdminField').next().next().each(function(){
        var href_value = this.getAttribute('href');
        if(/rtn_url/.test(href_value)){
            href_value += '?rtn_url=' + $('input[name="url"]').val().replace(/\/(\w+)\/$/, '/');
            this.setAttribute('href',href_value);
        }
    });
    // for action confirm
    // change sync btn actions
    var sync_btn = $('[href="syncto"]');
    if(sync_btn.length>0){
        sync_btn[0].setAttribute('onclick',"event.preventDefault();sync_to_line();");
    }
    extra_confirm();
});

