<?php
class DB extends PDO{

  //creamos la conexión a la base de datos prueba
	public function __construct(){
		include(dirname(__FILE__) . '/../../resources/conf.php');
		$dbdata = $config["db"]["db1"];
	    //print_r($dbdata);
		try {
			//print_r($dbdata);
			$this->dbh = parent::__construct("pgsql:host=".$dbdata['host'].";dbname=".$dbdata['dbname'].";user=".$dbdata['username'].";password=".$dbdata['password']);

			$metodos = get_class_methods('DB');
			$this->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
			$this->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
		} catch(PDOException $e) {
	    	//print_r($dbdata);
			echo  $e->getMessage();
		}
	}

	//función para cerrar una conexión pdo
	public function close_con(){
		$this->dbh = null;
	}

	public function executeQuery($sql_string,$params=null){
		try{
			$query = $this->prepare($sql_string);
			if(isset($params)){
				$query->execute($params);
			}else{

				$query->execute();
			}
			$this->close_con();
			return $query->fetchAll();
		}catch(PDOException $e) {
			echo  $e->getMessage();
		}
	}
}
