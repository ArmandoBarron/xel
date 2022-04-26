<?php

include_once("../../includes/clases/class.DB.php");
include_once("collaborative_filtering.class.php");

$cf = new CollaborativeFiltering(15);
$cf->make_recommendations();


function printAsHTML($array){
  $db = new DB();
  $imgs = $db->executeQuery("select distinct idimagen from puntuaciones");
  echo "<table border=1><tr><th>Usuario</th>";
  foreach ($imgs as $key => $val) {
    echo "<th>$val[0]</th>";
  }
  echo "</tr>";


  foreach ($array as $key => $value) {
    echo "<tr><td><strong>$key</strong></td>";
    foreach ($value as $key_rate => $rating) {
      echo "<td>".$rating."</td>";
    }
    echo "</tr>";
  }
}
?>
