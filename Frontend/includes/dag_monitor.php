<?php
if (!(isset($_POST['rn'])))
{
	$_POST = json_decode(file_get_contents('php://input'), true);
}
#print_r($_POST['dag']);
#echo isset($_POST['dag_parameters']);
if(isset($_POST['rn'])){
	#$IP = "148.247.201.211"; #compute 8 
	$IP = "148.247.201.227"; #compute 6 
	$IP = "192.168.1.71";#local
	#$IP = "148.247.201.140"; #compute 1 disys0
	$IP = $_ENV["XEL_IP"];
	$PORT = $_ENV["XEL_PORT"];

	#$IP = "3.129.5.12"; #amazon 6 

	#echo "is here";
	$RN = $_POST['rn'];
	$host = $_POST['host'];
	
	if($host != ""){$url = "http://".$host."/monitor/".$RN;}
	else{$url = "http://".$IP.":".$PORT."/monitor/".$RN;}

	
	
	#echo $data_string;   
	$ch = curl_init($url);                                                                      
	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");                                                                     
	#curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);                                                                  
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
	#curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
	#	'Content-Type: application/json',                                                                                
	#	'Content-Length: ' . strlen($data_string))                                                                       
	#);																											
	$result = curl_exec($ch);

	print_r($result);
}