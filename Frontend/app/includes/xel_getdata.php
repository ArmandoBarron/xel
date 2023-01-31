<?php
ini_set('memory_limit', '-1');

function my_utf8_encode(array $in): array
{
    foreach ($in as $key => $record) {
        if (is_array($record)) {
            $in[$key] = my_utf8_encode($record);
        } else {
            $in[$key] = utf8_encode($record);
        }
    }

    return $in;
}


function file_post_contents(string $url, array $data, string $username = null, string $password = null)
{
    $data     = my_utf8_encode($data);
    $postdata = json_encode($data);
    if (is_null($postdata)) {
        throw new \Exception('decoding params');
    }
    
    $access_token = $_COOKIE['access_token'];           
    $opts = array('http' =>
        array(
            'method'  => 'POST',
            'header'  =>  array('Content-type: application/json','x-access-token:'.$access_token ),
            'content' => $postdata
        )
    );

    #if (!is_null($username) && !is_null($password)) {
    #    $opts['http']['header'] .= "Authorization: Basic " . base64_encode("$username:$password");
    #}

                                          


    $context = stream_context_create($opts);

    try {
        $response = file_get_contents($url, false, $context);
    } catch (\ErrorException $ex) {

        throw new \Exception($ex->getMessage(), $ex->getCode(), $ex->getPrevious());
    }
    if ($response === false) {

        throw new \Exception();
    }

    return $response;
}

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
	$dir = $_SERVER['DOCUMENT_ROOT']."/limbo/";

    
	$HOST = $IP.$PORT;
	if(isset($_POST['HOST'])){
		if($_POST['HOST'] != ""){
		$HOST = $_POST['HOST'];
		}
	}
	$file_name ="Unnamed";
	if(isset($_POST['METADATA']['file_ext'])){		#si existe una ext, entonces se genera el nombre del archivo
		$name = $_POST['REQUEST']['data']['task'];
		$ext = $_POST['METADATA']['file_ext'];
		$date_produced = date("d-m-Y-h-i-s");
		$file_name = $name."_".$date_produced.".".$ext;
	}
	if(isset($_POST['METADATA']['file_name'])){
		$file_name = $_POST['METADATA']['file_name'];
	}

	$url = "http://".$HOST."/".$_POST['SERVICE'];
	$data_string = json_encode($_POST['REQUEST']);

	file_put_contents($dir.$file_name, file_post_contents($url,$_POST['REQUEST']));
	chmod($dir.$file_name, 0664);

	$newurl = "./includes/xel_downloadfile.php?filename=".$file_name."";

	echo $newurl;
}