frappe.listview_settings['Availo'] = {
    onload: function(list) {
        list.page.add_inner_button(
            __('Sync'),
            function() {
                frappe.prompt(
                    [
                        {
                            fieldname: 'date_from',
                            fieldtype: 'Date',
                            label: __('From Date'),
                            'default': 'Today',
                            reqd: 1,
                            bold: 1
                        },
                        {
                            fieldname: 'date_to',
                            fieldtype: 'Date',
                            label: __('To Date'),
                            'default': 'Today',
                            reqd: 1,
                            bold: 1
                        },
                    ],
                    function(values) {
                        frappe.call({
                            method: 'masar_availo.utils.enqueue_sync_attendance',
                            args: {
                                date_from: values.date_from,
                                date_to: values.date_to,
                            },
                            callback: function(ret) {},
                        });
                        frappe.show_alert({
                            message: __('Sync has started in the background.'),
                            indicator: 'green',
                        });
                        frappe.socketio.init();
                        frappe.realtime.on('attendance_synced', function() {
                            list.refresh();
                        });
                    },
                    __('Sync Date Range'),
                    __('Sync')
                );
            },
            null,
            'primary'
        );
        list.page.add_inner_button(
            __('Insert CheckIn'),
            function() {
                frappe.call({
                    method: 'masar_availo.utils.sync_checkin',
                    callback: function(ret) {},
                });
            },
            null,
            'primary'
        );
    }
};


// frappe.listview_settings['Availo'] = {
//     onload: function(list) {
//         list.page.add_inner_button(
//             __('Insert CheckIn'),
//             function() {
//                 frappe.call({
//                     method: 'masar_availo.utils.sync_checkin',
//                     callback: function(ret) {},
//                 });
//             },
//             null,
//             'primary'
//         );
//     }
// };
