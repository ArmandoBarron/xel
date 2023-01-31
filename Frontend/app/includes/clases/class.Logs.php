<?php
include_once("class.DB.php");
class Logs{

	public static $types_clics = array('view_image'  => 1,'view_products' => 2,'view_polygon' => 3,
		'view_image_on_map' => 4,'view_metadata' => 5,
		'view_polygon_poly' => 6,
		'view_image_on_map_poly' => 7,
		'view_polygon_overlap' => 8,"gallery_overlap" => 9,
		"gallery_poly" => 10, "download_poly" => 11, 
		"download_overlap" => 12);

  /**
  * REGISTRA UNA SESIÓN
  * @return ID DE LA SESIÓN
  */
  public static function saveSession($user,$ip,$lat,$lon,$locByIp){
  	try{
  		$conn = new DB();
  		$sql = "INSERT INTO sesiones(iduser,ip,lat,lon,locationbyip) 
  		VALUES(:user,:ip,:lat,:lon,:locationbyip) returning idsesion";
  		$data = array("user" => $user, "ip" => $ip, "lat" => $lat, "lon" => $lon,"locationbyip" => $locByIp);
  		$res = $conn->executeQuery($sql,$data);
                return $res[0][0];
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  	}
  }

  public static function getTypes($type){
  	try{
  		$conn = new DB();
  		$sql = "SELECT idtype from typeofsearch where tipo = '$type'";
  	        $res = $conn->executeQuery($sql);
                return $res[0][0];
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  		return -1;
  	}
  }

  public static function save_search($usuario,$date1,$date2,$filtro,$type,$show_products,$id_session){
  	$type = Logs::getTypes($type);
  	if($type < 0)
  		return -1;
  	try{
  		$conn = new DB();
  		if(strlen($date1) > 0 && strlen($date2) > 0 || $date1 != $date2){
  			$data = array('tipo' => $type , 'fecha_inicial' => $date1, 'fecha_final' => $date2, 'user' => $usuario, 'filtro' => $filtro, 'derivados' => $show_products,"sesion" => $id_session);
  		}
  		else{
  			$data = array('tipo' => $type , 'fecha_inicial' => NULL, 'fecha_final' => NULL, 'user' => $usuario, 'filtro' => $filtro, 'derivados' => $show_products,"sesion" => $id_session);
  		}

  		$sql = "INSERT into busquedas(tipo,fecha_inicial,fecha_final,\"user\",filtro,derivados,sesion) values(:tipo,:fecha_inicial,:fecha_final,:user,:filtro,:derivados,:sesion)  RETURNING idbusqueda";
  		$idbusqueda = $conn->executeQuery($sql,$data);
                $idbusqueda = $idbusqueda[0][0];

  		$sql = "UPDATE busquedas SET hash_key = crypt(idbusqueda::text,gen_salt('xdes')) where idbusqueda = :idbusqueda RETURNING hash_key";
  		$data = array("idbusqueda" => $idbusqueda);
  		$hash = $conn->executeQuery($sql,$data);
                $hash = $hash[0][0];
  		return array("hash" => $hash,"idbusqueda" => $idbusqueda);
  	}catch(PODException $e){
  		echo "ERROR SAVE SEARCH";
  		echo $e->getMessage();
  		return -1;
  	}
  }

  public static function getIdSatelite($satelite){
  	try{
  		$conn = new DB();
  		$sql = "SELECT idelemento from elementos where UPPER(descriptor) = UPPER('$satelite') and typeofelement = 3";
  		$res = $conn->executeQuery($sql);
                return $res[0][0];
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  		return -1;
  	}
  }

  public static function save_satelite($idbusqueda,$satelites){
  	try{
  		$conn = new DB();
  		foreach ($satelites as $key => $value) {
  			$idsatelite = Logs::getIdSatelite($value);
  			$sql = "INSERT INTO busquedas_satelites(idbusqueda,idsatelite) VALUES($idbusqueda,$idsatelite)";
  			$conn->executeQuery($sql);
  		}
  		$conn->close_con();
  	}catch(PDOException $e){
  		echo "ERROR save_satelite";
  		echo  $e->getMessage();
  	}
  }

  public static function add_log_polygon($id_session,$usuario,$type,$poligono,$date1,$date2,$filtro,$satelites,$show_products){
  	try{

  		$searchdata = Logs::save_search($usuario,$date1,$date2,$filtro,$type,$show_products,$id_session);
  		$idbusqueda = $searchdata['idbusqueda'];
  		if($idbusqueda < 0){
  			echo "ERROR";
  			return;
  		}
  		$conn = new DB();
  		$sql = "INSERT into busquedabypolygon(idbusqueda,\"polygon\") values(:idbusqueda,$poligono)";
  		$data = array('idbusqueda' => $idbusqueda);
  		$conn->executeQuery($sql,$data);
  		Logs::save_satelite($idbusqueda,$satelites);
  		$polygon = str_replace("(","", $poligono);
  		$polygon = str_replace(")","", $polygon);
  		$polygon = str_replace("'","", $polygon);
  		$polygon = substr($polygon,7);
  		$coors = explode(",",$polygon);
  		$n = count($coors);
  		for($i=0;$i<$n;$i+=2){
        //$coors[$i] = $coor
  			$sql = "INSERT INTO poly_edges(idbusqueda,lat,lon) VALUES(:id,:lat,:lon)";
  			$data = array("id" => $idbusqueda,"lat" => $coors[$i+1],"lon" => $coors[$i]);
        //print_r($data);
  			$conn->executeQuery($sql,$data);
  		}
      //print_r($coors);
  		return $searchdata;
  	} catch(PDOException $e) {
  		echo "ERROR add_log_polygon";
  		echo  $e->getMessage();
  	}
  }


  public static function add_log_circle($id_session,$usuario,$type,$date1,$date2,$filtro,$center_lat,$center_lon,$radius,$satelites,$show_products){
  	try{
  		$searchdata = Logs::save_search($usuario,$date1,$date2,$filtro,$type,$show_products,$id_session);
  		$idbusqueda = $searchdata['idbusqueda'];
  		if($idbusqueda < 0){
  			echo "ERROR";
  			return;
  		}
  		$conn = new DB();
  		$sql = "INSERT into busquedabycircle(idbusqueda,center_lat,center_lon,radius) values('$idbusqueda','$center_lat','$center_lon','$radius')";
  		$conn->executeQuery($sql);
  		Logs::save_satelite($idbusqueda,$satelites);
  		return $searchdata;
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  	}
  }

  public static function add_log_point($id_session,$usuario,$type,$date1,$date2,$filtro,$lat,$lon,$satelites,$show_products,$city,$state,$country){
  	try{
  		$searchdata = Logs::save_search($usuario,$date1,$date2,$filtro,$type,$show_products,$id_session);
  		$idbusqueda = $searchdata['idbusqueda'];
  		if($idbusqueda < 0){
  			echo "ERROR";
  			return;
  		}
  		$conn = new DB();
  		$sql = "INSERT into busquedabypoint(idbusqueda,lat,lon,city,state,country) values(:idbusqueda,:lat,:lon,:city,:state,:country)";
  		$data = array("idbusqueda" => $idbusqueda, "lat" => $lat, "lon" => $lon, "city" => $city, "state" => $state, "country" => $country);
  		$conn->executeQuery($sql,$data);
  		Logs::save_satelite($idbusqueda,$satelites);
  		return $searchdata;
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  	}
  }

  public static function add_download($idbusqueda,$ishash=false){
  	try{
  		$conn = new DB();
  		if($ishash && $idbusqueda > 0){
  			$idbusqueda = Logs::getIdSearchFromHash($idbusqueda);
  		}else if($idbusqueda == 0){
  			$idbusqueda = NULL;
  		}
  		$sql = "INSERT into descargas(idbusqueda) values(:idbusqueda) RETURNING iddescarga";
  		$data = array("idbusqueda" => $idbusqueda);
  		$res =  $conn->executeQuery($sql,$data);
                return $res[0][0];
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  	}
  }

  public static function add_download_overleap($iddescarga,$path,$row){
  	try{
  		$conn = new DB();
  		$sql = "INSERT into downloadbyoverleap(iddescarga,\"path\",row) values('$iddescarga','$path','$row')";
  		$conn->executeQuery($sql);
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  	}
  }

  public static function add_download_polygon($iddescarga,$month,$year){
  	try{
  		$conn = new DB();
  		$sql = "INSERT into downloadbypolygon(iddescarga,month,year) values('$iddescarga','$month','$year')";
  		$conn->executeQuery($sql);
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  	}
  }

  public static function get_id_image($descriptor){
  	try{
  		$conn = new DB();
  		$sql = "SELECT idelemento from elementos where UPPER(descriptor) = UPPER('$descriptor')";
  		$res = $conn->executeQuery($sql);
		return $res[0][0];
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  		return -1;
  	}
  }

  public static function add_download_image($iddescarga,$descriptor){
  	try{
  		$idelemento = Logs::get_id_image($descriptor);
  		if($idelemento < 0){
  			echo "ERROR";
  			return;
  		}

  		$conn = new DB();
  		$sql = "INSERT INTO descargas_imagenes(iddescarga,idimagen) VALUES($iddescarga,$idelemento)";
  		$conn->executeQuery($sql);
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  	}
  }

  public static function getSats($idbusqueda){
  	try{
  		$conn = new DB();
  		$sql = "SELECT distinct descriptor FROM busquedas_satelites inner join elementos on idsatelite = idelemento where idbusqueda = :idbusqueda";
  		$data = array("idbusqueda" => $idbusqueda);
  		return $conn->executeQuery($sql,$data);
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  	}
  }

  public static function getSearch($idbusqueda,$ishash=false){
  	try{
  		$conn = new DB();
  		if($ishash){
  			$sql = "SELECT * FROM busquedas as b inner join busquedas_satelites as bs on b.idbusqueda = bs.idbusqueda where b.hash_key = :idbusqueda";
  		}else{
  			$sql = "SELECT * FROM busquedas as b inner join busquedas_satelites as bs on b.idbusqueda = bs.idbusqueda where bs.idbusqueda = :idbusqueda";
  		}
  		$data = array("idbusqueda" => $idbusqueda);
  		$busqueda = $conn->executeQuery($sql,$data);
  		$data["idbusqueda"] = $busqueda[0]['idbusqueda'];
  		switch (intval($busqueda[0]['tipo'])) {
  			case 1:
  			case 3:
  			$sql = "SELECT * FROM busquedabypolygon  where idbusqueda = :idbusqueda";
  			break;
  			case 2:
  			$sql = "SELECT * FROM busquedabycircle  where idbusqueda = :idbusqueda";
  			break;
  			case 4:
  			$sql = "SELECT * FROM busquedabypoint  where idbusqueda = :idbusqueda";
  			break;
  		}
  		$data = $conn->executeQuery($sql,$data);

  		return array("busqueda" => $busqueda, "data" => $data,"satelites" => Logs::getSats($busqueda[0]['idbusqueda']));
  	} catch(PDOException $e) {
  		echo  $e->getMessage();
  	}
  }

  /**
  * REGRESA EL ID DE LA BUSQUEDA A PARTIR DEL HASH
  */
  public static function getIdSearchFromHash($hash){
  	#print_r("xxxxx");
  	#print_r($hash);
  	$sql = "select idbusqueda from busquedas where hash_key = :hash";
  	$conn = new DB();
  	$data = array("hash" => $hash);
  	$id = $conn->executeQuery($sql,$data);
  	$id = $id[0][0];
	return $id;
  }

  /**
  * GUARDA UNA ACCION DE CLIC
  */
  public static function addClick($type,$image,$user,$rightP=false,$idreco){
  	$idreco = $idreco == -1 ? null:$idreco;
    //print_r("xxx".$type." ".self::$types_clics[$type]);
  	$rightP = ($rightP != true) ? "false" : "true";
  	$sql = "INSERT INTO clics(iduser,idimage,action,rightpanel,idrecomendacion) VALUES(:iduser,:idimage,:action,:rightpanel,:idrecomendacion)";
  	$data = array('iduser' => $user,'idimage' => $image,'action' => self::$types_clics[$type],"rightpanel" => $rightP,"idrecomendacion" => $idreco);
    //print_r($data);
  	$conn = new DB();
  	$conn->executeQuery($sql,$data);
  }

  public static function getSearcherNumber($user){
  	$sql = "select count(b.tipo),max(t.tipo) from busquedas as b inner join typeofsearch as t on b.tipo = idtype where b.user = :user group by b.tipo order by 1 desc";
  	$data = array("user" => $user);
  	$conn = new DB();
  	$res = $conn->executeQuery($sql,$data);
  	return $res;
  }

  public static function getSearcherWayNumber($user){
  	$sql = "select count(b.filtro),max(f.filtro) from busquedas as b inner join filtros as f on b.filtro = idfiltro where b.user = :user group by b.filtro order by 1 desc";
  	$data = array("user" => $user);
  	$conn = new DB();
  	$res = $conn->executeQuery($sql,$data);
  	return $res;
  }

  public static function getRecommendationsImgs($user){
  	$sql = "select fn_get_clicked_recom_imgs(:user) as clicked,
  	fn_get_recommended_img_number(:user) as cantidad;";
  	$data = array("user" => $user);
  	$conn = new DB();
  	$res = $conn->executeQuery($sql,$data);
  	return $res;
  }

  public static function getRecommendationsPolys($user){
  	$sql = "select fn_get_clicked_recom_polys(:user) as clicked,
  	fn_get_recommended_polys_number(:user) as cantidad;";
  	$data = array("user" => $user);
  	$conn = new DB();
  	$res = $conn->executeQuery($sql,$data);
  	return $res;
  }

  public static function getRecommendationsOverlaps($user){
  	$sql = "select fn_get_clicked_recom_overlaps(:user) as clicked,
  	fn_get_recommended_overlaps_number(:user) as cantidad;";
  	$data = array("user" => $user);
  	$conn = new DB();
  	$res = $conn->executeQuery($sql,$data);
  	return $res;
  }
}
?>
