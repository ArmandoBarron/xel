<?php
include_once("class.DB.php");
include_once("class.Circunferencia.php");
include_once("class.Logs.php");

/**
* CLASE PARA OBTENER LA INFORMACION DE UNA IMAGEN/ELEMENTO
*/
class Images{

  private $con; //CONEXCION A LA BASE DE DATOS
  private $idimg; //ID DE LA IMAGEN
  private $imgs; //IMGANES GENERADAS CON LA BUSQUEDA
  private $poligono;
  private $totalImages;
  private $idbusqueda;
  //FILTROS DE BUSQUEDA
  private $FILTROS = array("TODAS"          => 1,
                           "POLIGONOS"      => 2,
                           "SOLAPAMIENTOS"  => 3);

  /**
  * CONSTRUCTOR
  */
  public function __construct(){
    $this->con = new DB();
    $this->totalImages = 0;
    if(func_num_args() > 0){ //si se le pasa el id, lo asigna la variable global
      $params = func_get_args();
      $this->idimg = $params[0];
    }
  }

  /**
  * REGRESA LA INFORMACIÓN DE LAS IMAGENES EN BASE DE LA CONSULTA
  * SQL RECIBIDA
  */
	public function getImagesFromPolygon($type_shape,$poligono,$satelites,$dateIni,$dateFin,$filtro,$show_products=false,$onlynames=false,$limit=0,$offset=0,$month,$year){
    $id_session = $_SESSION['session_id']; //OBTIENE EL NÚMERO DE LA SESION
    $user = $_SESSION['id'];
    $sql = $this->form_sql_string($user,$satelites,$dateIni,$dateFin,$filtro,$show_products,$onlynames,false,$month,$year);
    $sql = $this->add_polygon_to_sql($sql,$poligono,$filtro,$onlynames);
    //echo $id_session;
    if(!$onlynames){
      $this->idbusqueda = Logs::add_log_polygon($id_session,$user,$type_shape,$this->poligono,$dateIni,$dateFin,$filtro,$satelites,$show_products);
      $this->idbusqueda = $this->idbusqueda['hash'];
    }
    $this->countImages($sql);
    if($limit > 0 && !$onlynames){
      $sql .= " limit ".$limit." offset ".$offset;
    }
    //echo $sql;
    $this->imgs = $this->con->executeQuery($sql);
    return $this->imgs;
	}

  /*
  * AGREGA EL POLIGONO A LA CADENA DE BUSQUEDA
  */
  private function add_polygon_to_sql($sql,$coors_poly,$filtro,$onlynames){
    $n = count($coors_poly);
    $this->poligono = "polygon('(";
    for ($i=0; $i < $n ; $i++) {
      $this->poligono .= "(".$coors_poly[$i]['lon'].",".$coors_poly[$i]['lat'].")";
      if($i<$n-1){
        $this->poligono .= ",";
      }
    }
    $this->poligono .= ")')";
    $sql .= " and (".$this->poligono;
    $sql .= "  @> point(''||p.lon||','||p.lat||'')";
    $sql .= "or (";
    for ($i=0; $i < $n ; $i++) {
      $sql .= " (poligono @> '(".$coors_poly[$i]["lon"].",".$coors_poly[$i]["lat"].")' )";
      if($i<$n-1){
        $sql .= " or ";
      }
    }
    $sql .= ") )";
    if($onlynames){
      if($filtro == $this->FILTROS['POLIGONOS']){
        $sql .= " group by yyyy,mmmm,satelite order by yyyy,mmmm";
      }if($filtro == $this->FILTROS['SOLAPAMIENTOS']){
        $sql .= " group by path,row,satelite order by path,row ";
      }else{
        $sql .= " order by 1,2,3,4";
      }
    }else if($filtro == $this->FILTROS['SOLAPAMIENTOS']){
      $sql .= " group by path,row,satelite order by path,row ";
    }else if($filtro == $this->FILTROS['POLIGONOS']){
      $sql .= " group by yyyy,mmmm,satelite order by yyyy,mmmm";
    }else{
      $sql.= " order by satelite,date,path,row,nombre ";
    }
    //echo $sql;
    return $sql;
  }

  /**
  * FORMA LA CADENA SQL
  */
  private function form_sql_string($user,$satelites,$startdate,$enddate,$filtro,$show_products=false,$onlynames=false,$with_coors=false,$month,$year){

    if(!isset($user)){
      $user = -1;
    }

    if($with_coors){
      $sql = "select  e.hash_name,extract(year from date) as yyyy,extract(month from date) as mmmm,e.idelemento as id,e.descriptor as nombre,e2.descriptor as satelite,ellipsoid,projection,path,row,date,p.lat,p.lon,rating,fn_get_place(m.idmetadato) as place from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join elementos as e2 on e.idpadre = e2.idelemento inner join points as p on p.idmetadatos = m.idmetadato left join puntuaciones as pu on e.idelemento = pu.idimagen and idusuario = $user ";
    }else if($onlynames){
      $sql = "select distinct e.idelemento as id,extract(year from date) as yyyy,extract(month from date) as mmmm,path,row,e.descriptor as nombre,e.hash_name from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join elementos as e2 on e.idpadre = e2.idelemento inner join points as p on p.idmetadatos = m.idmetadato ";
        if($filtro == $this->FILTROS['POLIGONOS']){
          $sql = 'select count(distinct e.descriptor) as numero,e2.descriptor as satelite,max(e.descriptor) as nombre,extract(year from date) as yyyy,extract(month from date) as mmmm from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join elementos as e2 on e.idpadre = e2.idelemento inner join points as p on p.idmetadatos = m.idmetadato ';
        }else if($filtro == $this->FILTROS['SOLAPAMIENTOS']){
          $sql = 'select  count(distinct e.descriptor) as numero,path,row,max(date) as newest,min(date) as oldest,e2.descriptor as satelite,max(e.descriptor) as nombre,max(e.hash_name) as hash_name,fn_get_place(max(m.idmetadato)) as place from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join elementos as e2 on e.idpadre = e2.idelemento inner join points as p on p.idmetadatos = m.idmetadato ';
        }
    }else if($filtro == $this->FILTROS['SOLAPAMIENTOS']){
      $sql = 'select  count(distinct e.descriptor) as numero,path,row,max(date) as newest,min(date) as oldest,e2.descriptor as satelite,max(e.descriptor) as nombre,max(e.hash_name) as hash_name,fn_get_place(max(m.idmetadato)) as place from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join elementos as e2 on e.idpadre = e2.idelemento inner join points as p on p.idmetadatos = m.idmetadato ';
    }else if($filtro == $this->FILTROS['POLIGONOS']){
      $sql = 'select count(distinct e.descriptor) as numero,e2.descriptor as satelite,max(e.descriptor) as nombre,extract(year from date) as yyyy,extract(month from date) as mmmm from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join elementos as e2 on e.idpadre = e2.idelemento inner join points as p on p.idmetadatos = m.idmetadato ';
    }else{
      $sql = "select distinct e.idelemento as id,e.hash_name,e.descriptor as nombre,ellipsoid,projection,path,row,date,e2.descriptor as satelite,rating,fn_get_place(m.idmetadato) as place from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join elementos as e2 on e.idpadre = e2.idelemento inner join points as p on p.idmetadatos = m.idmetadato left join puntuaciones as pu on e.idelemento = pu.idimagen  and idusuario = $user ";
    }

    if($show_products){
      $sql .= " inner join elementos as e3 on e3.idpadre = e.idelemento ";
    }

    $sql.= " where (";
    if($onlynames && in_array('landsat',$satelites)){
      $sql .= " UPPER(e2.descriptor) = 'LANDSAT'";
    }else{
      for($i=0;$i<count($satelites);$i++){
        $sql .= " UPPER(e2.descriptor) = UPPER('".$satelites[$i]."')";
        if($i < count($satelites)-1)
          $sql .= " or ";
      }
    }
    $sql.=")";

    if(strlen($startdate) > 0 && strlen($enddate) > 0 ){
      $sql .= " and (date, date) OVERLAPS ('".$startdate."'::DATE, '".$enddate."'::DATE)";
    }else if(strlen($startdate) > 0){
      $sql .= " and date = '$startdate'";
    }

    if($month > -1 && $year > -1){
      $sql .= " and (extract(month from date) = $month and extract(year from date) = $year)";
    } 

    return $sql;
  }

  //AGREGA LA LAT AND LON A LA CADENA DE BUSQUEDA
  private function add_lat_lon_to_sql($lat,$lon,$sql,$filtro,$onlynames){
    $sql .= "or poligono @> '($lon,$lat)')";
    if($onlynames){
      $sql .= " order by 1,2,3,4";
    }else if($filtro == $this->FILTROS['SOLAPAMIENTOS']){
      $sql .= " group by path,row,satelite order by 1,satelite";
    }else if($filtro == $this->FILTROS['POLIGONOS']){
      $sql .= " group by date,satelite order by satelite";
    }else{
      $sql.= " order by satelite,date,path,row,nombre ";
    }
    //echo $sql;
    return $sql;
  }

  /**
  * REGRESA EL NÚMERO DE IMAGENES EN BASE A LA CONSULTA SQL
  */
  private function countImages($sql){
    try{
      $res = $this->con->executeQuery($sql);
      $this->totalImages =  count($res);
    } catch(PDOException $e) {
      echo  $e->getMessage();
    }
  }

  private function getAllImages($user,$satelites,$startdate,$enddate,$filtro,$show_products=false,$onlynames=false,$with_coors,$month,$year){
    $sql = $this->form_sql_string($user,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,$with_coors,$month,$year);
    $sql .= " order by satelite,date,path,row,nombre";

    $imgs = $this->con->executeQuery($sql);
    return $imgs;
  }

  /**
  * REGRESA LAS IAMGENES QUE ESTAN DENTRO DE UNA CIRCUNFERENCIA
  */
  public function getImagesInCircle($radio_o,$c_x,$c_y,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,$with_coors,$month,$year,$divide=true){
    $id_session = $_SESSION['session_id']; //OBTIENE EL NÚMERO DE LA SESION
    $user = $_SESSION['id'];
    $imgs = $this->getAllImages($user,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,$with_coors,$month,$year);
    //echo $radio_o;
    $c = new Circunferencia($c_x,$c_y);
    $radio = $divide ? $radio_o/1000 : $radio_o;
    //echo $radio;
    $i=0;
    $res = array();
    $nombres =  array();
    $n = count($imgs);

    for($i=0;$i<$n;$i++){
      if($c->getDistance($imgs[$i]["lat"],$imgs[$i]["lon"]) < $radio){
        if(!in_array($imgs[$i]["nombre"],$nombres)){
          $res[] = $imgs[$i];
          $nombres[] = $imgs[$i]["nombre"];
        }
      }
    }
    $this->totalImages = count($res);
    if(!$onlynames){
      $this->idbusqueda = Logs::add_log_circle($id_session,$user,"circulo",$startdate,$enddate,$filtro,$c_x,$c_y,$radio_o,$satelites,$show_products);
      $this->idbusqueda = $this->idbusqueda['hash'];
    }

    return $res;
  }

  /**
  * REGRESA LAS IAMGENES QUE ESTAN DENTRO DE UNA CIRCUNFERENCIA
  * ORDENADAS POR PATH Y ROW
  */
  public function getImagesInCircleByGroup($radio,$coors_poly,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,$with_coors,$month,$year,$imgs=null){
    $id_session = $_SESSION['session_id']; //OBTIENE EL NÚMERO DE LA SESION
    $user = $_SESSION['id'];
    if($imgs == null){
      $imgs = $this->getAllImages($user,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,$with_coors,$month,$year);
    }
    

    $c_x = $coors_poly[0]["lat"];
    $c_y = $coors_poly[0]["lon"];

    $c = new Circunferencia($c_x,$c_y);
    $radio = $radio/1000;
    $i=0;
    $res = array();
    $nombres =  array();
    $n = count($imgs);
    $fecha_menor = new DateTime("2020/01/03");
    $fecha_mayor = new DateTime("1990/01/03");
    $contadores = array();

    for($i=0;$i<$n;$i++){
      if($c->getDistance($imgs[$i]["lat"],$imgs[$i]["lon"]) < $radio){
        if(!in_array($imgs[$i]["nombre"],$nombres)){
          if(isset($contadores[$imgs[$i]["satelite"]][$imgs[$i]["path"]][$imgs[$i]["row"]]["cantidad"])){
            $contadores[$imgs[$i]["satelite"]][$imgs[$i]["path"]][$imgs[$i]["row"]]["cantidad"] ++;
          }else{
            $contadores[$imgs[$i]["satelite"]][$imgs[$i]["path"]][$imgs[$i]["row"]]["cantidad"] = 1;
          }

          #$contadores[$imgs[$i]["satelite"]][$imgs[$i]["path"]][$imgs[$i]["row"]]["cantidad"] ++;
          $contadores[$imgs[$i]["satelite"]][$imgs[$i]["path"]][$imgs[$i]["row"]]["imagen"] = $imgs[$i];
          $date = new DateTime($imgs[$i]["date"]);
          if($fecha_menor > $date){
            $fecha_menor = $date;
          }

          if($fecha_mayor < $date){
            $fecha_mayor = $date;
          }
          #$res[] = $imgs[$i];
          $nombres[] = $imgs[$i]["nombre"];
        }
      }
    }

    foreach ($contadores as $key => $value) {
      foreach ($value as $path => $value2) {
        foreach ($value2 as $row => $value3) {
          //print_r($value3);
	  $imagen = $value3["imagen"];
          $res[] = array("nombre" => $imagen["nombre"],
                    "path"  =>  $path,
                    "row"   =>  $row,
                    "newest" => $fecha_menor->format('Y-m-d'),
                    "oldest" => $fecha_mayor->format('Y-m-d'),
                    "satelite" => $key,
                    "numero" => $value3["cantidad"],
                    "place" => $value3["imagen"]["place"],
                    "hash_name" => $value3["imagen"]["hash_name"]);
        }
      }
    }
    $this->totalImages = count($res);
    if(!$onlynames){
      $this->idbusqueda = Logs::add_log_circle($id_session,$user,"circulo",$startdate,$enddate,$filtro,$coors_poly[0]["lat"],$coors_poly[0]["lon"],$radio,$satelites,$show_products);
      $this->idbusqueda = $this->idbusqueda["hash"];
    }
    return $res;
  }

  /**
  * REGRESA LAS IAMGENES QUE ESTAN DENTRO DE UNA CIRCUNFERENCIA
  * ORDENADAS POR FECHA
  */
  public function getImagesInCircleByDate($radio,$coors_poly,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,$with_coors,$month,$year,$divide=true){
    $id_session = $_SESSION['session_id']; //OBTIENE EL NÚMERO DE LA SESION
    $user = $_SESSION['id'];
    $imgs = $this->getAllImages($user,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,$with_coors,$month,$year);

    $c_x = $coors_poly[0]["lat"];
    $c_y = $coors_poly[0]["lon"];
    $c = new Circunferencia($c_x,$c_y);
    if($divide){
      $radio = $radio/1000;
    }
    
    $i=0;
    $res = array();
    $nombres =  array();
    $n = count($imgs);
    $contadores = array();

    for($i=0;$i<$n;$i++){
      if($c->getDistance($imgs[$i]["lat"],$imgs[$i]["lon"]) < $radio){
        if(!in_array($imgs[$i]["nombre"],$nombres)){
          if(isset($contadores[$imgs[$i]["satelite"]][$imgs[$i]["yyyy"]."/".$imgs[$i]["mmmm"]]["cantidad"])){
            #echo $imgs[$i]["yyyy"]."/".$imgs[$i]["mmmm"];
            #echo "<br>";
            $contadores[$imgs[$i]["satelite"]][$imgs[$i]["yyyy"]."/".$imgs[$i]["mmmm"]]["cantidad"] ++;
          }else{
             $contadores[$imgs[$i]["satelite"]][$imgs[$i]["yyyy"]."/".$imgs[$i]["mmmm"]]["cantidad"] = 1;
          }
          $contadores[$imgs[$i]["satelite"]][$imgs[$i]["yyyy"]."/".$imgs[$i]["mmmm"]]["nombre"] = $imgs[$i]["nombre"];
          $nombres[] = $imgs[$i]["nombre"];
        }
      }
    }
    //print_r($contadores);
    foreach ($contadores as $key => $value) {
      foreach ($value as $date => $value2) {
        $date = explode("/", $date);
        $res[] = array("nombre" => $value2["nombre"],
                  "yyyy" => $date[0],
                  "mmmm" => $date[1],
                  "satelite" => $key,
                  "numero" => $value2["cantidad"]);
      }
    }
    $this->totalImages = count($res);
    if(!$onlynames){
      $this->idbusqueda = Logs::add_log_circle($id_session,$user,"circulo",$startdate,$enddate,$filtro,$coors_poly[0]["lat"],$coors_poly[0]["lon"],$radio,$satelites,$show_products);
      $this->idbusqueda = $this->idbusqueda['hash'];
    }
    return $res;
  }

  /**
  * REGRESA LAS IMAGENES QUE ESTEN EN UN LUGAR
  */
  public function getImagesInPlace($lat,$lon,$city,$state,$country,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,$limit,$offset,$month,$year){

    $id_session = $_SESSION['session_id']; //OBTIENE EL NÚMERO DE LA SESION
    $user = $_SESSION['id'];
    $sql = $this->form_sql_string($user,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,false,$month,$year);
    if(strlen($country) > 0){
      $sql .= " and (country LIKE '%$country%' ";
    }
    if(strlen($state) > 0){
      $sql .= " and state LIKE '%$state%' ";
    }
    if(strlen($city) > 0){
      $sql .= " and city LIKE '%$city%' ";
    }
    $sql = $this->add_lat_lon_to_sql($lat,$lon,$sql,$filtro,$onlynames);
    //echo $sql;
    $this->countImages($sql);
    if($limit > 0){
      $sql .= " limit ".$limit." offset ".$offset;
    }
    //echo $sql;
    $this->imgs = $this->con->executeQuery($sql);

    if(!$onlynames){
      $this->idbusqueda = Logs::add_log_point($id_session,$user,"point",$startdate,$enddate,$filtro,$lat,$lon,$satelites,$show_products,$city,$state,$country);
      $this->idbusqueda = $this->idbusqueda['hash'];
    }
    return $this->imgs;
  }

  /**
  * REGRESA EL ID DEL PADRE DE LA IMAGEN
  */
  public function getPadre($idelement,$ishash=false){
    if($ishash){
      $sql = "select e.idpadre,e2.typeofelement,e2.descriptor,e2.hash_name from elementos as e inner join elementos as e2 on e2.idelemento = e.idpadre where e.hash_name = :idelemento";
    }else{
      $sql = "select e.idpadre,e2.typeofelement,e2.descriptor,e2.hash_name from elementos as e inner join elementos as e2 on e2.idelemento = e.idpadre where e.idelemento = :idelemento";
    }
    $data = array("idelemento" => $idelement);
    try{
      return $this->con->executeQuery($sql,$data);
    }catch(PDOException $e) {
      echo  "getPadre".$e->getMessage();
    }
  }

  /**
  * REGRESA EL NOMBRE (DESCRIPTOR) EN BASE AL ID RECIBIDO
  */
  public function getName($idelement,$ishash=false){
    if($ishash){
      $sql = "select idelemento,descriptor,hash_name from elementos where hash_name = :idelemento";
    }else{
      $sql = "select idelemento,descriptor,hash_name from elementos where idelemento = :idelemento";
    }

    $data = array("idelemento" => $idelement);
    try{
      $res = $this->con->executeQuery($sql,$data);
      return $res[0];
    }catch(PDOException $e) {
      echo  "getName".$e->getMessage();
    }
  }

  /**
  * REGRESA LOS ELEMENTOS ANTERIORES A LA IMAGEN
  */
  public function getAncestors($idelement,$res){
    try{
      $nivel = $this->getType($idelement,true);
    }catch(Exception $e){
      return $e->getMessage();
    }

    if($nivel == 2){
      return $res;
    }else{
      //$aux = getPadre($idelement);
      $img = $this->getName($idelement,true);
      $padre = $this->getPadre($idelement,true);
      $padre = $padre[0];
      $res[] = $img;
      return $this->getAncestors($padre['hash_name'],$res);
    }
  }

  /**
  * REGRESA EL TIPO DE UNA IMAGEN
  */
  public function getType(){
    $num_params = func_num_args();
    if($num_params == 1){
      $idimg = func_get_args();
      $idimg = $idimg[0];
    }else if($num_params == 2){
      $idimg = func_get_args();
      $idimg = $idimg[0];
      $is_hash = func_get_args();
      $is_hash = $is_hash[0];
    }else{
      $idimg = $this->idimg;
    }
    if($is_hash){
      $sql = "select typeofelement from elementos where :idelemento = hash_name";
    }else{
      $sql = "select typeofelement from elementos where idelemento=:idelemento";
    }
    $data = array("idelemento" => $idimg);
    $res = $this->con->executeQuery($sql,$data);
    if(count($res) == 0){
      throw new Exception('El elemento no existe.');
    }else{
      return $res[0][0];
    }
  }

  /**
  * REGRESA EL NÚMERO TOTAL DE IMAGENES EN LA QUERY
  */
  public function getNumberOfImages(){
    return $this->totalImages;
  }

  /**
  * REGRESA EL ARREGLO DE IMAGENES
  */
  public function getImgsArr(){
    return $this->imgs;
  }

  public function getIdBusqueda(){
    return $this->idbusqueda;
  }

  public function setIdBusqueda($idbusqueda){
    $this->idbusqueda = $idbusqueda;
  }

  /**
  * REGRESA LOS PRODUCTOS DERIVADOS DE UNA IMAGEN
  */
  public function getDerivados($id,$user){
    $sql = "select e.hash_name,e.descriptor,mp.description,mp.short_description,e.idelemento,
     rating from elementos as e inner join metadatos_productos as mp on mp.idelemento = e.idelemento left join puntuaciones as pu on e.idelemento = pu.idimagen and idusuario = :usuario where idpadre = :idimagen order by e.idelemento,descriptor";
    $data = array("idimagen" => $id,"usuario" => $user);
    $res = $this->con->executeQuery($sql,$data);
    return $res;
  }

  /**
  * REGRESA LAS IMÁGENES QUE ESTAN EN UN PATH/ROW
  */
  public function getImagesInPathRow($path,$row,$satelite){
    $sql = "SELECT  e.descriptor as nombre,date,e.idelemento as id from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join elementos as e2 on e.idpadre = e2.idelemento where  path = :path and row = :row and UPPER(e2.descriptor) = UPPER(:satelite) order by date,nombre";
    $data = array("path" => $path,"row" => $row,"satelite" => $satelite);
    $res = $this->con->executeQuery($sql,$data);
    return $res;
  }

  /**
  * REGRESA EL POLIGONO DE UNA IMAGEN
  */
  public function getPolygon($image){
    $sql = "SELECT  e.descriptor as nombre,e2.descriptor as satelite,ellipsoid,projection,path,row,date,p.lat as lat,p.lon as lon,city,state,country,position from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join elementos as e2 on e.idpadre = e2.idelemento inner join points as p on p.idmetadatos = m.idmetadato  where e.idelemento = :image";

    $data = array("image" => $image);
    $res = $this->con->executeQuery($sql,$data);
    #print_r($res);
    return $res;
  }

  /**
  * REGRESA EL POLIGONO DE UN PATH ROW ESPECIFICADO
  */
  public function getPathRowPoly($path,$row){
    $sql = "SELECT * FROM wrscornerpoints where path = :path and row = :row";
    $data = array("path" => $path,"row" => $row);
    $res = $this->con->executeQuery($sql,$data);
    return $res;
  }

  /**
  * REGRESA EL ID DE UN ELEMENTO EN BASE A SU HASH
  */
  public function getId($hash){
    $sql = "select idelemento from elementos where hash_name = :hash";
    $data = array("hash" => $hash);
    $res = $this->con->executeQuery($sql,$data);
    return $res[0][0];
  }

  /**
  * REGRESA LA INFORMACIÓN DE UN ELEMENTO
  */
  public function getElementInfo($element,$user,$ishash=false){
    $tipo = $this->getType($element,true);
    if($ishash){
      $element = $this->getId($element);
    }
    switch ($tipo) {
      case 1:
        $sql = "select distinct e.hash_name,e.typeofelement as tipo,e.idelemento,e.descriptor as nombre from elementos as e where e.idelemento = :element";
        $data = array("element" => $element);
        break;
      case 2:
      case 3:
        $sql = "select distinct e.hash_name,e.typeofelement as tipo,e.idpadre,e.idelemento,e.descriptor as nombre,e2.descriptor as nombrepadre,t.descriptor,t2.descriptor as tipopadre,t2.idtypeofelement as idtipopadre from elementos as e inner join elementos as e2 on e.idpadre = e2.idelemento inner join typeofelement as t on e.typeofelement = t.idtypeofelement inner join typeofelement as t2 on e2.typeofelement = t2.idtypeofelement  where e.idelemento = :element";
        $data = array("element" => $element);
        break;
      case 4:
        $sql = "select distinct e.hash_name,e.typeofelement as tipo,fn_count_downloads(e.idelemento) as descargas,lat,lon,e.idpadre,e.idelemento,e.descriptor as nombre,e2.descriptor as nombrepadre,t.descriptor,t2.descriptor as tipopadre,t2.idtypeofelement as idtipopadre,path,row,date,projection,ellipsoid,rating,fn_avg_ranked(e.idelemento) as average from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join elementos as e2 on e.idpadre = e2.idelemento inner join points as p on p.idmetadatos = m.idmetadato and p.position = 'CENTER' inner join typeofelement as t on e.typeofelement = t.idtypeofelement inner join typeofelement as t2 on e2.typeofelement = t2.idtypeofelement left join puntuaciones as pu on e.idelemento = pu.idimagen and idusuario = :user  where e.idelemento = :element";
        $data = array("user" => $user, "element" => $element);
        break;
      case 5:
        $sql = "select distinct e.hash_name,e.typeofelement as tipo,e.idpadre,composition,e.idelemento,e.descriptor as nombre,e2.descriptor as nombrepadre,t.descriptor,t2.descriptor as tipopadre,t2.idtypeofelement as idtipopadre,description from elementos as e inner join elementos as e2 on e.idpadre = e2.idelemento inner join typeofelement as t on e.typeofelement = t.idtypeofelement inner join typeofelement as t2 on e2.typeofelement = t2.idtypeofelement inner join metadatos_productos as mp on mp.idelemento = e.idelemento  where  e.idelemento = :element";
        $data = array("element" => $element);
        break;
    }
    //echo $sql;
    $res = $this->con->executeQuery($sql,$data);
    return $res[0];
  }

  /**
  * REGRESA EL NÚMERO DE HIJOS QUE TIENE UN ELEMENTO
  */
  public function countChilds($element,$ishash=false){
    if($ishash){
      $element = $this->getId($element);
    }
    $sql = "select count(*) from elementos where idpadre = :element";
    $data = array("element" => $element);
    $res = $this->con->executeQuery($sql,$data);
    return $res[0][0];
  }

  /**
  * REGRESA LOS HIJOS DE UN ELEMENTO
  * @params elemento, número de resultados, inicio de los resultados
  */
  public function getChilds($element,$limit,$offset,$ishash){
    $tipo = $this->getType($element,$ishash);
    if($ishash){
      $element = $this->getId($element,$ishash);
    }
    if($tipo == 4){
      $sql = "select * from elementos as e inner join metadatos_productos as mp on mp.idelemento = e.idelemento where idpadre = :element order by e.idelemento,descriptor";
    }else{
      $sql = "select idelemento as id,descriptor as nombre,hash_name from elementos where idpadre = :element order by idelemento,descriptor ";
    }

    $data = array("element" => $element);
    if($limit > 0){
      $sql .= " limit ".$limit." offset ".$offset;
    }
    $res = $this->con->executeQuery($sql,$data);
    return $res;
  }

  /**
  * REGRESA EL ID DE LA IMAGEN A PARTIR DEL HASH RECIBIDO
  * @return ID DE LA IMAGEN
  */
  public function getIdImageFromHash($hash){
    $sql = "SELECT e.idelemento,descriptor,city,state,country from elementos as e inner join metadatos as m on m.idelemento = e.idelemento inner join points as p on p.idmetadatos = m.idmetadato and position = 'CENTER' where hash_name = :hash";
    $data = array("hash" => $hash);
    $res = $this->con->executeQuery($sql,$data);
    if(count($res) > 0){
      return $res[0];
    }else{
      return -1;
    }
  }

  public function getEncryptID($idelement){
    $sql = "select crypt(idelemento::text, gen_salt('bf', 8)) from elementos where idelemento = :idelemento";
    $data = array("idelemento" => $idelement);
    $res = $this->con->executeQuery($sql,$data);
    return $res[0][0];
  }
}
?>