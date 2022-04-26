<?php
//INCLUYE LOS ARCHIVOS NECESARIOS
include_once("class.DB.php");
include_once(dirname(__FILE__) . "/recomendations/collaborative_filtering.class.php");
include_once("class.Images.php");

class Recomendations{

  private $cf;
  
  public function __construct($user){
    $this->cf = new CollaborativeFiltering($user);
    $this->cf->make_recommendations();
  }

  public static function most_liked($user){
    $sql = "select * from fn_best_ranked($user)";
    try{
      $con = new DB();
      return $con->executeQuery($sql);
    }catch(PDOException $e) {
      echo  $e->getMessage();
    }
    return null;
  }

  public static function most_downloaded($user){
    $sql = "select * from fn_most_downloaded($user)";
    try{
      $con = new DB();
      return $con->executeQuery($sql);
    }catch(PDOException $e) {
      echo  $e->getMessage();
    }
    return null;
  }

  public function get_recommended_images(){
    $res = array();
    try{
      $imgs = $this->cf->getImages();
      $con = new DB();
      foreach ($imgs as  $img) {
        $sql = "select e.hash_name,e.idelemento as id,e.descriptor as nombre,date as \"date\",path as \"path\",row as row,e2.descriptor as \"satelite\" from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join elementos as e2 on e2.idelemento = e.idpadre where e.idelemento  = $img";
        $r = $con->executeQuery($sql);
        $res[] = $r[0];
      }
    }catch(Exception $e){
      echo 'Excepción capturada: ',  $e->getMessage(), "\n";
    }
    return $res;
  }

  public function get_recommended_overlaps(){
    $res = array();
    try{
      $overlaps = $this->cf->getOverlaps();
      $con = new DB();
      foreach ($overlaps as  $o) {    
        $sql = "select * from fn_get_overlap_info(:path,:row,:satelite);";
        $data = array("path" => $o["path"],"row" => $o["row"],"satelite" => $o["satelite"]);
        $r = $con->executeQuery($sql,$data);
        $res[] = $r[0];
      }
    }catch(Exception $e){
      echo 'Excepción capturada: ',  $e->getMessage(), "\n";
    }
    return $res;
  }

  public function get_recommenden_polys(){
    $res = array();
    try{
      $con = new DB();
      $polys = $this->cf->getPolygons();
      $imgObj = new Images();
      $center = array(array("lat" => $polys["center"][0],"lon" => $polys["center"][1]));
      foreach ($polys["polis"] as $poly) {
        switch ($poly["satelite"]) {
          case 3:
            $sats = array("Landsat");
            break;
          case 4:
            $sats = array("terra");
            break;
          case 4:
            $sats = array("aqua");
            break;
        }
        $res[] = $imgObj->getImagesInCircleByDate($polys['radius'],$center,$sats,null,null,null,null,1,true,$poly['month'],$poly['year'],false);        
      }
    }catch(Exception $e){
      echo 'Excepción capturada: ',  $e->getMessage(), "\n";
    }
    return $res;
  }

  public static function add_recommendation($sesion,$title){
    $data = array("idsesion" => $sesion,"title" => $title);
    $sql = "INSERT INTO recomendaciones(type_recommendation,idsesion) VALUES(:title,:idsesion) returning idrecomendacion";
    $con = new DB();
    $r = $con->executeQuery($sql,$data);
    $res = $r[0][0];
    return $res;
  }

  public static function save_recomendations_over($arr,$title,$sesion){
    $con = new DB();
    $res = Recomendations::add_recommendation($sesion,$title);
    foreach ($arr as $overlap) {
      switch ($overlap["satelite"]) {
        case "landsat":
          $data = array("satelite"=>3,"path"=>$overlap["path"],"row"=>$overlap["row"],"idrecomendacion"=>$res);
          break;
        case "aqua":
          $data = array("satelite"=>4,"path"=>$overlap["path"],"row"=>$overlap["row"],"idrecomendacion"=>$res);
          break;
        case "terra":
          $data = array("satelite"=>5,"path"=>$overlap["path"],"row"=>$overlap["row"],"idrecomendacion"=>$res);
          break;
      }
      $sql = "insert into recomendaciones_solap(idrecomendacion,path,row,satelite) values(:idrecomendacion,:path,:row,:satelite)";
      $con->executeQuery($sql,$data);
    }
    return $res;
  }

  public static function save_recomendations_poly($arr,$title,$sesion){
    $con = new DB();
    $res = Recomendations::add_recommendation($sesion,$title);
    foreach ($arr as $poly) {
      $poly = $poly[0];
      switch ($poly["satelite"]) {
        case "landsat":
          $data = array("satelite"=>3,"month"=>$poly["mmmm"],"year"=>$poly["yyyy"],"idrecomendacion"=>$res);
          break;
        case "aqua":
          $data = array("satelite"=>4,"month"=>$poly["mmmm"],"year"=>$poly["yyyy"],"idrecomendacion"=>$res);
          break;
        case "terra":
          $data = array("satelite"=>5,"month"=>$poly["mmmm"],"year"=>$poly["yyyy"],"idrecomendacion"=>$res);
          break;
      }
      $sql = "insert into recomendaciones_polys(idrecomendacion,month,year,satelite) values(:idrecomendacion,:month,:year,:satelite)";
      $con->executeQuery($sql,$data);
    }
    return $res;
  }

  public static function save_recomendations($arr,$title,$sesion){
    
    $con = new DB();
    $res = Recomendations::add_recommendation($sesion,$title);
    //print_r($res);
    $sql = "INSERT INTO recomendaciones_imagenes(idrecomendacion,idimagen) VALUES(:idrecomendacion,:idimagen)";
    foreach ($arr as $img) {
      $data = array("idrecomendacion" => $res,"idimagen" => $img['id']);
      $con->executeQuery($sql,$data);
    }
    return $res;
  }
}
?>
