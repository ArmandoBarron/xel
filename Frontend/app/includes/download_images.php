<?php
set_time_limit(0);
include_once("../resources/conf.php");
include_once(SESIONES);
//INICIA LA SESIÓN
Sessions::startSession("buscador");
include_once(CLASES . "/class.Route.php");
include_once(CLASES . "/class.Logs.php");

if(!isset($_SESSION['descargasAnt'])){
  $_SESSION['descargasAnt'] = array();
}

if(isset($_SESSION['descargas']) && count($_SESSION['descargas']) > 0){
  $imgs_names = $_SESSION['descargas'];
  $repo = Route::getRoute("repo");
  $imgs = Route::getRoute("imgs");
  $meta = Route::getRoute("meta");
  $tars = Route::getRoute("tars");
  $dir_imgs = $config["paths"]["resources"] . "/" . $repo[0]['route'] ."/". $imgs[0]['route'] . "/";
  $dir_meta_base = $config["paths"]["resources"] . "/" . $repo[0]['route'] . "/" . $meta[0]['route']."/";
  $dir_meta_landsat = $dir_meta_base."Report.PAR/";
  $dir_meta = $dir_meta_base."map.reference/";
  $routedownload = "resources/".$tars."/";
  $folder =  $config["paths"]["resources"] . "/" .$tars[0]['route']."/";

  $onlyjpgs = $config["paths"]["resources"] . "/" . $repo[0]['route']  . '/493c51eac801368a6bd65f974b313859/onlyjpg/';
  $onlymeta = $config["paths"]["resources"] . "/" . $repo[0]['route'] . '/493c51eac801368a6bd65f974b313859/onlymeta/';
  $both = $config["paths"]["resources"] . "/" . $repo[0]['route'] . '/493c51eac801368a6bd65f974b313859/both/';

  $filename = "imagenes".date('m-d-Y_hia');

  if(file_exists($folder.$filename.'.tar.gz')){
    $filename .= rand(0,1000);
  }

  $final_tar = new PharData($folder.$filename.'.tar');

  foreach ($imgs_names as $key => $value) {
    $idbusqueda = isset($_SESSION['busqueda']) ? $_SESSION['busqueda'] : null;
    if($idbusqueda != null){
      $iddescarga = Logs::add_download($idbusqueda,true);
    }else{
      $iddescarga = Logs::add_download(0,false);
    }
    saveLog($value,$iddescarga);

    if($value['isfolder'] == "true"){ //SI LAS IMAGENES VAN EN UN SUBFOLDER
      $sub_tar = createTar($value['folder'],$folder);
      if($sub_tar != null){
        foreach ($value['imgs'] as $imgKey => $image) {
          $file_tar = $both.$image["id"].".tar.gz";
          addToFinalTar($file_tar, $image['id'],null,$sub_tar,$folder,$value['folder']);

          Logs::add_download_image($iddescarga,$image["id"]);
        }
        $metadatatar = $sub_tar->getMetadata();
        $fileU = $folder.$metadatatar['name'].".tar";
        addToFinalTar($fileU, $metadatatar['name'].".tar",null,$final_tar,$folder);
        //echo $folder.$value['folder']."tar.gz";
        //addToFinalTar($sub_tar,$final_tar,$folder);
      }
    }else{
      try{
        //addImageToTar($value["opciones"],$value["id"],$sub_tar,$dir_imgs);
        //addMetaToTar($value["opciones"],$value["id"],$sub_tar,$dir_meta_landsat,$dir_meta);
        $file_tar = "";
        if(in_array("jpg",$value["opciones"]) && in_array("meta",$value["opciones"])){
          $file_tar = $both.$value["id"].".tar.gz";
        }else if(in_array("jpg",$value["opciones"])){
          $file_tar = $onlyjpgs.$value["id"].".tar.gz";
        }else if(in_array("meta",$value["opciones"])){
          $file_tar = $onlymeta.$value["id"].".tar.gz";
        }
        addToFinalTar($file_tar, $value['id'],null,$final_tar,$folder);
      }catch(Exception $e){
        echo $e->getMessage();
      }
      Logs::add_download_image($iddescarga,$value["id"]);
    }
  }

  $final_tar->compress(Phar::GZ);
  //unlink($folder.$filename.'.tar');
  $url = $routedownload.$filename.'.tar.gz';
  $_SESSION['urlAnt'] = $url;
  $_SESSION['descargasAnt'] = $_SESSION['descargas'];
  echo $url;
}

function addToFinalTar($file_tar, $file, $tar,$final_tar,$folder,$subfolder=""){
  $final_tar->addFile($file_tar,$subfolder.$file."tar.gz");
}

function addMetaToTar($opciones,$image,$tar,$dir_meta_landsat,$dir_meta){
  if(in_array("meta",$opciones)){
    if(substr($image, 0, 3) === "CHM" || substr($image, 0, 2) === "LC"){
      if(file_exists($dir_meta_landsat.$image."Report.PAR")){
        $tar->addFile($dir_meta_landsat.$image."Report.PAR",$image."Report.PAR");
      }
    }else{
      if(file_exists($dir_meta.$image."map.reference")){
        $tar->addFile($dir_meta.$image."map.reference",$image."map.reference");
      }
    }
  }
}

function addImageToTar($opciones,$image,$tar,$dir_imgs){
  if(in_array("jpg",$opciones)){
    if(file_exists($dir_imgs.$image.".jpg")){
      try{
        $tar->addFile($dir_imgs.$image.".jpg",$image.".jpg");
      }catch(Exception $e){
        echo $e->getMessage();
      }
    }
  }
}

function createTar($prov_name,$folder){
  try{
    $tar_name = $prov_name.date('m-d-Y_hia').rand(0,1000);
    $sub_tar = new PharData($folder.$tar_name.'.tar');
    $sub_tar->setMetadata(array('name' => $tar_name));
    return $sub_tar;
  }catch(Exception $e){
    echo  $e->getMessage();
  }
  return null;
}

function saveLog($item,$iddescarga){
  if($item["type"] == "overleap"){
    Logs::add_download_overleap($iddescarga,$item["path"],$item["row"]);
  }else if($item["type"] == "polygon"){
    Logs::add_download_polygon($iddescarga,$item["month"],$item["year"]);
  }
}
?>
