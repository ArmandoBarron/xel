<?php

// 	#$IP = "148.247.201.211"; #compute 8 
	$IP = "148.247.201.227"; #compute 6 
// 	#$IP = "192.168.200.73"; #local 
# 	$IP = "148.247.204.9";
 	$url = "http://".$IP.":5555/guardar";

	
	header("Content-Type: application/json");
	// // build a PHP variable from JSON sent using POST method
	// $v = json_decode(stripslashes(file_get_contents("php://input")));
	// // build a PHP variable from JSON sent using POST method
	// $v = $_POST["DATA"];
	// encode the PHP variable to JSON and send it back on client-side

	$v = json_decode(file_get_contents('php://input'), true);
	// print_r($v);

	$json = json_encode($v);
	//echo $json;
	$ch = curl_init($url);                                                                      
	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");                                                                     
	curl_setopt($ch, CURLOPT_POSTFIELDS, $json);                                                                  
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
	curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
	   'Content-Type: application/json',                                                                                
	   'Content-Length: ' . strlen($json))                                                                       
	);                                                                                                                                                         
	$result = curl_exec($ch);
	
	print_r($result);
