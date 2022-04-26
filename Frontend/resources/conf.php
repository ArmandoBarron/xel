<?php

/*
    CONFIGURACIONES DEL PROYECTO
*/
$config = array(
    "db" => array(
        "db1" => array(
            "dbname" => "geodatabase",
            "username" => "postgres",
            "password" => 'postgres',
            "host" => "database",
            "port" => "5432"
        )
    ),
    "urls" => array(
        "baseUrl" => "http://localhost/AEM-Eris"
    ),
    "paths" => array(
        "resources" => $_SERVER["DOCUMENT_ROOT"] . "/AEM-Eris/resources"
    )
);

$_ENV["tokenOrg"] = "7aeb2660e8aac9ee0dc09a22a45e799ed73c78942df55017d857654cd940998c";
$_ENV["IP_SKY"] = "disys0.tamps.cinvestav.mx:4747";

/*
    Creating constants for heavily used paths makes things a lot easier.
    ex. require_once(LIBRARY_PATH . "Paginator.php")
*/
defined("LIBRARY")
    or define("LIBRARY", realpath(dirname(__FILE__) . '/library'));
defined("PASSWORDS")
    or define("PASSWORDS", realpath(dirname(__FILE__) . '/library/password.php'));
defined("CLASES")
    or define("CLASES", realpath(dirname(__FILE__) . '/../includes/clases'));
defined("ARCHIVOS")
    or define("ARCHIVOS", realpath(dirname(__FILE__) . '/src'));
defined("SESIONES")
    or define("SESIONES", realpath(dirname(__FILE__) . '/../includes/clases/class.Sessions.php'));
defined("TEMPLATES")
    or define("TEMPLATES", realpath(dirname(__FILE__) . '/templates'));
defined("VISTAS")
    or define("VISTAS", realpath(dirname(__FILE__) . '/../includes'));
defined("LANGS")
    or define("LANGS", realpath(dirname(__FILE__) . '/langs.json'));

/*
    Error reporting.
*/
ini_set("error_reporting", "true");
error_reporting(E_ALL|E_STRCT);

?>
