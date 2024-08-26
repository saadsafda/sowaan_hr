def get_data():
    return [
        {
            "label": _("Sowaan HR"),
            "icon": "octicon octicon-book",
            "items": [
                {
                    "type": "doctype",
                    "name": "GPS Locations",
                    "label": _("GPS Locations"),
                    "description": _("Manage Books"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Employee GPS Locations",
                    "label": _("Employee GPS Locations"),
                    "description": _("Manage Members"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 0,
                }
            ]
        }
    ]