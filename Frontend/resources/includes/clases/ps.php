<?php

include_once("class.DB.php"); 
include_once("../../resources/conf.php"); 
include_once("class.Images.php"); 
include_once("class.PageManagment.php"); 
include_once(PASSWORDS); 
include_once(LIBRARY . "/Facebook/autoload.php"); 


changePassword('$2a$06$KkRVyLkkSqu9YaIWaZR7h.oz2dzizSOWaPqR7A1e1Vlxv1e5OiQUq',"edilhg"); 


echo "cambiada";

function changePassword($user,$pass){ $pass = password_hash($pass, PASSWORD_BCRYPT); $sql = "UPDATE usuarios set password = :pass where hash_name = :hash returning keyuser"; $data = array("hash" => $user,"pass" => $pass); $res = $this->con->executeQuery($sql,$data); $sql = "UPDATE passwordsreset set used = true where iduser = :iduser"; $data = array("iduser" => $res[0]["keyuser"]); $this->con->executeQuery($sql,$data); return $res[0]; } 
