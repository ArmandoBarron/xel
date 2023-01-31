<?php 
include_once("../resources/conf.php");
include_once(SESIONES);
include_once(dirname(__FILE__) . "/clases/recomendations/collaborative_filtering.class.php");

Sessions::startSession("buscador");


//print_r($clusters);

echo "<h2>Ubicación de los usuarios</h2>";

?>

<div style="height: 500px;background-color: #bbdefb" id="map"></div>