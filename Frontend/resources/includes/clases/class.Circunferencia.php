<?php

class Circunferencia{

  private $EARTH_RADIUS = 6371;

  public function __construct($lat,$lon){
    $this->lat_center = $lat;
    $this->lon_center = $lon;
  }

  public function getDistance($latitude,$longitude){
    $dLat = deg2rad( $latitude - $this->lat_center );
    $dLon = deg2rad( $longitude - $this->lon_center );
    $a = sin($dLat/2) * sin($dLat/2) + cos(deg2rad($this->lat_center)) * cos(deg2rad($latitude)) * sin($dLon/2) * sin($dLon/2);
    $c = 2 * asin(sqrt($a));
    $d = $this->EARTH_RADIUS * $c;

    return $d;

  }
}


?>
