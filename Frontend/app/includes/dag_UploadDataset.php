<?php
ini_set('memory_limit', '-1');
ini_set('upload_max_filesize', '6G');
ini_set('post_max_size', '6G');
#ini_set('max_input_time', 3000);
#ini_set('max_execution_time', 3000);

#print_r($_POST);

function post($url, $data, $headers)
{
    $curl = curl_init();
    curl_setopt_array($curl, array(
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true, // return the transfer as a string of the return value
        CURLOPT_TIMEOUT => 0,   // The maximum number of seconds to allow cURL functions to execute.
        CURLOPT_POST => true,   // This line must place before CURLOPT_POSTFIELDS
        CURLOPT_POSTFIELDS => $data // The full data to post
    ));
    // Set Header
    if (!empty($headers)) {
        curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);
    }
    $response = curl_exec($curl);
    $errno = curl_errno($curl);
    if ($errno) {
        return false;
    }
    
	$httpcode = curl_getinfo($curl, CURLINFO_HTTP_CODE);
	http_response_code($httpcode);
	curl_close($curl);
    return $response;
}


if(isset($_REQUEST['workspace'])){
	#$IP = "148.247.201.227"; #compute 6
	#$IP = "192.168.1.65"; #local
	#$IP = "192.168.1.66";
	#$IP = "192.168.1.71";#local
	#$IP = "148.247.201.140"; #compute 1 disys0
	$IP = $_ENV["XEL_IP"];
	$PORT = $_ENV["XEL_PORT"];
	
	$url = "http://".$IP.":".$PORT."/UploadDataset";

	$temp_name = $_FILES['file']['tmp_name']; //temporal path of the file
	$original_name = $_FILES['file']['name'];

	$data = [
		"original_name" => $original_name,
		"workspace"=> $_REQUEST['workspace'],
		"user"=> $_REQUEST['user']
	];
	if (function_exists('curl_file_create')) {
		$data['file'] = curl_file_create($temp_name, $_FILES['file']['type'], $original_name);
	} else {
		$data['file'] = '@' . realpath($temp_name);
	}
	$access_token = $_COOKIE['access_token']; 
	$headers = ["User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
				"x-access-token:".$access_token];
	$result= post($url, $data, $headers);


	print_r($result);

}
?>
