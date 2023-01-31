<?php
include_once("../../resources/conf.php");
include_once(SESIONES);
include_once(CLASES . "/class.DB.php");
include_once(CLASES . "/class.Logs.php");

//INICIA LA SESIÓN
Sessions::startSession("buscador");

/**
* ARCHIVO PARA EL MANEJO DE LAS SESIONES
*/


if(isset($_POST['action'])){
  $action = $_POST['action'];
  $session = new Sessions();
  switch($action) {
    case 'check': //checa la sesion
    $x = isset($_SESSION['user']) ? true : false;
    echo json_encode($x);
    break;
    case 'login': //inicio de sesion

    if(isset($_POST['username']) && isset($_POST['password'])){
      $res = $session->login($_POST['username'],$_POST['password']);
      if($res['codigo'] == 0){
        $_SESSION['user'] = $res['username'];
        $_SESSION['email'] = $res['email'];
        $_SESSION['id'] = $res['id'];
        $_SESSION['superuser'] = $res['superuser'];
        $ip = isset($_POST['ip']) && !empty($_POST['ip']) ? $_POST['ip'] : null;
        $lat = isset($_POST['lat']) && !empty($_POST['lat']) ? $_POST['lat'] : null;
        $lon = isset($_POST['lon']) && !empty($_POST['lon']) ? $_POST['lon'] : null;
        $locByIp = isset($_POST['locationByIp']) && !empty($_POST['locationByIp']) ? $_POST['locationByIp'] : null;
        $s = Logs::saveSession($res['id'],$ip,$lat,$lon,$locByIp);
        $_SESSION['session_id'] = $s;
      }

      echo json_encode($res);
    }
    break;
    case 'signup': //registro
    if(isset($_POST['username']) && isset($_POST['password']) && isset($_POST['email'])){
      $res = $session->signup($_POST['email'],$_POST['username'],$_POST['password']);
      echo json_encode($res);
    }
    break;
    case 'checkmail':
    if(isset($_POST['email'])){
      $res = $session->checkemail($_POST['email']);
      echo json_encode($res);
    }
    break;
    case "changepass":
    if(isset($_POST['user']) && isset($_POST['password'])){
      $user = $_POST['user'];
      $pass = $_POST['password'];
      $res = $session->changePassword($user,$pass);
      echo json_encode($res);
    }
    break;
    case "sendmailpass":
    if(isset($_POST['email']) && isset($_POST['hash']) && isset($_POST['id'])){
      $session->sendMailPass($_POST['email'],$_POST['hash'],$_POST['id']);
    }
    break;
    case "comment": //agrega un comentario
    if(!isset($_SESSION['id'])){
      echo json_encode(array('mensaje' => 'Debe de iniciar sesión para comentar','status' => -1));
    }else{
      $comment = $_POST['comment'];
      $idimagen = $_POST['element'];
      $iduser = $_SESSION['id'];
      $session->addCommnet($comment,$idimagen,$iduser,true);
      echo json_encode(array('mensaje' => 'Comentario agregado','status' => 0));
    }
    break;
    case "getcomments": //obtiene todos los comentarios
    if(isset($_POST['element'])){
      $idimagen = $_POST['element'];
      $comments = $session->getcomments($idimagen,true);
      echo json_encode($comments);
    }
    break;
    case "rate": //rankeo de imageenes
    if(isset($_POST['img']) && isset($_POST['rating']) && isset($_SESSION['user'])){
      $user = $_SESSION['id'];
      $img = $_POST['img'];
      $rating = $_POST["rating"];
      $session->rate($user,$img,$rating);
    }
    break;
    case "get_ubication":
    if(isset($_SESSION['id'])){
      $user = $_SESSION['id'];
      $ubication = $session->getUbication($user);
      echo json_encode($ubication);
    }
    break;
    case "save_location":
    if(isset($_SESSION['id']) && isset($_POST['lat']) && 
     isset($_POST['lon']) && isset($_POST['radio']) && isset($_POST['definedbyuser'])){
      $user = $_SESSION['id'];
    $lat = $_POST['lat'];
    $lon = $_POST['lon'];
    $radio = $_POST['radio'];
    $band = $_POST['definedbyuser'];
    $res = $session->saveLocation($user,$lat,$lon,$radio,$band);
    echo json_encode($res);
  }
  break;
}
}else{ //cierre de sesion
  unset($_SESSION["user"]);
  unset($_SESSION["id"]);
  unset($_SESSION["email"]);
  unset($_SESSION["FBRLH_state"]);
  session_unset();
  session_destroy();
  header("Location: ../../index.php");
}
