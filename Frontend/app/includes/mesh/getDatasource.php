<?php



if(isset($_POST['coordenadas']) && isset($_POST['startDate']) && isset($_POST['endDate'])){
	#$IP = "148.247.201.211"; #compute 8 
	$IP = "148.247.201.227"; #compute 6
	$IP = "148.247.201.140"; #compute 1 disys0
	#$IP = "148.247.204.228"; #local
	#$IP = "192.168.200.21";
	
	$url = "http://".$IP.":5200/Clustering";
	$start_date = $_POST['startDate'];
	$end_date = $_POST['endDate'];
	$start_date = date("d-m-Y", strtotime($start_date));
	$end_date = date("d-m-Y", strtotime($end_date));
	$polygon = $_POST['coordenadas'];
	$polygon_array = json_decode($polygon, true);
	$n_coors = count($polygon_array)-1;
	$K = $_POST['K'];
	$type = $_POST['type'];
	$fill = $_POST['fillblank'];
	$fuentes = $_POST['fuentes'];
	$variables = $_POST['variables'];
	$group = 0;
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
	if(isset($_POST['group'])){
		$group = $_POST['group'];
		$data = array("polygon" => $polygon_array, "inicio" => $start_date, "fin" => $end_date, "K" => $K, "type" => $type, "fill" => $fill,
		"fuentes" => $fuentes, "variables" => $variables, "group" => $group );
	}
	else{
		$data = array("polygon" => $polygon_array, "inicio" => $start_date, "fin" => $end_date, "K" => $K, "type" => $type, "fill" => $fill,
		"fuentes" => $fuentes, "variables" => $variables);
	}

	$data_string = json_encode($data);    
	$ch = curl_init($url);                                                                      
	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");                                                                     
	curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);                                                                  
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
	curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
		'Content-Type: application/json',                                                                                
		'Content-Length: ' . strlen($data_string))                                                                       
	);																											
	$result = curl_exec($ch);


	if($K == 0){
		$temp = json_decode($result);


		if (!file_exists('../static')) {
			mkdir("../static");
		}
		foreach ($temp as $key => $value) { 
		  if ($key == "images"){
			$value = json_decode(json_encode($value),true);
			if($group == 0){
				$pathimg = explode ("/", $value['path']);
				$folderNumber=$pathimg[2];
				#print($folderNumber);
				$img = file_get_contents("http://".$IP.":5200".$value['path']);
				file_put_contents('../static/'.$folderNumber, $img);
			}
			else{
				foreach($value as $am){
					$pathimg = explode ("/", $am['path']);
					$folderNumber=$pathimg[2];
					#print($folderNumber);
					$img = file_get_contents("http://".$IP.":5200".$am['path']);
					file_put_contents('../static/'.$folderNumber, $img);
				}
			}


		  }
		  }
	  
		#crear ZIP
		#$folder="../static/Zips/";
		#if (!file_exists($folder)) {
		#	mkdir($folder);
		#  }
	  
		#$filename = "ImagesSill_".$folderNumber;
		#$final_tar = new PharData($folder.$filename.'.tar');
		#$target = "../static/clust/".$folderNumber."/";
		#$final_tar -> buildFromDirectory($target);
	
	}

	print_r($result);
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