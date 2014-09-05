{
		"name" : "OpenDAS Server Extended functions hr",
		"version" : "0.1",
		"author" : "OpenDAS",
		"website" : "http://www.opendas.org",
		"category" : "OpenDAS",
		"description": """  """,
		"depends" : [
					 'hr',
					 'hr_attendance',
					 'mrp_operations',
					 'mrp',
					 'hr_timesheet',
					 ],
		"init_xml" : [ ],
		"demo_xml" : [ ],
		"update_xml" : [
					"report/hr_report.xml",
					#'wizard/hr_wizard.xml',
					'view/hr_attendance_view.xml',
					'view/account_analytic_view.xml',
					'view/mrp_view.xml',
                        ],
		"installable": True
}