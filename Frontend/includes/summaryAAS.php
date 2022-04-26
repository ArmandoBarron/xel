<?php

if(isset($_POST['datos']) && isset($_POST['params'])){
	#$IP = "148.247.201.211"; #compute 8 
	$IP = "148.247.201.227"; #compute 6 
	#$IP = "148.247.203.225"; #local 
	$IP = "192.168.1.71"; #local
	//$IP = "148.247.201.141"; #compute 2 disys1


	$urlSummary = "http://".$IP.":5200/summary-aas";


	$data = array("data" => $_POST['datos'], "params" => $_POST['params']);
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
else{
	//echo "Something wrong in server";
	print_r($_POST['params']);
}