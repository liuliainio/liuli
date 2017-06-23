(function ($) {
    $.fn.DateRange = function (options) {
        var
            today = new Date(),
            one_day = 1000*60*60*24,

            defaults = {
                value: "[d30:d1]",
                onSelect: function(){},
                locStrings: {
                    today: gettext('Today'),
                    yesterday: gettext('Yesterday'),
                    last7Days: gettext('Last 7 Days'),
                    last30Days: gettext('Last 30 Days'),
                    last90Days: gettext('Last 90 Days'),
                    prevMonth: gettext('Previous Month'),
                    prevQuarter: gettext('Previous Quarter'),
                    month2Date: gettext('Month to Date'),
                    quarter2Date: gettext('Quarter to Date'),
                    customDate: gettext('Custom Date'),

                    startText: gettext('Start'),
                    endText: gettext('End'),
                    submitText: gettext('Submit'),
                    cancelText: gettext('Cancel')
                }
            },

            attach = function(inst) {
                var tpl = '' +
                    '<select>' +
                        '<option class="custom_range" disabled="disabled" style="display:none;"></option>' +
                        '<option value="[d0:d0]">' + inst.locStrings.today + '</option>' +
                        '<option value="[d1:d1]">' + inst.locStrings.yesterday + '</option>' +
                        '<option value="[d7:d1]">' + inst.locStrings.last7Days + '</option>' +
                        '<option value="[d30:d1]">' + inst.locStrings.last30Days + '</option>' +
                        '<option value="[d90:d1]">' + inst.locStrings.last90Days + '</option>' +
                        '<option value="[m1:m0)">' + inst.locStrings.prevMonth + '</option>' +
                        '<option value="[q1:q0)">' + inst.locStrings.prevQuarter + '</option>' +
                        '<option value="[m0:d0]">' + inst.locStrings.month2Date + '</option>' +
                        '<option value="[q0:d0]">' + inst.locStrings.quarter2Date + '</option>' +
                        '<option value="custom">' + inst.locStrings.customDate + '</option>' +
                    '</select>' +
                    '<span class="date_range_start_end" style="display:none;">' +
                        '<span>' +
                            '<span class="close"></span>' +
                            '<table width="100%">' +
                                '<tr>' +
                                    '<td align="left">' + inst.locStrings.startText + '</td>' +
                                    '<td align="left">' + inst.locStrings.endText + '</td>' +
                                '</tr>' +
                                '<tr>' +
                                    '<td align="left"><input type="text" class="start_date" name="start_date" readonly="readonly" /></td>' +
                                    '<td align="left"><input type="text" class="end_date" name="end_date" readonly="readonly" /></td>' +
                                '</tr>' +
                                '<tr>' +
                                    '<td style="vertical-align:top;"><div class="datepicker start_date"></div></td>' +
                                    '<td style="vertical-align:top;"><div class="datepicker end_date"></div></td>' +
                                '</tr>' +
                                '<tr>' +
                                    '<td colspan="2" align="center">' +
                                        '<a href="javascript:void(0)" class="submit">' + inst.locStrings.submitText + '</a>' +
                                        '&nbsp;&nbsp;' +
                                        '<a href="javascript:void(0)" class="close">' + inst.locStrings.cancelText + '</a>' +
                                    '</td>' +
                                '</tr>' +
                            '</table>' +
                        '</span>' +
                    '</span>';

                $(tpl).appendTo(inst.target);
            },

            bindEvent = function(inst) {
                var target = inst.target;
                var customDatesChooser = $(".date_range_start_end", target);

                inst.selector = $("select", target);
                inst.selector.val(inst.value);

                jQuery(".datepicker", target).datepicker({
                    dateFormat: 'yy/mm/dd',
                    maxDate: new Date(),
                    onSelect: function(dateText, inst) {
                        element = jQuery(this);
                        if(element.hasClass('start_date')) {
                            jQuery('.datepicker.end_date', customDatesChooser).datepicker("option", "minDate", new Date(dateText));
                            jQuery('input.start_date', customDatesChooser).val(dateText);
                        }
                        if(element.hasClass('end_date')) {
                            jQuery('.datepicker.start_date', customDatesChooser).datepicker("option", "maxDate", new Date(dateText));
                            jQuery('input.end_date', customDatesChooser).val(dateText);
                        } 
                    }
                });

                inst.selector.bind('mouseover', function() {
                    // store the current value for further display usage
                    var element = $(this);
                    if (!customDatesChooser.is(":visible")) {
                        inst.value = element.val();
                    }
                });

                inst.selector.bind('change', function() {
                    if(inst.selector.val() == 'custom') {
                        var dates = getDateRange(inst.value);

                        var start_datepicker = $(".datepicker.start_date", customDatesChooser);
                        start_datepicker.datepicker("setDate", dates[0]);
                        start_datepicker.datepicker("option", "maxDate", dates[1]);

                        var end_datepicker = $(".datepicker.end_date", customDatesChooser);
                        end_datepicker.datepicker("setDate", dates[1]);
                        end_datepicker.datepicker("option", "minDate", dates[0]);

                        $('input.start_date', customDatesChooser).val(strDate(dates[0]));
                        $('input.end_date', customDatesChooser).val(strDate(dates[1]));

                        customDatesChooser.show();
                   } else {
                        customDatesChooser.hide();
                        inst.value = inst.selector.val();
                        inst.onSelect.call(inst.target, getDateRange(inst.value));
                   }
                });

                $('a', target).button();

                $('.close', target).click(function() {
                    customDatesChooser.hide();
                    inst.selector.val(inst.value);
                });

                $(".submit", target).click(function() {
                    setDateRange(
                            inst,
                            $("input.start_date", customDatesChooser).val(),
                            $("input.end_date", customDatesChooser).val()
                        );

                    customDatesChooser.hide();
                    inst.onSelect.call(inst.target, getDateRange(inst.value));
                });
            },

            setDateRange = function(inst, startDate, endDate) {
                var start = new Date(startDate);
                var end = new Date(endDate);

                var startDays = Math.floor((today.getTime() - start.getTime()) / one_day);
                var endDays = Math.floor((today.getTime() - end.getTime()) / one_day);
                var valueRange = "[d" + startDays + ":d" + endDays + "]";

                inst.selector.val(valueRange);
                inst.value = valueRange;

                // custom date range needs showup
                if (inst.selector.val() != valueRange) {
                    var displayRange = strDate(start) + " - " + strDate(end);
                    var customRangeOption = $('option.custom_range', inst.selector);

                    customRangeOption.attr('value', valueRange);
                    customRangeOption.removeAttr('disabled');
                    customRangeOption.html(displayRange);
                    customRangeOption.show();
                    inst.selector.val(valueRange);
                }
            },

            getDateRange = function(strRange) {
                var range_length = strRange.length;
                var left_contain = strRange.slice(0, 1) != "(";
                var right_contain = strRange.slice(range_length - 1) != ")";
                var tripped_range = strRange.slice(1, range_length - 1);
                var dates = tripped_range.split(':', 2);

                dates[0] = shortcutToDate(dates[0], true, left_contain);
                dates[1] = shortcutToDate(dates[1], false, right_contain);

                return dates;
            },

            shortcutToDate = function(shortcut, forward, contain) {
                var mode = shortcut.slice(0, 1);
                var range = parseInt(shortcut.slice(1));
                var today = new Date();
                var year = today.getFullYear();
                var month = today.getMonth();
                var date = today.getDate();

                switch(mode) {
                    case "d": var target_date = new Date(year, month, date - range); break;
                    case "m": var target_date = new Date(year, month - range, 1); break;
                    case "q": var target_date = new Date(year, month - month % 3 - range * 3 , 1); break;
                }
                return contain ? target_date : oneDayShift(target_date, forward);
            },

            oneDayShift = function(date, forward) {
                if (forward) {
                    date.setDate(date.getDate() + 1);
                } else {
                    date.setDate(date.getDate() - 1);
                }
                return date;
            },

            strDate = function(date) {
                return date.getFullYear() + "/" +
                    (date.getMonth() + 1) + "/" +
                    date.getDate();
            },

            getInst = function(target) {
                return target.data("daterange");
            },

            initial = function(target, options) {
                inst = $.extend({}, defaults, options||{});
                inst.target = target;

                target.data("daterange", inst);

                attach(inst);
                bindEvent(inst);

                if ("startDate" in options
                    && "endDate" in options) {
                    setDateRange(inst, options.startDate, options.endDate);
                }
            };

        var otherArgs = arguments[1];

        this.each(function(){
            var target = $(this);

            if (typeof options == 'string') {
                ;// TODO: some API could provide here
            } else {
                initial(target, options);
            }
        });

        return this;
    };
})(jQuery);
