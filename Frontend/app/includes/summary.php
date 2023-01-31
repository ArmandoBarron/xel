<?php

if(isset($_POST['coordenadas']) && isset($_POST['startDate']) && isset($_POST['endDate'])){
	#$IP = "148.247.201.211"; #compute 8 
	$IP = "148.247.201.227"; #compute 6 
	$IP = "148.247.201.141"; #compute 2 disys1

	#$IP = "148.247.203.225"; #local 
	#$IP = "148.247.204.6";
	$urlSummary = "http://".$IP.":5200/summary";
	$start_date = $_POST['startDate'];
	$end_date = $_POST['endDate'];
	$start_date = date("d-m-Y", strtotime($start_date));
	$end_date = date("d-m-Y", strtotime($end_date));
	$polygon = $_POST['coordenadas'];
	$polygon_array = json_decode($polygon, true);
	$n_coors = count($polygon_array)-1;
	$K = $_POST['K'];
	$json_poly = "{";
	foreach($polygon_array as $index => $poly){
		$json_poly .= "\"".($index+1)."\":{\"lat\":\"".$poly["lat"]."\",\"lon\":\"".$poly["lon"]."\"}";
		#echo gettype($n_coors); 
		#echo gettype($index);
		//echo $n_coors == $index;
		if($n_coors != $index){
			$json_poly .= ",";
		}
	}
	$json_poly .= "}";
	//echo ".";
	//echo $json_poly;
	$polygon_array = json_decode($json_poly, true);
	$data = array("polygon" => $polygon_array, "inicio" => $start_date, "fin" => $end_date, "K" => $K);
	$data_string = json_encode($data);    

	$summary = curl_init($urlSummary);
	curl_setopt($summary, CURLOPT_CUSTOMREQUEST, "POST");                                                                     
	curl_setopt($summary, CURLOPT_POSTFIELDS, $data_string);                                                                  
	curl_setopt($summary, CURLOPT_RETURNTRANSFER, true);                                                                      
	curl_setopt($summary, CURLOPT_HTTPHEADER, array(                                                                          
		'Content-Type: application/json',                                                                                
		'Content-Length: ' . strlen($data_string))                                                                       
	);
																												
	$resultSummary = curl_exec($summary);
	$resultsJSON = json_encode($resultSummary);
	print_r($resultsJSON);
}


#{"1":{"lat":"26.29824","lon":"-105.14286"},
# "2":{"lat":"25.5473","lon":"-98.68289"},
# "3":{"lat":"21.64201","lon":"-97.97977"}
# }

/*if(isset($_GET['k'])){
	$k = $_GET['k'];
	$url = "http://disys0.tamps.cinvestav.mx:5000/clustering/".$k;
	//Initialize cURL.
$ch = curl_init();

//Set the URL that you want to GET by using the CURLOPT_URL option.
curl_setopt($ch, CURLOPT_URL, $url);

//Set CURLOPT_RETURNTRANSFER so that the content is returned as a variable.
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

//Set CURLOPT_FOLLOWLOCATION to true to follow redirects.
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

//Execute the request.
$data = curl_exec($ch);

//Close the cURL handle.
curl_close($ch);

//Print the data out onto the page.
echo $data;
}*/