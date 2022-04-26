<?php
include_once("class.DB.php");
class Route{
  public static function getRoute($description){
    try{
      $sql = "select route from routes where description = '$description'";
      $con = new DB();
      return $con->executeQuery($sql);
		} catch(PDOException $e) {
	    echo  $e->getMessage();
	  }
  }
}
?>
