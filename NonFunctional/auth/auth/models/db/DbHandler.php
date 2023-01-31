<?php

require_once dirname(__FILE__) . '/Connection.php';
require_once dirname(__FILE__) . '/../log/Log.php';

class DbHandler {
	/**
	* @var db
	* @var log
	*/
	private $db;
	private $log;

	/**
	* DbHandler constructor.
	*/
	public function __construct() {
		$db = new Connection();
		$this->db = $db->getConnection();
		$this->log = new Log;
	}
	
	public function deactivateUser($keyuser){
		try {
			$sql = "UPDATE users SET isactive='F' WHERE keyuser=:ku;";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":ku", $keyuser, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount()) {
				$stmt=null;
				return 'ok';
			}else{
				$stmt=null;
				return 'err';
			}
		} catch (Exception $e) {
			$stmt=null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
  	}

	public function activateUser($keyuser){
		try {
			$sql = "UPDATE users SET isactive='T' WHERE keyuser=:ku;";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":ku", $keyuser, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount()) {
				$stmt=null;
				return 'ok';
			}else{
				$stmt=null;
				return 'err';
			}
		} catch (Exception $e) {
			$stmt=null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
  	}

	

	public function removeKey($user){
		try {
			$sql = "DELETE FROM users WHERE tokenuser=?;";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $user, PDO::PARAM_STR);
			//$res=$stmt->execute();
			$stmt->execute();
			//if ($res == 'DELETE 0') {
			if ($stmt->rowCount()>0) {
				$res = 'tover';
			}else{
				$res = 'invlink';
			}
			return $res;
			$stmt=null;
		} catch (PDOException $e) {
			$stmt=null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function removeCode($keyuser){
		try {
			$sql = "UPDATE users SET code='' WHERE tokenuser=:ku;";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":ku", $keyuser, PDO::PARAM_STR);
			$stmt->execute();
			$stmt=null;		
			return true;
		} catch (Exception $e) {
			$stmt=null;		
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function setActive($keyuser){
		try {
			$sql = "UPDATE users SET isactive='T' WHERE tokenuser=:ku;";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":ku", $keyuser, PDO::PARAM_STR);
			$stmt->execute();
			$stmt=null;	
			return true;
		} catch (PDOException $e) {
			$stmt=null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function getAllUserData($keyu){
        try {
            $sql = 'SELECT * FROM users WHERE keyuser=?;';
            $stmt = $this->db->prepare($sql);
            $stmt->bindParam(1, $keyu, PDO::PARAM_STR);
            $stmt->execute();
            $res=$stmt->fetch(PDO::FETCH_ASSOC);
            $stmt=null;
            return $res;
        } catch (PDOException $e) {
            $stmt=null;
            $this->log->lwrite($e->getMessage());
            return false;
        }
	}

	
	
	public function activation($code, $tokenuser){
		$data=$this->isValidLinkAndTime($tokenuser, $code);
		
        if($data['isvalid'] == 1){
            $this->setActive($tokenuser);
            $this->removeCode($tokenuser);
            return 'ok';
        }else{
			$this->removeKey($tokenuser);
            return  json_encode($data);
        }
    }

	public function isValidLinkAndTime($tokenuser, $code){
        try {
            //$sql = 'SELECT CASE WHEN NOW() < dateexp THEN 1 ELSE 0 END AS isvalid FROM users WHERE tokenuser=:ku AND code=:cd;';
            $sql = "SELECT CASE WHEN NOW() < dateexp THEN 1 ELSE 0 END AS isvalid FROM users WHERE tokenuser=:ku;";
//             echo $sql;
            $stmt = $this->db->prepare($sql);
            $stmt->bindParam(":ku", $tokenuser, PDO::PARAM_STR);
            //$stmt->bindParam(":cd", $code, PDO::PARAM_STR);
			$stmt->execute();
			return $stmt->fetch(PDO::FETCH_ASSOC);
			if($stmt->rowCount() > 0){
				$res = $stmt->fetch(PDO::FETCH_ASSOC);
			}else{
				$res = false;
			}
            $stmt=null;
            return $res;
        } catch (PDOException $e) {
            $stmt=null;
            $this->log->lwrite($e->getMessage());
            return false;
        }
	}

	

	public function insertLog($operation,$access_token,$ip,$status){
		try {
			$stmt=$this->db->prepare("INSERT INTO logs (operation, token, ipadress, status) VALUES(:op,:tk,:ip,:st)");
			$stmt->bindParam(":op",$operation,PDO::PARAM_STR);
			$stmt->bindParam(":tk",$access_token,PDO::PARAM_STR);
			$stmt->bindParam(":ip",$ip,PDO::PARAM_STR);
			$stmt->bindParam(":st",$status,PDO::PARAM_STR);
			$stmt->execute();
			$stmt = null;
			return true; 
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
  	}

	public function getTimestamp(){
		try {
			//32 equivale a un minuto 
            //1920 una hora
            //46080 un dia
            //1382400 un mes de 30 dias
            //5529600 cuatro meses de 30 dias
            //return strtotime("now")+1920; 
            return strtotime("now");
		} catch (PDOException $e) {
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	

	

	public function getUser($id) {
		try {
			$sql = 'SELECT username, email, isactive FROM users WHERE keyuser = ?;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $id ,PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() == 1) {
				$user = $stmt->fetch(PDO::FETCH_ASSOC);
			} else {
				$user = false;
			}
			$stmt = null;
			return $user;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}
	
	public function getAllUsers() {
		try {
			$sql = 'SELECT username, email, tokenuser, created_at FROM users;';
			//$sql = 'SELECT * FROM users;';
			$stmt = $this->db->prepare($sql);
			$stmt->execute();
			if ($stmt->rowCount()>0) {
				$res = $stmt->fetchAll(PDO::FETCH_ASSOC);
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function getFullData() {
		try {
			$sql = 'SELECT keyuser, username, email, isactive, created_at FROM users;';
			$stmt = $this->db->prepare($sql);
			if ($stmt->execute()) {
				$users = $stmt->fetchAll(PDO::FETCH_ASSOC);
			} else {
				$users = false;
			}
			$stmt = null;
			return $users;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	// -----------------------------------------
	
    
	
	

	public function checkLogin($user,$pass) {
		// fetching user by email
		try {
			require_once 'PassHash.php';
			$sql = "SELECT password FROM users WHERE (email=:ur OR username=:ur) AND isactive='T';";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":ur", $user ,PDO::PARAM_STR);
			$stmt->execute();

			if ($stmt->rowCount() > 0) {
				// Found user with the email
				// Now verify the password
				$row = $stmt->fetch(PDO::FETCH_ASSOC);
				$stmt = null;

				if (PassHash::checkPassword($row['password'], $pass)) {
					// User password is correct
					return true;
				} else {
					// user password is incorrect
					return false;
				}
			} else {
				$stmt = null;
				// user not exist with the email
				return false;
			}
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	

	/**
	* Fetching user by email
	* @param String $email User email
	* @return Array        User info
	*/
	public function getUserByEmail($email) {
		try {
			$sql = 'SELECT keyuser, tokenuser, username, email, apikey, tokenorg, access_token, isadmin, isactive FROM users WHERE email=:ur OR username=:ur';
			//$sql = 'SELECT * FROM users WHERE email = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":ur", $email, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() == 1) {
				$user = $stmt->fetch(PDO::FETCH_ASSOC);
			} else {
				$user = false;
			}
			$stmt = null;
			return $user;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function getUserByEmailWithOrg($email) {
		try {
			$sql = 'SELECT keyuser, tokenuser, username, email, apikey, u.tokenorg, access_token, isadmin, isactive, acronym, fullname FROM users AS u JOIN hierarchy AS h ON u.tokenorg=h.tokenhierarchy JOIN token_mapping AS m ON h.keyhierarchy=m.keyhierarchy WHERE email=:ur OR username=:ur';
			//$sql = 'SELECT * FROM users WHERE email = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":ur", $email, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() == 1) {
				$user = $stmt->fetch(PDO::FETCH_ASSOC);
			} else {
				$user = false;
			}
			$stmt = null;
			return $user;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	/**
	* Fetching user api key
	* @param String $userId  User id
	* @return String         User api key
	*/
	public function getApiKeyById($userId) {
		try {
			$sql = 'SELECT apikey FROM users WHERE keyuser = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $userId, PDO::PARAM_INT);
			if ($stmt->execute()) {
				$row = $stmt->fetch(PDO::FETCH_ASSOC);
				$apiKey = $row['api_key'];
			} else {
				$apiKey = false;
			}
			$stmt = null;
			return $apiKey;
		} catch (PDOException $e) {
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	/**
	* Fetching user id by api key
	* @param String $apiKey  User api key
	* @return String         User id
	*/
	public function getUserId($apiKey) {
		try {
			$sql = 'SELECT id FROM users WHERE api_key = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $apiKey, PDO::PARAM_STR);
			if ($stmt->execute()) {
				$row = $stmt->fetch(PDO::FETCH_ASSOC);
				$userId = $row['id'];
			} else {
				$userId = false;
			}
			$stmt = null;
			return $userId;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	/**
	* Validating user access token
	* If the access token is there in db, it is a valid key
	* @param String $apiKey User access token
	* @return Boolean
	*/
	public function isValidAccessToken($accessToken) {
		try {
			$sql = 'SELECT username, email, tokenuser FROM users WHERE access_token = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $accessToken, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$user = $stmt->fetch(PDO::FETCH_ASSOC);
			} else {
				$user = false;
			}
			$stmt = null;
			return $user;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	/**
	* Validating user api key
	* If the api key is there in db, it is a valid key
	* @param String $apiKey User api key
	* @return Boolean
	*/
	public function isValidApiKey($apiKey) {
		try {
			$sql = 'SELECT keyuser FROM users WHERE apikey = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $apiKey, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() == 1) {
				$user = $stmt->fetch(PDO::FETCH_ASSOC);
			} else {
				$user = false;
			}
			$stmt = null;
			return $user;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	/**
	* Validating user access token
	* If the access token is there in db, it is a valid key
	* @param String $apiKey User access token
	* @return Boolean
	*/
	public function isValidOrgToken($orgToken) {
		try {
			$sql = 'SELECT keyuser FROM users WHERE tokenorg = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $orgToken, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$user = true;
			} else {
				$user = false;
			}
			$stmt = null;
			return $user;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function getUsersByOrgToken($orgToken) {
		try {
			$sql = 'SELECT username, email, tokenuser FROM users WHERE tokenorg = ? AND isadmin=false';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $orgToken, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$user = $stmt->fetchAll(PDO::FETCH_ASSOC);
			} else {
				$user = false;
			}
			$stmt = null;
			return $user;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	
	



	//--------------------------------------------------------------------------
    //--------------------------- USERS -------------------------------
	//--------------------------------------------------------------------------
	public function validateTokenorg($orgToken) {
		try {
			$sql = 'SELECT * FROM token_mapping WHERE tokenorg = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $orgToken, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function insertUser($keyuser,$tokenuser,$username,$email,$pass,$tokenorg,$access_token,$apikey,$active,$admin,$code){
		try {
			$stmt = $this->db->prepare("INSERT INTO users(keyuser, tokenuser, username, email, password, tokenorg, access_token, apikey, 
				isactive, isadmin, code) VALUES(:ku,:tu,:un,:em,:ps,:to,:at,:ak,:act,:adm,:cd);");
			$stmt->bindParam(":ku", $keyuser,PDO::PARAM_STR);
			$stmt->bindParam(":tu", $tokenuser,PDO::PARAM_STR);
			$stmt->bindParam(":un", $username,PDO::PARAM_STR);
			$stmt->bindParam(":em", $email,PDO::PARAM_STR);
			$stmt->bindParam(":ps", $pass,PDO::PARAM_STR);
			$stmt->bindParam(":to", $tokenorg,PDO::PARAM_STR);
			$stmt->bindParam(":at", $access_token,PDO::PARAM_STR);
			$stmt->bindParam(":ak", $apikey,PDO::PARAM_STR);
			$stmt->bindParam(":act", $active,PDO::PARAM_BOOL);
			$stmt->bindParam(":adm", $admin,PDO::PARAM_BOOL);
			$stmt->bindParam(":cd", $code,PDO::PARAM_STR);
			$stmt->execute();
			// Check for successful insertion
			if ($stmt->rowCount()==1) {
					// User successfully inserted
					$res = true;
			} else {
					// Failed to create user
					$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;			
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	
	public function isUserExist($user,$email) {
		try {
			$sql = 'SELECT * FROM users WHERE username=? OR email = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $user, PDO::PARAM_STR);
			$stmt->bindParam(2, $email, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				/*$sql = 'SELECT * FROM users WHERE username = ?';
				$stmt = $this->db->prepare($sql);
				$stmt->bindParam(1, $user['username'], PDO::PARAM_STR);
				$stmt->execute();
				$num = $stmt->rowCount();
				if ($num > 0)
					return 'name';
				else
					return 'ok';*/
					$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function validateAccessToken($token) {
		try {
			$sql = 'SELECT * FROM users WHERE access_token = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $token, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function deleteUser($id) {
		try {
			$sql = 'DELETE FROM users WHERE tokenuser = ?;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $id, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		} 
	}
	
	//--------------------------- edit user -------------------------------
	public function validateUsername($token) {
		try {
			$sql = 'SELECT * FROM users WHERE username = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $token, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function editUserName($user,$uname){
		try {
			$sql = "UPDATE users SET username=:un WHERE tokenuser=:ku;";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":un", $uname, PDO::PARAM_STR);
			$stmt->bindParam(":ku", $user, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount()>0) {
				$res = true;
			}else{
				$res = false;
			}
			$stmt=null;		
			return $res;
		} catch (PDOException $e) {
			$stmt=null;		
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}
	  
	public function validateEmail($email) {
		try {
			$sql = 'SELECT * FROM users WHERE email = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $email, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function editUserEmail($user,$email){
		try {
			$sql = "UPDATE users SET email=:em WHERE tokenuser=:ku;";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":em", $email, PDO::PARAM_STR);
			$stmt->bindParam(":ku", $user, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount()>0) {
				$res = true;
			}else{
				$res = false;
			}
			$stmt=null;
			return $res;
		} catch (PDOException $e) {
			$stmt=null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
  	}

	//--------------------------- edit pass -------------------------------
	public function getPassByToken($user) {
		try {
			$sql = 'SELECT password FROM users WHERE tokenuser = ?;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $user ,PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = $stmt->fetch(PDO::FETCH_ASSOC);
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}
			  
  	public function editUserPass($user,$pass){
		try {
			$sql = "UPDATE users SET password=:ps WHERE tokenuser=:ku;";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":ps", $pass, PDO::PARAM_STR);
			$stmt->bindParam(":ku", $user, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			}else{
				$res = false;
			}
			return $res;
		} catch (PDOException $e) {
			$stmt=null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
  	}

	//--------------------------- login -------------------------------		
	public function getPassByUser($user) {
		try {
			$act=true;
			//$sql = "SELECT password,tokenuser,access_token,tokenorg,apikey FROM users WHERE (email=:ur OR username=:ur) AND isactive=:ia;";
			$sql = "SELECT password,tokenuser,access_token,tokenorg,apikey FROM users WHERE (email=:ur OR username=:ur) ;";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":ur", $user ,PDO::PARAM_STR);
			//$stmt->bindParam(":ia", $act ,PDO::PARAM_BOOL);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = $stmt->fetch(PDO::FETCH_ASSOC);
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}
	
	
    //--------------------------- change user tokens -------------------------------		
	public function getKeyUsers() {
		try {
			$sql = 'SELECT keyuser FROM users;';
			$stmt = $this->db->prepare($sql);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = $stmt->fetchAll(PDO::FETCH_ASSOC);
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function changeToken($newToken,$user) {
		try {
			$sql = 'UPDATE users SET access_token=? WHERE tokenuser=?;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1,$newToken,PDO::PARAM_STR);
			$stmt->bindParam(2,$user,PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function getUserByToken($token) {
		try {
			//echo $token;
			//$sql = 'SELECT * FROM users WHERE tokenuser = ?';
			$sql = 'SELECT username, email FROM users WHERE tokenuser = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $token, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$user = $stmt->fetch(PDO::FETCH_ASSOC);
			} else {
				$user = false;
			}
			$stmt = null;
			return $user;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}


	public function validateTokenUser($token) {
		try {
			$sql = 'SELECT * FROM users WHERE tokenuser = ?';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $token, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}







	//--------------------------------------------------------------------------
    //--------------------------- HIERARCHY -------------------------------
	//--------------------------------------------------------------------------
	public function hierarchyExist($acr,$name) {
		try {
			$sql = "SELECT * FROM hierarchy WHERE acronym=? AND fullname=?;";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $acr, PDO::PARAM_STR);
			$stmt->bindParam(2, $name, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount()>0) {
				$res = true;
			}else{
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function hierarchyExist2($key) {
		try {
			$sql = "SELECT * FROM hierarchy WHERE keyhierarchy=(SELECT keyhierarchy FROM token_mapping WHERE tokenorg=?);";
			// SELECT * FROM hierarchy WHERE keyhierarchy=(SELECT keyhierarchy FROM token_mapping WHERE token='');
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $key, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount()>0) {
				$res = true;
			}else{
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function tokenFatherHExist($token) {
		try {
			//$sql = "SELECT acronym, fullname, tokenhierarchy, father FROM hierarchy AS h JOIN token_mapping AS tm ON h.keyhierarchy=tm.keyhierarchy WHERE tokenhierarchy=?;";
			$sql = "SELECT * FROM hierarchy AS h JOIN token_mapping AS tm ON h.keyhierarchy=tm.keyhierarchy WHERE tokenhierarchy=?;";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $token, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() == 1) {
				$res = $stmt->fetch(PDO::FETCH_ASSOC);
			}else{
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function newHierarchy($key,$acron,$fname,$tokenH,$father) {
		try {
			$sql = "INSERT INTO hierarchy(keyhierarchy, acronym, fullname,tokenhierarchy, father) VALUES(:id,:ac,:fn,:th,:ft);";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":id", $key, PDO::PARAM_STR);
			$stmt->bindParam(":ac", $acron, PDO::PARAM_STR);
			$stmt->bindParam(":fn", $fname, PDO::PARAM_STR);
			$stmt->bindParam(":th", $tokenH, PDO::PARAM_STR);
			$stmt->bindParam(":ft", $father, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount()==1) {
					$res = true;
			}else{
					$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function insertTokenHierarchyMapping($key,$tokenH) {
		try {
			$sql = "INSERT INTO token_mapping(keyhierarchy,tokenorg) VALUES(:id,:th);";
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":id", $key, PDO::PARAM_STR);
			$stmt->bindParam(":th", $tokenH, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount()==1) {
					$res = true;
			}else{
					$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function deleteHierarchy($id) {
		try {
			//$sql = 'DELETE FROM hierarchy WHERE keyhierarchy = (SELECT keyhierarchy FROM token_mapping WHERE tokenhierarchy=?);';
			$sql = 'DELETE FROM hierarchy WHERE tokenhierarchy=?;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $id, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		} 
	}

	public function deleteHierarchyByKey($id) {
		try {
			//$sql = 'DELETE FROM hierarchy WHERE keyhierarchy = (SELECT keyhierarchy FROM token_mapping WHERE tokenhierarchy=?);';
			$sql = 'DELETE FROM hierarchy WHERE keyhierarchy=?;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $id, PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		} 
	}

	public function modifyHierarchy($key,$acr,$fname) {
		try {
				//$sql = 'UPDATE hierarchy SET acronym=:na, fullname=:fn WHERE keyhierarchy=(SELECT keyhierarchy FROM token_mapping WHERE tokenorg=:id);';
				$sql = 'UPDATE hierarchy SET acronym=:na, fullname=:fn WHERE tokenhierarchy=:id;';
				$stmt = $this->db->prepare($sql);
				$stmt->bindParam(":na", $acr, PDO::PARAM_STR);
				$stmt->bindParam(":fn", $fname, PDO::PARAM_STR);
				$stmt->bindParam(":id", $key, PDO::PARAM_STR);
				$stmt->execute();
				if ($stmt->rowCount()==1) {
					$res = true;
				}else{
					$res = false;
				}
				$stmt = null;
				return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	//--------------------------- change hierarchy tokens -------------------------------	
	public function getKeyHierarchyByOrg($org) {
		try {
			$sql = 'SELECT keyhierarchy FROM hierarchy WHERE tokenhierarchy=?;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1, $org, PDO::PARAM_STR);			
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = $stmt->fetch(PDO::FETCH_ASSOC);
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function getKeyHierarchy() {
		try {
			$sql = 'SELECT keyhierarchy FROM hierarchy;';
			$stmt = $this->db->prepare($sql);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = $stmt->fetchAll(PDO::FETCH_ASSOC);
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function changeTokenHierarchy($newToken,$key) {
		try {
			$sql = 'UPDATE hierarchy SET tokenhierarchy=? WHERE keyhierarchy=?;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1,$newToken,PDO::PARAM_STR);
			$stmt->bindParam(2,$key,PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function changeTokenHierarchyOrg($newToken,$org) {
		try {
			$sql = 'UPDATE token_mapping SET tokenorg=? WHERE tokenorg=?;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(1,$newToken,PDO::PARAM_STR);
			$stmt->bindParam(2,$org,PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = true;
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

    //--------------------------- view down -------------------------------
	public function selectChildrenH($val) {
		try {
			//$sql = 'SELECT keyhierarchy FROM hierarchy WHERE father=:va;';
			$sql = 'SELECT keyhierarchy, acronym,fullname,tokenhierarchy,father FROM hierarchy WHERE father=:va;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":va",$val,PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount() > 0) {
				$res = $stmt->fetchAll(PDO::FETCH_ASSOC);
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

	public function selectChildrenTH($val) {
		try {
			//$sql = 'SELECT keyhierarchy FROM hierarchy WHERE father=:va;';
			$sql = 'SELECT acronym,fullname,tokenhierarchy,father FROM hierarchy WHERE father=:va;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":va",$val,PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount()>0) {
				$res = $stmt->fetchAll(PDO::FETCH_ASSOC);
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}

    //--------------------------- view up -------------------------------
	public function selectNodeH($val) {
		try {
			//$sql = 'SELECT father FROM hierarchy WHERE keyhierarchy=:va;';
			$sql = 'SELECT acronym,fullname,tokenhierarchy,father FROM hierarchy WHERE keyhierarchy=:va;';
			$stmt = $this->db->prepare($sql);
			$stmt->bindParam(":va",$val,PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount()>0) {
				$res = $stmt->fetch(PDO::FETCH_ASSOC);
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}




	//--------------------------------------------------------------------------
    //--------------------------- dev only -------------------------------
    //--------------------------------------------------------------------------
	public function getAllHierarchy() {
		try {
			$sql = 'SELECT acronym, fullname, tokenhierarchy, father,tokenorg FROM hierarchy AS h JOIN token_mapping AS m ON h.keyhierarchy=m.keyhierarchy ;';
			//$sql = 'SELECT * FROM hierarchy AS h JOIN token_mapping AS m ON h.keyhierarchy=m.keyhierarchy ;';
			$stmt = $this->db->prepare($sql);
			//$stmt->bindParam(1, $id ,PDO::PARAM_STR);
			$stmt->execute();
			if ($stmt->rowCount()>0) {
				$res = $stmt->fetchAll(PDO::FETCH_ASSOC);
			} else {
				$res = false;
			}
			$stmt = null;
			return $res;
		} catch (PDOException $e) {
			$stmt = null;
			$this->log->lwrite($e->getMessage());
			return false;
		}
	}
	

	/**
	* Close connection
	*/
	public function __destruct() {
		$this->db = null;
	}

}
