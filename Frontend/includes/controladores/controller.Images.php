<?php

include_once("../../resources/conf.php");
include_once(SESIONES);
include_once(CLASES . "/class.Logs.php");
include_once(CLASES . "/class.Images.php");
include_once(VISTAS . "/show_results.php");
include_once(CLASES . "/class.Weather.php");

//INICIA LA SESIÓN
Sessions::startSession("buscador");
if(isset($_POST['action'])){
  $action = $_POST['action'];
  $id_user = $_SESSION['id'];
  $idreco = -1;
  /**
  * INICIALIZA EL OBJETO DE DONDE OBTENDRA LAS IMAGENES
  */
  $images = new Images();
  switch($action){
    case "view_image":
      $hash = $_POST['image'];
      $id_image = $images->getIdImageFromHash($hash);
      
      $rightP = $_POST['rightP'];
      $idreco = $_POST['idrecomendacion'];
      if($id_image[0] > -1){
        Logs::addClick($action,$id_image[0],$id_user,$rightP,$idreco);
        echo json_encode($id_image);
      }
      break;
    case "get_derivados": //REGRESA LOS PRODUCTOS DERIVADOS DE UNA IMAGEN EN FORMATO JSON
      if(isset($_POST['img'])){
        $id = $_POST['img'];
        $res = $images->getDerivados($id,$id_user);
        $url = $_SERVER["HTTP_HOST"]."/AEM-Eris/element.php?elemento=";
        echo json_encode(array("derivados" => $res,"url" => $url));
      }
      break;
    case "get_images_in_shape": //MUESTRA LOS RESULTADOS DE UNA BUSQUEDA
      //print_r($_POST);
      if(isset($_POST['clima'])){
        if($_POST['clima'] == 'historico'){
          getWeatherData();
        }else if($_POST['clima'] == 'estados'){
          getStatesClustering();
        }
      }else{
        getImagesInShape($images);
      }
      
      break;
    case "get_from_search":
      if(isset($_POST['id']) && isset($_POST['nivel'])){
        $idelemento = $_POST['idelemento'];
        $idsearch = $_POST['idsearch'];
      }
      break;
    case "get_in_path_row":
      if(isset($_POST['satelite']) && isset($_POST['path']) && isset($_POST['row'])){
        $satelite = $_POST['satelite'];
        $path = $_POST['path'];
        $row = $_POST['row'];
        $res = $images->getImagesInPathRow($path,$row,$satelite);
        $idreco = isset($_POST['idrecomendacion']) ? $_POST['idrecomendacion'] : -1;
        $rightP = isset($_POST['rightP']) && $_POST['rightP'] == true;
        $action = $_POST['clic'];
        Logs::addClick($action,$res[0]["id"],$id_user,$rightP,$idreco);
        echo json_encode($res);
      }
      break;
    case "view_metadata": //REGRESA LOS METADATOS
    case "view_polygon": //REGRESA EL POLIGONO DE UNA IMAGEN
    case "view_image_on_map": //REGRESA EL POLIGONO DE UNA IMAGEN
    case "view_image_on_map_poly": //REGRESA EL POLIGONO DE UNA IMAGEN
    case "view_polygon_poly": //REGRESA EL POLIGONO DE UNA IMAGEN
    case "view_polygon_overlap":
      //print_r($_POST);
      if(isset($_POST['imagen'])){
        $hash = $_POST['imagen'];
        $res = $images->getIdImageFromHash($hash);
        $id_image = $res[0];
        $rightP = isset($_POST['rightP']) && $_POST['rightP'] == true;
        $idreco = $_POST['idrecomendacion'];
        if($id_image > -1){
          $res = $images->getPolygon($id_image);
          Logs::addClick($action,$id_image,$id_user,$rightP,$idreco);
          echo json_encode($res);
        }
      }
      break;
    case "get_pathrow_poly": //REGRESA EL POLIGONO DE UN PATH/ROW
      if(isset($_POST['row']) && isset($_POST['path'])){
        $path = $_POST['path'];
        $row = $_POST['row'];
        $res = $images->getPathRowPoly($path,$row);
        echo json_encode($res);
      }
      break;
    case "get_images_date_point": //REGRESA LAS IMAGENES EN UN PUNTO Y FECHA ESPECIFICADOS
      if(isset($_POST['satelites']) && isset($_POST['year']) && isset($_POST['month'])  && isset($_POST['lat'])&& isset($_POST['lon'])){
        $satelites = $_POST['satelites'];
        $year = $_POST['year'];
        $month = $_POST['month'];
        $lat = $_POST['lat'];
        $lon = $_POST['lon'];
        $state = $_POST['state'];
        $country = $_POST['country'];
        $city = $_POST['city'];
        $imgs = $images->getImagesInPlace($lat,$lon,$city,$state,$country,$satelites,$date,null,null,null,1,0,0);
        echo json_encode($imgs);
      }
      break;
    case "get_images_date_shape": //REGRESA LAS IMAGENES EN UNA FECHA Y EN UNA FORMA ESPECIFICADA
      if(isset($_POST['satelites']) && isset($_POST['year']) && isset($_POST['month'])  && isset($_POST['shape'])){
        $satelites = $_POST['satelites'];
        $year = $_POST['year'];
        $month = $_POST['month'];
        $shape = $_POST['shape'];
        $rightP = isset($_POST['rightP']) && $_POST['rightP'] == true;
        $action = $_POST['clic'];

        if($rightP){
          $c_x = $_SESSION['lat_ctr'];
          $c_y = $_SESSION['lon_ctr'];
          $shape = "circulo";
          $idreco = $_POST["idrecomendacion"];
        }else{
          $coors_poly = $_POST["result"];
          $coors_poly = json_decode("$coors_poly", true);
          $c_x = $coors_poly[0]['lat'];
          $c_y = $coors_poly[0]['lon'];
          $rightP = 0;
        }

        if($shape == "circulo"){
          if(isset($_POST['radio'])){
            $radio = $rightP ? $_SESSION['usrRadius'] : $_POST['radio'];
            $imgs = $images->getImagesInCircle($radio,$c_x,$c_y,$satelites,null,null,null,null,1,true,$month,$year,!$rightP);
          }
        }else{
          $imgs = $images->getImagesFromPolygon($shape,$coors_poly,$satelites,null,null,null,null,1,0,0,$month,$year);
        }
        //print_r($rightP);
        
        if(isset($action)){
          Logs::addClick($action,$imgs[0]['id'],$id_user,$rightP,$idreco);
        }
        
        echo json_encode($imgs);
      }
      break;
  }
}

/**
* REALIZA LA BÚSQUEDA DE IMAGENES EN BASE A LOS PARAMETROS OBTENIDOS POR MEDIO DEL METODO POST
*/
function getImagesInShape($images){
  print_r($_POST['shape']);
  if(isset($_POST['shape'])){
    $shape = $_POST['shape']; //FIGURA DE BUSQUEDA
    $filtro = $_POST['filtro']; //GUARDA EL VALOR DE LO QUE MOSTRARA COMO RESULTADO
    $show_products = $_POST['showproducts']; //SI LA BUSQUEDA ES POR POLYGONOS
    $onlynames = $_POST['onlynames']; //SOLO SE REQUIERE LA INFORMACION DE LA IMAGEN Y NO MOSTRARLA
    $startdate = isDate($_POST['startDate']); //FECHA INICIAL DE LA BUSQUEDA
    $enddate = isDate($_POST['endDate']); //FECHA  FINAL DE LA BUSQUEDA
    $satelites = $_POST['satelites']; //SATELITES DE LA BUSQUEDA
    $page = (isset($_POST['page']) && !empty($_POST['page']))?$_POST['page']:1; //PAGINA EN LA QUE SE ENCUENTRA
    $height = $_POST["height"]; //ALTURA DEL DIV DE RESULTADOS
    $polis = json_decode($_POST['polis']); //POLIGONOS MOSTRADOS EN EL MAPA
    $overlaps = json_decode($_POST['overlaps']); //IMAGENES MOSTRADAS EN EL MAPA
    $adjacents  = 4; //brecha entre páginas después de varios adyacentes
    $per_page = 10; //la cantidad de registros que desea mostrar
    $offset = ($page - 1) * $per_page; //INICIO DE LA PAGINACIÓN
    $month = (isset($_POST['month']) && !empty($_POST['month']))?$_POST['month']:-1;
    $year = (isset($_POST['year']) && !empty($_POST['year']))?$_POST['year']:-1;

    switch ($shape) {
      case 'lugar': //EN EL CASO DE QUE LA BUSQUEDA HAYA SIDO POR LOCALIZACIÓN DE LUGAR
        if(isset($_POST['lat']) && isset($_POST['lon'])){
          
          $lat = $_POST['lat'];
          $lon = $_POST['lon'];
          $state = $_POST['state'];
          $country = $_POST['country'];
          $city = $_POST['city'];
          $imgs = $images->getImagesInPlace($lat,$lon,$city,$state,$country,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,$per_page,$offset,$month,$year);
        }
        break;
      case 'circulo': //BUSQUEDA POR CIRCULO
        if(isset($_POST['coordenadas']) && isset($_POST['radio']) ){
          $center = json_decode($_POST['coordenadas'],true);
          $c_x = $center[0]['lat'];
          $c_y = $center[0]['lon'];
          $radio = $_POST['radio'];
          if($filtro == 3 && !$onlynames){
            $imgs = $images->getImagesInCircleByGroup($radio,$center,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,true,$month,$year);
          }else if($filtro == 2 && !$onlynames){
            $imgs = $images->getImagesInCircleByDate($radio,$center,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,true,$month,$year);
          }else{
            $imgs = $images->getImagesInCircle($radio,$c_x,$c_y,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,true,$month,$year);
          }
        }
        break;
      case 'pathrow':
        $shape = "poligono";
      case 'rectangulo': //POLIGNO Y RECTANGULO
      case 'poligono':
        if(isset($_POST['coordenadas'])){
          $poligono = json_decode($_POST['coordenadas'],true);
          $imgs = $images->getImagesFromPolygon($shape,$poligono,$satelites,$startdate,$enddate,$filtro,$show_products,$onlynames,$per_page,$offset,$month,$year);
        }
        break;
    }
    if(!$onlynames){
      $number_res = $images->getNumberOfImages();
      $idbusqueda = $images->getIdBusqueda();
      $_SESSION['busqueda'] = $idbusqueda;
      //MUESTRA LOS RESULTADOS EN LA VISTA
      //print_r($imgs);
      if($filtro == 3){
        results_overlaps($imgs,$polis,$number_res,$per_page,$offset,$height,$adjacents,$page,$shape);
      }else if($filtro == 2){
        results_polygons($imgs,$polis,$number_res,$per_page,$offset,$height,$adjacents,$page,$shape);
      }else if($filtro == 1){
        results_imgs($imgs,$polis,$overlaps,$number_res,$per_page,$offset,$height,$adjacents,$page,$idbusqueda,$shape);
      }
    }else{
      echo json_encode($imgs);
    }
  }
}



/**
* VERIFICA SI ES UNA FECHA VALIDA
*/
function isDate($date){
  if (DateTime::createFromFormat('Y-m-d', $date) !== FALSE) {
    return $date;
  }
  return "";
}


function getStatesClustering(){
  $url = "http://disys0.tamps.cinvestav.mx:5000/clustering/" + $_POST['k'];
  $result = "";
  
  // Get cURL resource
  $curl = curl_init();
  // Set some options - we are passing in a useragent too here
  curl_setopt_array($curl, array(
    CURLOPT_RETURNTRANSFER => 1,
    CURLOPT_URL => $url,
  ));
  // Send the request & save response to $resp
  $resp = curl_exec($curl);
  // Close request to clear up some resources
  curl_close($curl);
  echo $result;
}
/***
*
**/
function getWeatherData(){
  $weather = new Weather();
  //print_r($_POST);
  $k = $_POST['k'];
  //echo $k;
  $url = "http://disys3.tamps.cinvestav.mx:8091/clustering?k=".$k;
  //$url = "http://148.247.201.140:8091/clustering?k=".$k;
  $data = array();
  $result = "";
  if(isset($_POST['shape'])){
    $shape = $_POST['shape']; //FIGURA DE BUSQUEDA
    switch ($shape) {
      case 'pathrow':
        $shape = "poligono";
      case 'rectangulo': //POLIGNO Y RECTANGULO
      case 'poligono':
        if(isset($_POST['coordenadas'])){
          $poligono = json_decode($_POST['coordenadas'],true);
          $data = $weather->getFromPolygon($poligono);
          //print(count($data));
          #print_r($data);
          $data_string = json_encode($data);
          #echo "x";
          //echo $data_string;
          $ch = curl_init($url);
          curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
          curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);          
          curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
          curl_setopt($ch, CURLOPT_HTTPHEADER, array(   
              'Content-Type: application/json',
              'Content-Length: ' . strlen($data_string))
          );
          //echo 1;
          $result = curl_exec($ch);
          //print_r($result);
        }
        break;
    }
  }
  echo $result;
}

?>
