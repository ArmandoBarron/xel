<?php
class Cluster {

  private $elements;
  private $centroid;
  private $id;

  public function __construct($id){
    $this->id = $id;
    $this->elements = array();
    $this->centroid =  null;
  }

  public function addElement($element){
    $element->setCluster($this->id);
    $this->elements[] = $element;
  }

  public function getElements(){
    return $this->elements;
  }

  public function getCentroid(){
    return $this->centroid;
  }

  public function getIdCluster(){
    return $this->id; 
  }

  public function size(){
    return count($this->elements);
  }

  public function setCentroid($centroid){
    $this->centroid = $centroid;
  }

  public function setElements($elements){
    $this->elements = $elements;
  }

  public function clear(){
    unset($this->elements);
    $this->elements = array();
  }

  public function printCluster(){
    echo "Cluster ".$this->id."<br>";
    foreach ($this->elements as $point) {
      echo $point->toString()."<br>";
    }
  }

  public function getUser($iduser){
    $user = array_values(array_filter($this->elements,function($var) use ($iduser){
      return $var->getUser() == $iduser;
    }));
    return $user[0];
  }

  public function contains($iduser){
    foreach ($this->elements as $user) {
      if($user->compare($iduser)){
        return true;
      }
    }
    return false;
  }

  /**
  * SERIALIZA UN OBJETO
  */
  public function jsonSerialize(){
    $vars = get_object_vars($this);
    return $vars;
  }

}
?>
