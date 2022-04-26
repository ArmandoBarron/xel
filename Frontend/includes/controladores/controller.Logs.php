<?php

include_once("../../resources/conf.php");
include_once(CLASES . "/class.Logs.php");
include_once(SESIONES);

//INICIA LA SESIÓN
Sessions::startSession("buscador");

if(isset($_POST['action'])){
  $action = $_POST['action'];
  switch ($action) {
    case 'get_search':
      if(isset($_POST['busqueda'])){
        $idbusqueda = $_POST['busqueda'];
        $res = Logs::getSearch($idbusqueda,true);
        echo json_encode($res);
      }
      break;
    case "get_searches_stats":
      if(isset($_SESSION['id'])){
        $user = $_SESSION['id'];
        $searches = Logs::getSearcherNumber($user);
        echo json_encode($searches);
      }
      break;
    case "get_searches_ways_stats":
      if(isset($_SESSION['id'])){
        $user = $_SESSION['id'];
        $searches = Logs::getSearcherWayNumber($user);
        echo json_encode($searches);
      }
      break;
    case "get_recommendations_imgs":
      if(isset($_SESSION['id'])){
        $user = $_SESSION['id'];
        $recommendations = Logs::getRecommendationsImgs($user);
        echo json_encode($recommendations);
      }
      break;
    case "get_recommendations_polys":
      if(isset($_SESSION['id'])){
        $user = $_SESSION['id'];
        $recommendations = Logs::getRecommendationsPolys($user);
        echo json_encode($recommendations);
      }
      break;
    case "get_recommendations_overlaps":
      if(isset($_SESSION['id'])){
        $user = $_SESSION['id'];
        $recommendations = Logs::getRecommendationsOverlaps($user);
        echo json_encode($recommendations);
      }
      break;
  }
}
