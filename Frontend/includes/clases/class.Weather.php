<?php
include_once("class.DB.php");
include_once("class.Circunferencia.php");
include_once("class.Logs.php"); 


/**
* CLASE PARA OBTENER LA INFORMACION DEL CLIMA
*/
class Weather{
	private $con; //CONEXCION A LA BASE DE DATOS

	/**
	* CONSTRUCTOR
	*/
	public function __construct(){
		$this->con = new DB();
	}

	/**
	* REGRESA LA INFORMACIÓN DE LAS IMAGENES EN BASE DE LA CONSULTA
	* SQL RECIBIDA
	*/
	public function getFromPolygon($poligono){
  
	    $sql = "select estacion,lat,lon from estaciones";
	    $sql = $this->add_polygon_to_sql($sql,$poligono);
	    
	    $data = $this->con->executeQuery($sql);
	    //print_r($sql);
	    return $data;
	}

	 /*
	* AGREGA EL POLIGONO A LA CADENA DE BUSQUEDA
	*/
	private function add_polygon_to_sql($sql,$coors_poly){
		$n = count($coors_poly);
		$this->poligono = "polygon('(";
		for ($i=0; $i < $n ; $i++) {
		  $this->poligono .= "(".$coors_poly[$i]['lon'].",".$coors_poly[$i]['lat'].")";
		  if($i<$n-1){
		    $this->poligono .= ",";
		  }
		}
		$this->poligono .= ")')";
		$sql .= " where ".$this->poligono;
		$sql .= "  @> point(''||lon||','||lat||'');";
		
		return $sql;
	}
}