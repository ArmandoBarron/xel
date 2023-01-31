<?php
//INCLUYE LOS ARCHIVOS NECESARIOS
include_once("../resources/conf.php");
include_once(SESIONES);

//INICIA LA SESIÓN
Sessions::startSession("buscador");

if(isset($_POST['action'])){
  $action = $_POST['action'];
  switch ($action) {
    case 'add':
      if(isset($_POST['agregadas'])){
        $opciones = $_POST['agregadas'];
        if(isset($opciones['id'])){
          $_SESSION['descargas'][$opciones['id']] = $opciones;
        }
      }
      echo count($_SESSION['descargas']);
      break;
    case 'remove':
      $id = $_POST['agregadas'];
      unset($_SESSION['descargas'][$id]);
      echo count($_SESSION['descargas']);
      break;
    case 'removeAll':
      $imgs = $_SESSION['descargas'];
      $_SESSION['descargas'] = array();
      echo json_encode($imgs);
      break;
  }
}
?>
