// cookie consent & tracking
window.addEventListener("load", function(){
	window.cookieconsent.initialise({
	  "palette": {
		"popup": {
		  "background": "#0099ff"
		},
		"button": {
		  "background": "#75ca2a"
		}
	  },
	  "theme": "edgeless",
	  "type": "opt-in",
	  "content": {
		"href": "http://agnessearch.nl/terms-of-use"
	  },
	  onInitialise: function (status) {
		  var type = this.options.type;
		  var didConsent = this.hasConsented();
		  if (type == 'opt-in' && didConsent) {
			(function(h,o,t,j,a,r){
				h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
				h._hjSettings={hjid:1041997,hjsv:6};
				a=o.getElementsByTagName('head')[0];
				r=o.createElement('script');r.async=1;
				r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
				a.appendChild(r);
			})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');

			(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
			(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
			m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
			})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

			ga('create', 'UA-106362473-1', 'auto');
			ga('send', 'pageview');
		  }
		  
		},
		 
		onStatusChange: function(status, chosenBefore) {
		  var type = this.options.type;
		  var didConsent = this.hasConsented();
		  if (type == 'opt-in' && didConsent) {
			(function(h,o,t,j,a,r){
				h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};
				h._hjSettings={hjid:1041997,hjsv:6};
				a=o.getElementsByTagName('head')[0];
				r=o.createElement('script');r.async=1;
				r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;
				a.appendChild(r);
			})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=');

			(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
			(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
			m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
			})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

			ga('create', 'UA-106362473-1', 'auto');
			ga('send', 'pageview');
		  }
		  
		},
		 
		onRevokeChoice: function() {
		  var type = this.options.type;
		  if (type == 'opt-in') {
			// disable cookies
		  }
		  
		},
	})
});

if (navigator.userAgent.match(/IEMobile\/10\.0/)) {
	var msViewportStyle = document.createElement('style');
	msViewportStyle.appendChild(
		document.createTextNode(
			'@-ms-viewport{width:auto!important}'
		)
	);
	document.querySelector('head').appendChild(msViewportStyle);
}





function showMessage(msg = 'Loading...',submsg = ''){
  data = '<h2 style="text-align:center;">'+msg+'</h2>';
  if(submsg){
	  data += '<p style="text-align:center;">'+submsg+'</p>';
  }
  data += '<div style="text-align:center;"><img style="width:70%;" src="assets/img/02-digger_v3.gif" alt="Digging..." /></div>';
  return $.featherlight(data, {});
}

$( function() {
	
	
	// reset search btn
	$('#reset-btn').click(function(e){
		url = location.protocol + '//' + location.host + location.pathname;
		document.location = url;
	});
	
	//facets filter button
	$('#apply-facets').click(function(e){
		showMessage('Resultaten aan het ophalen...');
		facets = {};
		$('.facet').each(function(){
			facetName = $(this).attr('id');
			facets[facetName] = [];
			$(this).find('input').each(function(){
				if($(this).is(':checked')){
					facets[facetName].push($(this).val());
				}
			});
		});
		json = encodeURIComponent(JSON.stringify(facets));
		document.location = window.location.href+'&facets='+json;
	});
	
	//html page preview popup		
	$('.pagePreview').click(function(e){
		e.preventDefault();
		loading = showMessage('Pagina aan het ophalen...');
		htmlurl = $(this).attr('href');
		fileLocation = 'get-page-preview.php?url='+encodeURIComponent(htmlurl); // go via php proxy as cross domain AJAX is not allowed
		
		$.get( fileLocation, function( data ) {
			data = highlightAndFixImages(data, htmlurl);
			loading.close();
			$.featherlight(data, {});
		}); 
	});
	
	//enlarge map button
	$('#toggle-search-form').click(function(e){
		e.preventDefault();
		if($(this).children('span').html() == 'Pas zoekopdracht aan'){
			el = $('.sidesearch')
			curHeight = el.height(),
			autoHeight = el.css('height', 'auto').height();
			el.height(curHeight).animate({height: autoHeight}, 500);
			$(this).children('span').html('Verberg zoekopdracht');
		}
		else {
			$('.sidesearch').css('height', '0px');
			$(this).children('span').html('Pas zoekopdracht aan');
		}
	});
	
	//show/hide search form button
	$('#enlarge-map').click(function(e){
		e.preventDefault();
		if($(this).html() == 'Verklein Kaart'){
			$('#map').css('height', '100px');
			google.maps.event.trigger(map, "resize");
			$(this).html('Vergroot Kaart');
		}
		else {
			$('#map').css('height', '500px');
			google.maps.event.trigger(map, "resize");
			$(this).html('Verklein Kaart');
		}
	});
	
	//more snippets button
	$('.show-more-snippets').click(function(e){
		e.preventDefault();
		if($(this).html() == 'Zie Minder Snippets'){
			$(this).prev().css('max-height', '97px').css('overflow-y','hidden');
			$(this).html('Zie Meer Snippets');
		}
		else {
			$(this).prev().css('max-height', '200px').css('overflow-y','scroll');
			$(this).html('Zie Minder Snippets');
		}
	});
	
	//pagination
	$('.pagination').jqPagination({
		paged: function(page) {
	showMessage('Resultaten aan het ophalen...');
			var url = new URL(document.location);
	var search_params = url.searchParams;
	search_params.set('page', page);
	url.search = search_params.toString();
	var new_url = url.toString();
	window.location = new_url;
		}
	});
	
	//results number selector
	$('#resultsperpageselect').change(function(){
		showMessage('Resultaten aan het ophalen...');
		var url = new URL(document.location);
		var search_params = url.searchParams;
		search_params.set('resultsperpage', $(this).val());
		url.search = search_params.toString();
		var new_url = url.toString();
		window.location = new_url;
	});
	
	// submit button
	$('#searchsubmit').click(function(e) {
		e.preventDefault();
		showMessage('Resultaten aan het ophalen...');
		// remove spaces (stringify) from advanced_query field, to stop 'too long uri' error
		if( $('#advanced_query').length )  {
			$('#advanced_query').val(
				JSON.stringify(JSON.parse($('#advanced_query').val()))
			);
		}
		
		$('#queryform').submit();
		
	});
	
});
 


function highlightAndFixImages(html, fileLocation){
	//console.log(html);
	if(search){ // if search, do highlighting
		
		//remove brackets and OR/AND
		search = search.replaceAll('(', '').replaceAll(')', '').replaceAll('OR ', '').replaceAll('AND ', '').replaceAll('  ', ' ').replaceAll('"', ' ').replaceAll("'", ' ');
			
		//get just body, to stop replacing header code and breaking html popup
		splitHtml = html.split('<body ');
		body = splitHtml[1].replace(search, '<span style="background:yellow">'+search+'</span>');
		terms = search.split(' ');
		terms.forEach(function(term) {
			//TODO if * in term, and it's at start or end, try and highlight the start/end of the word as well
			term = term.replace('*', '');
			if(term && term.length > 2){
				//console.log(term);
				body = body.replaceAll(term, '<span style="background:yellow">'+term+'</span>');
				capTerm = term.charAt(0).toUpperCase() + term.slice(1);
				body = body.replaceAll(capTerm, '<span style="background:yellow">'+capTerm+'</span>');
			}	
			// Ijzertijd / IJzertijd problem
			if(term == 'ijzertijd'){
				body = body.replace(new RegExp('IJzertijd', 'g'), '<span style="background:yellow">'+term+'</span>');
			}
		});
		output = splitHtml[0]+'<body '+body;
	}
	else {
		output = html
	}
	
	//fix images
	re = /index-[0-9]+.html/;
	folder = fileLocation.replace(re,'');
	output = output.replace('src="', 'src="'+folder);
	
	//fix css affecting for rest of page
	output = output.replace('p {','.featherlight-content p {');
	
	return output;
}


// js for the results map  --------------------------------------------

var map;
var drawingManager;
var shape;
var geomorph;
function initMap() {
	
	map = new google.maps.Map(document.getElementById('map'), {
		zoom: 7,
		center: new google.maps.LatLng(52.243333,5.634167),
		mapTypeId: 'terrain'
	});

	if(resultsFound){
		// Loop through the results array and place a marker for each set of coordinates.
		var infoWindow = new google.maps.InfoWindow(), marker, i;
		var contentStrings = [];
		for (var i = 0; i < geopoints.length; i++) {
			if(geopoints[i]['archisLink']){
				var archis = " / <a href='"+geopoints[i]['archisLink']+"' target='_blank'>Bekijk in Archis</a>"
			}
			contentStrings[i] = '<div id="content">'+
				'<p><strong>'+geopoints[i]['title']+'</strong></p>'+
				'<p>'+
					'<a href="'+geopoints[i]['doi']+'" class="" target="_blank">'+
						'Download PDF via archief'+
					'</a>'+
					//archis+
				'</p>'+
			'</div>';

			var latLng = new google.maps.LatLng(geopoints[i]['lat'],geopoints[i]['lon']);
			var marker = new google.maps.Marker({
				position: latLng,
				map: map,
				title: geopoints[i]['title']
			});
			google.maps.event.addListener(marker, 'click', (function(marker, i) {
				return function() {
					infoWindow.setContent(contentStrings[i]);
					infoWindow.open(map, marker);
				}
			})(marker, i));
		}
	}
	

	if(queryExecuted && coords){
		// place polygon on map
		coords = JSON.parse(coords);
		coords.forEach(function(coord){
			coord['lng'] = parseFloat(coord['lon']);
			delete coord['lon'];
			coord['lat'] = parseFloat(coord['lat']);
		});
		coords.push(coords[0]); // add first point as last point to close shape
		
		// Construct the polygon.
		shape = new google.maps.Polygon({
			paths: coords,
			editable: true,
			fillColor: '#0099ff',
			strokeColor: '#0099ff'
		});
		shape.setMap(map);
		
		polygonDrawnEvents();

		drawingManager.setOptions({
			drawingMode: null
		});
	}
	else if(queryExecuted){
		drawingManager.setOptions({
			drawingMode: null
		});
	}
	
	// SET UP OVERLAYS (https://github.com/beaugrantham/wmsmaptype)
	// geomorph map 
	geomorph = new WmsMapType(
		"Geomorfologische kaart",
		"https://service.pdok.nl/bzk/bro-geomorfologischekaart/wms/v1_0", // https://www.pdok.nl/-/wms-service-voor-bro-geomorfologische-kaart
		{layers: "view_geomorphological_area"},
		{opacity: 0.8}
	);
	// AHN map 
	ahn = new WmsMapType(
		"AHN",
		"https://service.pdok.nl/rws/ahn/wms/v1_0", // https://www.nationaalgeoregister.nl/geonetwork/srv/api/records/94e5b115-bece-4140-99ed-93b8f363948e
		{layers: "dtm_05m"},
		{opacity: 0.8}
	);
	
	// geomorph overlay toggle button
	var geomorphControlDiv = document.createElement('div');
	var geomorphControl = new GeomorphControl(geomorphControlDiv, map);
	geomorphControlDiv.index = 1;
	map.controls[google.maps.ControlPosition.TOP_LEFT].push(geomorphControlDiv);
	// AHN overlay toggle button
	var ahnControlDiv = document.createElement('div');
	var ahnControl = new AhnControl(ahnControlDiv, map);
	ahnControlDiv.index = 1;
	map.controls[google.maps.ControlPosition.TOP_LEFT].push(ahnControlDiv);
	
}

function polygonDrawnEvents(){
	shape.type = 'polygon';
		
	// stop user from drawing 2 polygons by hiding the controls
	toggleDrawing(false);
	
	// pass coords to input on page
	putCoordsInInput(shape);
	
	// listeners for when polygon is edited
	google.maps.event.addListener(shape.getPath(), 'insert_at', function(index, obj) {
		putCoordsInInput(shape);
	});
	google.maps.event.addListener(shape.getPath(), 'set_at', function(index, obj) {
		putCoordsInInput(shape);
	});
	google.maps.event.addListener(shape.getPath(), 'remove_at', function(index, obj) {
		putCoordsInInput(shape);
	});
	
	// set up 'remove shape' button
	setupRemoveBtn();
}

function setupRemoveBtn(){
	// set up 'remove shape' button
	var removeControlDiv = document.createElement('div');
	var removeControl = new CenterControl(removeControlDiv, map);

	removeControlDiv.index = 1;
	map.controls[google.maps.ControlPosition.TOP_CENTER].push(removeControlDiv);
}

function toggleDrawing(state){
	drawingManager.setOptions({
		drawingControl: state,
		drawingMode: null
	});
	// TODO set drawing mode to /hand/ so you can edit the shape
}

function putCoordsInInput(shape){
	if(shape.type == 'rectangle'){
		var bounds = shape.getBounds().toJSON();
		var coords = [
			{'lat': bounds['north'], 'lon': bounds['west']}, // north west point
			{'lat': bounds['north'], 'lon': bounds['east']}, // north east point
			{'lat': bounds['south'], 'lon': bounds['east']}, // south east point
			{'lat': bounds['south'], 'lon': bounds['west']}, // south west point
		]
	}
	else { // it's a polygon
		var len = shape.getPath().getLength();
		var coords = [];
		for (var i = 0; i < len; i++) {
			latlng = shape.getPath().getAt(i).toUrlValue(5).split(',');
			latlng = {'lat': latlng[0], 'lon': latlng[1]};
			coords.push(latlng);
		}
	}
	
	//console.log(coords);
	$('#coords').val(JSON.stringify(coords));
	
	// also set search level to document
	$('#searchLvl').val('document');
}

// remove shape control
var removeControlUI = false;
function CenterControl(controlDiv, map) {
	
	if(shape.type == 'rectangle'){
		shapeName = 'rechthoek';
	}
	else {
		shapeName = 'polygoon';
	}

	// Set CSS for the control border.
	removeControlUI = document.createElement('div');
	removeControlUI.style.backgroundColor = '#fff';
	removeControlUI.style.borderRadius = '2px';
	removeControlUI.style.boxShadow = 'rgba(0, 0, 0, 0.3) 0px 1px 4px -1px';
	removeControlUI.style.cursor = 'pointer';
	removeControlUI.style.margin = '10px 10px 10px -10px';
	removeControlUI.style.textAlign = 'center';
	removeControlUI.title = 'Klik om '+shapeName+' te verwijderen';
	controlDiv.appendChild(removeControlUI);

	// Set CSS for the control interior.
	var controlText = document.createElement('div');
	controlText.style.color = 'rgb(86,86,86)';
	controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
	controlText.style.fontSize = '11px';
	controlText.style.padding = '8px';
	controlText.innerHTML = '<i class="glyphicon glyphicon-remove-circle" style="color:red;"></i> Verwijder '+shapeName;
	removeControlUI.appendChild(controlText);


	// Setup the click event listener to remove shape
	removeControlUI.addEventListener('click', function() {
		// remove shape
		shape.setMap(null);
		
		// remove control div
		removeElement(removeControlUI);
		
		// restore draw controls
		toggleDrawing(true);
	});

}

// geomorph control
function GeomorphControl(controlDiv, map) {

	// Set CSS for the control border.
	controlUI = document.createElement('div');
	controlUI.style.backgroundColor = '#fff';
	controlUI.style.borderRadius = '2px';
	controlUI.style.boxShadow = 'rgba(0, 0, 0, 0.3) 0px 1px 4px -1px';
	controlUI.style.cursor = 'pointer';
	controlUI.style.margin = '10px 10px 10px -10px';
	controlUI.style.textAlign = 'center';
	controlUI.title = 'Geomorphologische kaart';
	controlUI.id = 'geomorphControlContainer';
	controlDiv.appendChild(controlUI);

	// Set CSS for the control interior.
	var controlText = document.createElement('div');
	controlText.style.color = 'rgb(86,86,86)';
	controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
	controlText.style.fontSize = '18px';
	controlText.style.padding = '8px';
	controlText.innerHTML = '<i class="glyphicon glyphicon-unchecked" id="geomorphCheckbox"></i> Geomorf. Kaart';
	controlUI.appendChild(controlText);


	// Setup the click event listener to toggle geomorph map
	controlUI.addEventListener('click', function() {
		
		if($('#geomorphCheckbox').hasClass("glyphicon-check")){
			$('#geomorphCheckbox').removeClass("glyphicon-check").addClass("glyphicon-unchecked");
			geomorph.removeFromMap(map);
		}
		else {
			$('#geomorphCheckbox').removeClass("glyphicon-unchecked").addClass("glyphicon-check");
			geomorph.addToMap(map);
		}
	});
}
// ahn control
function AhnControl(controlDiv, map) {

	// Set CSS for the control border.
	controlUI = document.createElement('div');
	controlUI.style.backgroundColor = '#fff';
	controlUI.style.borderRadius = '2px';
	controlUI.style.boxShadow = 'rgba(0, 0, 0, 0.3) 0px 1px 4px -1px';
	controlUI.style.cursor = 'pointer';
	controlUI.style.margin = '10px 10px 10px -10px';
	controlUI.style.textAlign = 'center';
	controlUI.title = 'AHN';
	controlUI.id = 'geomorphControlContainer';
	controlDiv.appendChild(controlUI);

	// Set CSS for the control interior.
	var controlText = document.createElement('div');
	controlText.style.color = 'rgb(86,86,86)';
	controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
	controlText.style.fontSize = '18px';
	controlText.style.padding = '8px';
	controlText.innerHTML = '<i class="glyphicon glyphicon-unchecked" id="ahnCheckbox"></i> AHN';
	controlUI.appendChild(controlText);


	// Setup the click event listener to toggle ahn map
	controlUI.addEventListener('click', function() {
		
		if($('#ahnCheckbox').hasClass("glyphicon-check")){
			$('#ahnCheckbox').removeClass("glyphicon-check").addClass("glyphicon-unchecked");
			ahn.removeFromMap(map);
		}
		else {
			$('#ahnCheckbox').removeClass("glyphicon-unchecked").addClass("glyphicon-check");
			ahn.addToMap(map);
		}
	});


}

function removeElement(elem) {
	return elem.parentNode.removeChild(elem);
}

function trackClick(click_type, data_source, doc_id){
	//console.log('recording click in log');
	$.ajax({
		//								  session_id,              search_id,               click_type,                data_source,           doc_id
		url: "/log-click.php?session_id="+session_id+"&search_id="+search_id+"&click_type="+click_type+"&data_source="+data_source+"&doc_id="+doc_id
	})
	.done(function( msg ) {
		//console.log( "Click recorded" );
	});
}

// make pressing the enter button in querybuilder submit the form
function makeInputsEnterable(){
	$('#builder input').on('keydown', function (e) {
		 if(e.which === 13){

			//Disable textbox to prevent multiple submit
			$(this).attr("disabled", "disabled");

			submitForm();

			//Enable the textbox again if needed.
			//$(this).removeAttr("disabled");
		 }
	});
}
$('#builder').on('afterAddGroup.queryBuilder', function(e, rule, error, value) {
	makeInputsEnterable();
});
$('#builder').on('afterAddRule.queryBuilder', function(e, rule, error, value) {
	makeInputsEnterable();
});
$('#builder').on('afterInit.queryBuilder', function(e, rule, error, value) {
	makeInputsEnterable();
});
$('#builder').on('afterCreateRuleInput.queryBuilder', function(e, rule, error, value) {
	makeInputsEnterable();
});

if (resultsFound) {
	initMap();
}


