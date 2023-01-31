<?php 


$file = $_GET['filename'];
$dir = $_SERVER['DOCUMENT_ROOT']."/limbo/";



$fileame = $dir.$file;
ignore_user_abort(true);

$access_token = $_COOKIE['access_token'];                                                       

header($_SERVER["SERVER_PROTOCOL"] . " 200 OK");
header("Cache-Control: public"); // needed for internet explorer
header("Content-Type: application/octet-stream");
header("Content-Transfer-Encoding: Binary");
header("Content-Length:".filesize($fileame));
header("Content-Disposition: attachment; filename=".$file);
header("x-access-token:".$access_token);

readfile($fileame);

ob_clean();
flush();

unlink(dirname(__FILE__) ."/". $fileame);