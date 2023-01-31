<?php
    session_start();
    
    $data = json_encode(array('keyuser' => $_GET['keyuser']));

	$url = 'http://'.$_SESSION['ip'].'/auth/v1/users/'.$_GET['keyuser'].'/deactivate';
	$ch = curl_init($url);

	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "PUT"); 
    curl_setopt($ch, CURLOPT_HEADER, false); 
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 
	curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data); 

	$response = curl_exec($ch);
	curl_close($ch);

    if (!$response) {
    	echo "ERROR";
    }else{
		header("Location: listaUsuarios.php");
    }

?>