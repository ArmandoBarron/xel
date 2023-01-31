<?php 
if(!isset($_GET['lang'])) {
  $idioma = substr($_SERVER["HTTP_ACCEPT_LANGUAGE"],0,2);
}else{
  $idioma = $_GET['lang'];
  if(!($idioma == "es" || $idioma == "en")){
    $idioma = substr($_SERVER["HTTP_ACCEPT_LANGUAGE"],0,2);
  }
}
$string = file_get_contents("resources/langs.json");
$json_a = json_decode($string, true);
$lngarr = $json_a[$idioma];
$_SESSION["lang"] = $idioma;

