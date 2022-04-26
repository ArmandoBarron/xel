<?php

include_once("cluster.class.php");
include_once("user.class.php");

/**
* CLASE PARA REALIAR LA CLASIFICACIÓN DE LOS DISTINTOS USUARIOS
* EN GRUPOS DEPENDIENDO DE SUS PREFERENCIAS
*/
class kmeans{

  /**
  * ATRIBUTOS
  */


  //VARIABLES
  private $data; //DATOS DE LOS USUARIOS
  private $clusters; //CLUSTERS GENERADOS
  private $k; //NÚMERO DE CLUSTERS
  private $n_dimensions; //NÚMERO DE DIMENSIONES DE LOS PUNTOS
  private $points_list; //LISTA DE PUNTOS O USUARIOS
  private $keys_imgs;
  private $min_value;
  private $max_value;

  /**
  * CONSTRUCTOR
  */
  public function __construct($data,$k){
    $this->data = $data;
    $this->k = $k;
    $this->min_value = $this->getMinValue();
    $this->max_value = $this->getMaxValue();
    $this->clusters = array();
    $this->prepare();
  }

  private function getMinValue(){
    $min = 100000;
    foreach ($this->data as $d) {
      if($d[0] < $min){
        $min = $d[0];
      }
      if($d[1] < $min){
        $min = $d[1];
      }
    }

    return $min;
  }

  private function getMaxValue(){
    $max = -100000;
    foreach ($this->data as $d) {
      if($d[0] > $max){
        $max = $d[0];
      }
      if($d[1] > $max){
        $max = $d[1];
      }
    }
    return $max;
  }

  /**
  * PREPARA LOS CENTROIDES PARA INICIAR CON LA CLASIFICACIÓN
  * @RETURN NULL
  */
  private function prepare(){
    $keys = array_keys($this->data);
    $this->n_dimensions = count($this->data[$keys[0]]);
    //$r = array();
    $r[0] = rand(0,count($this->data)-1);
    $r[1] = rand(0,count($this->data)-1);
    while($r[0] == $r[1]){
      $r[1] = rand(0,count($this->data));
    }
    for($i=0;$i<$this->k;$i++){
      $cluster = new Cluster($i);
      $centroid = $this->data[$keys[$r[$i]]];
      $cluster->setCentroid($centroid);
      $this->clusters[] = $cluster;
    }
    $this->generatePoints();
  }

  /**
  * FUNCIÓN QUE INICIA CON EL PROCESO DE CLASIFICACIÓN
  **/
  public function make_clusters(){
    $finish = false;
    while(!$finish){
      $this->clearClusters();
      $old_centroids = $this->getCentroids();
      $this->assignCluster();
      //$this->printClusters();
      //echo "<br>";
      $this->recalculateCentroids();
      $new_centroids = $this->getCentroids();
      $distance = $this->distanceBetweenCentroids($old_centroids,$new_centroids);
      if($distance == 0){
        $finish = true;
      }
    }
    return $this->clusters;
  }

  /**
  * REGRESA EL CLUSTER AL QUE PERTENECE UN USUARIO EN BASE A SU ID
  */
  public function getCluster($iduser){
    foreach ($this->clusters as $cluster) {
      if($cluster->contains($iduser)){
        return $cluster;
      }
    }
    return null;
  }

  /**
  * FUNCIÓN QUE REGRESA EL CONJUNTO DE CLUSTERS GENERADOS
  */
  public function getClusters(){
    return $this->clusters;
  }

  /**
  * REGRESA LOS CENTROIDES DE LOS CLUSTERS
  * @RETURN ARREGLO CON LOS CENTROIDES
  */
  public function getCentroids(){
    foreach ($this->clusters as $key => $cluster) {
      $centroids[] = $cluster->getCentroid();
    }
    return $centroids;
  }

  /**
  * BORRA EL CONTENIDO DE TODOS LOS CLUSTERS
  */
  private function clearClusters(){
    foreach ($this->clusters as $key => $cluster) {
      $cluster->clear();
    }
  }

  /**
  * REALIA LA ASIGNACIÓN DE CLUSTER A CADA ELEMENTO
  **/
  private function assignCluster(){
    $closest_cluster = 0;
    foreach ($this->points_list as $point) {
      $min = PHP_INT_MAX;
      for($i=0;$i<$this->k;$i++){
        $cluster = $this->clusters[$i];
        $distance = Kmeans::get_distance($point->getRatings(),$cluster->getCentroid(),2);
        if($distance < $min){
          $min = $distance;
          $closest_cluster = $i;
        }
      }
      $point->setCluster($closest_cluster);
      $this->clusters[$closest_cluster]->addElement($point);
    }
  }

  /**
  * CALCULA LA DISTANCIA MINKOWSKI ENTRE DOS PUNTOS
  */
  public static function get_distance($point1,$point2,$potencia){
    $lat_p1 = deg2rad($point1[0]);
    $lon_p1 = deg2rad($point1[1]);
    $lat_p2 = deg2rad($point2[0]);
    $lon_p2 = deg2rad($point2[1]);
    if($lat_p1 == $lat_p2 && $lon_p1 == $lon_p2){
      return 0;
    }
    $p1 = sin($lat_p1) * sin($lat_p2);
    $p2 = cos($lat_p1) * cos($lat_p2) * cos($lon_p1 - $lon_p2);
    $degrees = acos($p1 + $p2); 
    $distance = $degrees * 111.13384;

    return $distance;
  }


  /**
  * CREA LA LISTA DE PUNTOS A PARTIR DE LA MATRIZ
  **/
  private function generatePoints(){
    foreach ($this->data as $key => $point) {
      $user = new User($key,$point);
      $this->points_list[$key] = $user;
    }
  }

  /**
  * RECALCULA LA POSICIÓN DE LOS CENTROIDES
  */
  private function recalculateCentroids(){
    foreach ($this->clusters as $cluster) {
      $points = $cluster->getElements();
      $n_points = count($points);
      if($n_points > 0){
        $aux = array();

        for($i=0;$i<$this->n_dimensions;$i++){
          $sum = 0;
          foreach ($points as $point) {
            $sum += $point->getRating($i);
          }
          $sum /= $n_points;
          $aux[$i] = $sum;
        }
        $cluster->setCentroid($aux);
      }
    }
  }

  /*
  * CALCULA LA DISTANCIA ENTRE LOS NUEVOS CENTROIDES Y LOS ANTERIORES
  */
  private function distanceBetweenCentroids($old_centroids,$new_centroids){
    $distance = 0;
    for($i=0;$i<$this->k;$i++){
      $distance += $this->get_distance($old_centroids[$i],$new_centroids[$i],2);
    }
    return $distance;
  }

  private function printClusters(){
    foreach ($this->clusters as $value) {
      $value->printCluster();
    }
  }
}
?>
