<?php
    session_start();
	/*$ds = DIRECTORY_SEPARATOR;
	$base_dir = realpath(dirname(__FILE__)  . $ds . '..') . $ds;
	require_once("{$base_dir}view{$ds}header.php");
	*/
    //include $_SERVER['DOCUMENT_ROOT'].'/view/header.php';
	include_once "views/header.php";
    
	if(isset($_SESSION["connected"]) && $_SESSION["connected"] == 1){
		include_once "views/home.php";
	}else{		
		include_once "views/login.php";
	}
?>