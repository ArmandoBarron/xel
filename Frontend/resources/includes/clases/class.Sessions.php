<?php

#echo realpath(dirname(__FILE__)."/../../resources/conf.php");


include_once("class.DB.php");
include_once(realpath(dirname(__FILE__)."/../../resources/conf.php"));
include_once("class.Images.php");
include_once("class.PageManagment.php");
include_once(PASSWORDS);
include_once(LIBRARY . "/Facebook/autoload.php");

ini_set('display_errors', 1);

/**
* CLASE PARA EL MANEJO DE SESIONES
*/
class Sessions{

  private $con;

  /**
  * CONSTRUCTOR
  */
  public function __construct(){
    $this->con = new DB();
  }

  /**
  * INICIA LA SESIÓN DE LA PAGINA
  */
  public static function startSession($session_name){
    //if (session_status() == PHP_SESSION_NONE) {
      session_name($session_name);
      session_start();
      header("Expires: Tue, 01 Jan 2000 00:00:00 GMT");
      header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT");
      header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
      header("Cache-Control: post-check=0, pre-check=0", false);
      header("Pragma: no-cache");
      $now = time();
      if (isset($_SESSION['discard_after']) && $now > $_SESSION['discard_after']) {
      // this session has worn out its welcome; kill it and start a brand new one
        session_unset();
        session_destroy();
        session_start();
      }

    // either new or old, it should live at most for another hour
      $_SESSION['discard_after'] = $now + 3600;
    //}
  }

  public static function checkFBSession(){
    /*$fb = new Facebook\Facebook(array(
      'app_id'                => '315200965581285',
      'app_secret'            => '55d2259705fda5fe2e3a8778f2efdfe6',
      'default_graph_version' => 'v2.10',
    ));

    $helper = $fb->getRedirectLoginHelper();

    $permissions = array('email'); // Optional permissions
    return $loginUrl = $helper->getLoginUrl('http://www.adaptivez.org.mx/AEM-Eris/includes/fb-callback.php', $permissions);*/
  }

  /**
  * VERIFICA SI HAY UN USUARIO REGISTRADO CON EL EMAIL INGRESADO
  */
  public function checkemail($email){
    try{
      $sql = "SELECT keyuser as res,hash_name FROM usuarios WHERE email = '$email'";
      $data = $this->con->executeQuery($sql);
      if(!empty($data[0]['res'])){
        return array('mensaje' => "El correo electrónico ya se encuentra asociado con otra cuenta.", 'codigo' => 1,'id' => $data[0]['res'],'hash' => $data[0]['hash_name']);
      }else{
        return array('mensaje' => "Correo electrónico disponible.", 'codigo' => 0 );
      }
    } catch(PDOException $e) {
      echo  $e->getMessage();
    }
  }

  /**
  * VERIFICA SI EL NOMBRE DE USUARIO NO EXISTE
  */
  public function checkusername($username ){
    try{
      $sql = "SELECT keyuser as res FROM usuarios WHERE nombre_usuario = '$username'";
      $data = $this->con->executeQuery($sql);
      if(!empty($data[0]['res'])){
        return array('mensaje' => "El nombre de usuario ya ha sido utilizado.", 'codigo' => 1,'id' => $data[0]['res']);
      }else{
        return array('mensaje' => "Nombre de usuario disponible.", 'codigo' => 0 );
      }
    } catch(PDOException $e) {
      echo  $e->getMessage();
    }
  }

  /**
  * COMPRUEBA SI LOS DATOS INGRESADOS POR UN USUARIO SON CORRECTOS
  */
  public function login($username,$password){
    try{
      $sql = "SELECT password,keyuser,nombre_usuario,email,superuser from usuarios where email = '$username' or nombre_usuario = '$username'";
      $data = $this->con->executeQuery($sql);

      if(count($data) > 0&&password_verify($password,$data[0]['password'])){
        return array('codigo' => 0, 'id' => $data[0]['keyuser'],'email' => $data[0]['email'], 'username' => $data[0]['nombre_usuario'],'mensaje' => "Datos correctos.","superuser" => $data[0]["superuser"]);
      }else{
        return array('mensaje' => "Datos incorrectos.", 'codigo' => 1 );
      }
    } catch(PDOException $e) {
      echo  $e->getMessage();
    }
  }

  /**
  * REGISTRA UN NUEVO USUARIO
  */
  public function signup($email,$username,$password){
    $password = password_hash($password, PASSWORD_BCRYPT);

    try{
      $msjuser = $this->checkusername($username);
      if($msjuser['codigo'] == 1){
        return $msjuser;
      }

      $msjemail = $this->checkemail($email);
      if($msjemail['codigo'] == 1){
        return $msjemail;
      }

      $sql = "INSERT INTO usuarios(password,email,nombre_usuario,hash_name) VALUES('$password','$email','$username',crypt('$username', gen_salt('bf'))) returning keyuser";
      //echo $sql;
      $data = $this->con->executeQuery($sql);
      return array('mensaje' => "Usuario registrado con éxito.", 'codigo' => 0,'id' => $data[0]['keyuser']);
    } catch(PDOException $e) {
      echo  $e->getMessage();
    }
  }

  /**
  * REGRESA TODOS LOS COMENTARIOS DE UNA IMAGEN
  */
  public function getComments($idimagen,$ishash=false){
    if($ishash){
      $imagenes = new Images();
      $idimagen = $imagenes->getId($idimagen);
    }
    $sql = "SELECT * FROM comments as c INNER JOIN comments_user as cu on cu.idcomment = c.idcomment INNER JOIN usuarios as u ON cu.iduser = keyuser WHERE c.idimagen = :idimagen order by \"date\" desc";
    $data = array('idimagen' => $idimagen);
    $comments = $this->con->executeQuery($sql,$data);
    return $comments;
  }

  /**
  * AGREGA UN NUEVO COMENTARIO
  */
  public function addCommnet($comment,$idimagen,$iduser,$ishash=false){
    if($ishash){
      $imagenes = new Images();
      $idimagen = $imagenes->getId($idimagen);
    }
    $sql = "INSERT INTO comments(comment,idimagen) VALUES(:comment,:idimagen) RETURNING idcomment";
    $data = array('comment' => $comment,'idimagen' => $idimagen);
    $id = $this->con->executeQuery($sql,$data);
    $id = $id[0][0];
    $data = array('idcomment' => $id,'iduser' => $iduser);
    $sql = "INSERT INTO comments_user(idcomment,iduser) VALUES(:idcomment,:iduser)";
    $this->con->executeQuery($sql,$data);
  }

  public function rate($user,$img,$rating){
    $sql = "SELECT fn_upd_rating(:img,:user,:rating)";
    $data = array("img" => $img,"user" => $user,"rating" => $rating);
    $this->con->executeQuery($sql,$data);
  }

  private function calculateUbicationFromSearches($data){
    $busquedas_poligonos = $this->con->executeQuery("select polygon from busquedas as b inner join busquedabypolygon as bp on bp.idbusqueda = b.idbusqueda where \"user\" = :user;",$data);
    $center_lat = 0;
    $center_lon = 0;
    foreach ($busquedas_poligonos as $key => $polygon) {
      $polygon = str_replace("(","", $polygon);
      $polygon = str_replace(")","", $polygon);
      $coors = explode(",",implode(",", $polygon));
      $n = count($coors);
      $sum_lat = 0;
      $sum_lon = 0;
      for($i=0;$i<$n;$i+=2){
        $sum_lon += $coors[$i];
        $sum_lat += $coors[$i+1];
      }
      $center_lat += $sum_lat/($n/2);
      $center_lon += $sum_lon/($n/2); 
    }
    $busquedas_circulos = $this->con->executeQuery("select center_lat,center_lon from busquedas as b inner join busquedabycircle as bp on bp.idbusqueda = b.idbusqueda where \"user\" = :user",$data);

    foreach($busquedas_circulos as $circle){
      $center_lat += $circle['center_lat'];
      $center_lon += $circle['center_lon'];
    }

    $busquedas_puntos = $this->con->executeQuery("select lat,lon from busquedas as b inner join busquedabypoint as bp on bp.idbusqueda = b.idbusqueda where \"user\" = :user;",$data);

    foreach($busquedas_puntos as $punto){
      $center_lat += $punto['lat'];
      $center_lon += $punto['lon'];
    }

    $m = count($busquedas_poligonos) + count($busquedas_circulos) + count($busquedas_puntos);
    $center_lat /= $m;
    $center_lon /= $m;
    return array("lat" => $center_lat, 
     "lon" => $center_lon,
     "definedByUser" => false,
     "radio" => 300000
   );
  }

  public function getUbication($user){
    $data = array("user" => $user);
    $sql = "select lat,lon,definedByUser,radio from zona_recomendaciones where iduser = :user";
    $res = $this->con->executeQuery($sql,$data);
    if(count($res) == 0){
      return $this->calculateUbicationFromSearches($data);
    }else{
      return $res[0];
    }
  }

  /**
  * ENVIA EL EMAIL DE RECUPERACION DE CONTRASEÑA
  */

  public function sendMailPass($email,$hash,$id){
    $idioma = $_SESSION["lang"];
    $lngarr = PageManagment::getLanguage($idioma);
    $asunto = $lngarr["passrecup"]." - Geoportal Ecosur";
    $destinatario = $email;
    $desde = "From: Geoportal-Ecosur";
    $headers = "MIME-Version: 1.0\r\n";
    $headers .= "Content-type: text/html; charset=iso-8859-1\r\n";
    //dirección del remitente
    $headers .= "From: Geoportal-Ecosur <ggeoportal@gmail.com>\r\n";
    //print_r($_SESSION);
    $mensaje = "<h1>".$lngarr["resetupass"]."</h1><br>".$lngarr["msjresetpass"]."<br><a href='http://".$_SERVER[HTTP_HOST]."/AEM-Eris/new_password.php?user=".$hash."'>".$lngarr["passrecup"]."</a>";
    echo $mensaje;
    mail($destinatario,$asunto,$mensaje,$headers);
    echo "Correo enviado";
    $sql = "INSERT INTO passwordsreset(iduser) VALUES(:id)";
    $data = array("id" => $id);
    $this->con->executeQuery($sql,$data);
  }

  /**
  * ACTUALIZA O GUARDA LA ZONA DE PREFERENCIA DEL USUARIO
  */
  public function saveLocation($user,$lat,$lon,$radius,$band){
    $sql = "select fn_upd_zone(:user,:lat,:lon,:band,:radio)";
    $data = array("user" => $user,"lat" => $lat,"lon" => $lon, "band" => $band,"radio" => $radius);
    $res = $this->con->executeQuery($sql,$data);
    if(count($res) == 1){
      return array("mensaje" => "Datos insertados.", "codigo" => 0);
    }else{
      return array("mensaje" => "Error.", "codigo" => 1);
    }
  }

  /**
  * REGRESA LOS DATOS DEL USUARIO A PARTIR DE SU HASH
  */
  public function getUserFromHash($hash){
    $sql = "SELECT * from usuarios as u inner join passwordsreset as pr on pr.iduser = u.keyuser where hash_name = :hash order by fecha desc";
    $data = array("hash" => $hash);
    $res = $this->con->executeQuery($sql,$data);
    //print_r($res[0]);
    return $res[0];
  }

  public function changePassword($user,$pass){
    $pass = password_hash($pass, PASSWORD_BCRYPT);
    $sql = "UPDATE usuarios set password = :pass where hash_name = :hash returning keyuser";
    $data = array("hash" => $user,"pass" => $pass);
    $res = $this->con->executeQuery($sql,$data);
    $sql = "UPDATE passwordsreset set used = true where iduser = :iduser";
    $data = array("iduser" => $res[0]["keyuser"]);
    $this->con->executeQuery($sql,$data);
    return $res[0];
  }
}
?>
