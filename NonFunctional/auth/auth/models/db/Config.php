<?php

$user = $_ENV['DB_USER'];
$pass = $_ENV['DB_PASSWORD'];
$name = $_ENV['DB_NAME'];
$host = $_ENV['DB_HOST'];
$port = $_ENV['DB_PORT'];

date_default_timezone_set('America/Mexico_City');
define('DB_USERNAME', $user);
define('DB_PASSWORD', $pass);
define('DB_HOST', $host);
define('DB_PORT', $port);
define('DB_NAME', $name);
define('AUTH_PORT', $_ENV['AUTH_PORT']);
define('FRONTEND_PORT', $_ENV['FRONTEND_PORT']);

define('USER_CREATED_SUCCESSFULLY', 0);
define('USER_CREATE_FAILED', 1);
define('EMAIL_ALREADY_EXIST', 2);
define('USER_ALREADY_EXIST', 3);
define('CANT_SEND_EMAIL', 4);

?>