<?php
    session_start();
    
	$url = 'http://'.$_SESSION['ip'].'/auth/v1/users/'.$_GET['keyuser'].'/delete';
	$ch = curl_init($url);

	curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "DELETE"); 
    curl_setopt($ch, CURLOPT_HEADER, false); 
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 
	$response = curl_exec($ch);
	curl_close($ch);

    if (!$response) {
    	echo "ERROR";
    }else{
		header("Location: listaUsuarios.php");
    }

?>