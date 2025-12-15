app_name = "car_repair_service"
app_title = "Car Repair service"
app_publisher = "dnyaneshwari"
app_description = "regarding car services"
app_email = "dnyaneshwari.sherkar@excelminds.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "car_repair_service",
# 		"logo": "/assets/car_repair_service/logo.png",
# 		"title": "Car Repair service",
# 		"route": "/car_repair_service",
# 		"has_permission": "car_repair_service.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/car_repair_service/css/car_repair_service.css"
# app_include_js = "/assets/car_repair_service/js/car_repair_service.js"

# include js, css files in header of web template
# web_include_css = "/assets/car_repair_service/css/car_repair_service.css"
# web_include_js = "/assets/car_repair_service/js/car_repair_service.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "car_repair_service/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "car_repair_service/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "car_repair_service.utils.jinja_methods",
# 	"filters": "car_repair_service.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "car_repair_service.install.before_install"
# after_install = "car_repair_service.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "car_repair_service.uninstall.before_uninstall"
# after_uninstall = "car_repair_service.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "car_repair_service.utils.before_app_install"
# after_app_install = "car_repair_service.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "car_repair_service.utils.before_app_uninstall"
# after_app_uninstall = "car_repair_service.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "car_repair_service.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"car_repair_service.tasks.all"
# 	],
# 	"daily": [
# 		"car_repair_service.tasks.daily"
# 	],
# 	"hourly": [
# 		"car_repair_service.tasks.hourly"
# 	],
# 	"weekly": [
# 		"car_repair_service.tasks.weekly"
# 	],
# 	"monthly": [
# 		"car_repair_service.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "car_repair_service.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "car_repair_service.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "car_repair_service.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["car_repair_service.utils.before_request"]
# after_request = ["car_repair_service.utils.after_request"]

# Job Events
# ----------
# before_job = ["car_repair_service.utils.before_job"]
# after_job = ["car_repair_service.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"car_repair_service.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# doc_events = {
#     "Quotation": {
#         "after_insert": "car_repair_service.api.quotation_mail.send_quotation_email",
#         "on_update": "car_repair_service.api.quotation_mail.send_quotation_email"
#         # "on_update": "car_repair_service.api.quotation_approved.create_car_repair_on_quotation_approval"
        
#     }
# }
# frappe-cars/frappe_cars/hooks.py

# before_request = ["car_repair_service.api.utils.check_authorization"]


permission_query_conditions = {
    "Car repair": "car_repair_service.api.car_repair.get_permission_query_conditions",
    "Car Repair Request": "car_repair_service.api.assign_adviser.get_permission_query_conditions",
    "Car Diagnosis": "car_repair_service.api.assign_adviser.get_permission_query_conditions",
    "Car Repair": "car_repair_service.api.assign_adviser.get_permission_query_conditions"
}



# doc_events = {
#     "Quotation": {
#         "after_insert": "car_repair_service.api.quotation_mail.send_quotation_created_email",
#         "on_update": "car_repair_service.api.quotation_mail.send_quotation_update_email",
#         "after_insert": "car_repair_service.api.padte.log_doc_created",
#         "on_update": "car_repair_service.api.padte.log_doc_updated",
#         "on_submit": "car_repair_service.api.padte.log_doc_submitted",
#         "on_cancel": "car_repair_service.api.padte.log_doc_cancelled",
#     },
#      "Car Repair Request": {
#         "after_insert": "car_repair_service.api.padte.log_doc_created",
#         "on_update": "car_repair_service.api.padte.log_doc_updated",
#     },
#     "Car Diagnosis": {
#         "after_insert": "car_repair_service.api.padte.log_doc_created",
#         "on_update": "car_repair_service.api.padte.log_doc_updated",
#     },
#     "Car Repair": {
#         "after_insert": "car_repair_service.api.padte.log_doc_created",
#         "on_update": "car_repair_service.api.padte.log_doc_updated",
#     }
    
# }


doc_events = {
    "Quotation": {
        "after_insert": [
            "car_repair_service.api.quotation_mail.send_quotation_created_email",
            "car_repair_service.api.padte.log_doc_created",
        ],
        "on_update": [
            "car_repair_service.api.quotation_mail.send_quotation_update_email",
            "car_repair_service.api.padte.log_doc_updated",
        ],
        "on_submit": "car_repair_service.api.padte.log_doc_submitted",
        "on_cancel": "car_repair_service.api.padte.log_doc_cancelled",
    },
    "Car Repair Request": {
        "after_insert": "car_repair_service.api.padte.log_doc_created",
        "on_update": "car_repair_service.api.padte.log_doc_updated",
    },
    "Car Diagnosis": {
        "after_insert": "car_repair_service.api.padte.log_doc_created",
        "on_update": "car_repair_service.api.padte.log_doc_updated",
    },
    "Car repair": {
        "after_insert": "car_repair_service.api.padte.log_doc_created",
        "on_update": "car_repair_service.api.padte.log_doc_updated",
    }
}

fixtures = [
    # 1️⃣ Export Quotation Custom Fields first
    {
        "dt": "Custom Field",
        "filters": [
            ["dt", "in", ["Quotation",
                          "Vehicle",
                          "User"]]
        ]
    },

    # 2️⃣ Client Scripts
    {
        "dt": "Client Script",
        "filters": [
            ["name", "in", [
                "Car Repair Request After Create Diagnosis",
                "Create Sales Invoice After Car Repair",
                "Create Quatation On Dignosis",
                "Car Repair Status Should Be Mark As Completed",
                "Item Maintain Stock Always Check Read Only",
                "Map Item Naming Series",
                "Item Name Blank",
                "Remove Spaces From Field",
                "Vehicle Pick Up Check Car Repair Images should be Manadatory",
                "Vehicle Pick Up Address Disply Bydefault",
                "Remove Spaces From Vehicle Doc",
                "image preview",
                "Book Appointement Vehicle Pickup",
                "Create Car Repair Request From Book Appointement",
                "Model name",
                "Filter Car According To Model",
                "Autopopulate MakeAnd Model On The Basis Of Car",
                "Customer Getting Vehicle",
                "Adding Customer On Car Repair Request When Not Exist",
                "Autoppulated Chassis No On The Basis Of Chassis No",
                "Filter Item In Car Repair According to Model",
                "Update Esimated Cost On Car Diagnosis According To Quantity",
                "Fetch Odometer value"
                
                
            ]]
        ]
    },

    # 3️⃣ Server Scripts
    {
        "dt": "Server Script",
        "filters": [
            ["name", "in", [
                "Car Repair Request Welcome Email To Customer",
                "Car Request Get Creaed Customer Getting Created In System",
                "Car Repair Status Should Be Completed",
                "Create Approve Car Repair Doc From Quotation",
                "Add Car Repair Request Reference No To Car Repair",
                "Add Car Repair Reference No To Car Diagnosis",
                "Quotation Approved Timstamp",
                "Book Appointment create vehicle record"
            ]]
        ]
    },

    # 4️⃣ Workflows (after Quotation exists)
    {
        "dt": "Workflow",
        "filters": [["name", "in", [
            "Workflow for Quotation",
            "Workflow for Sales Invoice"
        ]]]
    },

    # 5️⃣ Website settings
    {
        "doctype": "Website Settings"
    },

    # 6️⃣ Workspaces
    {
        "dt": "Workspace",
        "filters": [
            ["name", "=", "Car Repair Service"]
        ]
    },

    # 7️⃣ Core doctypes modified (keep at bottom)
    {
        "dt": "DocType",
        "filters": [
            ["name", "in", [
                "Item",
                "Sales Invoice",
                "Sales Invoice Item",
                "Vehicle",
                "employee"
            ]]
        ]
    },

    # 8️⃣ Reports
    {
        "dt": "Report",
        "filters": [
            ["name", "in", ["Car Repair History Log Report"]]
        ]
    },
    {
        "doctype": "Role",
        "filters": {
            "name": ["in", ["Assign Advisor","Receptionist"]]
        }
    }
]
