<?php 

$url = "http://disys3.tamps.cinvestav.mx:8091/regression";
$stations = $_POST['stations'];
//print_r($stations);
$res = array();
$aux = '[';
$n = count($stations);
$i = 0;
foreach ($stations as $s) {
	#echo $s;
	$aux .= $s;
	$i++;
	if($i < $n){
		$aux .= ",";
	}
}

$aux .= ']';
$res['stations'] = $aux;
#$stations['stations'] = $_POST['stations'];
$data_string = json_encode($res); 
//echo $data_string;
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);          
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, array(   
  'Content-Type: application/json',
  'Content-Length: ' . strlen($data_string))
);
$result = curl_exec($ch);
//$httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
//echo $httpcode;
//print_r($result);
//echo "aqui";
//print_r($resjs);
$resjs = json_decode($result,true);
//print_r($resjs);
foreach($resjs as $r){
   $destination = $r;
   $source = "http://disys3.tamps.cinvestav.mx:50000/".$r;
   //echo $source;
	$ch = curl_init();
	curl_setopt($ch, CURLOPT_URL, $source);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);	
	curl_setopt($ch, CURLOPT_SSLVERSION,3);
	$data = curl_exec ($ch);
	$error = curl_error($ch); 
	curl_close ($ch);
	//$resjs = json_decode($result,true);
	$file = fopen($r, "w+");
	fputs($file, $data);
	fclose($file);
}
//$destination = $resjs[0];
//$file = fopen($destination, "w+");
//fputs($file, $data);
//fclose($file);

echo $result;

