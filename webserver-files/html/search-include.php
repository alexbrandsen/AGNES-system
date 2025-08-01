<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ERROR);

// set session id 
session_start();
if (empty($_SESSION['id'])) {
   $_SESSION['id'] = uniqid();
}

//do "sudo service elasticsearch start" before running this 

use Elasticsearch\ClientBuilder;

//include composer file needed for ES
require 'vendor/autoload.php';

$base_url = ( isset($_SERVER['HTTPS']) && $_SERVER['HTTPS']=='on' ? 'https' : 'http' ) . '://' .  $_SERVER['HTTP_HOST'];
$current_url = urlencode($base_url . $_SERVER["REQUEST_URI"]);

// set geopoints so we don't get an error in the JS if no results
$geoPoints = '""';

if($_GET['query'] || $_GET['coords'] || ( $_GET['startdate'] && $_GET['enddate'] ) || $_GET['ART'] || $_GET['CON'] || $_GET['SPE'] || $_GET['advanced_query']  ){
	
	// set query flag
	$queryFired = True;
	
	if($_GET['resultsperpage']){
		$numPerPage = $_GET['resultsperpage'];
	}
	else {
		$numPerPage = 10;
	}
	
	if($_GET['page']){
		$from = ($_GET['page']-1) * $numPerPage; // minus 1 as ES indexes from 0
	}
	else {
		$from = 0; //  ES indexes from 0
		$_GET['page'] = 1;
	}

	$esIndex = 'agnesv2-nested'; 
	
	$hosts = [
		'http://localhost:9200'
	];

	$client = Elasticsearch\ClientBuilder::create()           // Instantiate a new ClientBuilder
				->setHosts($hosts)      		// Set the hosts
				->setBasicAuthentication('USERNAME', 'PASSWORD') // set username / password
				->build(); 
	// if getting a 'no nodes in cluster' error at this point, update selinux to allow internal http connections with: setsebool -P httpd_can_network_connect 1
	
	
	
	if($_GET['advanced_query']){ // json query from kibana
	
		
		// get query from full kibana query
		$query = json_decode($_GET['advanced_query'],true)['query']['bool']['filter'];
		
		//set score_mode to default (avg) so we get scores
		array_walk_recursive(
			$query,
			function (&$value, $key) {
				if ($key == 'score_mode' && $value == 'none') {
					$value = 'avg';
				}
			}
		);
		
		//set filter to must, so we can get relevance scores
		$json_string = json_encode($query);
		//print_r($json_string);exit;
		$json_string = str_replace(
			'"filter"',
			'"must"',
			$json_string);
		$query = json_decode($json_string,true);

		//add inner_hits for page preview
		$query[0]['nested']['inner_hits'] = ["size"=>10];
			
		// set query in right format
		$body['query']['bool']['must'] = $query;
		
		// set highlight (snippets) on text query
		$body['highlight'] = [
			'fields' => [
				'document.pages.content' => (object)[]
			],
			'fragment_size' => 200,
			'max_analyzed_offset' => 1000000 // to prevent error when content is too long for highlighting
		]; 
		
		
	}
	else { // normal search
	
		//get rid of 'AND ' at end of query, if leftover from autocomplete
		if(substr($_GET['query'], -4) == 'AND '){
			$_GET['query'] = substr($_GET['query'], 0, -4);
		}
	
		$enteredQuery = json_decode($_GET['query'],true);
		if($_GET['searchLvl']){
			$searchLvl = $_GET['searchLvl'];
		}
		else {
			$searchLvl = 'document';
		}

		if($_GET['searchType'] == 'or'){
			$searchType = $_GET['searchType'];
		}
		else {
			$searchType = 'and';
		}

		 
		$entitiesSearchedFor = '';

		
		//create query 
		$operators = array(
			'is' => 'match',
			'begins_with' => 'prefix',
			'contains' => 'wildcard',
			'ends_with' => 'wildcard'
			
		);
		$topLevelOperator = ($_GET['searchType'] == 'and') ? 'must' : 'should';
		$query = [
			'bool' => [
				'must' => []
			]
		];
			  
		

		$entitiesSearchedFor = ' ';
		# entity search ARTefact
		if( strlen($_GET['ART'])){
			array_push(
				$query['bool']['must'],
				[
					'bool' => [
						$topLevelOperator => [
							'match' => [
								'document.pages.ner_entities.ART' => [
									'query' => strtolower($_GET['ART']), 
									'fuzziness' => 'AUTO'
								]  
							]
						]
					]
				]
			);
			$entitiesSearchedFor .= ' '.$_GET['ART'];
			

		}
		# entity search CONtext
		if( strlen($_GET['CON'])){
			array_push(
				$query['bool']['must'],
				[
					'bool' => [
						$topLevelOperator => [
							'match' => [
								'document.pages.ner_entities.CON' => [
									'query' => strtolower($_GET['CON']), 
									'fuzziness' => 'AUTO'
								]  
							]
						]
					]
				]
			);
			$entitiesSearchedFor .= ' '.$_GET['CON'];
		}
		# entity search SPEcies
		if( strlen($_GET['SPE'])){
			array_push(
				$query['bool']['must'],
				[
					'bool' => [
						$topLevelOperator => [
							'match' => [
								'document.pages.ner_entities.SPE' => [
									'query' => strtolower($_GET['SPE']), 
									'fuzziness' => 'AUTO'
								]  
							]
						]
					]
				]
			);
			$entitiesSearchedFor .= ' '.$_GET['SPE'];
		}
		
		if( strlen($_GET['query']) ) { 
			// get rid of html quotes
			$_GET['query'] = str_replace('&quot;','"',$_GET['query']);
			
			


			if($_GET['advanced_search']){

				
				array_push(
					$query['bool']['must'],
					[
						'bool' => [
							$topLevelOperator => [
								'query_string' => [
									'fields' => ['document.pages.content'],
									'query' => $_GET['query']
								]
							]
						]
					]
				); 
				
			} else {

			

			
			
			
				// phrase search with quotes around it
				if( 
					(substr($_GET['query'],0,1) == '"' || substr($_GET['query'],0,1) == "'" ) &&
					(substr($_GET['query'],-1) == '"' || substr($_GET['query'],-1) == "'" )
				){             
					array_push(
						$query['bool']['must'],
						[
							'bool' => [
								$topLevelOperator => [
									'match_phrase' => [
										'document.pages.content' => [
											'query' => strtolower(substr($_GET['query'],1,-1))
										]  
									]
								]
							]
						]
					); 
				} 
				// normal match, no phrase  
				else { 


					if (strpos($term, '*') !== false) { // wildcard search with *
						array_push(
							$query['bool']['must'],
							[
								'bool' => [ 
									$topLevelOperator => [
										'wildcard' => [
											'document.pages.content' => [
												'value' => strtolower($_GET['query']),
												'operator' => strtoupper($searchType)
											]  
										]
									]
								]
							]
						);
					}
					else { // 'normal' search, do fuzzyness to catch (ocr) errors (e.g. "kogelpot" will also match "kogelpat"
						if($_GET['fuzzyness']){
							$fuzzyness = $_GET['fuzzyness'];
						}
						else {
							$fuzzyness = '0';
						}
						array_push(
							$query['bool']['must'],
							[
								'bool' => [
									$topLevelOperator => [
										'match' => [
											'document.pages.content' => [
												'query' => strtolower($_GET['query']), 
												'fuzziness' => $fuzzyness,
												'operator' => strtoupper($searchType)
											]  
										]
									]
								]
							]
						);  
					}              
				}
			} 
			
			

			
			if($_GET['export'] == 'csv'){
				$fragment_size = 300;
			}
			else {
				$fragment_size = 100;
			}
			
			// set highlight (snippets) on text query (highlight for entities/timespans done below)
			$body['highlight'] = [
				'fields' => [
					'document.pages.content' => (object)[]
				],
				'fragment_size' => $fragment_size,
				'max_analyzed_offset' => 1000000 // to prevent error when content is too long for hightlighting
			]; 

			
		}

		// timespan search
		if( strlen($_GET['startdate']) && strlen($_GET['enddate']) ){
			array_push(
				$query['bool']['must'],
				["nested" => [
					'path' => 'document.pages.timespans', // name of sub-object
					 "inner_hits" => [ // return which timeperiods were found
						 "size" => 5 // max number to return (default 3)
					 ], 
					'query' => [
						'bool' => [ 
							'should' => [ // at least one of these 'should' match
									['range' => 
										['document.pages.timespans.startdate' =>  // 450
											[
												'gte' => $_GET['startdate'], // timespan has start that lies within search OR
												'lte' => $_GET['enddate']
											]                                                                   
										]
									],
									[ 'range' =>  
										['document.pages.timespans.enddate' =>  //1300
											[
												'gte' => $_GET['startdate'], // timespan has end that lies within search OR
												'lte' => $_GET['enddate']
											]                                                                   
										]
									],
									['bool' =>
										['must' => 
											[
												['range' => 
													['document.pages.timespans.startdate' =>  // 450
														[
															'lte' => $_GET['startdate'] // timespan starts before search AND
														]                                                                   
													]
												],
												[ 'range' =>  
													['document.pages.timespans.enddate' =>  //1300
														[
															'gte' => $_GET['enddate'] // timespan ends after search
														]                                                                   
													]
												]
											]
										]
									]
								]
							]
						]
					 ]
				 ]
			); 
		} 
		

			
		
		$body['query'] = [
			
			"nested" => [
				"path" => "document",
				"inner_hits" => ["size" => 10],
				"query" => [
					"bool" => [
						"must" => [
							"nested" => [
								"path" => "document.pages",
								"inner_hits" => ["size" => 10],
								"query" => $query
							]
						]
					]
				]
			]
				
		];
		
		
		
		# location filter by bounding box
		if( strlen($_GET['top']) && strlen($_GET['bottom']) && strlen($_GET['left']) && strlen($_GET['right']) ){
		
			$body['query']['nested']['query']['bool']['filter'] = [];
			array_push(
				$body['query']['nested']['query']['bool']['filter'],
				[
					"geo_bounding_box" => [
						"document.location" => [
							"top" => $_GET['top'],
							"left" => $_GET['left'],
							"bottom" => $_GET['bottom'],
							"right" => $_GET['right']
						]
					]
				]
			);

		}
		
		// filter on source
		if(!$_GET['dans'] || !$_GET['archis'] || !$_GET['onroerend_erfgoed'] || !$_GET['onroerend_erfgoed_notas'] || !$_GET['kb'] || !$_GET['sidestone']){
			
			//if not location filter, add empty filter to query to append document sources to
			if(!$body['query']['nested']['query']['bool']['filter']){
				$body['query']['nested']['query']['bool']['filter'] = [];
			}
			
			$source_should = [];
			
			if($_GET['dans']){
				array_push(
					$source_should,
					[ 'term' => ['document.source' => 'DANS']]
				);
				array_push(
					$source_should,
					[ 'term' => ['document.source' => 'dans']]
				);
				array_push(
					$source_should,
					[ 'term' => ['document.source' => 'Dans']]
				);
				array_push(
					$source_should,
					['bool' => ['must_not' => [ 'exists' => ['field' => 'document.source']]]]
				);
			}
			if($_GET['archis']){
				array_push(
					$source_should,
					[ 'term' => ['document.source' => 'archis']]
				);
				array_push(
					$source_should,
					[ 'term' => ['document.source' => 'Archis']]
				);
			}
			if($_GET['onroerend_erfgoed']){
				array_push(
					$source_should,
					[ 'term' => ['document.source' => 'onroerend_erfgoed']]
				);
			}
			if($_GET['onroerend_erfgoed_notas']){
				array_push(
					$source_should,
					[ 'term' => ['document.source' => 'onroerend_erfgoed_notas']]
				);
			}
			if($_GET['kb']){
				array_push(
					$source_should,
					[ 'term' => ['document.source' => 'kb']]
				);
			}
			if($_GET['sidestone']){
				array_push(
					$source_should,
					[ 'term' => ['document.source' => 'sidestone']]
				);
			}
			
			array_push(
				$body['query']['nested']['query']['bool']['filter'],
				[ 'bool' => [ 'should' => $source_should ]]
			);
		}

		

		// location search polygon (not used at the moment)
		if($_GET['coords']){
			$body['query']['bool']['filter'] = [
				'geo_polygon' => [
					'document.location' => [
						'points' => json_decode($_GET['coords'])
					]
				]
			];
			if(!$_GET['query']){ // only coord search, set match_all
				$body['query']['bool']['must'] = ['match_all' => ['boost'=>1.0]]; 
			}
		}
		
		

		
		// filter on facets/aggregations, if any
		if($_GET['facets']){
			
			$body['query']['bool']['must'] = $body['query']; //add bool -> must layer for filter to go next to
			unset($body['query']['nested']); // delete existing nest as we just copied it
			$body['query']['bool']['filter']['bool']['should'] = [];
			$facets = json_decode(urldecode($_GET['facets']));
			$selectedFacets = $facets;
			
			foreach($facets as $name => $facet){
				if(count($facet)){
					foreach($facet as $f){
						array_push(
							$body['query']['bool']['filter']['bool']['should'], 	
							[ 'term' => [ $name.'.keyword' => $f]]
						);
					}
				}
			}
		}
		
		
		
		


		
	
	} // end normal query
	
	// exclude stuff we don't need
	$body['_source'] = [
		'excludes' => [
			"document.pages"
		]
	];  
		
	// set size and page
	$body['size'] = $numPerPage;
	$body['from'] = $from;
		
	$params = [
		'index' => $esIndex,
		//'type' => $searchLvl,
		//'type' => 'timespan',          
		'body' => $body
	];

	if($_GET['debug'] && !$_GET['export']){
		print_r($params);//exit;
	}
	
	

	// get results from ES
	try {
		$results = $client->search($params);
	} catch (\Elasticsearch\Common\Exceptions\Serializer\JsonErrorException $e) {
		echo "JSON Error: " . $e->getMessage();
		echo "Raw Response: " . $e->getRawResponse();
	}


	if($_GET['debug'] && !$_GET['export']){
		print_r($body); 
		print_r($results);
		exit;
	}
	
	

	
	// EXPORT, loop through ALL results (may take while...)
	if($_GET['export'] == 'geojson' || $_GET['export'] == 'csv' || $_GET['export'] == 'ris'){

		$geoJson = array(
			'type' => 'FeatureCollection',
			'features' => []
		);
		$csvOutput = 'id,title,authors,publication_year,file_type,snippets,page_numbers,page_links,subjects,locations,doi,archis_nummer,lat,lon,coordX,coordY,description,estimated_relevance_score
';
		$risOutput = '';

		// do first batch to see how many batches we need
		$params['body']['size'] = 100;
		$first = $client->search($params);
		$numberofpages = round($first['hits']['total']['value'] / $params['body']['size'])+1;
		
		# ES doesn't like to go over 20.000 results, so cap the pages to 199
		if($numberofpages > 199){
			$numberofpages = 199;
		}

		for ($i = 0; $i <= $numberofpages; $i++) {
			$params['body']['from'] = $i*$params['body']['size'];
			
			try {
				$results = $client->search($params);
			} 
			catch (\Elasticsearch\Common\Exceptions\Serializer\JsonErrorException $e) {
				$bla = 1;
			}

			
			foreach($results['hits']['hits'] as $hit){
				
				$doc = $hit['_source']['document'];
				
				$id = $hit['_id'];
				$file_name = $doc['file_name'];
				$file_location = $doc['file_location'];
				$file_type = $doc['file_type'];
				$lat = $doc['location']['lat'];
				$lon = $doc['location']['lon'];
				$coordX = $doc['coordX'];
				$coordY = $doc['coordY'];
				$title = $doc['title'];
				$description = $doc['description'];
				$created_at = $doc['createdAt']; 
				$score = $hit['_score']; 
				
				$creators = '';
				if($doc['creators']){
					foreach($doc['creators'] as $creator){
						$creators .= $creator.'
';
					} 
					$creators = substr($creators,0,-1); // take off trailing linebreak
				}
				
				$subjects = '';
				if($doc['subjects']){
					foreach($doc['subjects'] as $subject){
						$subjects .= $subject.'
';
					}
					$subjects = substr($subjects,0,-1); // take off trailing linebreak
				}
				
				$locations = '';
				if($doc['locations']){
					foreach($doc['locations'] as $location){
						$locations .= $location.'
';
					}
					$locations = substr($locations,0,-1); // take off trailing linebreak
				}

				$doi = '';
				if($doc['identifiers']['DOI']){
					$doi = "https://doi.org/".$doc['identifiers']['DOI'];
				}
				elseif($doc['identifiers']['doi']){
					$doi = "https://doi.org/".$doc['identifiers']['doi'];
				}
				elseif ($doc['identifiers']['uri']){
					$doi = $doc['identifiers']['uri'];
				}
				
				$archisLink = '';
				$archis_nummer = $doc['identifiers']['Archis_onderzoek_m_nr'];
				if($doc['identifiers']['Archis_onderzoek_m_nr']){
					$archisLink = "https://zoeken.cultureelerfgoed.nl/#/zaak/search/(zaak:(fields:(archis2_onderzoekmeldingsnummer:%27".$doc['identifiers']['Archis_onderzoek_m_nr']."%27)))";
					$archis_nummer = $doc['identifiers']['Archis_onderzoek_m_nr'];
				}
				elseif($doc['identifiers']['archis_zaakidentificatie']){
					$archis_nummer = $doc['identifiers']['archis_zaakidentificatie'];
				}
				
				$page_number = '';
				$page_links = '';
				

				
				if($hit['inner_hits']['document']['hits']['hits'][0]['inner_hits']['document.pages']['hits']['hits']){
					
					foreach($hit['inner_hits']['document']['hits']['hits'][0]['inner_hits']['document.pages']['hits']['hits'] as $document){
						
						// make page link based on source
						if( $hit['_source']['document']['source'] ){
							if( $hit['_source']['document']['source'] == 'onroerend_erfgoed' || $hit['_source']['document']['source'] == 'onroerend_erfgoed_notas' ){ // OE
								$page_links .= 'https://agnessearch.nl/html/'.$hit['_source']['document']['source'].'/'.$hit['_source']['document']['identifiers']['oe_id'].'_'.str_replace('.pdf','/index-'.$document['_source']['page_number'].'.html',$hit['_source']['document']['file_name']).'
';
							}
							elseif( $hit['_source']['document']['source'] == 'archis' ){ // archis
								$page_links .= 'https://agnessearch.nl/html/archis/'.str_replace('.pdf','/index-'.$document['_source']['page_number'].'.html',$hit['_source']['document']['file_name']).'
';
							}
							elseif( $hit['_source']['document']['source'] == 'kb' ){ // kb
								$page_links .= 'https://agnessearch.nl/html/kb/'.$hit['_source']['document']['identifiers']['ppn'].'/index-'.$document['_source']['page_number'].'.html
';
							}
							elseif( $hit['_source']['document']['source'] == 'sidestone' ){ // sidestone
								$page_links .= 'https://agnessearch.nl/html/sidestone/'.$hit['_source']['document']['identifiers']['ISBN'].'/index-'.$document['_source']['page_number'].'.html
';
							}
							elseif( $hit['_source']['document']['source'] == 'dans' ){ // dans
								$page_links .= 'https://agnessearch.nl/html/dans/'.str_replace('.pdf','/index-'.$document['_source']['page_number'].'.html',$hit['_source']['document']['file_name']).'
';
							}
							
						}
						else { // no source filled in, early DANS import
							$page_links .= 'https://agnessearch.nl/html/dans/'.str_replace('.pdf','/index-'.$document['_source']['page_number'].'.html',$hit['_source']['document']['file_name']).'
';
						}
						$page_number .= $document['_source']['page_number'].' / ';
					}
					$page_number = substr($page_number,0,-3); // take off trailing slash
					$page_links = substr($page_links,0,-1); // take off trailing linebreak
				}
				
				$snippets = '';
				foreach($hit['highlight']['document.pages.content'] as $snippet){
					$snippets .= $snippet.'
';
				}
				
				// if geojson export requested, add to array
				if($_GET['export'] == 'geojson'){
					array_push($geoJson['features'], array( 
						'type' => 'Feature',
						'geometry' => [
							'type' => 'Point',
							'coordinates' => [$lon, $lat]
						],
						'properties' => [
							'title' => $title,
							'doi' => $doi,
							'creators' => $creators,
							'subjects' => $subjects,
							'locations' => $locations,
							'description' => $description,
							'created_at' => $created_at,
							'snippets' => $snippets,
							// TODO add entities / other info
						]
					));
				}
				// if csv export requested, add to string
				if($_GET['export'] == 'csv'){    
					$csvOutput .= '"'.str_replace('"',"'",$id).'",';
					$csvOutput .= '"'.str_replace('"',"'",$title).'",';
					$csvOutput .= '"'.str_replace('"',"'",$creators).'",';
					$csvOutput .= $created_at.',';
					$csvOutput .= $file_type.',';
					$csvOutput .= '"'.str_replace('"',"'",$snippets).'",';
					$csvOutput .= $page_number.',';
					$csvOutput .= '"'.str_replace('"',"'",$page_links).'",';
					$csvOutput .= '"'.str_replace('"',"'",$subjects).'",';
					$csvOutput .= '"'.str_replace('"',"'",$locations).'",';
					$csvOutput .= $doi.',';
					$csvOutput .= $archis_nummer.',';
					$csvOutput .= $lat.',';
					$csvOutput .= $lon.',';
					$csvOutput .= $coordX.',';
					$csvOutput .= $coordY.',';
					$csvOutput .= '"'.str_replace('"',"'",$description).'",';
					$csvOutput .= $score;
					$csvOutput .= '
';
				}
				
				// if RIS export requested, add to string [NOT FINISHED]
				if($_GET['export'] == 'ris'){
					$risOutput .= 'TY  - RPRT
';
					if($doc['creators']){
						foreach($doc['creators'] as $creator){
							$risOutput .= 'AU  - '+$creator.'
';
						} 
					} 
				}
				
			}
			
		}
		
		$querydesc = '';
		if($_GET['query']){
			$querydesc .= str_replace(' ','-',str_replace('"','',str_replace('*','-wildcard',trim($_GET['query'])))).'_';
			$querydesc = str_replace('
','',$querydesc);
		}
		if($_GET['startdate']){$querydesc .= $_GET['startdate'].'-';}
		if($_GET['enddate']){$querydesc .= $_GET['enddate'].'_';}
		if($_GET['ART']){$querydesc .= $_GET['ART'].'_';}
		if($_GET['CON']){$querydesc .= $_GET['CON'].'_';}
		if($_GET['SPE']){$querydesc .= $_GET['SPE'].'_';}
		
		// slice desc if too long
		$querydesc = substr($querydesc, 0, 30);
		
		$filename = 'AGNES_export_'.$querydesc.date("d-m-Y");
		
		// if geojson requested, output it as a file download
		if($_GET['export'] == 'geojson'){
			header('Content-type: text/plain');
			header('Content-Disposition: attachment; filename="'.$filename.'.geojson"');
			$geoJson = json_encode($geoJson, JSON_PRETTY_PRINT);
			echo $geoJson;
		}
		
		// if csv requested, output it as a file download
		if($_GET['export'] == 'csv'){
			header("Content-type: application/octet-stream");
			header('Content-Disposition: attachment; filename="'.$filename.'.csv"');
			echo $csvOutput;
		}
		
		exit;
	}

	// NOT export, normal search, get first 100 results to show on map TODO: make ajax to save loading time.
	else {      

		// get 100 results, more will take too long
		$body['size'] = 100;
		$body['from'] = 0;
		$params = [
			'index' => $esIndex,
			//'type' => $searchLvl,
			'body' => $body
		];
		
		try {
			$allResults = $client->search($params);
		} 
		catch (\Elasticsearch\Common\Exceptions\Serializer\JsonErrorException $e) {
			$bla = 1;
		}

			  
		$geoPoints = array();
		$foundDocs = array();
		

		foreach($allResults['hits']['hits'] as $hit){

			$doc = false;

			$doc = $hit['_source']['document'];
			
			if($doc){
				$page_number = '';
				$lat = $doc['location']['lat'];
				$lon = $doc['location']['lon'];
				$title = $doc['title'];
				
				
				$doi = '';
				if($doc['identifiers']['DOI']){
					$doi = "https://doi.org/".$doc['identifiers']['DOI'];
				}
				elseif($doc['identifiers']['doi']){
					$doi = "https://doi.org/".$doc['identifiers']['doi'];
				}
				elseif ($doc['identifiers']['uri']){
					$doi = $doc['identifiers']['uri'];
				}
				
				if($doc['identifiers']['Archis_onderzoek_m_nr']){
					$archisLink = "https://zoeken.cultureelerfgoed.nl/#/zaak/search/(zaak:(fields:(archis2_onderzoekmeldingsnummer:%27".$doc['identifiers']['Archis_onderzoek_m_nr']."%27)))";
					$archis_nummer = $doc['identifiers']['Archis_onderzoek_m_nr'];
				}
				elseif($doc['identifiers']['archis_zaakidentificatie']){
					$archis_nummer = $doc['identifiers']['archis_zaakidentificatie'];
				}
				else {
					$archisLink = '';
				}
				
				array_push($geoPoints, array( 
					'lat' => $lat,
					'lon' => $lon,
					'title' => $title,
					'doi' => $doi,
					'archisLink' => $archisLink
				));
				 
			}
		}

			  
		$jsonGeopoints = json_encode($geoPoints);
		$geoPoints = $jsonGeopoints;
		
		
		// set search id, so we can link the search log to the click log
		$_SESSION['search_id'] = uniqid();
		
		// record search in log
		$log_file = 'logs/search.log';
		//session_id,search_id,datetime,searchterm,startyear,endyear,artefact,context,species,fuzzyness,number_of_results,num_per_page,results_page
		$log_line = $_SESSION['id'].','.$_SESSION['search_id'].','.date("Y-m-d H:i:s").',"'.str_replace('"',"''",$_GET['query']).'",'.$_GET['startdate'].','.$_GET['enddate'].',"'.str_replace('"',"''",$_GET['ART']).'","'.str_replace('"',"''",$_GET['CON']).'","'.str_replace('"',"''",$_GET['SPE']).'",'.$_GET['fuzzyness'].','.$results['hits']['total']['value'].','.$numPerPage.','.$_GET['page']."\n";
		file_put_contents($log_file, $log_line, FILE_APPEND | LOCK_EX);
		
		
	}

}        
	

?>
