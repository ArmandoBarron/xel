<?php

	session_start();

  	unset($_SESSION["keyuser"]); 

  	session_destroy();
  	header("Location: ../index.php");
  	exit;
?>

