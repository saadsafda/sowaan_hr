from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label": _("Sowaan HR"),
            "icon": "octicon octicon-book",
            "items": [
                {
				   "description": "Sowaan HR", 
				   "name": "sowaanhr", 
				   "label": "sowaanhr", 					
				   "type": "page"
                }, 
                {
                    "type": "doctype",
                    "name": "Allowed GPS Locations",
                    "label": _("Allowed GPS Locations"),
                    "description": _("Allowed GPS Locations"),
                    "onboard": 1,
                }
            ]
        }
    ]