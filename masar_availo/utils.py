#from future import unicode_literals
import frappe, erpnext
from frappe.utils import flt, cstr, nowdate, comma_and
from frappe import throw, msgprint, _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
import requests , json,datetime
from datetime import datetime
from frappe.utils import get_request_session
from frappe.utils import(
	formatdate,
	getdate,
	DATE_FORMAT
)

@frappe.whitelist(allow_guest=True)
def enqueue_sync_attendance(date_from, date_to):
    date_from = str(date_from)
    date_to = str(date_to)
    date_difference = (datetime.strptime(str(date_to), '%Y-%m-%d') - datetime.strptime(str(date_from), '%Y-%m-%d')).days
    if date_difference <2:
        sync_attendance(date_from, date_to)
        frappe.msgprint('Sync Complete')
    else:
        frappe.enqueue(
            method='masar_availo.utils.sync_attendance',
            queue= 'long',
            timeout= 5000,
            date_from = date_from, 
            date_to = date_to
        )
        frappe.msgprint('Job is working in Background')
def sync_attendance(date_from, date_to):
    url = "https://availo-integrationapi.availo.app:8443/api/ExternalReports/GetWorkingReportAllEmployee"
    payload = {
        "pageNumber": 0,
        "pageSize": 0,
        "data": {
            "timeZoneOffset": -120,
            "fromDate": date_from,
            "toDate": date_to,
            "displayType": 1
        }
    }
    headers = {
        "Language": "0",
        "service_key": "52B5F329-B9AE-446C-9260-B624FD1569CF",
        "authentication_type": "service_key",
        "Content-Type": "application/json"        
    }
    
    request_return =  requests.post(url , json=payload, headers=headers , timeout=(300, 2000)) 
    response = request_return.json()
    status_code = request_return.status_code
    response = parse_json(response)
    if status_code not in [200, 201]:
        frappe.throw(_("The response was not resolved."))
        return False

    if not isinstance(response, dict):
       frappe.throw(_("The response received from API is invalid."))
    data = response["data"]
    lst = data['list']
    total_count_of_lst = len(data['list'] )
    store_attendance(lst , total_count_of_lst)  
   

def store_attendance(data , total_count_of_lst):
    for item in range(total_count_of_lst):
        add_attendance(data[item])
def add_attendance(data):
    total_count_of_employee_lst = data["workReportTransactions"]["totalCount"] ## 31 
    for month_dates in range(total_count_of_employee_lst):
        transaction = data["workReportTransactions"]["list"][month_dates]
        entry = {	
                "job_code": data["jobNumber"],
                "employee": data["userName"],
                "employee_name": data["fullName"],
                "total_plan_work_hour_during_interval":data["totalPlanWorkHourDuringInterval"],
                "total_hours_work_during_interval":data["totalHoursWorkDuringInterval"],
                "total_checkin_late_hours_during_interval":data["totalCheckInLateHoursDuringInterval"],
                "total_checkout_late_hours_during_interval":data["totalCheckOutLateHoursDuringInterval"],
                ##### in workReportTransactions now 
                "selected_date":transaction["selectedDate"],
                "status":transaction["status"],
                "working_hours":transaction["workingHours"],
                "checkin_date":transaction["checkInDate"],
                "sub_type_id":transaction["subTypeID"],
                "checkin_access_gate_name_ar":transaction["checkInAccessGateNameAr"],
                "checkin_access_gate_name_en":transaction["checkInAccessGateNameEn"],
                "checkout_date":transaction["checkOutDate"],
                "checkout_date_time":transaction["checkOutDateTime"],
                "checkout_access_gate_name_ar":transaction["checkOutAccessGateNameAr"],
                "checkout_access_gate_name_en":transaction["checkOutAccessGateNameEn"],
                "actual_working_hours":transaction["actualWorkingHours"],
                "session_total_checkin_late_hours":transaction["sessionTotalCheckInLateHours"],
                "session_total_checkout_late_hours":transaction["sessionTotalCheckOutLateHours"],
                "session_total_shortes_hours":transaction["sessionTotalShortesHours"],
                "session_total_overtime_hours":transaction["sessionTotalOverTimeHours"],
                "session_total_overtime_extra_hours":transaction["sessionTotalOverTimeExtraHours"],
                "session_total_holiday_overtime_hours":transaction["sessionTotalHolidayOverTimeHours"],
                "first_shift_start_time":transaction["firstShiftStartTime"],
                "first_shift_end_time":transaction["firstShiftEndTime"],
                "sec_shift_start_time":transaction["secShiftStartTime"],
                "sec_shift_end_time":transaction["secShiftEndTime"],
            }
        # Insert the attendance entry
        frappe.new_doc("Availo").update(entry).insert(ignore_permissions=True, ignore_mandatory=True)

def error(text, throw=True):
    if not isinstance(text, str):
        text = to_json(text, str(text))
    frappe.log_error("Availo", text)
    if throw:
        frappe.throw(text, title="Availo")

def parse_json(data, default=None):
    if not isinstance(data, str):
        return data
    if default is None:
        default = data
    try:
        return json.loads(data)
    except Exception:
        return default

def to_json(data, default=None):
    if isinstance(data, str):
        return data
    if default is None:
        default = data
    try:
        return json.dumps(data)
    except Exception:
        return default



@frappe.whitelist()
def enqueue_sync_checkin(date_from, date_to):
    date_from = str(date_from)
    date_to = str(date_to)
    date_difference = (datetime.strptime(str(date_to), '%Y-%m-%d') - datetime.strptime(str(date_from), '%Y-%m-%d')).days
    if date_difference <2:
        checkin_insert_data(date_from, date_to)
    else:
        frappe.enqueue(
            method='masar_availo.utils.checkin_insert_data',
            queue= 'long',
            timeout= 5000,
            date_from = date_from,
            date_to = date_to
        )
        frappe.msgprint('Job is working in Background')     
        
def checkin_insert_data(date_from, date_to):
    data = frappe.db.sql("""
        SELECT 
            ta.name, ta.status,
            ta.job_code,
            ta.selected_date,
            ta.checkin_date,
            ta.checkout_date,
            ta.checkin_access_gate_name_en,
            ta.checkout_access_gate_name_en,
            te.default_shift,
            tsa.shift_type
        FROM 
            `tabAvailo` ta
        LEFT JOIN 
            `tabEmployee` te ON te.name = ta.job_code
        LEFT JOIN 
            `tabShift Assignment` tsa ON tsa.employee = te.name
        WHERE 
            ta.status NOT IN ('Absence', '_') 
            AND ta.checkin_date != '-' 
            AND ta.checkout_date != '-'
            AND ta.selected_date BETWEEN %s AND %s
    """, (date_from, date_to), as_dict=True)
    
    for record in data:
        availo = record["name"]
        employee = record['job_code']
        selected_date_sql = record['selected_date']
        checkin_date_sql = record['checkin_date']
        checkout_date_sql = record['checkout_date']
        checkin_access_gate = record['checkin_access_gate_name_en']
        checkout_access_gate = record['checkout_access_gate_name_en']
        selected_datetime = datetime.strptime(selected_date_sql, '%Y-%m-%dT%H:%M:%S')
        checkin_time = datetime.combine(
            selected_datetime.date(), 
            datetime.strptime(checkin_date_sql, '%H:%M').time()
        )
        checkout_time = datetime.combine(
            selected_datetime.date(), 
            datetime.strptime(checkout_date_sql, '%H:%M').time()
        )
        emp_shift = record['default_shift'] or record['shift_type']
        if not frappe.db.exists("Employee Checkin", {
            "employee": employee,
            "time": checkin_time,
            "log_type": "IN"
        }):
            in_entry = {
                "employee": employee,
                "availo": availo,
                "log_type": "IN",
                "time": checkin_time,
                "device_id": checkin_access_gate,
                "shift_type": emp_shift,
                "latitude": 0, 
                "longitude": 0 
            }
            frappe.new_doc('Employee Checkin').update(in_entry).save()
        if not frappe.db.exists("Employee Checkin", {
            "employee": employee,
            "time": checkout_time,
            "log_type": "OUT"
        }):
            out_entry = {
                "employee": employee,
                "availo": availo,
                "log_type": "OUT",
                "time": checkout_time,
                "device_id": checkout_access_gate,
                "shift_type": emp_shift, 
                "latitude": 0, 
                "longitude": 0 
            }
            frappe.new_doc('Employee Checkin').update(out_entry).save()
    frappe.db.commit()
    frappe.msgprint("Sync completed.")