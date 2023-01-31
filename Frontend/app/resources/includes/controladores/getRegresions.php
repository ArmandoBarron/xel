<?php 
$url = "http://148.247.201.227:8091/regression";
$stations = $_POST['stations'];
#print_r($stations);
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
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);          
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, array(   
  'Content-Type: application/json',
  'Content-Length: ' . strlen($data_string))
);
$result = curl_exec($ch);
echo $result;