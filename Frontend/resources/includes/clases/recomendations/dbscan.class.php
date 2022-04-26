<?php

include_once("cluster.class.php");
include_once("user.class.php");

class DBSCAN{

	//VARIABLES
	private $data; //DATOS DE LOS USUARIOS
	private $clusters; //CLUSTERS GENERADOS
	private $points_list; //LISTA DE PUNTOS O USUARIOS
	private $min_pts = 3;
	private $visited;
	private $max_distance;

	public function __construct($data){
		$this->data = $data;
		$this->clusters = array();
		$this->generatePoints();
		$this->visited = array();
		$this->max_distance = 300;
		$this->preInit();
		$this->cluster();
	}

	private function preInit(){
		$distances = array();
		$sum = 0;
		foreach ($this->points_list as $point1) {
			foreach ($this->points_list as $point2) {
				if($point1 !== $point2){
					$distancia = $this->get_distance($point1->getRatings(),$point2->getRatings(),2);
					$distances[] = $distancia;
					$sum += $distancia;
				}
			}
		}
		sort($distances);
		$n = count($distances);
		$difmay = 0;
		for($i=0;$i<$n-1;$i++){
			$dif = $distances[$i+1] - $distances[$i];
			if($difmay < $dif){
				$difmay = $dif;
			}
		}

	}

	/**
	* CREA LA LISTA DE PUNTOS A PARTIR DE LA MATRIZ
	**/
	private function generatePoints(){
		foreach ($this->data as $key => $point) {
		  $user = new User($key,$point["point"],$point["username"]);
		  $this->points_list[] = $user;
		}
	}

	public function cluster(){
		$n = 0;
		foreach ($this->points_list as $point) {
			$this->visited[$n] = false;
			$n++;
		}

		$n = 0;
		foreach ($this->points_list as $point) {
			//echo $n."<br>";
			#print_r($this->visited);
			#echo "x = " . array_key_exists($n, $this->visited) . "<br>";
			if(!$this->visited[$n]){
				$this->visited[$n] = true;
				$neighbors = $this->getNeighbors($point);
				
				if(count($neighbors) >= $this->min_pts){
					$c = new Cluster(count($this->clusters));
					$this->buildCluster($point,$c,$neighbors);
					$this->clusters[] = $c;
				}
			}
			$n++;
		}

		/*foreach ($this->clusters as $cluster) {
			$cluster->printCluster();
			echo "<br>";
		}*/

		return $this->clusters;
	}

	/***
	* REGRESA LOS CLUSTERS GENERADOS
	*/
	public function getClusters(){
		return $this->clusters;
	}

	/**
	* REGRESA EL CLUSTER DONDE SE ENCUENTRE EL USUARIO ESPECIFICADO
	*/
	public function getCluster($iduser){
		//print_r($this->clusters);
	    foreach ($this->clusters as $cluster) {
	      if($cluster->contains($iduser)){
	        return $cluster;
	      }
	    }
	    return null;
  	}

  	/**
  	* CONSTRUYE UN CLUSTER
  	*/
	public function buildCluster($dp,$c,$neighbors){
		$c->addElement($dp);
		foreach ($neighbors as $ind) {
			$p = $this->points_list[$ind];
			if(!$this->visited[$ind]){
				$this->visited[$ind] = true;
				$newNeighbors = $this->getNeighbors($p);
				if(count($newNeighbors) >= $this->min_pts){
					array_merge($neighbors,$newNeighbors);
				}
			}
			if($p->getCluster() == -1){
				$c->addElement($p);
			}
		}
	}

	/**
	* REGRESA LOS VECINOS DE UN PUNTO
	*/
	public function getNeighbors($dp){
		$neighbors = array();
		$i = 0;
		foreach ($this->points_list as $point) {
			$distance = $this->get_distance($dp->getRatings(),$point->getRatings());

			//echo "$this->max_distance  $distance<br>";
			if($distance <= $this->max_distance){
				$neighbors[] = $i;
			}
			$i++;
		}
		return $neighbors;
	}

	/**
	* CALCULA LA DISTANCIA ENTRE DOS PUNTOS GEOGRAFICOS
	*/
	public static function get_distance($point1,$point2){
		if($point1[0] == $point2[0] && $point1[1] == $point2[1]){
		  return 0;
		}

		$point1_lat = deg2rad($point1[0]);
		$point1_long = deg2rad($point1[1]);
		$point2_lat = deg2rad($point2[0]);
		$point2_long = deg2rad($point2[1]);
		$dif_lat = $point2_lat - $point1_lat;
		$dif_long = $point2_long - $point1_long;
		$radiusOfEarth = 6372.795477598;// Earth's radius in meters.
		
		$distance = 2 * $radiusOfEarth * asin(sqrt(sin($dif_lat/2) * sin($dif_lat/2) 
				+ cos($point1_lat) * cos($point2_lat) * sin($dif_long/2) * sin($dif_long/2)));
		
		return $distance;
	}
}