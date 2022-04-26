<?php
if (!(isset($_POST['rn']) && isset($_POST['task'])))
{
	$_POST = json_decode(file_get_contents('php://input'), true);
}
#print_r($_POST['dag']);
#echo isset($_POST['dag_parameters']);
if(isset($_POST['rn']) && isset($_POST['task'])){
	#$IP = "148.247.201.211"; #compute 8 
	$IP = "148.247.201.227"; #compute 6 
	$IP = "192.168.1.71";#local
	#$IP = "148.247.201.140"; #compute 1 disys0
	$IP = $_ENV["XEL_IP"];
	$PORT = $_ENV["XEL_PORT"];

	#$IP = "3.129.5.12"; #amazon 6 

	#echo "is here";
	$RN = $_POST['rn'];
	$task = $_POST['task'];
	$host = $_POST['host'];
	$file_name = "ejemplo.csv";
	$dir = "./limbo/";

	if($host != ""){ $url = "http://".$host."/getfile/".$RN."/".$task;}
	else{$url = "http://".$IP.":".$PORT."/getfile/".$RN."/".$task;}

	// Use file_get_contents() function to get the file
	// from url and use file_put_contents() function to

	file_put_contents($dir.$file_name, file_get_contents($url));
	chmod($dir.$file_name, 0777);

	$newurl = "./includes/xel_downloadfile.php?filename=".$file_name."";

	echo $newurl;
}