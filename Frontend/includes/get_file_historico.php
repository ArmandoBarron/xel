<?php
#print_r($_POST['dag']);
#echo isset($_POST['dag_parameters']);
if(isset($_GET['file'])){
	#$IP = "148.247.201.211"; #compute 8 
	$IP = "148.247.201.227"; #compute 6 
	$IP = "192.168.1.71";#local
	$IP = "148.247.201.141"; #compute 2 disys1
	$IP = getenv('METEOTS_IP');

	#$IP = "3.129.5.12"; #amazon 6 

	#echo "is here";
	$filename = $_GET['file'];
	$url = "http://".$IP.":5200/getfile/".$filename;

	
	
	#echo $data_string;   
	$ch = curl_init($url);                                                                      
	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "GET");       
	curl_setopt($ch, CURLOPT_SSLVERSION,3);                                                              
	#curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);                                                                  
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
	#curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
	#	'Content-Type: application/json',                                                                                
	#	'Content-Length: ' . strlen($data_string))                                                                       
	#);																											
	

	//$contentType = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
	//$pathinfo = pathinfo($url);
	//$extension = $pathinfo['extension'];

    //header("Cache-Control: no-cache private");
    //header("Content-Description: File Transfer");
    //header('Content-disposition: attachment; filename='.$fileinfo['filename']);
    //header("Content-Type: application/vnd.ms-excel");
    //header("Content-Transfer-Encoding: binary");
	//header('Content-Length: '. strlen($file));
	$data = curl_exec($ch);
	header($_SERVER["SERVER_PROTOCOL"] . " 200 OK");
            header("Cache-Control: public"); // needed for internet explorer
            header("Content-Type: application/octet-stream");
            header("Content-Transfer-Encoding: Binary");
            header("Content-Length:".strlen($data));
			header("Content-Disposition: attachment; filename=".$filename);
			echo $data;
	die();
    //echo $data;
}