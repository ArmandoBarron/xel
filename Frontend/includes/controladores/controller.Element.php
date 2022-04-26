<?php
include_once("../../resources/conf.php");
include_once(SESIONES);
include_once(CLASES . "/class.Logs.php");
include_once(CLASES . "/class.Images.php");
include_once(VISTAS . "/show_childs.php");

//INICIA LA SESIÓN
Sessions::startSession("buscador");

/**
* CONTROLADOR DE LA INFO QUE SE MOSTRARA EN LA VISTA DE ELEMENTOS
*/

if(isset($_POST['action'])){
  $action = $_POST['action'];
  switch ($action) {
    case 'get_info': //OBTIENE LA INFORMACION DE UN ELEMENTO
      if(isset($_POST['element'])){
        $element = $_POST['element'];
        $user = isset($_SESSION['id']) ? $_SESSION['id'] : -1;
        $image = new Images();
        $data = $image->getElementInfo($element,$user,true);
        echo json_encode($data);
      }
      break;
    case "show_childs"://regresa una tabla con los hijos del elemento recibido
      if(isset($_POST['nombre']) &&  isset($_POST['id']) && isset($_POST['page']) && isset($_POST['nivel'])){
        $page = (isset($_POST['page']) && !empty($_POST['page']))?$_POST['page']:1;
        $id = $_POST['id'];
        $nivel = $_POST['nivel'];
        $hashsearch = $_POST['busqueda'];
        $nombre = $_POST['nombre'];
        $adjacents  = 4; //brecha entre páginas después de varios adyacentes
        $per_page = 8; //la cantidad de registros que desea mostrar
        $offset = ($page - 1) * $per_page;
        $image = new Images();
        $idbusqueda = Logs::getIdSearchFromHash($hashsearch);
        $image->setIdBusqueda($idbusqueda);
        if($nivel != 3){
          $number_res = $image->countChilds($id);
          $hijos = $image->getChilds($id,$per_page,$offset);
          show_childs($hijos,$number_res,$nivel,$per_page,$adjacents,$hashsearch);
        }else{
          //echo $idbusqueda;
          if($idbusqueda > 0){
            $busqueda = Logs::getSearch($idbusqueda);
            $typeofsearch = $busqueda['busqueda'][0]['tipo'];
            $satelites = array($nombre);
            $stardate = $busqueda['busqueda'][0]['fecha_inicial'];
            $enddate = $busqueda['busqueda'][0]['fecha_final'];
            $filtro = $busqueda['busqueda'][0]['filtro'];

            switch ($typeofsearch) {
              case 1: //poligono
              case 3: //rectangulo
                $coors_poly = $busqueda['data'][0]['polygon'];
                $coors_poly = str_replace("(", "",$coors_poly);
                $coors_poly = str_replace(")", "",$coors_poly);
                $coors_poly = explode(",",$coors_poly);
                $n = count($coors_poly);
                $coors = array();
                for($i=0;$i<$n;$i+=2){
                  $coors[] = array("lon" => $coors_poly[$i],"lat" => $coors_poly[$i+1]);
                }
                $imgs = $image->getImagesFromPolygon($coors,$satelites,$stardate,$enddate,$filtro,0,0,$per_page,$offset);
                $number_res = $image->getNumberOfImages();
                show_childs($imgs,$number_res,$nivel,$per_page,$adjacents,$hashsearch,1);
                break;
              case 2: //circulo
                $radio = $busqueda['data'][0]['radius'];
                $imgs = $image->getImagesInCircle($radio,$busqueda['data'][0]['center_lat'],$busqueda['data'][0]['center_lon'],$satelites,$stardate,$enddate,$filtro,0,0,true);
                $number_res = $image->getNumberOfImages();

                //echo $number_res;
                show_childs($imgs,$number_res,$nivel,$per_page,$adjacents,$hashsearch,2,$offset);
                //print_r($imgs);
                break;
              case 4: //punto
                $lat = $busqueda['data'][0]['lat'];
                $lon = $busqueda['data'][0]['lon'];
                $state = $busqueda['data'][0]['state'];
                $country = $busqueda['data'][0]['country'];
                $city = $busqueda['data'][0]['city'];
                $imgs = $image->getImagesInPlace($lat,$lon,$city,$state,$country,$satelites,$stardate,$enddate,$filtro,0,0,$per_page,$offset);
                $number_res = $image->getNumberOfImages();
                show_childs($imgs,$number_res,$nivel,$per_page,$adjacents,$hashsearch,4);
                break;
            }
          }else{
            $number_res = $image->countChilds($id);
            $hijos = $image->getChilds($id,$per_page,$offset);
            show_childs($hijos,$number_res,$nivel,$per_page,$adjacents,$hashsearch);
          }
        }

      }
      break;
  }
}
?>
