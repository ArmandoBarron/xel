<?php
//148.247.204.7
// 148.247.201.211
function rrmdir($dir) {
   if (is_dir($dir)) {
     $objects = scandir($dir);
     foreach ($objects as $object) {
       if ($object != "." && $object != "..") {
         if (filetype($dir."/".$object) == "dir") rrmdir($dir."/".$object); else unlink($dir."/".$object);
       }
     }
     reset($objects);
     rmdir($dir);
   }
} 

if(isset($_POST['coordenadas']) && isset($_POST['startDate']) && isset($_POST['endDate'])){
  #$IP = "148.247.201.211"; #compute 8 
  $IP = "148.247.201.227"; #compute 6 
  #$IP = "148.247.204.6"; #local 
  $url = "http://".$IP.":5200/GraphStations";
  $start_date = $_POST['startDate'];
  $end_date = $_POST['endDate'];
  $start_date = date("d-m-Y", strtotime($start_date));
  $end_date = date("d-m-Y", strtotime($end_date));
  $polygon = $_POST['coordenadas'];
  $polygon_array = json_decode($polygon, true);
  $n_coors = count($polygon_array)-1;
  $K = $_POST['K'];
  $json_poly = "{";
  foreach($polygon_array as $index => $poly){
    $json_poly .= "\"".($index+1)."\":{\"lat\":\"".$poly["lat"]."\",\"lon\":\"".$poly["lon"]."\"}";
    #echo gettype($n_coors); 
    #echo gettype($index);
    //echo $n_coors == $index;
    if($n_coors != $index){
      $json_poly .= ",";
    }
  }
  $json_poly .= "}";
  //echo ".";
  //echo $json_poly;
  $polygon_array = json_decode($json_poly, true);
  $data = array("polygon" => $polygon_array, "inicio" => $start_date, "fin" => $end_date, "K" => $K);
  $data_string = json_encode($data);    
  $ch = curl_init($url);                                                                      
  curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");                                                                     
  curl_setopt($ch, CURLOPT_POSTFIELDS, $data_string);                                                                  
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);                                                                      
  curl_setopt($ch, CURLOPT_HTTPHEADER, array(                                                                          
    'Content-Type: application/json',                                                                                
    'Content-Length: ' . strlen($data_string))                                                                       
  );                                                                                                                                                         
  $result = curl_exec($ch);
  $temp = json_decode($result); 

  if (!file_exists('../static')) {
      mkdir("../static");
  }

  $verify = True;
  foreach ($temp as $reg) {
    foreach ($reg as $key => $value ) {  
    $str_arr = explode ("/", $value);
    $folderNumber=$str_arr[2];
    $img = file_get_contents("http://".$IP.":5200/".$value);
    if (!file_exists('../static/'.$str_arr[1])) {
      mkdir('../static/'.$str_arr[1]);
    }
    if (!file_exists('../static/'.$str_arr[1].'/'.$str_arr[2])) {
      mkdir('../static/'.$str_arr[1].'/'.$str_arr[2]);
    }
    else #Si existe la carpeta hay que borrarla y rehacerla
    {
      if(file_exists('../static/'.$str_arr[1].'/'.$str_arr[2]) && $verify==True){
        rrmdir('../static/'.$str_arr[1].'/'.$str_arr[2]);
        mkdir('../static/'.$str_arr[1].'/'.$str_arr[2]);
      }
    }
    $verify=False;
    file_put_contents('../static/'.$str_arr[1].'/'.$str_arr[2].'/'.$str_arr[3], $img);
    }

  }

  #crear ZIP
  $folder="../static/Zips/";
   if (!file_exists($folder)) {
      mkdir($folder);
    }

  $filename = "ImagesStations_".$folderNumber;
  $final_tar = new PharData($folder.$filename.'.tar');
  $target = "../static/plots/".$folderNumber."/";
  $final_tar -> buildFromDirectory($target);

  print_r($result);
}

