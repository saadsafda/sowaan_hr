// Copyright (c) 2022, Sowaan and contributors
// For license information, please see license.txt

frappe.ui.form.on('GPS Locations', {
	refresh: function(frm){
        $('.leaflet-draw-draw-polyline').remove();
        $('.leaflet-draw-draw-polygon').remove();
        $('.leaflet-draw-draw-rectangle').remove();
        $('.leaflet-draw-draw-circlemarker').remove();  
    },
    map: function(frm) {
        var myMap = JSON.parse(frm.doc.map);
	    console.log(myMap);
	    if(myMap.features.length>0){
	        if(myMap.features[0].geometry.type != "Polygon" && myMap.features[0].geometry.type != "LineString")
	        {
	            var coords =  myMap.features[0].geometry.coordinates;
            	frm.set_value('location_gps', coords[1]+","+coords[0]);
            	if(myMap.features[0].properties && myMap.features[0].properties.radius){
            	    frm.set_value('allowed_radius', myMap.features[0].properties.radius.toFixed(0));
            	}
	        }
	    }
	}
});
