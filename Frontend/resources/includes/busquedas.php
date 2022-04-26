<?php
//INCLUYE LOS ARCHIVOS NECESARIOS
include_once("../resources/conf.php");
include_once(TEMPLATES . "/pagination.php");
include_once(SESIONES);
include_once(CLASES . "class.DB.php");
Sessions::startSession("buscador");
if(!empty($_SESSION['id'])){
  $server = $_SERVER[HTTP_HOST];
  $iduser = $_SESSION['id'];
  $page = (isset($_POST['page']) && !empty($_POST['page']))?$_POST['page']:1; //PAGINA EN LA QUE SE ENCUENTRA
  $adjacents  = 4; //brecha entre páginas después de varios adyacentes
  $per_page = 12; //la cantidad de registros que desea mostrar
  $offset = ($page - 1) * $per_page;
  $db = new DB();
  $sql = "SELECT count(*) FROM busquedas as b inner join typeofsearch as t on t.idtype= b.tipo where b.user = :iduser";
  $total_pages = ceil($db->executeQuery($sql,array("iduser" => $iduser))[0][0]/$per_page);
    $sql = "SELECT * FROM busquedas as b inner join typeofsearch as t on t.idtype= b.tipo where b.user = :iduser order by b.search_date asc limit $per_page offset $offset";
  $busquedas = $db->executeQuery($sql,array("iduser" => $iduser));

  $table = '<table class="table table-striped"><thead><tr><th>#</th><th>Fecha de la descarga</th><th>Búsqueda</th><th>Filtro</th><th>Solo con derivados</th><th>Filtro de fecha</th><th>Copiar URL</th><th>Ir</th></tr><tbody>';

  foreach ($busquedas as $key => $busqueda) {
    //print_r($busqueda);
    $url = "index.php?busqueda=".$busqueda['hash_key'];
    $ir = "<td><a href='$url'><span class='glyphicon glyphicon-share-alt' aria-hidden='true'></span></a></td>";
    $table .= "<tr><td>".$busqueda['idbusqueda']."</td><td>".$busqueda['search_date']."</td><td>".$busqueda['tipo']."</td><td>".$busqueda['filtro']."</td><td>".$busqueda['derivados']."</td><td>".$busqueda['fecha_inicial']."/".$busqueda['fecha_final']."</td><td><button type='button' title='Copiar URL al portapapeles' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-copy' aria-hidden='true' onclick='copyTextToClipboard(\"".$url."\")'></span></button>";
    $table .= $ir . "</tr>";
  }

  $table .= "</tbody></table>";
  echo $table;
  paginate($page, $total_pages, $adjacents,"cargarBusquedas");
}
