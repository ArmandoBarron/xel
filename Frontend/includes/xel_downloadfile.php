<?php 


$file = $_GET['filename'];
$dir = "limbo/";
$fileame = $dir.$file;
ignore_user_abort(true);

header($_SERVER["SERVER_PROTOCOL"] . " 200 OK");
header("Cache-Control: public"); // needed for internet explorer
header("Content-Type: application/octet-stream");
header("Content-Transfer-Encoding: Binary");
header("Content-Length:".filesize($fileame));
header("Content-Disposition: attachment; filename=".$file);
readfile($fileame);

ob_clean();
flush();

unlink(dirname(__FILE__) ."/". $fileame);