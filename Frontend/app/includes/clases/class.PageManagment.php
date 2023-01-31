<?php
include_once("class.Route.php");

class PageManagment{
  /**
  * CARGA EL HEADER HTML DE LA PÁGINA CON TODAS LAS INCLUSIONES CSS
  */
  public static function loadHTMLHeader($pagename){
    require_once(TEMPLATES . "/html_header.php");
  }

  public static function getLanguage($ln){
    $string = file_get_contents(LANGS);
    $json_a = json_decode($string, true);
    $lngarr = $json_a[$ln];
    return $lngarr;
  }

  /**
  * CARGA EL ARCHIVO ESPECIFICADO
  */
  public static function loadHTMLFile($file){
    global $lngarr;
    require_once(TEMPLATES . "/$file.php");
  }

  /**
  * CARGA LOS MODALES
  */
  public static function loadModals($loginUrl){
    global $lngarr;
    require_once(TEMPLATES . "/modales.php");
  }

  /**
  * CARGA LOS COMENTARIOS
  */
  public static function loadComments($element){
    global $lngarr;
    require_once(TEMPLATES . "/comentarios.php");
  }

  /**
  * CARGA LOS BREADCRUMBS
  */
  public static function loadBreadcrumbs($ancestors,$res,$idbusqueda){
    global $lngarr;
    require_once(TEMPLATES . "/breadcrumbs.php");
  }

  /**
  * CARGA EL CONTENIDO DE UN ELEMENTOS
  */
  public static function loadContentElement($tipo,$element,$res){
    global $lngarr;
    require_once(TEMPLATES . "/content_element.php");
  }

  /**
  * CARGA LA INFORMACIÓN DEL ELEMENTO ESPECIFICADO
  */
  public static function loadElement($element,$user){
    require_once(TEMPLATES . "/element.php");
  }

  /**
  * MUESTRA LA MINIATURA DE LA IMAGEN
  */
  public static function showMiniature($imgname,$hash,$dir_imgs,$id_recomendacion){
    echo "<div class='imagen_res'>
    <center>
    <img id='$imgname' onclick='showImage(\"$hash\",true,\"$id_recomendacion\")' height='60' width='60' src='".$dir_imgs.$imgname."quickview.jpg'/>
    </center>
    </div>";
  }

  /**
  * MUESTRA LAS ESTRELLAS QUE TIENE UNA IMAGEN
  */
  public static function showStars($calification,$idimg){
    echo "<div  class='likes'>";
    for ($i=1; $i <= 5; $i++) {
      if($i < $calification){
        $class = "glyphicon glyphicon-star";
      }else{
        $class = "glyphicon glyphicon-star-empty";
      }
      echo "<button id='btnStar".$idimg.$i."' onclick='checkSession(\"rate\",this,\"$idimg\",\"$i\",true)' type='button' class='btn btn-default btn-xs'><span class='$class' aria-hidden='true'></span></button>";
    }
    echo "</div>";
  }

  public static function showInfoImage($img){
    global $lngarr;
    echo "<div class='info'>
    <b>".$lngarr['id'].": </b><a href='element.php?elemento=".$img['hash_name']."'>".$img['nombre']."</a><br>
    <b>".$lngarr['path']."</b>: ".$img['path']." &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>".$lngarr['row']."</b>:".$img['row']."<br>
    <b>".$lngarr['date'].":</b> ".$img['date']."<br>
    <b>".$lngarr['catalog']."</b>:".$img['satelite']."
    </div>";
  }

  public static function showButtons($img,$showpoly,$showoverlap,$todownload,$id_recomendacion){
    global $lngarr;
    echo "<div class='botones'>";
    echo "<button type='button' id='btnShowProducts".$img['nombre']."'   onclick='verProducts(\"".$img['id']."\",\"".$img['nombre']."\")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-globe' aria-hidden='true'></span> ".$lngarr['products']."</button>";
    if($showpoly){
      $text = $lngarr['hidepoly'];
      $class = 'glyphicon glyphicon-eye-close';
    }else{
      $text = $lngarr['polygon'];
      $class = 'glyphicon glyphicon-eye-open';
    }
    echo "&nbsp&nbsp<button type='button' onclick='polygonToMap(this,\"".$img['hash_name']."\",\"view_polygon\",true,\"$id_recomendacion\")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span>$text</button>";
    if($showoverlap){
      $text = $lngarr['hideimg'];
      $class = 'glyphicon glyphicon-eye-close';
    }else{
      $text = $lngarr['descimgbtn'];
      $class = 'glyphicon glyphicon-picture';
    }
    echo "&nbsp&nbsp<button type='button' title='$text' onclick='imageToMap(this,\"".$img['hash_name']."\",\"view_image_on_map\",true,\"$id_recomendacion\")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-picture' aria-hidden='true'></span></button>";
    echo "&nbsp&nbsp<button type='button' title='".$lngarr['descmetbtn']."' onclick='verMeta(\"".$img['hash_name']."\",true,\"$id_recomendacion\")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-file' aria-hidden='true'></span></button>";
    if($todownload){
      $text = $lngarr['removedown'];
      $class = 'glyphicon glyphicon-minus';
      $action = "remove";
    }else{
      $text = $lngarr['descdwbtn'];
      $class = 'glyphicon glyphicon-plus';
      $action = "add";
    }
    
    echo "&nbsp&nbsp<button title='$text' type='button'  onclick='checkSession(\"addToCar\",\"".$img['nombre']."\",\"".$action."\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span></button>";
    echo "</div>";
  }

  /**
  * MUESTRA LAS IMAGENES DEL PANEL DERECHO
  **/
  public static function rightPanelImages($arr,$id_recomendacion){
    //OBTIENE LAS RUTAS DE LAS MINIATURAS
    $route_repo = Route::getRoute("repo");
    $route_mins = Route::getRoute("mins");
    
    $dir_imgs = "resources/".$route_repo[0]['route']."/".$route_mins[0]['route']."/";
    $todownload = isset($_SESSION['descargas']) ? $_SESSION['descargas'] : array(); //IMAGENES A DESCARGAR
    $n_imgs = count($arr);

    if($n_imgs == 0){
      echo "<div class='resultadosbusqueda'>La busqueda no ha producido resultados.</div>";
    }else{
      echo '<div class="resultadosbusqueda">';
      foreach ($arr as $key => $img) {
        echo "<div  class='resultados item'>";
        echo "<div  class='miniatura'>";
        PageManagment::showMiniature($img['nombre'],$img['hash_name'],$dir_imgs,$id_recomendacion);
        #print_r($img);
        #PageManagment::showStars($img['rating'],$img['id']);
        echo "</div>";
        PageManagment::showInfoImage($img);
        PageManagment::showButtons($img,false,false,false,$id_recomendacion);
        echo "</div>";
      }
      echo '</div>';
    }
  }

  /**
  * MUESTRA LOS SOLAPAMIENTOS EN PANEL DERECHO
  **/
  public static function rightPanelOverlaps($arr,$id_recomendacion){
    global $lngarr;
    //OBTIENE LAS RUTAS DE LAS MINIATURAS
    $route_repo = Route::getRoute("repo");
    $route_mins = Route::getRoute("mins");
    
    $dir_imgs = "resources/".$route_repo[0]['route']."/".$route_mins[0]['route']."/";

    //$dir_imgs = "resources/".Route::getRoute("repo")[0]['route']."/".Route::getRoute("mins")[0]['route']."/";
    $todownload = isset($_SESSION['descargas']) ? $_SESSION['descargas'] : array(); //IMAGENES A DESCARGAR
    $n_imgs = count($arr);

    if($n_imgs == 0){
      echo "<div class='resultadosbusqueda'>".$lngarr['noresults']."</div>";
    }else{
      echo '<div class="resultadosbusqueda">';
      foreach ($arr as $key => $img) {
        echo "<div  class='resultados item'>";
        echo "<div  class='miniatura'>";
        echo "<div class='imagen_res'>
        <center>
        <img id='".$img['nombre']."' onclick='showImagesGroup(\"".$img['path']."\",\"".$img['row']."\",\"".$img['satelite']."\",1,$id_recomendacion)' height='60' width='60' src='".$dir_imgs.$img['nombre']."quickview.jpg'/>
        </center>
        </div>";
        echo "</div>";
        echo "<div class='info'>
        <b>".$lngarr['path']."</b> : ".$img['path']." &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>".$lngarr['row']."</b> :".$img['row']."<br>
        <b>".$lngarr['newest'].": </b> ".$img['newest']."<br>
        <b>".$lngarr['oldest'].": </b> ".$img['oldest']."<br>
        <b>".$lngarr['catalog']."</b>: ".$img['satelite']."<br>
        <b>".$lngarr['numberimages']."</b>: ".$img['numero']."<br>
        <b>".$lngarr['placew']."</b>: ".$img['place']."
        </div>";
        echo "<div class='botones'>";

        /*if($showpoly){
          $text = $lngarr['hidepoly'];
          $class = 'glyphicon glyphicon-eye-close';
        }else{*/
          $text = $lngarr['polygon'];
          $class = 'glyphicon glyphicon-eye-open';
        //}

        echo "&nbsp&nbsp<button type='button' onclick='polygonToMap(this,\"".$img['hash_name']."\",\"view_polygon\",true,\"$id_recomendacion\")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span>$text</button>";
        if(array_key_exists($img["path"]."_".$img["row"]."_".$img["satelite"],$todownload)){
          $text = $lngarr['removedown'];
          $class = 'glyphicon glyphicon-minus';
          $classB = 'btn btn-danger btn-xs';
          $action = "remove";
        }else{
          $text = $lngarr['descdwbtn'];
          $class = 'glyphicon glyphicon-plus';
          $classB = 'btn btn-default btn-xs';
          $action = "add";
        }

        echo "&nbsp&nbsp<span id='btn".$img['path']."_".$img['row']."_".$img['satelite']."'><button title='$text' type='button'  onclick='checkSession(\"addToCarOverleap\",\"".$img['nombre']."\",\"".$img['path']."\",\"".$img['row']."\",\"".$img['satelite']."\",\"".$action."\")' class='$classB'><span class='$class' aria-hidden='true'></span>$text</button></span>";
        echo "</div>";
        echo "</div>";
      }
      echo '</div>';
    }
  }

  public static function rightPanelPolys($arr,$id_recomendacion){
    global $lngarr;
    $route_repo = Route::getRoute("repo");
    $route_mins = Route::getRoute("mins");
    
    $dir_imgs = "resources/".$route_repo[0]['route']."/".$route_mins[0]['route']."/";

    // $dir_imgs = "resources/".Route::getRoute("repo")[0]['route']."/".Route::getRoute("mins")[0]['route']."/";
    $todownload = isset($_SESSION['descargas']) ? $_SESSION['descargas'] : array(); //IMAGENES A DESCARGAR
    $n_imgs = count($arr);
    $meses = $lngarr["months"];
    if($n_imgs == 0){
      echo "<div class='resultadosbusqueda'>".$lngarr['noresults']."</div>";
    }else{
      echo '<div class="resultadosbusqueda">';
      foreach ($arr as $key => $img) {
        if(count($img) > 0){
          $img = $img[0];
          echo "<div  class='resultados item'>";
          echo "<div  class='miniatura'>";
          echo "<div class='imagen_res'>
          <center>
          <img id='".$img['nombre']."' onclick='showImagesPolygon(\"".$img['yyyy']."\",\"".$img['mmmm']."\",\"".$img['satelite']."\",true,$id_recomendacion)' height='60' width='60' src='".$dir_imgs.$img['nombre']."quickview.jpg'/>
          </center>
          </div>";
          echo "</div>";
          echo "<div class='info'>
          <b>".$lngarr['date']."</b> : ".$meses[$img["mmmm"]]."  ".$img["yyyy"]."<br>
          <b>".$lngarr['catalog']."</b>: ".$img['satelite']."<br>
          <b>".$lngarr['numberimages']."</b>: ".$img['numero']."
          </div>";
          echo "<div class='botones'>";


          $text = $lngarr['polygon'];
          $class = 'glyphicon glyphicon-eye-open';
          
          echo "&nbsp&nbsp<button type='button' onclick='polygonImagesToMap(this,\"".$img['yyyy']."\",\"".$img['mmmm']."\",\"poligono\",\"".$img['satelite']."\",true,$id_recomendacion)' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span>$text</button>";


          $text = $lngarr['descimgbtn'];
          $class = 'glyphicon glyphicon-picture';
          
          echo "&nbsp&nbsp<button type='button' title='$text' onclick='polygonImagesToMap(this,\"".$img['yyyy']."\",\"".$img['mmmm']."\",\"image\",\"".$img['satelite']."\",true,$id_recomendacion)' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-picture' aria-hidden='true'></span></button>";
          #print_r($img);
          /*if(array_key_exists($img["path"]."_".$img["row"]."_".$img["satelite"],$todownload)){
            $text1 = $lngarr['removedown'];
            $class = 'glyphicon glyphicon-minus';
            $classB = 'btn btn-danger btn-xs';
            $action = "remove";
          }else{*/
            $text1 = $lngarr['descdwbtn'];
            $class = 'glyphicon glyphicon-plus';
            $classB = 'btn btn-default btn-xs';
            $action = "add";
          //}
          
          echo "&nbsp&nbsp<span id='btn".$img['yyyy'].$img['mmmm'].$img['satelite'].
          "'><button title='$text' type='button'  onclick='checkSession(\"addToCarPolygon\",\"".
          $img['yyyy']."\",\"".$img['mmmm']."\",\"$action\",\"".$img['satelite']."\",true,$id_recomendacion)' class='$classB'><span class='$class' aria-hidden='true'></span>$text1</button></span>";
          echo "</div>";
          echo "</div>";
        }
      }
      echo '</div>';
    }
  }
}
?>
