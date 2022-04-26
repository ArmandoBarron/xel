<?php

if(isset($_GET['id'])){
// $url = "http://192.168.200.21:5505/find_muni/".$id;
$id = $_GET['id'];
$url = "http://148.247.201.227:5505/find_muni/". $id; //compute 6
// $url = "http://148.247.204.85:5505/find_muni/". $id; //cinves
// $url = "http://192.168.43.150:5505/find_muni/". $id; //telefono
// $url = "http://192.168.0.10:5505/find_muni/". $id; //mi casa

// echo $url;
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
}