<?php

include_once('/var/www/html/AEM-Eris/includes/clases/class.DB.php');
include_once("kmeans.class.php");


/**
* CLASE QUE HACE LAS PREDICCIONES DE LOS RATINGS EN BASE
* A LOS CLUSTERS GENERADOS
**/
class Prediction{
  /**
  * ATRIBUTOS
  */
  private $cluster; //cluster de usuarios
  private $user; //usuario sobre el cuál se haran las predicciones
  private $item; //item el cual será rankeado

  /**
  * CONSTRUCTORES
  */
  public function __construct($user,$cluster){
    $this->cluster = $cluster;
    $this->user = $user;
  }

  /****
  * SETTERS
  ****/
  public function setUser($user){
    $this->user = $user;
  }

  public function setItem($item){
    $this->item = $item;
  }

  public function setCluster($cluster){
    $this->cluster = $cluster;
  }

  /****
  * GETTERS
  ****/
  public function getUser(){
    return $this->user;
  }

  public function getItem(){
    return $this->item;
  }

  public function getCluster(){
    return $this->cluster;
  }

  /**
  * FUNCTIÓN QUE REALIZA LA PREDICCIÓN DE LA PUNTUACIÓN DE UN USUARIO HACIA
  * UN ITEM EN BASE A LAS PUNTUACIONES DE OTROS USUARIOS
  */
  public function make_prediction(){
    $neighbors = $this->cluster->getElements();
    $cantN = count($neighbors)-2;
    if($cantN < 0){
      throw new Exception("Error Processing Request", 1);
    }
    $i = 0;
    $votes = array();
    $sql = "select idimagen,sum(cantidad),max(lat) as lat,max(lon) as lon from ( ";
    foreach ($neighbors as $key => $neighbor) {
      $idneighbor = $neighbor->getUser();
      if($idneighbor != $this->user){
        $sql .= "(select idimagen,sum(cantidad)  as cantidad,max(lat) as lat ,max(lon) as lon from(select * from fn_count_clics_img_user($idneighbor) union all select * from fn_count_downloads_user($idneighbor)) a group by idimagen order by 2 desc)";
        if($i<$cantN){
          $sql .= " union all ";
        }
        $i++;
      }else{
        $this->usrObj = $neighbor;
      }
    }
    $sql .= ") a group by idimagen order by 2 desc";
    $db = new DB();
    $imgs = $db->executeQuery($sql);
    
    $res = array();
    foreach($imgs as $img){
      $cant = $this->usrObj->getImgCount($img['idimagen']);
      if($cant == 0){
        //print_r($img);
        $distance = kmeans::get_distance($this->usrObj->getRatings(),array($img['lat'],$img['lon']),2);

        //echo $distance."<br>";
        $res[$img['idimagen']] = $distance;
      }
    }

    asort($res);
    //print_r(asort($res));
    return array_keys($res);
  }

  public function make_prediction_polygons(){
    $neighbors = $this->cluster->getElements();
    $cantN = count($neighbors)-2;
    $usrObj = $this->cluster->getUser($this->user);
    $_SESSION['usrRadius'] = $usrObj->getRadius();
    $ratings = $usrObj->getRatings();
    $_SESSION['lat_ctr'] = $ratings[0];
    $_SESSION['lon_ctr'] = $ratings[1];
    $usrRadius = $usrObj->getRadius();
    $sql = "select month,year,satelite,sum(cantidad) from ( ";
    $i = 0;
    foreach ($neighbors as $key => $neighbor) {
      $idneighbor = $neighbor->getUser();
      if($idneighbor != $this->user){
        $sql .= "(select month,year,satelite,sum(cantidad) as cantidad from(select * from fn_count_downloads_polygon_user($idneighbor) union all select * from fn_count_clics_polygon_user($idneighbor)) a group by year,month,satelite order by 4 desc)";
        if($i<$cantN){
          $sql .= " union all ";
        }
        $i++;
      }
    }
    $sql .= ") a group by year,month,satelite order by 4 desc";
    $db = new DB();
    $polys = $db->executeQuery($sql);
    return array("polis" => $polys,"radius"=>$usrRadius,"center"=>$usrObj->getRatings());
  }

  public function make_prediction_overlaps(){
    $neighbors = $this->cluster->getElements();
    $cantN = count($neighbors)-2;
    $i = 0;
    $votes = array();
    $sql = "select path,row,sum(cantidad),max(lat) as lat,max(lon) as lon,satelite from ( ";
    foreach ($neighbors as $key => $neighbor) {
      $idneighbor = $neighbor->getUser();
      if($idneighbor != $this->user){
        $sql .= "(select path,row,sum(cantidad) as cantidad,max(lat) as lat ,max(lon) as lon,max(satelite) as satelite from(select * from fn_count_downloads_overlaps_user($idneighbor) union all select * from fn_count_clics_overlaps_user($idneighbor)) a group by path,row order by 2 desc)";
        if($i<$cantN){
          $sql .= " union all ";
        }
        $i++;
      }else{
        $this->usrObj = $neighbor;
      }
    }
    $sql .= ") a group by path,row,satelite order by 3 desc";
    $db = new DB();
    $imgs = $db->executeQuery($sql);
    return $imgs;
  }
}
?>
