<?php
include_once(TEMPLATES . "/pagination.php");
include_once(CLASES . "/class.PageManagment.php");

function show_childs($hijos,$number_res,$nivel,$per_page,$adjacents,$idbusqueda,$shape,$offset){
  $idioma = $_SESSION['lang'];
  $lngarr = PageManagment::getLanguage($idioma);

  if($number_res > 0){
    $total_pages = ceil($number_res/$per_page);
    if($nivel == 4){
      $res = "<table class='table'><thead><tr><th>#</th><th>".$lngarr['name']."</th><th>Producto</th><th>".$lngarr['descprod']."</th></tr></thead><tbody >";
    }else{
      $res = "<table class='table'><thead><tr><th>#</th><th>".$lngarr['name']."</th></tr></thead><tbody >";
    }
    //$i = 0;
    if($shape == 2){
      for ($i=$offset; $i < $number_res && $i<$offset+$per_page; $i++){
        $value = $hijos[$i];

        if($nivel == 4){
          $res .= "<tr><td>".$value['idelemento']."</td><td><a href=?elemento=".$value['hash_name']."&busqueda=".$idbusqueda.">".$value['descriptor']."</a></td><td>".$value['short_description']."</td><td>".$value['description']."</td></tr>";
        }else{
          $res .= "<tr><td>".$value['id']."</td><td><a href=?elemento=".$value['hash_name']."&busqueda=".$idbusqueda.">".$value['nombre']."</a></td></tr>";
        }
      }
    }else{
      foreach ($hijos as $key => $value) {
        if($nivel == 4){
          $res .= "<tr><td>".$value['idelemento']."</td><td><a href=?elemento=".$value['hash_name']."&busqueda=".$idbusqueda.">".$value['descriptor']."</a></td><td>".$value['short_description']."</td><td>".$value['description']."</td></tr>";
        }else{
          $res .= "<tr><td>".$value['id']."</td><td><a href=?elemento=".$value['hash_name']."&busqueda=".$idbusqueda.">".$value['nombre']."</a></td></tr>";
        }
      }
    }

    $res .= "</tbody></table>";
    echo $res;
    //echo $total_pages;
    if($total_pages > 1){
      paginate($page, $total_pages, $adjacents,"cargarTabla");
    }
  }else{
    echo "<h6>".$lngarr['theelement'].$lngarr['donthave']."</h6>";
  }
}
