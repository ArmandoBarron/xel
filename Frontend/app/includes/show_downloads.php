<?php
//INCLUYE LOS ARCHIVOS NECESARIOS
include_once("../resources/conf.php");
include_once(SESIONES);
include_once(CLASES . "class.DB.php");
Sessions::startSession("buscador");
if(!empty($_SESSION['id'])){
  $server = $_SERVER[HTTP_HOST];
  $iduser = $_SESSION['id'];
  $db = new DB();
  $sql = "SELECT * FROM descargas as d inner join busquedas as b on d.idbusqueda = b.idbusqueda  where b.user = :iduser";
  $busquedas = $db->executeQuery($sql,array("iduser" => $iduser));

  $table = '<table class="table table-striped"><thead><tr><th>#</th><th>Fecha de la búsqueda</th><th>Tipo</th><th>Filtro</th><th>Solo con derivados</th><th>Filtro de fecha</th><th>Copiar URL</th><th>Ir</th></tr><tbody>';

  foreach ($busquedas as $key => $busqueda) {
    $url = "index.php?busqueda=".$busqueda['idbusqueda'];
    $ir = "<td><a href='$url'><span class='glyphicon glyphicon-share-alt' aria-hidden='true'></span></a></td>";
    $table .= "<tr><td>".$busqueda['idbusqueda']."</td><td>".$busqueda['search_date']."</td><td>".$busqueda['tipo']."</td><td>".$busqueda['filtro']."</td><td>".$busqueda['derivados']."</td><td>".$busqueda['fecha_inicial']."/".$busqueda['fecha_final']."</td><td><button type='button' title='Copiar URL al portapapeles' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-copy' aria-hidden='true' onclick='copyTextToClipboard(\"".$url."\")'></span></button>";
    $table .= $ir . "</tr>";
  }

  $table .= "</tbody></table>";
  echo $table;
}