<?php 

include_once("../../resources/conf.php");
include_once(SESIONES);
include_once(CLASES . "/recomendations/collaborative_filtering.class.php");

Sessions::startSession("buscador");
//print_r($_POST);
if(isset($_POST['action'])){
	$user = $_SESSION['id'];
	//print_r($user);
	switch ($_POST['action']) {
		case 'get_clusters':
			$cf = new CollaborativeFiltering($user);
			$clusters = $cf->getClusters();
			echo json_encode($clusters,true);
			break;
	}
}