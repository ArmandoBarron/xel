<?php

include_once("class.DB.php");
include_once("class.Curl.php");

class Catalogs{
    public static function getCatalogs(){
        $sql = "SELECT token FROM catalogos";
        $con = new DB();
        $data = $con->executeQuery($sql);
        return $data;
    }

    public static function getFilesDB($catalog){
        
        $sql = "SELECT token from catalogsElements where catalogToken = '$catalog' and usrToken = '".$_SESSION['tokenuser']."'";
        //echo $sql ."<br>";
        $con = new DB();
        $data = $con->executeQuery($sql);
        $res = array();
        foreach($data as $d){
            $res[] = $d['token'];
        }
        return $res;
    }

    public static function insertElement($catalog, $element){
        $sql = "INSERT INTO catalogsElements(catalogToken, token, usrToken) 
                VALUES('$catalog', '$element', '".$_SESSION['tokenuser']."')";
        $con = new DB();
        $data = $con->executeQuery($sql);
    }

    public static function getElementsCatSky($catalog){
        
        $url = "http://".$_ENV["IP_SKY"]."/pub_sub/v1/view/files/catalog/".$catalog."?access_token=".$_SESSION['access_token'];
        
        $filesSky = json_decode(Curl::get($url), true);
       
        $filesNew = array();
        if($filesSky['message'] == "Ok"){
            $filesSky = $filesSky["data"];
            $filesSeen = Catalogs::getFilesDB($catalog);
            //print_r($filesSeen);
            foreach($filesSky as $f){
                if(!in_array($f['keyfile'], $filesSeen)){
                    //print_r($f);
                    $filesNew[] = $f;
                    Catalogs::insertElement($catalog, $f["keyfile"]);
                }
            }
        }
        
        return $filesNew;
    }
}