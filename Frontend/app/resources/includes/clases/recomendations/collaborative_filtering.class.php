<?php
include_once(dirname(__FILE__) . "/../class.DB.php");
include_once("kmeans.class.php");
include_once("dbscan.class.php");
include_once("prediction.class.php");

class CollaborativeFiltering{

  /**
  * ATRIBUTOS
  */

  //VARIABLES
  private $clusters_number = 3;
  private $iduser;
  private $data;
  private $recommendations;
  private $items;
  private $clustering;

  /**
  * CONSTRUCTOR
  */
  public function __construct($iduser){
    $this->iduser = $iduser;
    $this->recommendations = array();
    $this->data = $this->loadData();
    //print_r($data);
    $this->clustering = new DBSCAN($this->data);
  }

  /**
  * REALIZA EL PROCESO PARA OBTENER NUEVAS RECOMENDACIONES PARA EL USUARIO
  */
  public function make_recommendations(){
    $usr_cluster = $this->clustering->getCluster($this->iduser);
    $id_clus = $usr_cluster->getIdCluster();
    //echo $this->iduser;
    $this->prediction = new Prediction($this->iduser,$usr_cluster);
  }

  public function getClusters(){
    return $this->clustering->getClusters();
  }

  public function getImages(){
    return $this->prediction->make_prediction();  
  }

  public function getOverlaps(){
    return $this->prediction->make_prediction_overlaps();  
  }

  public function getPolygons(){
    return $this->prediction->make_prediction_polygons();
  }

  private function checkUser(){
    $db = new DB();
    $sql = "select 1 from busquedas where \"user\" = $this->iduser";
    $result = $db->executeQuery($sql);
    return $result[0][0];
  }

  /**
  * CARGA LOS DATOS DESDE LA BASE DE DATOS
  */
  private function loadData(){
    if(!$this->checkUser()){
      throw new Exception('No hay elementos.');
    }
    $db = new DB();
    $sql = "select distinct \"user\",nombre_usuario from busquedas as b inner join usuarios as u on keyuser = \"user\"";
    $users = $db->executeQuery($sql);
    foreach ($users as $user) {
      $data[$user[0]]["point"] = $this->getMeanCenter($db,$user[0]);  
      $data[$user[0]]["username"] = $user[1];    
    }
    return $data;
  }

  private function getMeanCenter($db,$user){
    $poli = $this->getSumSearchesPolygon($db,$user);
    $circle = $this->getSumSearchesCircle($db,$user);
    $points = $this->getSumSearchesPoint($db,$user);
    $m = $poli['cant'] + $circle['cant'] + $points['cant'];
    $mean_lat = ($poli['lat'] + $circle['lat'] + $points['lat']) / $m;
    $mean_lon = ($poli['lon'] + $circle['lon'] + $points['lon']) / $m;
    return array($mean_lat,$mean_lon);
  }

  function getSumSearchesPoint($db,$user){
    $busquedas_puntos = $db->executeQuery("select sum(lat),sum(lon),count(lat) from busquedas as b inner join busquedabypoint as bp on bp.idbusqueda = b.idbusqueda where \"user\" = $user;");

    return array("lat" => $busquedas_puntos[0][0], "lon" => $busquedas_puntos[0][1],"cant" => $busquedas_puntos[0][2]);
  }

  function getSumSearchesCircle($db,$user){
    $busquedas_circulos = $db->executeQuery("select sum(center_lat),sum(center_lon),count(center_lat) from busquedas as b inner join busquedabycircle as bp on bp.idbusqueda = b.idbusqueda where \"user\" = $user;");

    return array("lat" => $busquedas_circulos[0][0], "lon" => $busquedas_circulos[0][1],"cant" => $busquedas_circulos[0][2]);
  }

  function getSumSearchesPolygon($db,$user){
    $sql = "select sum(lat) as lat,sum(lon) as lon,count(*) from (select p.idbusqueda,sum(lat)/count(*) as lat,sum(lon)/count(*) as lon from poly_edges as p inner join busquedas as b on b.idbusqueda = p.idbusqueda where \"user\" = $user group by p.idbusqueda) a;";
    $busquedas_poligonos = $db->executeQuery($sql);
    return array("cant" => $busquedas_poligonos[0][2],"lat" => $busquedas_poligonos[0][0], "lon" => $busquedas_poligonos[0][1]);
  }
}
?>
