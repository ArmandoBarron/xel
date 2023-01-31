<?php

//INCLUYE LOS ARCHIVOS NECESARIOS
include_once("resources/conf.php");
include_once(SESIONES);
include_once(CLASES . "/class.PageManagment.php");

//print_r(CLASES);

$loginUrl = "";

//INICIA LA SESIÓN
Sessions::startSession("buscador");
if(empty($_SESSION['user'])){
  $loginUrl = Sessions::checkFBSession();
}

$user = isset($_SESSION['id']) ? $_SESSION['id'] : -1;

$_SESSION['actual_url'] = "http://$_SERVER[HTTP_HOST]$_SERVER[REQUEST_URI]";


$busqueda = isset($_GET['busqueda']) &&  !empty($_GET['busqueda']) ? intval($_GET['busqueda']) : 0;

include_once("includes/get_language.php");
//echo $busqueda;
?>

<!DOCTYPE html>
<html>
<?php //CARGA EL HTML HEADER CON TODOS LOS CSS
PageManagment::loadHTMLHeader($lngarr['searcher']); ?>
<body style="height: 99vh;overflow: auto">
  <?php

  echo "<div id='container-fluid wrapper' style='height:100%'>";
    //CARGA EL HEADER DE LA PÁGINA
    PageManagment::loadHTMLFile("header");

    //CARGA EL CONTENIDO
    PageManagment::loadHTMLFile("searcher");

  echo "</div>";

  //CARGA EL PANEL DERECHO
  //if(isset($_SESSION['id'])){
    //PageManagment::loadHTMLFile("rightPanel");
  //}

  PageManagment::loadModals($loginUrl);

  //CARGA LOS ARCHIVOS JS
  PageManagment::loadHTMLFile("js_imports");
  //PageManagment::loadHTMLFile("footer");
  ?>
</body>
</html>
