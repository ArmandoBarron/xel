<?php

#print_r($_POST);
#print_r($_POST['dag']);
#echo isset($_POST['dag_parameters']);
if(isset($_POST['REQUEST']) && isset($_POST['SERVICE'])){

	# especificar ip del servidor
	$IP = "192.168.1.71";#local
	#$IP = "148.247.201.140"; #compute 1 disys0
	#$IP = "3.129.5.12"; #amazon 6 
	#$IP = "gamma.tamps.cinvestav.mx";#local
	$IP = $_ENV["XEL_IP"];
	
	# especificar puerto del servidor
	$PORT=":25000";
	$PORT=":".$_ENV["XEL_PORT"];

	$HOST = $IP.$PORT;
	if(isset($_POST['HOST'])){
		if($_POST['HOST'] != ""){
		$HOST = $_POST['HOST'];
		}
	}

	$url = "http://".$HOST."/".$_POST['SERVICE'];

	#$tosend = array("data" => $data, "DAG" => $dag,"auth"=>$auth);
	
	$data_string = json_encode($_POST['REQUEST']);
	#echo $data_string;   
	$ch = curl_init($url);   
	curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);                                                                    
	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");                                                                     
	curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);                                                                  
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
	curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
		'Content-Type: application/json',                                                                                
		'Content-Length: ' . strlen($data_string))                                                                       
	);																											
	$result = curl_exec($ch);

	print_r($result);
}