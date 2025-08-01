<?php
	include 'search-include.php';
?>

<!-- 
=========================================================
 Light Bootstrap Dashboard - v2.0.1
=========================================================

 Product Page: https://www.creative-tim.com/product/light-bootstrap-dashboard
 Copyright 2019 Creative Tim (https://www.creative-tim.com)
 Licensed under MIT (https://github.com/creativetimofficial/light-bootstrap-dashboard/blob/master/LICENSE)

 Coded by Creative Tim

=========================================================

 The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.  -->
 
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="utf-8" />
	
    <!--     favicons     -->
    <link rel="apple-touch-icon" sizes="57x57" href="assets/img/favicons/apple-icon-57x57.png">
	<link rel="apple-touch-icon" sizes="60x60" href="assets/img/favicons/apple-icon-60x60.png">
	<link rel="apple-touch-icon" sizes="72x72" href="assets/img/favicons/apple-icon-72x72.png">
	<link rel="apple-touch-icon" sizes="76x76" href="assets/img/favicons/apple-icon-76x76.png">
	<link rel="apple-touch-icon" sizes="114x114" href="assets/img/favicons/apple-icon-114x114.png">
	<link rel="apple-touch-icon" sizes="120x120" href="assets/img/favicons/apple-icon-120x120.png">
	<link rel="apple-touch-icon" sizes="144x144" href="assets/img/favicons/apple-icon-144x144.png">
	<link rel="apple-touch-icon" sizes="152x152" href="assets/img/favicons/apple-icon-152x152.png">
	<link rel="apple-touch-icon" sizes="180x180" href="assets/img/favicons/apple-icon-180x180.png">
	<link rel="icon" type="image/png" sizes="192x192"  href="assets/img/favicons/android-icon-192x192.png">
	<link rel="icon" type="image/png" sizes="32x32" href="assets/img/favicons/favicon-32x32.png">
	<link rel="icon" type="image/png" sizes="96x96" href="assets/img/favicons/favicon-96x96.png">
	<link rel="icon" type="image/png" sizes="16x16" href="assets/img/favicons/favicon-16x16.png">
	<link rel="manifest" href="assets/img/favicons/manifest.json">
	<meta name="msapplication-TileColor" content="#75ca2a">
	<meta name="msapplication-TileImage" content="assets/img/favicons/ms-icon-144x144.png">
	<meta name="theme-color" content="#75ca2a">
	
    <title>AGNES - slimme zoekmachine voor de Nederlandse archeologie</title>
	
    <meta content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0, shrink-to-fit=no' name='viewport' />
	
    <!--     Fonts and icons     -->
    <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700,200" rel="stylesheet" />
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/latest/css/font-awesome.min.css" />
	
    <!-- CSS Files (plugins) -->
    <link href="assets/css/bootstrap.min.css" rel="stylesheet" />
    <link href="assets/css/light-bootstrap-dashboard.css?v=2.0.0 " rel="stylesheet" />
	<link href="assets/css/jqpagination.css" rel="stylesheet" type="text/css" media="all">	
	<link href="assets/css/featherlight.css" rel="stylesheet" type="text/css" media="all">
	<link rel="stylesheet" type="text/css" href="//cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.1.0/cookieconsent.min.css" />
	<link rel="stylesheet" href="https://code.jquery.com/ui/1.14.1/themes/base/jquery-ui.css">
	
    <!-- Main CSS file -->
	<link href="assets/css/main.css" rel="stylesheet" type="text/css" media="all">

</head>

<body class="<?php if($queryFired){ echo 'queryFired';}?>" >
    <div class="wrapper">
        <div class="sidebar" data-image="assets/img/arch-bg.jpg" data-color="blue">

            <div class="sidebar-wrapper">
                <div class="logo">
                    <a href="/" class="simple-text">
                        <img src="assets/img/agnes-logo-white-400w.png" alt="AGNES logo" />
                    </a>
                </div>
				
				<div class="sidesearch" style="height:auto;">
					<form method="get" id="queryform">
					
						<?php if($_GET['advanced'] || $_GET['advanced_query']){ // begin advanced query?>
						
							<div>
								<strong>Advanced Query</strong>
							</div>
							<textarea id="advanced_query" name="advanced_query" style="width:100%;height:300px;"><?php echo str_replace('"','&quot;',$_GET['advanced_query']);?></textarea>
						
						<?php } else { // begin normal search ?>
					
							<div>
								<strong>Zoekopdracht</strong>
								<a href="#" class="dropdown-toggle" data-toggle="dropdown" >
									<i class="nc-icon nc-bulb-63"></i>
								</a>
								<div class="dropdown-menu">
									<p>Vul 1 of meerdere zoektermen in. Voor meer informatie, zie de <a  href="#" data-featherlight="#handleiding">handleiding</a>.</p>
								</div>
							</div>
							<textarea name="query" id="query" class="autocomplete-query" style="margin-top:6px;height:60px;"><?php echo str_replace('"','&quot;',$_GET['query']);?></textarea>
							
							<div id="advsearch" >
								<a href="#" class="dropdown-toggle" data-toggle="dropdown" >
									<i class="nc-icon nc-bulb-63"></i>
								</a>
								<div class="dropdown-menu">
									<p>Zie de <a href="#" data-featherlight="#handleiding">handleiding</a> voor de mogelijkheden.</a>.</p>
								</div>
								<input type="checkbox" class="advanced_search" name="advanced_search" value="1" <?php if($_GET['advanced_search']){echo 'checked="checked"';}?> style="width:auto;margin-right:5px;">
								<label for="advanced_search"> Geavanceerd zoeken?</label><br>
							</div>
							
							
							<br />
							<button type="submit" id="searchsubmit" class="btn btn-success btn-wd" >
								<i class="nc-icon nc-zoom-split"></i>
								Zoeken
							</button>

					
							<hr />
							
							<div>						
							
								<a href="#" class="dropdown-toggle" data-toggle="dropdown" >
									<i class="nc-icon nc-bulb-63"></i>
								</a>
								<div class="dropdown-menu">
									<p>Selecteer in welke bronnen je wilt zoeken</p>
								</div>
								<em>Bronnen</em><br>
								
								<input type="checkbox" class="source_checkbox" name="dans" value="Dans" <?php if($_GET['dans'] || !$_GET['query']){echo 'checked="checked"';} ?>>
								<label for="dans"> DANS</label><br/>
								<input type="checkbox" class="source_checkbox" name="archis" value="Archis" <?php if($_GET['archis'] || !$_GET['query']){echo 'checked="checked"';} ?>>
								<label for="archis"> Archis</label><br/>
								<input type="checkbox" class="source_checkbox" name="onroerend_erfgoed" value="Onroerend Erfgoed Rapporten" <?php if($_GET['onroerend_erfgoed'] || !$_GET['query']){echo 'checked="checked"';} ?>>
								<label for="onroerend_erfgoed"> Onroerend Erfgoed Rapporten</label><br/>
								<input type="checkbox" class="source_checkbox" name="onroerend_erfgoed_notas" value="Onroerend Erfgoed Nota's" <?php if($_GET['onroerend_erfgoed_notas'] || !$_GET['query']){echo 'checked="checked"';} ?>>
								<label for="onroerend_erfgoed_notas"> Onroerend Erfgoed Nota's</label><br/>
								<input type="checkbox" class="source_checkbox" name="kb" value="KB" <?php if($_GET['kb'] || !$_GET['query']){echo 'checked="checked"';} ?>>
								<label for="kb"> Koninklijke Bibliotheek (1960-1990)</label><br/>
								<input type="checkbox" class="source_checkbox" name="sidestone" value="Sidestone" <?php if($_GET['sidestone'] || !$_GET['query']){echo 'checked="checked"';} ?>>
								<label for="sidestone"> Sidestone Press</label><br/>

								<hr />
							
							</div>
							
						   
							<div style="margin-bottom:10px;">
								<em>Tijdsperiode</em>
								<a href="#" class="dropdown-toggle" data-toggle="dropdown" >
									<i class="nc-icon nc-bulb-63"></i>
								</a>
								<div class="dropdown-menu">
									<p>Optioneel: vul een start en eind jaar in. Gebruik een min streepje (-) voor jaartallen voor Christus.</p>
								</div>
							</div>
						
							<label>Begin jaar: </label>
							<input type="number" name="startdate" value="<?php echo $_GET['startdate'];?>" />
							
							<label>Eind jaar: </label>
							<input type="number" name="enddate" value="<?php echo $_GET['enddate'];?>" />

							<hr />
						   
							<div style="margin-bottom:10px;">
								<em>Specifiek zoeken</em>
								<a href="#" class="dropdown-toggle" data-toggle="dropdown" >
									<i class="nc-icon nc-bulb-63"></i>
								</a>
								<div class="dropdown-menu">
									<p>Geen goede resultaten? Probeer te zoeken op concepten</p>
								</div>
							</div>
							
							<label style="width:120px;">Artefact: &nbsp; </label>
								<input type="text" name="ART" value="<?php echo $_GET['ART'];?>" />
							<br/>
							<label style="width:120px;">Context: &nbsp; </label>
								<input type="text" name="CON" value="<?php echo $_GET['CON'];?>" />
							<br/>
							<label style="width:120px;">Soortnaam: &nbsp; </label>
							<input type="text" name="SPE" value="<?php echo $_GET['SPE'];?>" />
						   
							<div style="clear:both;"></div>
							<hr/>
							
							
						
							
							
							
							
							<input type="hidden" name="top" value="<?php echo $_GET['top'];?>" />
							<input type="hidden" name="bottom" value="<?php echo $_GET['bottom'];?>" />
							<input type="hidden" name="left" value="<?php echo $_GET['left'];?>" />
							<input type="hidden" name="right" value="<?php echo $_GET['right'];?>" />

							<hr />
							
						<?php } // end normal search ?>
						
						<!--input type="hidden" name="coords" id="coords" value='<?php echo $_GET['coords']; ?>'  /-->
						<input type="hidden" name="resultsperpage" id="resultsperpage" value='<?php echo $_GET['resultsperpage']; ?>'  />
						
						
						<button type="submit" id="searchsubmit" class="btn btn-success btn-wd" >
							<i class="nc-icon nc-zoom-split"></i>
							Zoeken
						</button>
						
					</form>
				</div>
				
				<div class="facets">
					<?php 
						if($queryFired){
					?>	
						<!--button type="button" class="btn btn-wd btn-info"  id="toggle-search-form" >
							<span class="label">Pas zoekopdracht aan</span>
							<i class="nc-icon nc-settings-tool-66"></i>
						</button-->
					<?php 
						}
					?>	
					
					
					<?php 
						if($results['aggregations']){ 
							// get abr codes to text translations
							$abr = explode(PHP_EOL, file_get_contents('data/abr_periode_en_complex_codes.csv'));
							$abrCodes = [];
							foreach($abr as $row){
								$rowArray = explode(',',$row);
								$abrCodes[$rowArray[0]] = $rowArray[1];
							}
							// facet to dutch translation
							$facetNames = [
								'file_type' => 'Type document',
								'subjects' => 'Onderwerp',
								'temporals' => 'Periode',
							];
					?>
							<hr/>
							
					<?php } ?>
                
				</div>
            </div>
        </div>
		
<!--   START MAIN PANEL ---------------------------------------------------------------------------------------------->		
		
        <div class="main-panel">
            <!-- Navbar -->
            <nav class="navbar navbar-expand-lg " color-on-scroll="500">
                <div class="container-fluid">
                    <a class="navbar-brand" href="/"> Dashboard </a>
                    <button href="" class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" aria-controls="navigation-index" aria-expanded="false" aria-label="Toggle navigation">
						<span class="navbar-toggler-bar burger-lines"></span>
						<span class="navbar-toggler-bar burger-lines"></span>
						<span class="navbar-toggler-bar burger-lines"></span>
					</button>
                    <div class="collapse navbar-collapse justify-content-end" id="navigation">
                        <ul class="navbar-nav ml-auto">
                            <li class="nav-item">
                                <a class="nav-link" href="#" data-featherlight="#handleiding">
                                    <span class="no-icon">Handleiding</span>
                                </a>
								<div id="handleiding" class="hidden">
									<h2>Handleiding</h2>
									<p>AGNES is een zoekmachine voor de Nederlandse archeologie. We nemen documenten op uit een aantal verschillende archieven, en maken die makkelijk doorzoekbaar.</p>
									
									<h3>Zoeken en Resultaten</h3>
									<p>De makkelijkste manier om te zoeken is via het 'zoekopdracht' veld. Vul simpelweg de gewenste term(en) in, klik op 'zoeken' en alle documenten waar die 1 of meer van die termen voorkomen op 1 pagina worden getoond, gesorteerd op relevantie (meer termen = hoger). De resultaten worden getoond met snippets en links naar zowel een preview van de pagina, als een link naar het archief om de PDF te downloaden. Ook is er metadata beschikbaar, zoals de beschrijving, auteurs, enzovoorts.</p>
									
									<h3>Geavanceerd zoeken</h3>
									<p>Voor complexe zoekopdrachten kan het 'Geavanceerd zoeken?' vinkje worden aangevinkt. Dit activeerd een aantal functies:
									<ul>
										<li>Precies zoeken. Gebruik hiervoor dubbele aanhalingstekens. Meerdere woorden binnen aanhalingstekens moeten precies zo, naast elkaar, voorkomen om gevonden te worden. Dus de zoekterm <em>romeinse wachttoren</em> vind documenten waar beide woorden ergens voorkomen, maar <em>"romeinse wachttoren"</em> vind alleen documenten waar die woorden precies zo naast elkaar staan.</li>
										<li>Combineren met plus en min. Als er meerdere termen in de zoekopdracht staan, neemt AGNES aan dat je 1 of meerdere wilt per document. Dus "bijl vuursteen graf" vind documenten die 1 of meer van die termen bevatten. Gebruik plus ("+") om aan te geven dat een term voor MOET komen, dus "+bijl +vuursteen graf" vind documenten die bijl en vuursteen bevatten, met of zonder de term neolithicum. Gebruik min ("-") om woorden uit te sluiten, dus "+bijl +vuursteen graf -hunebed" vind documenten die bijl en vuursteen bevatten, wel of niet graf bevatten, en geen hunebedden bevatten.</li>
										<li>Combineren met AND, OR, NOT, en haakjes. In plaats van + en -, kunnen zoekopdrachten ook uitgedrukt worden met AND/OR/NOT en haakjes. De vorige zoekopdracht ziet er dan zo uit: "((bijl AND vuursteen) OR graf) AND NOT hunebed.</li>
										<li>Wildcards. Gebruik hiervoor het asterisk/sterretje ("*"). De asterisk staat voor 0, 1, of meer letters. Bijvoorbeeld, de zoekterm "ploegspo*" vind zowel "ploegspo" (mocht dit voorkomen), als "ploegspoor" en ook "ploegsporen". Gebruik vraagteken ("?") om precies 1 letter te vervangen, dus "m?nt" vind zowel "munt" als "mint". Dit kan gecombineerd worden met gecombineerd zoeken zoals hierboven.</li>
										<li>Fuzzyness. Gebruik hiervoor de tilde ("~") en het cijfer 1 of 2. Hiermee kan je woorden vinden die 1 of 2 letters verschillen van de zoekterm. Zo vind 'schraper~1' ook de termen 'scraper' en 'sraper' bijvoorbeeld, en 'schraper~2' ook 'scrape' en 'shrapel', enz. Fuzzyness kan niet gecombineerd worden met wildcards, maar wel met gecombineerd zoeken.</li>
									</ul>
									<p>Het is goed om te weten dat als een geavanceerde zoekopdracht niet goed geformatteerd is, of als er speciale karakters in voorkomen, er zich een error voor doet. Check in dit geval nog een keer goed de zoekopdracht.</p>
									
									<h3>Filteren en Specifiek Zoeken<h3>
									<p>Naast het zoeken op een zoekopdracht, is het ook mogelijk om te filteren. De Tijdsperiode velden kunnen gebruikt worden om een bepaalde periode aan te geven, via een start en eind jaar. Gebruik een min streepje ("-") om voor Christus aan te geven. We gebruiken kunstmatige intelligentie om automatisch alle verschillende uitdrukkingen van tijdsperiodes om te rekenen naar een start en eind jaar. Een zoekopdracht van 500 tot 1500 n.Chr. zal dan ook resultaten weergeven van bv. 'middeleeuwen', 'merovingisch', '1200 n.Chr', '12e eeuw' en '1024 BP +/- 12'. Wees je er echter wel bewust van dat dit niet 100% accuraat is, en ook dat de tijdsperiode voor moet komen op dezelfde pagina als de zoekterm.</p>
									<p>Onder 'Specifiek zoeken' is het mogelijk om op artefacten, contexten, en soortnamen te zoeken. Hier weet het systeem het verschil tussen bijvoorbeeld "Meneer Bijl" en "een vuursteen bijl", en zal alleen het tweede resultaat laten zien. Dit is echter nog een experimentele functie, en is de normale zoekopdracht betrouwbaarder, zeker als de zoekopdracht een redelijk unieke archeologische term is.</p>
									
									<h3>Kaart</h3>
									<p>De resultaten worden ook op de kaart weergegeven. Let wel op: de kaart is geen volledig overzicht! Het laat alleen de eerste 100 resultaten zien, en alleen documenten waarvan coordinaten bekend zijn. </p>
									
									<h3>Export</h3>
									<p>Gebruik de GeoJSON of Excel CSV export knop om alle resultaten te exporteren voor verdere analyse. GeoJSON kan geopend worden in GIS programma's, en CSV in Excel / Calc / Google Sheets, of andere software.<p>
									<p>Voor het verder verwerkern van de CSV export, is er een Excel bestand met macro's beschikbaar, dat bijvoorbeeld kan filteren op onderwerp, document type, en dubbele documenten kan verwijderen. Deze tool is ontwikkeld door Martha Schuppert, en is hier te downloaden: <a href="assets/Workflow_AGNES_export_NL.xlsm">Excel Workflow</a>.</p>
									<p> </p>
									<p>Toch nog vragen? Neem contact op via <a href="mailto:a.brandsen@arch.leidenuniv.nl?subject=Vraag over AGNES">a.brandsen@arch.leidenuniv.nl</a>.</p>
								</div>
                            </li>
							<li class="nav-item">
                                <a class="nav-link" href="#" data-featherlight="#bronnen">
                                    <span class="no-icon">Databronnen</span>
                                </a>
								<div id="bronnen" class="hidden">
									<h2>Databronnen</h2>
									<p>AGNES neemt documenten op uit meerdere bronnen. Echter zijn op dit moment niet alle bronnen helemaal up-to-date, hier wordt wel aan gewerkt. In de huidige versie van AGNES (versie 3.2), zijn de volgende bronnen opgenomen:</p>
									<ul>
										<li>Alle documenten uit het <a href="https://archaeology.datastations.nl/dataverse/root?q=" target="_blank">DANS</a> archief gemarkeerd met de 'Archeologie' tag, wekelijks geupdate met nieuwe documenten</li>
										<li>Alle documenten uit <a href="https://archis.cultureelerfgoed.nl/" target="_blank">Archis</a>, tot en met december 2021</li>
										<li>Alle rapporten uit het <a href="https://oar.onroerenderfgoed.be/" target="_blank">Onroerend Erfgoed</a> archief,  wekelijks geupdate met nieuwe documenten</li>
										<li>Alle nota's uit het <a href="https://oar.onroerenderfgoed.be/" target="_blank">Onroerend Erfgoed</a> archief,  wekelijks geupdate met nieuwe documenten</li>
										<li>Boeken uit de <a href="https://www.kb.nl/" target="_blank">Nationale Bibliotheek</a> met het onderwerp archeologie, van 1960 tot 1990</li>
										<li>Boeken uit de collectie van <a href="https://www.sidestone.com/" target="_blank">Sidestone Press</a> met het onderwerp archeologie, alleen boeken in het Nederlands, Duits of Engels</li>
									</ul>
								</div>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="mailto:a.brandsen@arch.leidenuniv.nl?subject=Contact over AGNES&body=<?php //echo $current_url; ?>">
                                    <span class="no-icon">Contact</span>
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
            <!-- End Navbar -->
			
            <div class="content">
                <div class="container-fluid">
                    <div class="row">
                        <div class="col-md-12">
                            <div class="card ">
                                <div class="card-header ">
                                    <h4 class="card-title">AGNES v3.2</h4>
                                    <p class="card-category"> (beta)</p>
                                </div>
                                <div class="card-body ">
								
									<p>Zoek door ~220.000 archaeologische documenten uit verschillende <a href="#" data-featherlight="#bronnen">archieven</a>. </p>
									
									
									<p class="show-on-desktop"><em>Gebruik de velden in de linker kolom om te zoeken.</em> Zie ook de <a href="#" data-featherlight="#handleiding">handleiding</a> voor meer informatie.</p>
									<p class="show-on-mobile"><em>Gebruik de menuknop rechts boven om te zoeken.</em> Zie ook de <a href="#" data-featherlight="#handleiding">handleiding</a> voor meer informatie.</p>
									
									<p><strong>Let op</strong>: deze versie is nog niet uitgebreid getest, gebruik op eigen risico. Mocht zich een foutmelding voor doen, of lukt iets niet, mail dan naar <a href="mailto:a.brandsen@arch.leidenuniv.nl?subject=Contact over AGNES&body=<?php //echo $current_url; ?>">a.brandsen@arch.leidenuniv.nl</a> en vermeld de foutmelding en de huidige URL (kopieer deze uit de adresbalk).</p>
                                </div>
                            </div>
                        </div>
                    </div>
					<div class="row map-row">
                        <div class="col-md-12">
                            <div class="card ">
                                <div class="card-header ">
									<button type="button" id="reset-btn" class="btn btn-primary" >
										Reset
										<i class="nc-icon nc-simple-remove"></i>
									</button>
                                    <h4 class="card-title">Kaart</h4>
									<p style="font-size:80%;">Let op: de kaart is geen volledig overzicht! Het laat alleen de eerste 100 resultaten zien, en alleen documenten waarvan coordinaten bekend zijn. Gebruik de GeoJSON export knop om meer dan 100 resultaten te exporteren, deze kan in een GIS programma geopend worden.</p>
                                </div>
                                <div class="card-body ">
					
									<?php if($results['hits']['total']['value'] == 0){ // if no hits, or no search, show empty search map ?>
										
										<div id="mapsearch" style="display:none;height:400px;">
											<div id="map"></div>
										</div>
									<?php } ?>
									
									<?php 
										if($queryFired){
											if($results['hits']['total']['value'] > 0){ 
									?>	
									
												<div id="map"></div>
												
												<button type="button" class="btn btn-xs btn-info export-btn"  onclick="showMessage('Export aan het ophalen...','Dit kan even duren als er veel resultaten zijn!');trackClick('geojsonExport','','');document.location='<?php echo $_SERVER['REQUEST_URI']; ?>&export=geojson';" >		 
													Export voor GIS (GeoJSON)  
													<i class="nc-icon nc-cloud-download-93"></i> 
												</button>
												<button type="button" class="btn btn-xs btn-info export-btn"  onclick="showMessage('Export aan het ophalen...','Dit kan even duren als er veel resultaten zijn!');trackClick('csvExport','','');document.location='<?php echo $_SERVER['REQUEST_URI']; ?>&export=csv';" >		 
													Export voor Excel (CSV)  
													<i class="nc-icon nc-cloud-download-93"></i> 
												</button>
												<button type="button" class="btn btn-xs btn-info"  id="enlarge-map" >		 
													<i class="nc-icon nc-map-big"></i> 
													Vergroot Kaart 
												</button>
												
									
												<hr/>
												
												
												
												<div id="results">
									
													<div class="row">
														<div class="col-sm-4 col-xs-4">
															<p>Aantal resultaten: <?php echo $results['hits']['total']['value']; ?></p>
														</div>
														<div class="col-sm-4 col-xs-4 textaligncenter">
															<p>Pagina <?php echo $_GET['page']; ?> van <?php echo floor($results['hits']['total']['value'] / $numPerPage)+1; ?></p>
														</div>
														<div class="col-sm-4 col-xs-4 textalignright">
															<p>
																Resultaten per pagina: 
																<select id="resultsperpageselect">
																	<?php
																		$values = array(10,25,50,100);
																		foreach($values as $value){
																			echo '<option value="'.$value.'" '.($_GET['resultsperpage'] == $value ? 'selected="selected"':'').'>'.$value.'</option>';
																		}
																	?>
																</select>
															</p>
														</div>
													</div>
													
													
													
													<div class="results">
														<?php 
															$documentsArray = array();
															//print_r($results);
															foreach ($results['hits']['hits'] as $hit) {
																//print_r( $hit);exit();
																$result = $hit['_source']['document'];  

																// set title
																if($result['title']){
																	$documentTitle = $result['title'];
																}
																else {
																	$documentTitle = '--Geen titel--';
																}
																
																// set source name
																if( $result['source'] ){
																	if( $result['source'] == 'onroerend_erfgoed' || $result['source'] == 'onroerend_erfgoed_notas' ){
																		$source = "Onroerend Erfgoed (Vlaanderen)";
																	}
																	elseif( $result['source'] == 'archis' ){
																		$source = 'Archis';
																	}
																	elseif( $result['source'] == 'kb' ){
																		$source = 'de Nationale Bibliotheek';
																	}
																	elseif( $result['source'] == 'dans' ){
																		$source = 'DANS';
																	}
																	elseif( $result['source'] == 'sidestone' ){
																		$source = 'Sidestone Press';
																	}
																}
																else {
																	$source = 'DANS';
																}
																
																// set file name
																$file_name = $result['file_name'];
																if( !$result['source'] || $result['source'] == 'dans'){
																	// dans, remove D number
																	#print_r(explode('_',$result['file_name']));
																	$file_array = explode('_',$result['file_name']);
																	array_shift($file_array);
																	$file_name = implode('_',$file_array);
																}
																
																// set archive link
																if( $result['identifiers']['DOI'] ){
																	$archive_link = 'https://doi.org/'.$result['identifiers']['DOI'];
																}
																elseif ( $result['identifiers']['doi'] ){
																	$archive_link = 'https://doi.org/'.$result['identifiers']['doi'];
																}
																elseif ( $result['identifiers']['ppn'] ){
																	$archive_link = 'https://webggc.oclc.org/cbs/DB=2.37/XMLPRS=Y/PPN?PPN='.$result['identifiers']['ppn'];
																}
																elseif ( $result['identifiers']['uri'] ){
																	$archive_link = $result['identifiers']['uri'];
																}
																													
												
																// page links  and timespans
																$pagePreviewHtml = ''; 
																$timespanString = ''; 
																
																														
																$pages = $hit['inner_hits']['document']['hits']['hits'][0]['inner_hits']['document.pages']['hits']['hits'];
																//print_r($hit['inner_hits']['document']['hits']['hits'][0]['inner_hits']['document.pages']['hits']['hits']);
																
																foreach($pages as $page){
																	//print_r($page);

																	// make page link based on source
																	if( $result['source'] ){
																		if( $result['source'] == 'onroerend_erfgoed' || $result['source'] == 'onroerend_erfgoed_notas' ){
																			$pageLink = 'https://agnessearch.nl/html/'.$result['source'].'/'.$result['identifiers']['oe_id'].'_'.str_replace('.pdf','/index-'.$page['_source']['page_number'].'.html',$result['file_name']);
																		}
																		elseif( $result['source'] == 'archis' ){
																			$pageLink = 'https://agnessearch.nl/html/archis/'.str_replace('.pdf','/index-'.$page['_source']['page_number'].'.html',$result['file_name']);
																		}
																		elseif( $result['source'] == 'kb' ){
																			$pageLink = 'https://agnessearch.nl/html/kb/'.$hit['_source']['document']['identifiers']['ppn'].'/index-'.$page['_source']['page_number'].'.html';
																		}
																		elseif( $result['source'] == 'sidestone' ){
																			$pageLink = 'https://agnessearch.nl/html/sidestone/'.$hit['_source']['document']['identifiers']['ISBN'].'/index-'.$page['_source']['page_number'].'.html';
																		}
																	}
																	else { // no source noted; early dans import
																		$pageLink = 'https://agnessearch.nl/html/dans/'.str_replace('.pdf','/index-'.$page['_source']['page_number'].'.html',$result['file_name']);
																	}
																	
																	$pagePreviewHtml .= '<a href="'.$pageLink.'" class="pagePreview" onclick="trackClick(\'pagePreview\',\''.$source.'\',\''.$hit['_id'].'\');">'.$page['_source']['page_number'].'</a> / ';
																	if($page['inner_hits']['document.pages.timespans']['hits']){
																		//print_r($page);
																		foreach($page['inner_hits']['document.pages.timespans']['hits']['hits'] as $timespan){
																			//print_r($timespan);
																			// get index of timespan from timespan nested, then retrieve string of that timespan via page.ner_entities.PER
																			$timespanString .= $page['_source']['ner_entities']['PER'][$timespan['_nested']['_nested']['_nested']['offset']]; 
																		} 
																	}    
																}
																
																			
																//print_r($result);
																
														?>
														
														<div class="result" data:id="<?php echo $documentID; ?>" id="<?php echo $documentID; ?>">
															<h3><?php echo $documentTitle; ?></h3>
															<p class="result-filename"><?php echo $file_name; ?> (uit <?php echo $source ?>)</p>
															<?php if($pagePreviewHtml){ ?>
																<p>Preview pagina: <?php echo substr($pagePreviewHtml,0,-2); ?></p>
															<?php } ?>
															<p>
																<a href="<?php echo $archive_link; ?>" class="" target="_blank" onclick="trackClick('toArchive','<?php echo $source; ?>','<?php echo $hit['_id']; ?>')">
																	Vind document in origineel archief
																</a>
																<?php
																	// TODO wrong number saved with files... need to check convert.py file to see what is going wrong
																	if($result['identifiers']['Archis_onderzoek_m_nr']){
																?>
																		/ <a href="https://zoeken.cultureelerfgoed.nl/#/zaak/search/(zaak:(fields:(archis2_onderzoekmeldingsnummer:'<?php echo $result['identifiers']['Archis_onderzoek_m_nr']; ?>')))" target='_blank'  onclick="trackClick('toArchis','<?php echo $source; ?>','<?php echo $hit['_id']; ?>')')">Bekijk in Archis</a>
																<?php
																	}
																	//print_r($document);
																?>
																/ <a href="javascript:void(0)" onclick="$(this).parent().next().slideToggle(); trackClick('openMetadata','<?php echo $source; ?>','<?php echo $hit['_id']; ?>')">Metadata</a>
															</p>
															
															<div class="metadata">
																<table>
																	<tr>
																		<td><strong>Bron</strong></td>
																		<td>
																			<p><?php echo $source; ?></p>
																		</td>
																	</tr>
																	<tr>
																		<td><strong>Bestandsnaam</strong></td>
																		<td>
																			<p><?php echo $result['file_name']; ?></p>
																		</td>
																	</tr>
																	<tr>
																		<td><strong>Beschrijving</strong></td>
																		<td>
																			<p><?php echo $result['description']; ?></p>
																		</td>
																	</tr>
																	<tr>
																		<td><strong>Auteurs</strong></td>
																		<td>
																			<ul>
																				<?php 
																					if($result['creators']){
																						foreach($result['creators'] as $creator){
																							echo '<li>'.$creator.'</li>';
																						}
																					}
																				?>
																			</ul>
																		</td>
																	</tr>
																	<tr>
																		<td><strong>Locaties</strong></td>
																		<td>
																			<ul>
																				<?php
																					if($result['locations']){
																						foreach($result['locations'] as $location){
																							echo '<li>'.$location.'</li>';
																						}
																					}
																				?>
																			</ul>
																		</td>
																	</tr>
																	<tr>
																		<td><strong>Onderwerpen</strong></td>
																		<td>
																			<ul>
																				<?php
																					if($result['subjects']){
																						foreach($result['subjects'] as $subject){
																							echo '<li>'.$subject.'</li>';
																						}
																					}
																				?>
																			</ul>
																		</td>
																	</tr>
																	<tr>
																		<td><strong>Archis onderzoekmeldingsnummer</strong></td>
																		<td>
																			<?php if($result['identifiers']['Archis_onderzoek_m_nr']){echo $result['identifiers']['Archis_onderzoek_m_nr'];} ?>
																		</td>
																	</tr>
																	<tr>
																		<td><strong>Archis zaakidentificatienummer</strong></td>
																		<td>
																			<?php if($result['identifiers']['archis_zaakidentificatie']){echo $result['identifiers']['archis_zaakidentificatie'];} ?>
																		</td>
																	</tr>
																</table>
															</div>
															
															<p>
																<?php 
																	if($timespanString){
																		//echo '<p>'.$timespanString.'</p>';
																	}
																	if($hit['highlight']){
																	  //print_r(  $hit['highlight']);                          
																		$snippetsArray = array();
																		foreach($hit['highlight']['document.pages.content'] as $snippet){
																			if(!$snippetsArray[$snippet]){ //don't display duplicates
																				echo $snippet.'<br/>';
																				$snippetsArray[$snippet] = 1;
																			}
																		}
																	}
																?>
															</p>
														</div>
														<?php		
															}
														?>
													</div>
													<div class="pagination">
														<a href="#" class="first" data-action="first">&laquo;</a>
														<a href="#" class="previous" data-action="previous">&lsaquo;</a>
														<input type="text" readonly="readonly" data-max-page="<?php echo floor($results['hits']['total']['value'] / $numPerPage)+1; ?>" data-current-page="<?php echo $_GET['page']; ?>" />
														<a href="#" class="next" data-action="next">&rsaquo;</a>
														<a href="#" class="last" data-action="last">&raquo;</a>
													</div>
												</div>
										<?php } else { ?>
											<p>Geen resultaten gevonden voor deze zoekopdracht</p>
										<?php } ?>
									<?php } ?>
										

									<div id="dialog" title="">
										<?php //this is where the preview page html will be injected via jQuery ajax ?>
									</div>
								</div>
                            </div>
                        </div>
                    </div>
									
													
                    
                </div>
            </div>
			
			
            <footer class="footer">
                <div class="container-fluid">
                    <p class="attribution copyright">Gravend loading icon ontworpen door <a href="https://maxsteenbergen.com">Max Steenbergen</a>.</p> 
					<p class="copyright text-center">
						© <?php echo date('Y'); ?> <a href="http://alexbrandsen.nl">Alex Brandsen</a>, EXALT project
					</p>
                    
                </div>
            </footer>
			
        </div>
    </div>

</body>




<!--   Core JS Files   -->
<script src="assets/js/core/jquery.3.2.1.min.js" type="text/javascript"></script>
<script src="https://code.jquery.com/ui/1.14.1/jquery-ui.js"></script>
<script src="assets/js/core/popper.min.js" type="text/javascript"></script>
<script src="assets/js/core/bootstrap.min.js" type="text/javascript"></script>

<!--   pagination   -->
<script type="text/javascript" src="assets/js/plugins/jquery.jqpagination.min.js"></script>

<!--   featherlight popup, for page preview   -->
<script type="text/javascript" src="assets/js/plugins/featherlight.js"></script>

<!--  Plugin for Switches, full documentation here: http://www.jque.re/plugins/version3/bootstrap.switch/ -->
<!--script src="assets/js/plugins/bootstrap-switch.js"></script-->

<!--  Google Maps     -->
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_KEY_GOES_HERE&libraries=drawing"></script>
<script src="assets/js/plugins/wmsMapType.js"></script>

<!--  Chartist Plugin  -->
<!--script src="assets/js/plugins/chartist.min.js"></script-->

<!--  Notifications Plugin    -->
<script src="assets/js/plugins/bootstrap-notify.js"></script>

<!-- Control Center for Light Bootstrap Dashboard: scripts for the example pages etc -->
<script src="assets/js/light-bootstrap-dashboard.js?v=2.0.0 " type="text/javascript"></script>

<!-- cookie consent -->
<script src="//cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.1.0/cookieconsent.min.js"></script>

<!-- application -->
<script>
	// set variables from php
	querystring = '<?php echo str_replace("
", "", str_replace("'", "", trim($_GET['query']))) ?>';
	querystring = querystring.trim();

	search = querystring+' <?php echo $entitiesSearchedFor; ?>'.trim();

	page = '<?php echo $_GET['page'] ?>';
	resultsPerPage = '<?php echo $numPerPage ?>';
	searchLvl = '<?php echo $_GET['searchLvl'] ?>';

	coords = '<?php echo $_GET['coords'] ?>';
	searchType = '<?php echo $_GET['searchType'] ?>';
	slop = '<?php echo $_GET['slop'] ?>';
	phraseSearch = '<?php echo $_GET['phraseSearch'] ?>';
	facets = '<?php echo $_GET['facets'] ?>';
	
	var queryExecuted = <?php if($_GET['search']){echo 'true';}else{echo 'false';} ?>;
	var resultsFound = <?php if($results['hits']['total']['value'] > 0){echo 'true';}else{echo 'false';} ?>;
	var coords = '<?php echo $_GET['coords']; ?>';
	
	var geopoints = <?php echo $geoPoints; ?>;
	
	var session_id = '<?php echo $_SESSION['id']; ?>';
	var search_id = '<?php echo $_SESSION['search_id']; ?>';
	

</script>
<script src="assets/js/main.js"></script>


</html>
