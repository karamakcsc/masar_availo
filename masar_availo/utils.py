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


# Send the from date and to date to this method
@frappe.whitelist()
def enqueue_sync_attendance(date_from,date_to):
	#date_from = str(datetime.date(2020, 10, 10))
	# date_to = str(datetime.date(2020, 11, 22))
	date_from = str(date_from)
	date_to = str(date_to)
	frappe.enqueue(
		# Put the python namespace before .sync_attendance
		method=sync_attendance,
		queue="long",
		is_async=True,
		enqueue_after_commit=True,
		date_from=date_from,
		date_to=date_to
	)
def sync_attendance(date_from,date_to):
	url = "https://availo-integrationapi.availo.app:8443/api/ExternalReports/GetWorkingReportAllEmployee"
	payload = json.dumps({
		"pageNumber": 1,
		"pageSize": 50,
		"data": {
			"timeZoneOffset": -120,
			"fromDate": date_from,
			"toDate": date_to,
			"displayType": 1
		}
	})
	headers = {
		"Language": "0",
		"service_key": "52B5F329-B9AE-446C-9260-B624FD1569CF",
		"authentication_type": "service_key",
		# "account_code": "MID",
		# "account_id": "441F8620-F708-42AA-8DF1-797B85FB2836"
		"Content-Type": "application/json"
	}
	# url = "https://availo-testingintegrationapi.t2.sa/api/ExternalReports/GetWorkingReportAllEmployee"
	# payload = json.dumps({
	# 	"pageNumber": 1,
	# 	"pageSize": 50,
	# 	"data": {
	# 		"timeZoneOffset": -120,
	# 		"fromDate": date_from,
	# 		"toDate": date_to,
	# 		"displayType": 1
	# 	}
	# })
	# headers = {
	# 	"Language": "0",
	# 	"service_key": "5bf66aea-0de5-4b6a-826e-897e59c2391d",
	# 	"authentication_type": "service_key",
	# 	"account_code": "QA",
	# 	"Content-Type": "application/json"
	# }

	try:
		request = get_request_session().request("POST", url, data=payload, headers=headers)
		# frappe.msgprint(request.txt)

		status_code = request.status_code
		response = request.json()
	except Exception as exc:
		error(str(exc))

	response = parse_json(response)

	if status_code != 200 and status_code != 201:
		error(_("The response was not resolved."))
		return False

	if not isinstance(response, dict):
		error(_("The response received from api is invalid."))

	data = response["data"]
	if not data.get("list") or not isinstance(data["list"], list):
		error(_("The response data list received from api is invalid."))
		return False

	data = response["data"]

	if not data.get("list") or not isinstance(data["list"], list):
		error(_("The response data list received from api is invalid."))

	store_attendance(data["list"])


def store_attendance(data):
	# This is used to reduce memory usage
	for i in range(len(data)):
		add_attendance(data.pop());

	frappe.publish_realtime(
		event="attendance_synced",
		message={"status": "done"},
		after_commit=True
	)


def add_attendance(data):
	# Add all the data to doctype
	for j in range(len(data.get("workReportTransactions").get("list"))):
		entry = {
			"job_code": data.get("jobNumber", ""),
			"employee": data.get("userName", ""),
			"employee_name": data.get("fullName", ""),
			"total_plan_work_hour_during_interval":data.get("totalPlanWorkHourDuringInterval", ""),
			"total_hours_work_during_interval":data.get("totalHoursWorkDuringInterval", ""),
			"total_checkin_late_hours_during_interval":data.get("totalCheckInLateHoursDuringInterval", ""),
			"total_checkout_late_hours_during_interval":data.get("totalCheckOutLateHoursDuringInterval", ""),
			"status":data.get("workReportTransactions").get("list")[j].get("status", ""),
			"selected_date":data.get("workReportTransactions").get("list")[j].get("selectedDate", ""),
			"working_hours":data.get("workReportTransactions").get("list")[j].get("workingHours", ""),
			"checkin_date":data.get("workReportTransactions").get("list")[j].get("checkInDate", ""),
			"sub_type_id":data.get("workReportTransactions").get("list")[j].get("subTypeID", ""),
			"checkin_access_gate_name_ar":data.get("workReportTransactions").get("list")[j].get("checkInAccessGateNameAr", ""),
			"checkin_access_gate_name_en":data.get("workReportTransactions").get("list")[j].get("checkInAccessGateNameEn", ""),
			"checkout_date":data.get("workReportTransactions").get("list")[j].get("checkOutDate", ""),
			"checkout_date_time":data.get("workReportTransactions").get("list")[j].get("checkOutDateTime", ""),
			"checkout_access_gate_name_ar":data.get("workReportTransactions").get("list")[j].get("checkOutAccessGateNameAr", ""),
			"checkout_access_gate_name_en":data.get("workReportTransactions").get("list")[j].get("checkOutAccessGateNameEn", ""),
			"actual_working_hours":data.get("workReportTransactions").get("list")[j].get("actualWorkingHours", ""),
			"session_total_checkin_late_hours":data.get("workReportTransactions").get("list")[j].get("sessionTotalCheckInLateHours", ""),
			"session_total_checkout_late_hours":data.get("workReportTransactions").get("list")[j].get("sessionTotalCheckOutLateHours", ""),
			"session_total_shortes_hours":data.get("workReportTransactions").get("list")[j].get("sessionTotalShortesHours", ""),
			"session_total_overtime_hours":data.get("workReportTransactions").get("list")[j].get("sessionTotalOverTimeHours", ""),
			"session_total_overtime_extra_hours":data.get("workReportTransactions").get("list")[j].get("sessionTotalOverTimeExtraHours", ""),
			"session_total_holiday_overtime_hours":data.get("workReportTransactions").get("list")[j].get("sessionTotalHolidayOverTimeHours", ""),
			"first_shift_start_time":data.get("workReportTransactions").get("list")[j].get("firstShiftStartTime", ""),
			"first_shift_end_time":data.get("workReportTransactions").get("list")[j].get("firstShiftEndTime", ""),
			"sec_shift_start_time":data.get("workReportTransactions").get("list")[j].get("secShiftStartTime", ""),
			"sec_shift_end_time":data.get("workReportTransactions").get("list")[j].get("secShiftEndTime", ""),
		}
		(frappe.new_doc("Availo")
			.update(entry)
			.insert(ignore_permissions=True, ignore_mandatory=True))


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

##################### Update CheckIn#### Start Code


@frappe.whitelist()
def sync_checkin():
	data=frappe.db.sql(f"""SELECT name, job_code, selected_date, checkin_date, checkout_date FROM tabAvailo""",as_dict=True)
	for i in range(len(data)):
		print(f"checkin_date: {data[i]['checkin_date']}")
		print(f"checkout_date: {data[i]['checkout_date']}")
		if data[i]['checkin_date']:
			try:
				checkin_time = datetime.strptime(data[i]["selected_date"][:10] + " " + data[i]["checkin_date"], "%Y-%m-%d %H:%M")
			except ValueError:
				print(f"Invalid checkin date: {data[i]['checkin_date']}")
				continue
			entry = {
				"employee": data[i]["job_code"],
				"time": checkin_time,
				"log_type": "IN",
				"timestamp": data[i]["selected_date"],
				"employee_field_value": "123",
				"device_id": data[i]["job_code"]
			}
			(frappe.new_doc("Employee Checkin")
				.update(entry)
				.insert(ignore_permissions=True, ignore_mandatory=True))

		if data[i]['checkout_date']:
			try:
				checkout_time = datetime.strptime(data[i]["selected_date"][:10] + " " + data[i]["checkout_date"], "%Y-%m-%d %H:%M")
			except ValueError:
				print(f"Invalid checkout date: {data[i]['checkout_date']}")
				continue
			entry = {
				"employee": data[i]["job_code"],
				"time": checkout_time,
				"log_type": "OUT",
				"availo": data[i]["name"],
				"timestamp":  data[i]["selected_date"],
				"employee_field_value": "123",
				"device_id": "123"
			}
			(frappe.new_doc("Employee Checkin")
				.update(entry)
				.insert(ignore_permissions=True, ignore_mandatory=True))

##################### Update CheckIn#### End Code
