 <?php

include_once(realpath(dirname(__FILE__) . '/../class.DB.php'));
class User {

  /****
  * ATTRIBUTES
  ****/
  private $id;
  private $ratings;
  private $cluster;
  private $imgs;
  private $radius;
  private $username;

  /****
  * CONSTRUCTOR
  ****/
  public function __construct($id,$ratings,$username){
    $this->id = $id;
    $this->ratings = $ratings;
    $this->username = $username;
    $this->cluster = -1;
    $this->loadUserData();
  }

  /****
  * GETTERS
  ****/
  public function getUser(){
    return $this->id;
  }

  public function getRatings(){
    return $this->ratings;
  }

  public function getRating($idimg){
    return $this->ratings[$idimg];
  }

  public function getCluster(){
    return $this->cluster;
  }

  function getRadius(){
    return $this->radius;
  }

  /****
  * SETTERS
  ****/
  public function setUser($id){
    $this->id = $id;
  }

  public function setRatings($ratings){
    $this->ratings = $ratigns;
  }

  public function setRating($idimg,$rating){
    $this->rating[$idimg] = $rating;
  }

  public function setCluster($cluster){
    $this->cluster = $cluster;
  }

  private function filterArray($value,$img){
    return ($value == $img);
  }

  public function getImgCount($img){
    $aux = array_values(array_filter($this->imgs,
                        function($value) use ($img){
                          return $value['idimagen'] == $img;
                        }));
    if(count($aux) >  0){
      return $aux[0]['cantidad'];
    }
    return 0;
    /*print_r(array_values(array_filter($this->imgs,
                        function($value) use ($img){
                          return $value['idimagen'] == $img;
                        })));
    return array_values(array_filter($this->imgs,
                        function($value) use ($img){
                          return $value['idimagen'] == $img;
                        }))[0]['cantidad'];*/
  }



  private function calculateRadius($db){
    $lat = $this->ratings[0];
    $lon = $this->ratings[1];

    $sql = "select sum(sum)/sum(count) * 111.13384 as radius from (
            (select sum(point(''||p.lon||','||p.lat||'') <-> point('$lon','$lat')),count(*) from poly_edges as p inner join busquedas as b on b.idbusqueda = p.idbusqueda where \"user\" = $this->id)  
              union all (select sum(point(''||p.lon||','||p.lat||'') <-> point('$lon','$lat')),count(*) from busquedabypoint as p inner join busquedas as b on b.idbusqueda = p.idbusqueda where \"user\" = $this->id)
              union all (select sum(point(''||p.center_lon||','||p.center_lat||'') <-> point('$lon','$lat')),count(*) from busquedabycircle as p inner join busquedas as b on b.idbusqueda = p.idbusqueda where \"user\" = $this->id))  a ;";
    $res = $db->executeQuery($sql);
    $this->radius = $res[0][0];
  }

  

  private function loadUserData(){
    $db = new DB();
    $sql = "select idimagen,sum(cantidad) as cantidad from(select * from fn_count_clics_img_user($this->id) union all select * from fn_count_clics_img_user($this->id)) a group by idimagen order by 2 desc;";
    $this->imgs = $db->executeQuery($sql);
    $this->calculateRadius($db);
  }
  /***
  * OTHER FUNCTIONS
  ***/
  /***
  * GENERA UN PUNTO CON NUMEROS RANDMOM, EN BASE A LOS VALORES MINIMOS Y
  * Y MAXIMOS RECIBIDOS, Y UTILIZA LAS DIMENSIONES COMO KEYS DE LOS ARREGLOS
  ***/
  public static function randomPoint($min,$max,$dimensions){
    for($i=0;$i<$dimensions;$i++){
      $point[$i] = rand($min,$max);
    }
    return $point;
  }

  /***
  * REGRESA LOS VALORES EN FORMA DE STRING
  ***/
  public function toString(){
    $str = "USER = " . $this->id ."<br>";
    foreach ($this->ratings as $key => $rating) {
      $str .= $rating . "  ";
    }
    return $str;
  }

  /***
  * COMPARA SI EL INDICE RECIBIDO ES IGUAL AL DEL USUARIO
  ***/
  public function compare($iduser){
    return $iduser == $this->id;
  }

  /**
  * SERIALIZA UN OBJETO
  */
  public function jsonSerialize(){
    $vars = get_object_vars($this);
    return $vars;
  }
}
 ?>