<?php
include_once(dirname(__FILE__) . "/../resources/conf.php");
include_once(TEMPLATES . "/pagination.php");
include_once(CLASES . "/class.Route.php");
include_once(CLASES . "/class.Images.php");
include_once(CLASES . "/class.PageManagment.php");
//include_once("get_number_images.php");
include_once(PASSWORDS);

/**
* MUESTRA LOS RESULTADOS DE LAS IMÁGENES CUANDO LA BUSQUEDA SE REALIZA POR POLIGONOS
*/
function results_polygons($res,$polis,$number_res,$per_page,$offset,$height,$adjacents,$page,$shape){
  //echo $dirname(__FILE__);
  $idioma = $_SESSION["lang"];
  $lngarr = PageManagment::getLanguage($idioma);
  $meses = $lngarr["months"];
  $todownload =  isset($_SESSION['descargas']) ? $_SESSION['descargas'] : array();
  $total_pages = ceil($number_res/$per_page);
  $overlaps = array();
  $repo = Route::getRoute("repo");
  $mins = Route::getRoute("mins");
  $dir_imgs = "resources/".$repo[0]['route']."/".$mins[0]['route']."/";
  if(count($res)==0):?>
  <br>
    <div class='resultadosbusqueda'>
      <br>
      <?php echo $lngarr['noresults'] ?>
    </div>
  <?php endif; ?>

  <div id="resultadosbusqueda" class="resultadosbusqueda"  style="height:<?php echo $height - 250; ?>px;" >
  <?php
  for ($i=$shape == "circulo" ? $offset : 0; $i < count($res) && $i<$offset+$per_page; $i++): ?>
    <?php if($shape == "circulo") echo $i+1; else echo $offset+$i+1;
    ?>)<br>
    <div  class='resultados'>
      <div class='miniatura' >
        <center>
          <img id="<?php echo $res[$i]["nombre"] ?>" onclick='showImagesPolygon("<?php echo $res[$i]["yyyy"] ?>","<?php echo $res[$i]["mmmm"] ?>","<?php echo $res[$i]["satelite"] ?>")' height='60' width='60' src='<?php echo $dir_imgs. $res[$i]["nombre"] ?>quickview.jpg'/>
        </center>
      </div>
      <div class='info'>
        <b><?php echo $lngarr['date'] ?>:</b> <?php echo $meses[$res[$i]["mmmm"]]." ".$res[$i]["yyyy"] ?><br>
        <b><?php echo $lngarr['catalog'] ?></b>: <?php echo $res[$i]["satelite"] ?><br>
        <b><?php echo $lngarr['numberimages'] ?></b>: <?php echo $res[$i]["numero"] ?>
      </div>
      <div class='botones'>
        <?php if(in_array($res[$i]["nombre"],$polis)):  ?>
          <button type='button'  onclick='polygonImagesToMap(this,"<?php echo $res[$i]["yyyy"] ?>","<?php echo $res[$i]["mmmm"] ?>","poligono","<?php echo $res[$i]["satelite"] ?>")' class='btn btn-secondary btn-xs'><span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span> <?php echo $lngarr['hidepoly'] ?></button>
        <?php else: ?>
          <button type='button'  onclick='polygonImagesToMap(this,"<?php echo $res[$i]["yyyy"] ?>","<?php echo $res[$i]["mmmm"] ?>","poligono","<?php echo $res[$i]["satelite"] ?>")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span> <?php echo $lngarr['polygon'] ?></button>
        <?php endif; ?>
        <?php if(in_array($res[$i]["nombre"],$overlaps)):  ?>
          <button type='button'   onclick='polygonImagesToMap(this,"<?php echo $res[$i]["yyyy"] ?>","<?php echo $res[$i]["mmmm"] ?>","image","<?php echo $res[$i]["satelite"] ?>")' class='btn btn-secondary btn-xs'><span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span></button>
        <?php else: ?>
          <button type='button'   onclick='polygonImagesToMap(this,"<?php echo $res[$i]["yyyy"] ?>","<?php echo $res[$i]["mmmm"] ?>","image","<?php echo $res[$i]["satelite"] ?>")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-picture' aria-hidden='true'></span></button>
        <?php endif; ?>
        <span id="btn<?php echo $res[$i]["yyyy"].$res[$i]["mmmm"].$res[$i]["satelite"] ?>">
          <?php if(array_key_exists($res[$i]["yyyy"].$res[$i]["mmmm"].$res[$i]["satelite"],$todownload)):  ?>
            <button type='button' onclick='checkSession("addToCarPolygon","<?php echo $res[$i]["yyyy"] ?>","<?php echo $res[$i]["mmmm"] ?>","remove","<?php echo $res[$i]["satelite"] ?>")' class='btn btn-danger btn-xs'> <?php echo $lngarr['removedown'] ?> </button>
          <?php else: ?>
            <button type='button'  onclick='checkSession("addToCarPolygon","<?php echo $res[$i]["yyyy"] ?>","<?php echo $res[$i]["mmmm"] ?>","add","<?php echo $res[$i]["satelite"] ?>")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span> <?php echo $lngarr['descdwbtn'] ?></button>
          <?php endif; ?>
        </span>


      </div>
    </div>
    <hr class='linea'>
  <?php endfor;  ?>
  </div>

  <?php
  paginate($page, $total_pages, $adjacents,"getResults");
}

/**
* MUESTRA LOS RESULTADOS DE LAS IMÁGENES CUANDO LA BUSQUEDA SE REALIZA POR SOLAPAMIENTOS
*/
function results_overlaps($res,$polis,$number_res,$per_page,$offset,$height,$adjacents,$page,$shape){
  $idioma = $_SESSION["lang"];
  $lngarr = PageManagment::getLanguage($idioma);
  $todownload =  isset($_SESSION['descargas']) ? $_SESSION['descargas'] : array();
  $total_pages = ceil($number_res/$per_page);
  //$dir_imgs = "resources/".Route::getRoute("repo")[0]['route']."/".Route::getRoute("mins")[0]['route']."/";
  $repo = Route::getRoute("repo");
  $mins = Route::getRoute("mins");
  $dir_imgs = "resources/".$repo[0]['route']."/".$mins[0]['route']."/";
  if(count($res)==0):?>
  <br>
    <div class='resultadosbusqueda'>
      <br>
      <?php echo $lngarr['noresults'] ?>
    </div>
  <?php endif; ?>

  <div id="resultadosbusqueda" class="resultadosbusqueda"  style="height:<?php echo $height - 250; ?>px;" >
  <?php
  for ($i=$shape == "circulo" ? $offset : 0; $i < count($res) && $i<$offset+$per_page; $i++): ?>
    <?php if($shape == "circulo") echo $i+1; else echo $offset+$i+1;
    if(!$res[$i]["numero"]){
      #print_r($_POST);
      $res[$i]["numero"] = getNumberImagesOverlaps($res[$i]["path"],$res[$i]["row"],$_POST['satelites']);
      $res[$i]["numero"] = $res[$i]["numero"][0][0];
      #echo "xx".$res[$i]["numero"];
    }
    ?>
    )<br>
    <div  class='resultados'>
      <div class='miniatura'  style="min-height:100px">
        <center>
          <img id="<?php echo $res[$i]["nombre"] ?>" onclick='showImagesGroup("<?php echo $res[$i]["path"] ?>","<?php echo $res[$i]["row"] ?>","<?php echo $res[$i]["satelite"] ?>")' height='60' width='60' src='<?php echo $dir_imgs. $res[$i]["nombre"] ?>quickview.jpg'/>
        <center>
      </div>
      <div class='info'  style="min-height:100px">
        <b><?php echo $lngarr['path'] ?></b>: <?php echo $res[$i]["path"] ?> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b><?php echo $lngarr['row'] ?></b>:<?php echo $res[$i]["row"] ?><br>
        <b><?php echo $lngarr['newest'] ?>:</b> <?php echo $res[$i]["newest"] ?><br>
        <b><?php echo $lngarr['oldest'] ?>:</b> <?php echo $res[$i]["oldest"] ?><br>
        <b><?php echo $lngarr['catalog'] ?></b>: <?php echo $res[$i]["satelite"] ?><br>
        <b><?php echo $lngarr['numberimages'] ?></b>: <?php echo $res[$i]["numero"] ?><br>
        <b><?php echo $lngarr['placew'] ?></b>: <?php echo $res[$i]["place"] ?>
      </div>
      <div class='botones'>
        <?php if(in_array($res[$i]["hash_name"],$polis)):  ?>
          <button type='button' onclick='polygonToMap(this,"<?php echo $res[$i]["hash_name"] ?>","view_polygon_overlap")' class='btn btn-secondary btn-xs'><span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span> <?php echo $lngarr['hidepoly'] ?></button>
        <?php else: ?>
          <button type='button'  onclick='polygonToMap(this,"<?php echo $res[$i]["hash_name"] ?>","view_polygon_overlap")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span> <?php echo $lngarr['polygon'] ?></button>
        <?php endif; ?>

        <span id="btn<?php  echo $res[$i]["path"]."_".$res[$i]["row"]."_".$res[$i]["satelite"]; ?>">
          <?php if(array_key_exists($res[$i]["path"]."_".$res[$i]["row"]."_".$res[$i]["satelite"],$todownload)):  ?>
            <button type='button' onclick='checkSession("addToCarOverleap","<?php echo $res[$i]["nombre"] ?>","<?php echo $res[$i]["path"] ?>","<?php echo $res[$i]["row"] ?>","<?php echo $res[$i]["satelite"] ?>","remove")' class='btn btn-danger btn-xs'> <?php echo $lngarr['removedown'] ?> </button>
          <?php else: ?>
            <button type='button'  onclick='checkSession("addToCarOverleap","<?php echo $res[$i]["nombre"] ?>","<?php echo $res[$i]["path"] ?>","<?php echo $res[$i]["row"] ?>","<?php echo $res[$i]["satelite"] ?>","add")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span> <?php echo $lngarr['descdwbtn'] ?> </button>
          <?php endif; ?>
        </span>
      </div>
    </div>
    <hr class='linea'>
  <?php endfor;  ?>
  </div>

  <?php
  paginate($page, $total_pages, $adjacents,"getResults");
}

/**
* MUESTRA LOS RESULTADOS DE LAS IMÁGENES CUANDO LA BUSQUEDA SE REALIZA POR RESULTADOS INDIVIDUALES
*/
function results_imgs($res,$polis,$overlaps,$number_res,$per_page,$offset,$height,$adjacents,$page,$idbusqueda,$shape){
  $idioma = $_SESSION["lang"];
  $lngarr = PageManagment::getLanguage($idioma);
  $image = new Images();
  $todownload =  isset($_SESSION['descargas']) ? $_SESSION['descargas'] : array();
  $total_pages = ceil($number_res/$per_page);
  $i = 0;
  //$dir_imgs = "resources/".Route::getRoute("repo")[0]['route']."/".Route::getRoute("mins")[0]['route']."/";
  $repo = Route::getRoute("repo"); 
  $mins = Route::getRoute("mins");
  $dir_imgs = "resources/".$repo[0]['route']."/".$mins[0]['route']."/";
  if(count($res)==0):?>
  <br>
    <div class='resultadosbusqueda'>
      <br>
      <?php echo $lngarr['noresults'] ?>
    </div>
  <?php endif; ?>

  <div id="resultadosbusqueda" class="resultadosbusqueda"  style="height:<?php echo $height - 250; ?>px;" >
  <?php
  for ($i=$shape == "circulo" ? $offset : 0; $i < count($res) && $i<$offset+$per_page; $i++):?>
    <?php if($shape == "circulo") echo $i+1; else echo $offset+$i+1;
    ?>)<br>
    <div  class='resultados item'>
      <div class='miniatura'>
        <div class="imagen_res">
          <center>
            <img onclick='showImage("<?php echo $res[$i]["hash_name"] ?>")' height='60' width='60' src='<?php echo $dir_imgs. $res[$i]["nombre"] ?>quickview.jpg'/>
          </center>
        </div>
        <div class="likes">
          <?php for ($j=1; $j <= 5; $j++):
            if($j <= intval($res[$i]["rating"])): ?>
              <button id="btnStar<?php echo $res[$i]["id"].$j ?>" onclick='checkSession("rate",this,"<?php echo $res[$i]['id'] ?>",<?php echo $j ?>)' type="button" class="btn btn-default btn-xs">
                <span class="glyphicon glyphicon-star" aria-hidden="true"></span>
              </button>
            <?php else: ?>
              <button id="btnStar<?php echo $res[$i]["id"].$j ?>" onclick='checkSession("rate",this,"<?php echo $res[$i]['id'] ?>",<?php echo $j ?>)' type="button" class="btn btn-default btn-xs">
                <span class="glyphicon glyphicon-star-empty" aria-hidden="true"></span>
              </button>
          <?php endif;
            endfor; ?>
        </div>
      </div>
      <div class='info'>
        <b><?php echo $lngarr['id'] ?>: </b><a href="element.php?elemento=<?php echo $res[$i]['hash_name']?>&busqueda=<?php echo $idbusqueda; ?>"><?php echo $res[$i]['nombre']; ?></a><br>
        <b><?php echo $lngarr['path'] ?></b>: <?php echo $res[$i]["path"] ?> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b><?php echo $lngarr['row'] ?></b>:<?php echo $res[$i]["row"] ?><br>
        <b><?php echo $lngarr['date'] ?>:</b> <?php echo $res[$i]["date"] ?><br>
        <b><?php echo $lngarr['catalog'] ?></b>: <?php echo $res[$i]["satelite"] ?><br><br>
        <b><?php echo $lngarr['placew'] ?></b>: <?php echo $res[$i]["place"] ?>
      </div>
      <div class='botones'>
        <button type='button' id="btnShowProducts<?php echo $res[$i]["nombre"] ?>"   onclick='verProducts("<?php echo $res[$i]["id"] ?>","<?php echo $res[$i]["nombre"] ?>")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-globe' aria-hidden='true'></span> <?php echo $lngarr['products'] ?></button>
        <?php if(in_array($res[$i]["hash_name"],$polis)):  ?>
          <button type='button' onclick='polygonToMap(this,"<?php echo $res[$i]["hash_name"] ?>","view_polygon")' class='btn btn-secondary btn-xs'><span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span><?php echo $lngarr['hidepoly'] ?></button>
        <?php else: ?>
          <button type='button' onclick='polygonToMap(this,"<?php echo $res[$i]["hash_name"] ?>","view_polygon")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span> <?php echo $lngarr['polygon'] ?></button>
        <?php endif; ?>
        <?php if(in_array($res[$i]["hash_name"],$overlaps)):  ?>
          <button type='button' id="btnShowImgMap<?php echo $res[$i]["id"] ?>" title="<?php echo $lngarr['hideimg'] ?>" onclick='imageToMap(this,"<?php echo $res[$i]["hash_name"] ?>","view_image_on_map")' class='btn btn-secondary btn-xs'><span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span></button>
        <?php else: ?>
          <button type='button' id="btnShowImgMap<?php echo $res[$i]["id"] ?>" title="<?php echo $lngarr['descimgbtn'] ?>" onclick='imageToMap(this,"<?php echo $res[$i]["hash_name"] ?>","view_image_on_map")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-picture' aria-hidden='true'></span></button>
        <?php endif; ?>
        <button type='button' title="<?php echo $lngarr['descmetbtn'] ?>" onclick='verMeta("<?php echo $res[$i]["hash_name"] ?>")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-file' aria-hidden='true'></span></button>
        <span id="btn<?php echo $res[$i]["nombre"] ?>">
          <?php if(array_key_exists($res[$i]["nombre"],$todownload)):  ?>
            <button title="<?php echo $lngarr['removedown'] ?>" type='button'  onclick='checkSession("addToCar","<?php echo $res[$i]["nombre"] ?>","remove")' class='btn btn-danger btn-xs'> <?php echo $lngarr['removedown'] ?></button>
          <?php else: ?>
            <button title="<?php echo $lngarr['descdwbtn'] ?>" type='button'  onclick='checkSession("addToCar","<?php echo $res[$i]["nombre"] ?>","add")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span></button>
          <?php endif; ?>
       </span>
       <button type='button' title="<?php echo $lngarr['desccopbtn'] ?>"  class='btn btn-info btn-xs'><span class='glyphicon glyphicon-copy' aria-hidden='true'></span></button>
      </div>
    </div>

  <?php endfor;  ?>
  </div>
  <?php
  if($page > 0){
    paginate($page, $total_pages, $adjacents,"getResults");
  }
}
?>
