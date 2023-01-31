<?php
/*
* Class Connection
* Author: Alfredo Barrón Rodríguez
* Company: Cinvestav-Tamaulipas
*/

include_once dirname(__FILE__) . '/Config.php';
include_once dirname(__FILE__) . '../../log/Log.php';

class Connection {
    /**
     * @var db
     * @var log
     */
    private $db;
    private $log;

    /**
     * Connection constructor.
     */
    public function __construct() {
        try {
            $this->log = new Log;
            $this->db = new PDO('pgsql:host='.DB_HOST.';port='.DB_PORT.';dbname='.DB_NAME, DB_USERNAME, DB_PASSWORD);
            $this->db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        } catch (PDOException $e) {
            $this->log->lwrite($e->getMessage());        
        }
    }

    /**
     * @return PDO
     */
    public function getConnection() {
        return $this->db;
    }

    /**
     * @return NULL
     */
    public function __destruct() {
         $this->db = null;
    }

}