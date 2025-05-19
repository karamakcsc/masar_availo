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
                            'default': frappe.datetime.get_today(),
                            reqd: 1,
                            bold: 1
                        },
                        {
                            fieldname: 'date_to',
                            fieldtype: 'Date',
                            label: __('To Date'),
                            'default': frappe.datetime.get_today(),
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
                            callback: function(ret) {   
                                // Handle the callback if needed
                            },
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
                frappe.prompt(
                    [
                        {
                            fieldname: 'date_from',
                            fieldtype: 'Date',
                            label: __('From Date'),
                            'default': frappe.datetime.get_today(),
                            reqd: 1,
                            bold: 1
                        },
                        {
                            fieldname: 'date_to',
                            fieldtype: 'Date',
                            label: __('To Date'),
                            'default': frappe.datetime.get_today(),
                            reqd: 1,
                            bold: 1
                        },
                    ],
                    function(values) {
                        frappe.call({
                            method: 'masar_availo.utils.enqueue_sync_checkin',
                            args: {
                                date_from: values.date_from,
                                date_to: values.date_to,
                            },
                            callback: function(ret) {
                                // Handle the callback if needed
                            },
                        });
                        frappe.socketio.init();
                        frappe.realtime.on('attendance_synced', function() {
                            list.refresh();
                        });
                    },
                    __('Insert CheckIn Date Range'),
                    __('Insert CheckIn')
                );
            },
            null,
            'primary'
        );
    }
};
