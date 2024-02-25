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

########This Code is working
# @frappe.whitelist()
# def receive_post_data():
# 	url = "https://availo-testingintegrationapi.t2.sa/api/ExternalReports/GetWorkingReportAllEmployee"
#
# 	doc = json.dumps({
# 	  "pageNumber": 1,
# 	  "pageSize": 50,
# 	  "data": {
# 		"timeZoneOffset": -120,
# 		"fromDate": "2020-10-10",
# 		"toDate": "2020-11-22",
# 		"displayType": 1
# 	  }
# 	})
# 	headers = {
# 	  'Language': '0',
# 	  'service_key': '5bf66aea-0de5-4b6a-826e-897e59c2391d',
# 	  'authentication_type': 'service_key',
# 	  'account_code': 'QA',
# 	  'Content-Type': 'application/json'
# 	}
#
# 	response = requests.request("POST", url, headers=headers, data=doc)
# 	local_item=json.loads(response._content)
# 	# print(local_item["data"].get("list")[0].get("jobNumber", ""))
# 	data=local_item["data"].get("list")
# 	for i in range(len(data)):
# 		for j in range(len(data[i].get("workReportTransactions").get("list"))):
# 			entry = {
# 				"job_code": data[i].get("jobNumber", ""),
# 				"employee": data[i].get("userName", ""),
# 				"employee_name": data[i].get("fullName", ""),
# 				"total_plan_work_hour_during_interval":data[i].get("totalPlanWorkHourDuringInterval", ""),
# 				"total_hours_work_during_interval":data[i].get("totalHoursWorkDuringInterval", ""),
# 				"total_checkin_late_hours_during_interval":data[i].get("totalCheckInLateHoursDuringInterval", ""),
# 				"total_checkout_late_hours_during_interval":data[i].get("totalCheckOutLateHoursDuringInterval", ""),
# 				"status":data[i].get("workReportTransactions").get("list")[j].get("status", ""),
# 				"selected_date":data[i].get("workReportTransactions").get("list")[j].get("selectedDate", ""),
# 				"working_hours":data[i].get("workReportTransactions").get("list")[j].get("workingHours", ""),
# 				"checkin_date":data[i].get("workReportTransactions").get("list")[j].get("checkInDate", ""),
# 				"sub_type_id":data[i].get("workReportTransactions").get("list")[j].get("subTypeID", ""),
# 				"checkin_access_gate_name_ar":data[i].get("workReportTransactions").get("list")[j].get("checkInAccessGateNameAr", ""),
# 				"checkin_access_gate_name_en":data[i].get("workReportTransactions").get("list")[j].get("checkInAccessGateNameEn", ""),
# 				"checkout_date":data[i].get("workReportTransactions").get("list")[j].get("checkOutDate", ""),
# 				"checkout_date_time":data[i].get("workReportTransactions").get("list")[j].get("checkOutDateTime", ""),
# 				"checkout_access_gate_name_ar":data[i].get("workReportTransactions").get("list")[j].get("checkOutAccessGateNameAr", ""),
# 				"checkout_access_gate_name_en":data[i].get("workReportTransactions").get("list")[j].get("checkOutAccessGateNameEn", ""),
# 				"actual_working_hours":data[i].get("workReportTransactions").get("list")[j].get("actualWorkingHours", ""),
# 				"session_total_checkin_late_hours":data[i].get("workReportTransactions").get("list")[j].get("sessionTotalCheckInLateHours", ""),
# 				"session_total_checkout_late_hours":data[i].get("workReportTransactions").get("list")[j].get("sessionTotalCheckOutLateHours", ""),
# 				"session_total_shortes_hours":data[i].get("workReportTransactions").get("list")[j].get("sessionTotalShortesHours", ""),
# 				"session_total_overtime_hours":data[i].get("workReportTransactions").get("list")[j].get("sessionTotalOverTimeHours", ""),
# 				"session_total_overtime_extra_hours":data[i].get("workReportTransactions").get("list")[j].get("sessionTotalOverTimeExtraHours", ""),
# 				"session_total_holiday_overtime_hours":data[i].get("workReportTransactions").get("list")[j].get("sessionTotalHolidayOverTimeHours", ""),
# 				"first_shift_start_time":data[i].get("workReportTransactions").get("list")[j].get("firstShiftStartTime", ""),
# 				"first_shift_end_time":data[i].get("workReportTransactions").get("list")[j].get("firstShiftEndTime", ""),
# 				"sec_shift_start_time":data[i].get("workReportTransactions").get("list")[j].get("secShiftStartTime", ""),
# 				"sec_shift_end_time":data[i].get("workReportTransactions").get("list")[j].get("secShiftEndTime", ""),
# 			}
#
# 			(frappe.new_doc("Availo")
# 				.update(entry)
# 				.insert(ignore_permissions=True, ignore_mandatory=True))
# 	return


# import json
# import frappe
# from masar_availo import get_request_session  # Assuming you have a module with this function

# Decorator to allow guest access
@frappe.whitelist(allow_guest=True)
def enqueue_sync_attendance(date_from, date_to):
    date_from = str(date_from)
    date_to = str(date_to)
    sync_attendance(date_from, date_to)
    # Enqueue the sync_attendance method for asynchronous processing
    # frappe.enqueue(
    #     method=sync_attendance,
    #     queue="long",
    #     is_async=True,
    #     enqueue_after_commit=True,
    #     date_from=date_from,
    #     date_to=date_to
    # )
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
        # "account_code": "MID",
        "Content-Type": "application/json"        
    }

    try:
        # Send a POST request to the external API
        # request = get_request_session().request("POST", url, data=payload, headers=headers)
        # status_code = request.status_code
        # response = request.json()
        request_return =  requests.post(url , json=payload, headers=headers) 
        response = request_return.json()
        status_code = request_return.status_code

    except Exception as exc:
        # Log and handle exceptions
        error(str(exc))
    
    # Parse the JSON response
    response = parse_json(response)
    # Check the status code and response validity
    if status_code not in [200, 201]:
        error(_("The response was not resolved."))
        return False

    if not isinstance(response, dict):
        error(_("The response received from API is invalid."))

    # data = response.get("data")
    data = response["data"]
    lst = data['list']
    total_count_of_lst = data["totalCount"] 
    if not data or not isinstance(lst, list):
        error(_("The response data list received from API is invalid."))
        return False
    # frappe.msgprint(str(data["totalCount"]))
    # # Store the attendance data
    store_attendance(lst , total_count_of_lst)
    frappe.msgprint("Sync completed.")

def store_attendance(data , total_count_of_lst):
    # frappe.publish_progress(25, title='Some title', description='Some description')
    for item in range(total_count_of_lst):
        # Add each attendance entry
        add_attendance(data[item])
    # Publish a realtime event after committing the changes
    
    # frappe.publish_realtime(
    #     event="attendance_synced",
    #     message={"status": "done"},
    #     after_commit=True
    # )

def add_attendance(data):
    # frappe.msgprint(str(data))
    total_count_of_employee_lst = data["workReportTransactions"]["totalCount"] ## 31 
    for month_dates in range(total_count_of_employee_lst):
    # frappe.msgprint(str(total_count_of_employee_lst) )
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
    # Log the error and optionally throw an exception
    if not isinstance(text, str):
        text = to_json(text, str(text))
    frappe.log_error("Availo", text)
    if throw:
        frappe.throw(text, title="Availo")

def parse_json(data, default=None):
    # Parse JSON data with a fallback value
    if not isinstance(data, str):
        return data
    if default is None:
        default = data
    try:
        return json.loads(data)
    except Exception:
        return default

def to_json(data, default=None):
    # Convert data to JSON with a fallback value
    if isinstance(data, str):
        return data
    if default is None:
        default = data
    try:
        return json.dumps(data)
    except Exception:
        return default



##################### Update CheckIn#### Start Code


# @frappe.whitelist()
# def sync_checkin():
# 	data=frappe.db.sql(f"""SELECT name, job_code, selected_date, checkin_date, checkout_date FROM tabAvailo""",as_dict=True)
# 	for i in range(len(data)):
# 		print(f"checkin_date: {data[i]['checkin_date']}")
# 		print(f"checkout_date: {data[i]['checkout_date']}")
# 		if data[i]['checkin_date']:
# 			try:
# 				checkin_time = datetime.strptime(data[i]["selected_date"][:10] + " " + data[i]["checkin_date"], "%Y-%m-%d %H:%M")
# 			except ValueError:
# 				print(f"Invalid checkin date: {data[i]['checkin_date']}")
# 				continue
# 			entry = {
# 				"employee": data[i]["job_code"],
# 				"time": checkin_time,
# 				"log_type": "IN",
# 				"timestamp": data[i]["selected_date"],
# 				"employee_field_value": "123",
# 				"device_id": data[i]["job_code"]
# 			}
# 			(frappe.new_doc("Employee Checkin")
# 				.update(entry)
# 				.insert(ignore_permissions=True, ignore_mandatory=True))

# 		if data[i]['checkout_date']:
# 			try:
# 				checkout_time = datetime.strptime(data[i]["selected_date"][:10] + " " + data[i]["checkout_date"], "%Y-%m-%d %H:%M")
# 			except ValueError:
# 				print(f"Invalid checkout date: {data[i]['checkout_date']}")
# 				continue
# 			entry = {
# 				"employee": data[i]["job_code"],
# 				"time": checkout_time,
# 				"log_type": "OUT",
# 				"availo": data[i]["name"],
# 				"timestamp":  data[i]["selected_date"],
# 				"employee_field_value": "123",
# 				"device_id": "123"
# 			}
# 			(frappe.new_doc("Employee Checkin")
# 				.update(entry)
# 				.insert(ignore_permissions=True, ignore_mandatory=True))
# 			frappe.db.commit()

##################### Update CheckIn#### End Code




# @frappe.whitelist()
# def sync_checkin(date_from, date_to):
#     date_from = str(date_from)
#     date_to = str(date_to)

#     # Query data from the custom table "tabAvailo"
#     data = frappe.db.sql(
#         """SELECT name, job_code, selected_date, checkin_date, checkout_date FROM tabAvailo
#         WHERE selected_date BETWEEN %s AND %s""",
#         (date_from, date_to),
#         as_dict=True,
#     )

#     for record in data:
#         # print(f"Processing record: {record['name']}")

#         if record['checkin_date']:
#             try:
#                 checkin_time = datetime.strptime(
#                     record["selected_date"][:10] + " " + record["checkin_date"], "%Y-%m-%d %H:%M"
#                 )
#             except ValueError:
#                 frappe.msgprint(f"Invalid check-in date: {record['checkin_date']}")
#                 continue

#             entry = {
#                 "employee": record["job_code"],
#                 "time": checkin_time,
#                 "log_type": "IN",
#                 "timestamp": record["selected_date"],
#                 "employee_field_value": "123",
#                 "device_id": record["job_code"],
#             }

#             try:
#                 new_checkin = frappe.get_doc({"doctype": "Employee Checkin", **entry})
#                 new_checkin.insert(ignore_permissions=True, ignore_mandatory=True)
#             except frappe.exceptions.DuplicateEntryError:
#                 frappe.msgprint(f"Duplicate timestamp for check-in: {record['selected_date']}")
#                 continue

#         if record['checkout_date']:
#             try:
#                 checkout_time = datetime.strptime(
#                     record["selected_date"][:10] + " " + record["checkout_date"], "%Y-%m-%d %H:%M"
#                 )
#             except ValueError:
#                 frappe.msgprint(f"Invalid checkout date: {record['checkout_date']}")
#                 continue

#             entry = {
#                 "employee": record["job_code"],
#                 "time": checkout_time,
#                 "log_type": "OUT",
#                 "availo": record["name"],
#                 "timestamp": record["selected_date"],
#                 "employee_field_value": "123",
#                 "device_id": "123",
#             }

#             try:
#                 new_checkout = frappe.get_doc({"doctype": "Employee Checkin", **entry})
#                 new_checkout.insert(ignore_permissions=True, ignore_mandatory=True)
#                 frappe.db.commit()
#             except frappe.exceptions.DuplicateEntryError:
#                 frappe.msgprint(f"Duplicate timestamp for check-out: {record['selected_date']}")
#                 continue

#     frappe.msgprint("Sync completed.")

# # Usage example:
# # sync_checkin("2023-07-01T00:00:00", "2023-07-31T23:59:59")
    




####################################################################################################
    
@frappe.whitelist()
def enqueue_sync_checkin(date_from, date_to):
    date_from = str(date_from)
    date_to = str(date_to)
    data = frappe.db.sql("""
SELECT 
            
ta.name,ta.status,
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
        left JOIN 
            `tabEmployee` te ON te.name = ta.job_code
        left JOIN 
            `tabShift Assignment` tsa ON tsa.employee = te.name
        WHERE 
           ta.status NOT IN ('Absence', '_') and ta.checkin_date != '-' and ta.checkout_date != '-'
        AND ta.selected_date BETWEEN %s AND %s
    """,(date_from, date_to),as_dict = True)
    emp_shift = None
    for record in data:
        availo               = record["name"]
        employee             = record['job_code']
        selected_date_sql    = record['selected_date']
        checkin_date_sql     = record['checkin_date']
        checkout_date_sql    = record['checkout_date']
        checkin_access_gate  = record['checkin_access_gate_name_en']
        checkout_access_gate = record['checkout_access_gate_name_en']
        selected_datetime = datetime.strptime(selected_date_sql, '%Y-%m-%dT%H:%M:%S')
        checkin_date = datetime.strptime(checkin_date_sql, '%H:%M').time()
        checkout_date = datetime.strptime(checkout_date_sql, '%H:%M').time()
        selected_date = selected_datetime.date() ######### selected date Y-M-D
        checkin_time = datetime.combine(selected_date, checkin_date)
        checkout_time = datetime.combine(selected_date, checkout_date)
        if record['default_shift'] is None:
            emp_shift = record['shift_type']
        else:
            emp_shift = record['default_shift']

        try:
            # new_checkin = frappe.new_doc('Employee Checkin')
            # new_checkin.employee = employee
            # new_checkin.availo = availo
            # new_checkin.log_type = "IN"
            # new_checkin.time = checkin_time
            # new_checkin.device_id = checkin_access_gate
            # new_checkin.shift_type = emp_shift
            # new_checkin.insert(ignore_permissions=True, ignore_mandatory=True) 
            # new_checkin.save()
            # new_checkout = frappe.new_doc('Employee Checkin')
            # new_checkout.employee = employee
            # new_checkout.availo = availo
            # new_checkout.log_type = "OUT"
            # new_checkout.time = checkout_time
            # new_checkout.device_id = checkout_access_gate
            # new_checkout.shift_type = emp_shift
            # new_checkout.insert(ignore_permissions=True, ignore_mandatory=True) 
            # new_checkout.save()
            
            entry = {
                "employee": employee,
                "availo": availo,
                "log_type": "IN",
                "time": checkin_time,
                "device_id": checkin_access_gate,
                "shift_type": emp_shift
            }
            new_checkin = frappe.get_doc({"doctype": "Employee Checkin", **entry})
            new_checkin.insert(ignore_permissions=True, ignore_mandatory=True)
            new_checkin.save()
        except Exception as e:
            print(f"Error occurred while recording employee check-in: {str(e)}")

        try:
            entry = {
                "employee": employee,
                "availo": availo,
                "log_type": "OUT",
                "time": checkout_time,
                "device_id": checkout_access_gate,
                "shift_type": emp_shift
            }
            new_checkout = frappe.get_doc({"doctype": "Employee Checkin", **entry})
            new_checkout.insert(ignore_permissions=True, ignore_mandatory=True)
            new_checkout.save()
        except Exception as e:
            print(f"Error occurred while recording employee check-out: {str(e)}")
        #print(f"checkIn is Created for {employee}") ###
    frappe.db.commit()
    frappe.msgprint("Sync completed.")