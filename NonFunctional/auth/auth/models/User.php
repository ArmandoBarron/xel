<?php

require_once "Rest.php";
require_once "db/DbHandler.php";
require_once "Curl.php";

class User extends REST
{

    public function deactivateUser()
    {
        if ($this->getRequestMethod() != "PUT") {
            $msg['message'] = "Bad Request.";
            $this->response($this->json($msg), 400);
        }
        if (isset($this->_request['keyuser'])) {
            $db = new DbHandler();
            $data = $db->deactivateUser($this->_request['keyuser']);
            switch ($data) {
                case 'empty':
                    $msg['message'] = "Some data is empty.";
                    $this->response($this->json($msg), 406);
                    break;
                case 'err':
                    $msg['message'] = "Invalid Data.";
                    $this->response($this->json($msg), 400);
                case 'ok':
                    $msg['message'] = "Deactivated.";
                    $this->response($this->json($msg), 200);
                    break;
                default:
                    $msg['message'] = "Something went wrong.";
                    $this->response($this->json($msg), 500);
                    break;
            }
        } else {
            $msg['message'] = "Invalid Data.";
            $this->response($this->json($msg), 400);
        }
    }

    public function activateUser()
    {
        if ($this->getRequestMethod() != "PUT") {
            $msg['message'] = "Bad Request.";
            $this->response($this->json($msg), 400);
        }
        //         print_r($this->_request);
        if (isset($this->_request['keyuser'])) {
            $db = new DbHandler();
            $data = $db->activateUser($this->_request['keyuser']);
            if ($data) {
                switch ($data) {
                    case 'empty':
                        $msg['message'] = "Some data is empty.";
                        $this->response($this->json($msg), 406);
                        break;
                    case 'err':
                        $msg['message'] = "Invalid Data.";
                        $this->response($this->json($msg), 400);
                    case 'ok':
                        $msg['message'] = "Activated.";
                        $this->response($this->json($msg), 200);
                        break;
                    default:
                        $msg['message'] = "Something went wrong.";
                        $this->response($this->json($msg), 500);
                        break;
                }
            }
        } else {
            $msg['message'] = "Invalid Data.";
            $this->response($this->json($msg), 400);
        }
    }

    public function editUserEmail()
    {
        if ($this->getRequestMethod() != "PUT") {
            $msg['message'] = "Bad Request.";
            $this->response($this->json($msg), 400);
        }
        if (isset($this->_request['keyuser']) && isset($this->_request['email'])) {
            $this->validateEmail($this->_request['email']);
            $db = new DbHandler();
            $data = $db->editUserEmail($this->_request);
            switch ($data) {
                case 'empty':
                    $msg['message'] = "Some data is empty.";
                    $this->response($this->json($msg), 406);
                    break;
                case 'err':
                    $msg['message'] = "Invalid Data.";
                    $this->response($this->json($msg), 400);
                    break;
                case 'ok':
                    $msg['message'] = "Done.";
                    $this->response($this->json($msg), 200);
                    break;
                case 'aexist':
                    $msg['message'] = "Email Already Registered.";
                    $this->response($this->json($msg), 400);
                    break;
                default:
                    $msg['message'] = "Something went wrong.";
                    $this->response($this->json($msg), 500);
                    break;
            }
        } else {
            $msg['message'] = "Invalid Data.";
            $this->response($this->json($msg), 400);
        }
    }



    public function editUserName9()
    {
        if ($this->getRequestMethod() != "PUT") {
            $msg['message'] = "Bad Request.";
            $this->response($this->json($msg), 400);
        }
        if (isset($this->_request['keyuser']) && isset($this->_request['username'])) {
            $this->validateUser($this->_request['username']);
            $db = new DbHandler();
            $data = $db->editUserName($this->_request);
            if ($data) {
                switch ($data) {
                    case 'err':
                        $msg['message'] = "Invalid Data.";
                        $this->response($this->json($msg), 400);
                        break;
                    case 'ok':
                        $msg['message'] = "Done.";
                        $this->response($this->json($msg), 200);
                        break;
                    default:
                        break;
                }
            } else {
                $msg['message'] = "Something went wrong.";
                $this->response($this->json($msg), 400);
            }
        } else {
            $msg['message'] = "Invalid Data.";
            $this->response($this->json($msg), 400);
        }
    }

    public function login()
    {
        if ($this->getRequestMethod() != "POST") {
            $msg['message'] = 'Something went wrong.';
            $msg['data'] = array();
            $this->response($this->json($msg), 400);
        }
        //print_r($this->_request);
        if (isset($this->_request['user']) && isset($this->_request['password'])) {
            $db = new DbHandler();
            $status = $db->checkLogin($this->_request['user'], $this->_request['password']);
            if ($status == true) {
                $data = $db->getUserByEmailWithOrg($this->_request['user']);
                unset($data['keyuser']);
                if ($data) {
                    $msg['message'] = 'Ok';
                    $msg['data'] = $data;
                    $this->response($this->json($msg), 200);
                } else {
                    $msg['message'] = 'An error occurred. Please try again.';
                    $msg['data'] = $this->_request;
                    $this->response($this->json($msg), 400);
                }
            } else if ($status == false) {
                $msg['message'] = 'Login failed. Incorrect credentials or user isn\'t activated.';
                $msg['data'] = $this->_request;
                $this->response($this->json($msg), 400);
            }
        } else {
            $msg['message'] = 'Something went wrong.';
            $msg['data'] = array();
            $this->response($this->json($msg), 400);
        }
    }

    public function activation($code, $tokenuser)
    {
        if ($this->getRequestMethod() != "GET") {
            $msg = array("message" => "Bad Request.");
            $this->response($this->json($msg), 400);
        }
        $db = new DbHandler();
        $status = $db->activation($code, $tokenuser);

        $msg['code'] = $code;
        $msg['tokenuser'] = $tokenuser;
        $msg['status'] = $status;

        //         print_r($status);

        switch ($status) {
            case 'ok':
                $sip = $this->getGeolocationIP();
                if ($sip) {
                    $redirectTo = 'http://' . $_ENV['FRONTEND'];
                    //$this->redirect();
                    $msg['redirectTo'] = $redirectTo;
                }
                $msg['message'] = "Account activated.";
                $this->response($this->json($msg), 200);
                break;
            case 'invlink':
                $msg['message'] = "Invalid Link.";
                $this->response($this->json($msg), 400);
                break;
            default:
                $msg = array("message" => "Something went wrong.");
                $this->response($this->json($msg), 406);
                break;
        }
    }

    public function createUserAdmin()
    {
        if ($this->getRequestMethod() != "POST") {
            $error = array("message" => "Something went wrong.");
            $this->response($this->json($error), 406);
        }
        if (isset($this->_request['username']) && isset($this->_request['email']) && isset($this->_request['password'])) {
            $this->validateEmail($this->_request['email']);
            $this->validatePass($this->_request['password']);
            $this->validateUser($this->_request['username']);

            $db = new DbHandler();
            require_once 'db/PassHash.php';

            $uex = $db->isUserExist($this->_request['username'], $this->_request['email']);

            if (!$uex) {
                $username = $this->_request['username'];
                $email = $this->_request['email'];
                $pass = $this->_request['password'];
                // Operation type
                $operation = 'Create user admin';
                $isadmin = true;
                $isactive = true;
                $status = 1;
                // Generating password hash
                $passwordHash = PassHash::hash($this->_request['password']);

                // Generating keys
                $keyuser = $this->generateToken();
                $apikey = $this->generateToken();
                $tokenorg = $this->generateToken();
                $access_token = $this->generateSHA256Token();

                // activation code and dates
                $code = uniqid();
                //$date = $this->getTimestamp()+1920;
                //$dateexp = date('Y-m-d H:i:s',$date);
                //$ip = $this->getGeolocationIP();

                // insert query
                $res = $db->insertUser($keyuser, $tokenuser, $username, $email, $passwordHash, $tokenorg, $access_token, $apikey, $isactive, $isadmin, $code);

                if ($res) {
                    // register log
                    //$db->insertLog($operation, $access_token,$ip,$status);
                    // send credentials by email
                    $res = $this->prepareMail($email, $keyuser, $username, $pass, $code, $ip);
                    if ($res) {
                        //$msg = array("message" => "User created, please check your email.");
                        $msg = array("message" => "User created.");
                        $this->response($this->json($msg), 201);
                    } else {
                        $msg = array("message" => "Oops! An error occurred while registering.");
                        $this->response($this->json($msg), 400);
                    }
                } else {
                    $msg = array("message" => "Oops! An error occurred while registering.");
                    $this->response($this->json($msg), 400);
                }
            } else {
                $msg = array("message" => "Sorry, this user o email already exist.");
                $this->response($this->json($msg), 400);
            }
        } else {
            $msg = array("message" => "Something went wrong.");
            $this->response($this->json($msg), 400);
        }
    }

    public function createUser()
    {
        if ($this->getRequestMethod() != "POST") {
            $error = array("message" => "Something went wrong.", "codigo" => 1);
            $this->response($this->json($error), 406);
        }
        if (isset($this->_request['username']) && isset($this->_request['email']) && isset($this->_request['password']) && isset($this->_request['tokenorg'])) {
            $email = $this->_request['email'];
            $pass = $this->_request['password'];
            $username = $this->_request['username'];
            $tokenorg = $this->_request['tokenorg'];
            $this->validateEmail($email);
            $this->validatePass($pass);
            $this->validateUser($username);
            $this->validateTokenorg($tokenorg);
            $db = new DbHandler();

            require_once 'db/PassHash.php';

            $uex = $db->isUserExist($username, $email);

            if (!$uex) {
                $tokenuser = $this->generateSHA256Token();
                // Operation type
                $operation = 'Create user';
                $isadmin = false;
                //$isactive=true;
                $isactive = true;
                $status = 1;
                // Generating password hash
                $passHash = PassHash::hash($pass);

                // Generating keys
                $keyuser = $this->generateToken();
                $apikey = $this->generateToken();
                $access_token = $this->generateSHA256Token();

                // activation code and dates
                $code = uniqid();
                $ip = $this->getGeolocationIP();

                // insert query 5b06d434c733c
                $res = $db->insertUser($keyuser, $tokenuser, $username, $email, $passHash, $tokenorg, $access_token, $apikey, $isactive, $isadmin, $code);
                $msg['msg'] = 'avsdgga';
                $msg['keyuser'] = $keyuser;
                $msg['username'] = $username;
                $msg['email'] = $email;
                $msg['passHash'] = $passHash;
                $msg['tokenorg'] = $tokenorg;
                $msg['access_token'] = $access_token;
                $msg['apikey'] = $apikey;
                $msg['isactive'] = $isactive;
                $msg['isadmin'] = $isadmin;
                $msg['code'] = $code;
                $msg['res'] = $res;
                if ($res) {
                    // register log
                    //$db->insertLog($operation, $access_token,$ip,$status);
                    // send credentials by email
                    $msg = array("message" => "User created.", "codigo" => 0);
                    $this->response($this->json($msg), 201);
                    /*$res = $this->prepareMail($email, $tokenuser, $username, $pass, $code, $ip);
                    if ($res) {
                        $msg = array("message" => "User created, please check your email.", "codigo" => 0);
                        $msg = array("message" => "User created.");
                        $this->response($this->json($msg), 201);
                    } else {
                        $msg = array("message" => "Cant send the email, please try again.", "codigo" => 1);
                        $this->response($this->json($msg), 400);
                    }*/
                } else {
                    $msg = array("message" => "Oops! An error occurred, please try again.", "codigo" => 1);
                    $this->response($this->json($msg), 400);
                }
            } else {
                $msg = array("message" => "Sorry, this user o email already exist.", "codigo" => 1);
                $this->response($this->json($msg), 400);
            }
        } else {
            $msg = array("message" => "Something went wrongx.", "codigo" => 1);
            $this->response($this->json($msg), 400);
        }
    }

    public function createUserFromGlobal()
    {
        if ($this->getRequestMethod() != "POST") {
            $error = array("message" => "Something went wrong.", "codigo" => 1);
            $this->response($this->json($error), 406);
        }
        if (isset($this->_request['username']) && isset($this->_request['email']) && isset($this->_request['password']) && isset($this->_request['tokenorg'])) {
            $email = $this->_request['email'];
            $pass = $this->_request['password'];
            $username = $this->_request['username'];
            $tokenorg = $this->_request['tokenorg'];
            $keyuser = $this->_request['keyuser'];
            $passHash = $this->_request['passHash'];
            $access_token = $this->_request['access_token'];
            $apikey = $this->_request['apikey'];
            $code = $this->_request['code'];
            $tokenuser = $this->_request['tokenuser'];
            $isactive = false;
            $isadmin = false;
            $db = new DbHandler();

            // insert query 5b06d434c733c
            $res = $db->insertUser($keyuser, $tokenuser, $username, $email, $passHash, $tokenorg, $access_token, $apikey, $isactive, $isadmin, $code);
            $msg['msg'] = 'avsdgga';
            $msg['keyuser'] = $keyuser;
            $msg['username'] = $username;
            $msg['email'] = $email;
            $msg['passHash'] = $passHash;
            $msg['tokenorg'] = $tokenorg;
            $msg['access_token'] = $access_token;
            $msg['apikey'] = $apikey;
            $msg['isactive'] = $isactive;
            $msg['isadmin'] = $isadmin;
            $msg['code'] = $code;
            $msg['res'] = $res;
            if ($res) {
                // register log
                //$db->insertLog($operation, $access_token,$ip,$status);
                // send credentials by email
                //$res=$this->prepareMail($email,$tokenuser,$username,$pass,$code,$ip);
                if ($res) {
                    $msg = array("message" => "User created, please check your email.", "codigo" => 0);
                    //$msg = array("message" => "User created.");
                    $this->response($this->json($msg), 201);
                } else {
                    $msg = array("message" => "Cant send the email, please try again.", "codigo" => 1);
                    $this->response($this->json($msg), 400);
                }
            } else {
                $msg = array("message" => "Oops! An error occurred, please try again.", "codigo" => 1);
                $this->response($this->json($msg), 400);
            }
        } else {
            $msg = array("message" => "Something went wrong.", "codigo" => 1);
            $this->response($this->json($msg), 400);
        }
    }

    public function getOne($id)
    {
        if ($this->getRequestMethod() != "GET") {
            $msg = array("message" => "Something went wrong.");
            $this->response($this->json($msg), 400);
        }
        $db = new DbHandler();
        $data = $db->getUser($id);
        if ($data) {
            $this->response($this->json($data), 200);
        } else {
            $msg = array("message" => "No user: " . $id);
            $this->response($this->json($msg), 404);
        }
    }

    //apigw
    public function getAll()
    {
        if ($this->getRequestMethod() != "GET") {
            $msg = array("message" => "Bad Request.");
            $this->response($this->json($msg), 400);
        }
        $db = new DbHandler();
        $a_token = $db->isValidAccessToken($_GET['access_token']);
        if (!$a_token) {
            $msg['message'] = "Access denied. Invalid access_token.";
            $this->response($this->json($msg), 401);
        }
        $data = $db->getAllUsers();
        if ($data) {
            $msg['message'] = 'Ok';
            $msg['data'] = $data;
            $this->response($this->json($msg), 200);
        } else {
            $msg = array("message" => "No data.");
            $this->response($this->json($msg), 404);
        }
    }

    public function getFullData()
    {
        if ($this->getRequestMethod() != "GET") {
            $msg = array("message" => "Bad Request.");
            $this->response($this->json($msg), 400);
        }
        $db = new DbHandler();
        $data = $db->getFullData();
        if ($data) {
            $this->response($this->json($data), 200);
        } else {
            $msg = array("message" => "No data.");
            $this->response($this->json($msg), 404);
        }
    }


    public function getUserByEmail($email)
    {
        if ($this->getRequestMethod() != "GET") {
            $msg = array("message" => "Something went wrong.");
            $this->response($this->json($msg), 400);
        }
        $db = new DbHandler();
        $data = $db->getUserByEmail($email);
        if ($data) {
            $this->response($this->json($data), 200);
        } else {
            $msg = array("message" => "No user with: " . $email);
            $this->response($this->json($msg), 404);
        }
    }

    public function getUserByAccessToken($access_token)
    {
        if ($this->getRequestMethod() != "GET") {
            $msg = array("message" => "Something went wrong.");
            $this->response($this->json($msg), 400);
        }
        $db = new DbHandler();
        $data = $db->isValidAccessToken($access_token);
        if ($data) {
            $msg['message'] = 'Ok';
            $msg['data'] = $data;
            $this->response($this->json($msg), 200);
        } else {
            $msg = array("message" => "No such user: " . $access_token);
            $this->response($this->json($msg), 404);
        }
    }

    public function getUserByApiKey($api_key)
    {
        if ($this->getRequestMethod() != "GET") {
            $msg = array("message" => "Something went wrong.");
            $this->response($this->json($msg), 400);
        }
        $db = new DbHandler();
        $data = $db->isValidApiKey($api_key);
        if ($data) {
            $this->response($this->json($data), 200);
        } else {
            $msg = array("message" => "No such user: " . $api_key);
            $this->response($this->json($msg), 404);
        }
    }

    public function getUsersByOrgToken($org_token)
    {
        if ($this->getRequestMethod() != "POST") {
            $msg = array("message" => "Something went wrong.");
            $this->response($this->json($msg), 400);
        }

        $db = new DbHandler();
        $data = $db->getUsersByOrgToken($org_token);
        if ($data) {
            $msg['message'] = 'Ok.';
            $msg['data'] = $data;
            $this->response($this->json($msg), 200);
        } else {
            $msg = array("message" => "No data.");
            $msg['data'] = array();
            $this->response($this->json($msg), 404);
        }
    }





    public function delete($id)
    {
        if ($this->getRequestMethod() != "DELETE") {
            $msg = array("message" => "Something went wrong.");
            $this->response($this->json($msg), 406);
        }
        $db = new DbHandler();
        $data = $db->deleteUser($id);
        if ($data) {
            $message = array("deleted" => $id);
            $this->response($this->json($message), 200);
        } else {
            $msg = array("message" => "No user found.");
            $this->response($this->json($msg), 404);
        }
    }


    public function sendEmail($email, $asunto, $msg)
    {
        try {
            $headers = "MIME-Version: 1.0\n";
            $headers .= "Content-Type: text/plain; charset=UTF-8\n";
            $headers .= "From: <noreply@gmail.com>";
            //mb_internal_encoding("UTF-8");
            return mb_send_mail($email, $asunto, $msg, $headers);
        } catch (Exception $e) {
            $this->log->lwrite($e->getMessage());
            return false;
        }
    }
    private function prepareMail($email, $keyuser, $username, $pass, $code, $ip)
    {
        try {
            $link = "http://" . $_ENV['FRONTEND'] . "/pages/validate.php?code=" . $code . "&keyuser=" . $keyuser;
            $asunto = "Activación de cuenta";
            $mensaje = "Registro\n\n";
            $mensaje .= "Estos son tus datos de registro:\n";
            $mensaje .= "Usuario: " . $username . "\n";
            $mensaje .= "Para activar tu cuenta pulsa el siguiente enlace: \n";
            $mensaje .= $link . "\n";
            $mensaje .= "El enlace expira en una hora, si esto pasa, favor de registrarse de nuevo.\n\n";
            $se = $this->sendEmail($email, $asunto, $mensaje);
            if ($se)
                $res = true;
            else
                $res = false;
            return $res;
        } catch (PDOException $e) {
            $this->log->lwrite($e->getMessage());
            return false;
        }
    }


    //--------------------------------------------------------------------------
    //--------------------------- USERS -------------------------------
    //--------------------------------------------------------------------------

    public function usersFunction()
    {
        if ($this->getRequestMethod() != "POST") {
            $msg = array("message" => "Something went wrong.");
            $this->response($this->json($msg), 406);
        }
        $db = new DbHandler();
        //$response = $db->isValidAccessToken($_GET['access_token']);
        //if ( isset($this->_request['option']) && isset($response['tokenuser']) ) {
        if (isset($this->_request['option'])) {
            switch ($this->_request['option']) {
                case 'NEW':
                    if (isset($this->_request['username']) && isset($this->_request['email']) && isset($this->_request['password']) && isset($this->_request['tokenorg'])) {
                        $this->validateEmail($this->_request['email']);
                        $this->validatePass($this->_request['password']);
                        $this->validateUser($this->_request['username']);
                        $this->validateTokenorg($this->_request['tokenorg']);

                        require_once 'db/PassHash.php';

                        $uex = $this->isUserExist($this->_request['username'], $this->_request['email']);

                        //if (!$uex) {
                        $username = $this->_request['username'];
                        $email = $this->_request['email'];
                        $pass = $this->_request['password'];
                        $isadmin = false;
                        $isactive = true;
                        // Generating password hash
                        $passwordHash = PassHash::hash($this->_request['password']);
                        // Generating keys
                        $keyuser = $this->generateToken();
                        $tokenuser = $this->generateSHA256Token();
                        $apikey = $this->generateToken();
                        $tokenorg = $this->_request['tokenorg'];
                        $access_token = $this->generateSHA256Token();

                        $operation = 'Create user';
                        $status = 1;
                        // activation code and dates
                        $code = uniqid();
                        //$ip = $this->getGeolocationIP();

                        // insert query
                        $res = $db->insertUser($keyuser, $tokenuser, $username, $email, $passwordHash, $tokenorg, $access_token, $apikey, $isactive, $isadmin, $code);

                        if ($res) {
                            // register log
                            //$db->insertLog($operation, $access_token,$ip,$status);
                            // send credentials by email
                            //$res=$this->prepareMail($email,$keyuser,$username,$pass,$code,$ip);
                            if ($res) {
                                //$msg = array("message" => "User created, please check your email.");
                                $msg['message'] = 'User created.';
                                //$msg['tokenuser'] = $tokenuser;
                                //$msg['access_token'] = $access_token;
                                $msg['username'] = $username;
                                $this->response($this->json($msg), 201);
                            } else {
                                $msg = array("message" => "Oops! An error occurred while registering.");
                                $this->response($this->json($msg), 400);
                            }
                        } else {
                            $msg = array("message" => "Oops! An error occurred while registering.");
                            $this->response($this->json($msg), 400);
                        }
                    } else {
                        $msg = array("message" => "Something went wrong.");
                        $this->response($this->json($msg), 400);
                    }

                    break;
                case 'DELETE':
                    $db = new DbHandler();
                    $a_token = $db->isValidAccessToken($_GET['access_token']);
                    if (!$a_token) {
                        $msg['message'] = "Access denied. Invalid access token.";
                        $this->response($this->json($msg), 401);
                    }
                    if (isset($this->_request['tokenuser'])) {
                        $this->validateTokenUser($this->_request['tokenuser']);
                        $data = $db->deleteUser($this->_request['tokenuser']);
                        if ($data) {
                            $msg['message'] = "Deleted ";
                            $msg['tokenuser'] = $this->_request['tokenuser'];
                            $this->response($this->json($msg), 200);
                        } else {
                            $msg = array("message" => "Something went wrong.");
                            $this->response($this->json($msg), 406);
                        }
                    } else {
                        $msg['message'] = "Invalid data.";
                        $this->response($this->json($msg), 400);
                    }
                    break;
                case 'MODIFY':
                    $a_token = $db->isValidAccessToken($_GET['access_token']);
                    if (!$a_token) {
                        $msg['message'] = "Access denied. Invalid access token.";
                        $this->response($this->json($msg), 401);
                    }
                    if (isset($this->_request['tokenuser'])) {
                        $this->validateTokenUser($this->_request['tokenuser']);
                        switch (true) {
                            case (isset($this->_request['username'])): //edit username
                                $data = $this->editUsername($this->_request['tokenuser'], $this->_request['username']);
                                if ($data) {
                                    $msg['message'] = "Username Modified";
                                    $msg['tokenuser'] = $this->_request['tokenuser'];
                                    $this->response($this->json($msg), 200);
                                } else {
                                    $msg = array("message" => "Something went wrong.");
                                    $this->response($this->json($msg), 406);
                                }
                                break;
                            case (isset($this->_request['email'])): //edit email
                                $data = $this->editEmail($this->_request['tokenuser'], $this->_request['email']);
                                if ($data) {
                                    $msg['message'] = "Email Modified";
                                    $msg['tokenuser'] = $this->_request['tokenuser'];
                                    $this->response($this->json($msg), 200);
                                } else {
                                    $msg = array("message" => "Something went wrong.");
                                    $this->response($this->json($msg), 406);
                                }
                                break;
                            case (isset($this->_request['old_password']) && isset($this->_request['new_password'])): //edit password
                                $data = $this->editUserPass($this->_request['tokenuser'], $this->_request['old_password'], $this->_request['new_password']);
                                if ($data) {
                                    $msg['message'] = "Password Modified";
                                    $msg['tokenuser'] = $this->_request['tokenuser'];
                                    $this->response($this->json($msg), 200);
                                } else {
                                    $msg = array("message" => "Something went wrong.");
                                    $this->response($this->json($msg), 406);
                                }
                                break;
                            default:
                                $msg['message'] = "Invalid action.";
                                $msg['request'] = $this->_request;
                                $this->response($this->json($msg), 400);
                                break;
                        }
                    } else {
                        $msg['message'] = "Invalid action.";
                        $this->response($this->json($msg), 400);
                    }
                    break;
                case 'LOGIN':
                    if (isset($this->_request['user']) && isset($this->_request['password'])) {
                        $data = $this->loginU($this->_request['user'], $this->_request['password']);
                        if ($data) {
                            $msg['message'] = "Ok.";
                            $msg['data'] = $data;
                            $this->response($this->json($msg), 200);
                        } else {
                            $msg['message'] = "Incorrect credentials.";
                            $this->response($this->json($msg), 406);
                        }
                    } else {
                        $msg['message'] = "Invalid action.";
                        $this->response($this->json($msg), 400);
                    }
                    break;
                case 'VIEW':
                    $a_token = $db->isValidAccessToken($_GET['access_token']);
                    if (!$a_token) {
                        $msg['message'] = "Access denied. Invalid access token.";
                        $this->response($this->json($msg), 401);
                    }
                    if (isset($this->_request['by'])) {
                        switch ($this->_request['by']) {
                            case 'ORG':
                                if (isset($this->_request['tokenorg'])) {
                                    $tokenorg = $this->_request['tokenorg'];
                                    $db = new DbHandler();
                                    $this->validateTokenorg($tokenorg);
                                    $data = $db->getUsersByOrgToken($tokenorg);
                                    if ($data) {
                                        $msg['message'] = "Ok";
                                        $msg['data'] = $data;
                                        $this->response($this->json($msg), 200);
                                    } else {
                                        $msg = array("message" => "No data.");
                                        $msg['data'] = array();
                                        $this->response($this->json($msg), 406);
                                    }
                                } else {
                                    $msg['message'] = "Invalid data.";
                                    $this->response($this->json($msg), 400);
                                }
                                break;
                        }
                    } else {
                        $msg['message'] = "Invalid action.";
                        $this->response($this->json($msg), 400);
                    }
                    break;
                case 'CHANGETOKEN':
                    $a_token = $db->isValidAccessToken($_GET['access_token']);
                    if (!$a_token) {
                        $msg['message'] = "Access denied. Invalid access token.";
                        $this->response($this->json($msg), 401);
                    }
                    if (isset($this->_request['tokenuser'])) {
                        $user = $this->changeUserTokens($this->_request['tokenuser']);
                        if ($user) {
                            $msg['message'] = "Token changed.";
                            //$msg['tokenuser'] = $this->_request['tokenuser'];
                            $this->response($this->json($msg), 200);
                        } else {
                            $msg['message'] = "Invalid token.";
                            $this->response($this->json($msg), 400);
                        }
                    }
                    break;
                default:
                    $msg['message'] = "Invalid action.";
                    $this->response($this->json($msg), 400);
                    break;
            }
        } else {
            $msg['message'] = "Something went wrong.";
            $msg['tokenuser'] = $_GET['access_token'];
            $msg['response'] = $response;
            $this->response($this->json($msg), 406);
        }
    }

    function validateUser($user)
    {
        if (!preg_match('/^[a-zA-Z0-9]{3,}$/', $user)) {
            $msg['message'] = "Invalid username.";
            $msg['codigo'] = 1;
            $this->response($this->json($msg), 400);
            exit();
        }
    }

    function validatePass($pass)
    {
        // ^(?=.*[A-Z].*[A-Z])(?=.*[!@#$&*])(?=.*[0-9].*[0-9])(?=.*[a-z].*[a-z].*[a-z]).{8}$
        if (!preg_match('/^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$/', $pass)) {
            $msg['message'] = "Insecure password.";
            $msg['codigo'] = 1;
            $this->response($this->json($msg), 400);
            exit();
        }
    }

    function validateEmail($email)
    {
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $msg['message'] = "Invalid email address.";
            $msg['codigo'] = 1;
            $this->response($this->json($msg), 400);
            exit();
        }
    }

    function validateTokenorg($org)
    {
        $db = new DbHandler();
        $valid = $db->validateTokenorg($org);
        if (!$valid) {
            $msg['message'] = "Invalid Organization Token.";
            //$msg['token'] = $org;
            //$msg['type'] = gettype($org);
            $this->response($this->json($msg), 400);
            exit();
        }
    }

    function isUserExist($user, $email)
    {
        $db = new DbHandler();
        $valid = $db->isUserExist($user, $email);
        if ($valid) {
            $msg = array("message" => "Sorry, this user o email already exist.");
            $this->response($this->json($msg), 400);
            exit();
        }
    }

    function validateAccessToken($token)
    {
        $db = new DbHandler();
        $valid = $db->validateAccessToken($token);
        if (!$valid) {
            $msg['message'] = "Invalid Token.";
            $this->response($this->json($msg), 400);
            exit();
        }
    }

    //--------------------------- edit user -------------------------------
    function validateUsername($uname)
    {
        $db = new DbHandler();
        $valid = $db->validateUsername($uname);
        if ($valid) {
            $msg['message'] = "Username already exist.";
            $this->response($this->json($msg), 400);
            exit();
        }
    }

    function editUsername($user, $uname)
    {
        $this->validateUsername($uname);
        $db = new DbHandler();
        $edit = $db->editUserName($user, $uname);
        return $edit;
    }


    function validateEmail2($email)
    {
        $db = new DbHandler();
        $valid = $db->validateEmail($email);
        if ($valid) {
            $msg['message'] = "Email already exist.";
            $this->response($this->json($msg), 400);
            exit();
        }
    }

    function editEmail($user, $email)
    {
        $this->validateEmail2($email);
        $db = new DbHandler();
        $edit = $db->editUserEmail($user, $email);
        return $edit;
    }

    //--------------------------- edit pass -------------------------------
    public function editUserPass($user, $oldpass, $newpass)
    {
        //if ($this->getRequestMethod() != "PUT") {
        //$msg['message'] = "Bad Request.";
        //$this->response($this->json($msg), 400);
        //}
        //if (isset($this->_request['keyuser']) && isset($this->_request['password'])) {
        require_once 'db/PassHash.php';
        $db = new DbHandler();
        $hash = $db->getPassByToken($user);

        if ($oldpass == $newpass) {
            $msg['message'] = "Equal Passwords.";
            $this->response($this->json($msg), 400);
        } elseif (!PassHash::checkPassword($hash['password'], $oldpass)) {
            $msg['message'] = "Access Denied.";
            $this->response($this->json($msg), 400);
        } elseif (PassHash::checkPassword($hash['password'], $newpass)) {
            $msg['message'] = "Cant use this password.";
            $this->response($this->json($msg), 400);
        } else {
            $this->validatePass($newpass);
            $pass = PassHash::hash($newpass);
            $data = $db->editUserPass($user, $pass);
            if ($data) {
                $res = true;
            } else {
                $res =  false;
            }
            return $res;
        }
    }

    //--------------------------- login -------------------------------
    public function loginU($user, $pass)
    {
        require_once 'db/PassHash.php';
        $db = new DbHandler();
        $hash = $db->getPassByUser($user);
        if (PassHash::checkPassword($hash['password'], $pass)) {
            // User password is correct
            unset($hash['password']);
            $res = $hash;
        } else {
            // user password is incorrect
            $res = false;
        }
        return $res;
    }


    //--------------------------- change user tokens -------------------------------
    function changeUserTokens($tuser)
    {
        $db = new DbHandler();
        $user = $db->getUserByToken($tuser);
        if ($user) {
            $newToken = $this->generateSHA256Token();
            $res = $db->changeToken($newToken, $tuser);
            if ($res) {
                return $newToken;
            } else {
                return false;
            }
        } else {
            $msg['message'] = "Invalid Token.";
            $this->response($this->json($msg), 400);
            exit();
        }
    }

    function changeUsersTokens()
    {
        $db = new DbHandler();
        $users = $db->getKeyUsers();
        //$failed = array();
        foreach ($users as $key) {
            $newToken = $this->generateSHA256Token();
            $res = $db->changeToken($newToken, $key['keyuser']);
            if (!$res) {
                //array_push($failed,$key['keyuser']);
                $failed[] = $key['keyuser'];
            }
        }
        if ($failed) {
            $msg['message'] = "Token change fails.";
            $msg['data'] = $failed;
            $this->response($this->json($msg), 400);
        } else {
            $msg['message'] = "Token changed.";
            $this->response($this->json($msg), 200);
            exit();
        }
    }

    //--------------------------- user by token -------------------------------
    public function getUserByTokenUser($token)
    {
        if ($this->getRequestMethod() != "GET") {
            $msg = array("message" => "Something went wrong.");
            $this->response($this->json($msg), 400);
        }
        $db = new DbHandler();
        $data = $db->getUserByToken($token);

        if ($data) {
            $msg['message'] = 'Ok.';
            $msg['data'] = $data;
            $this->response($this->json($msg), 200);
        } else {
            $msg = array("message" => "No data.");
            $msg['data'] = array();
            $this->response($this->json($msg), 404);
        }
    }

    function validateTokenUser($token)
    {
        $db = new DbHandler();
        $valid = $db->validateTokenUser($token);
        if (!$valid) {
            $msg['message'] = "Invalid Token.";
            $this->response($this->json($msg), 400);
            exit();
        }
    }



    //--------------------------------------------------------------------------
    //--------------------------- HIERARCHY -------------------------------
    //--------------------------------------------------------------------------

    public function hierarchyFunction()
    {
        if ($this->getRequestMethod() != "POST") {
            $msg = array("message" => "Something went wrong.");
            $this->response($this->json($msg), 406);
        }
        //$response = $this->auth();
        //if ( isset($this->_request['option']) && isset($response['tokenuser']) ) {
        if (isset($this->_request['option'])) {
            switch ($this->_request['option']) {
                case 'NEW':
                    if (isset($this->_request['acronym']) && isset($this->_request['fullname']) && isset($this->_request['fathers_token'])) {
                        //$this->_request['fullname'] = str_replace(" ", "_", $this->_request['fullname']);
                        $db = new DbHandler();
                        $this->hierarchyExist($this->_request['acronym'], $this->_request['fullname']);
                        $keyhierarchy = $this->generateToken();
                        $tokenH = $this->generateSHA256Token();
                        if ($this->_request['fathers_token'] == '/') {

                            $data = $db->newHierarchy($keyhierarchy, $this->_request['acronym'], $this->_request['fullname'], $tokenH, $this->_request['fathers_token']);
                            if ($data) {
                                //$tokenOrg = $this->generateSHA256Token();
                                $db->insertTokenHierarchyMapping($keyhierarchy, $tokenH);
                                //$msg['message'] = "Created org ".$this->_request['acronym'];
                                $msg['message'] = "Organization Created";
                                $msg['tokenhierarchy'] = $tokenH;
                                $this->response($this->json($msg), 201);
                            } else {
                                $msg = array("message" => "Something went wrong.112");
                                $this->response($this->json($msg), 406);
                            }
                        } else {
                            $father = $this->tokenFatherHExist($this->_request['fathers_token']);
                            //$keyhierarchy = $this->generateToken();
                            //$tokenH = $this->generateSHA256Token();
                            $data = $db->newHierarchy($keyhierarchy, $this->_request['acronym'], $this->_request['fullname'], $tokenH, $father['keyhierarchy']);
                            if ($data) {
                                $db->insertTokenHierarchyMapping($keyhierarchy, $father['tokenorg']);
                                $msg['message'] = "Created: " . $this->_request['acronym'];
                                $msg['tokenhierarchy'] = $tokenH;
                                $msg['token organization'] = $father['tokenorg'];
                                $this->response($this->json($msg), 201);
                            } else {
                                $msg = array("message" => "Something went wrong.122");
                                $this->response($this->json($msg), 406);
                            }
                        }
                    } else {
                        $msg['message'] = "Invalid data.";
                        $this->response($this->json($msg), 400);
                    }
                    break;
                case 'DELETE':
                    $db = new DbHandler();
                    $a_token = $db->isValidAccessToken($_GET['access_token']);
                    if (!$a_token) {
                        $msg['message'] = "Access denied. Invalid access token.";
                        $this->response($this->json($msg), 401);
                    }
                    if (isset($this->_request['tokenhierarchy'])) {
                        $hi = $this->tokenFatherHExist($this->_request['tokenhierarchy']);
                        $del = $db->deleteHierarchy($this->_request['tokenhierarchy']);
                        //borrar recursivo
                        $child = $this->display_childrenH($hi['keyhierarchy'], 0);
                        foreach ($child as $k) {
                            $db->deleteHierarchyByKey($k['keyhierarchy']);
                        }
                        if ($child || $del) {
                            $msg['message'] = "Deleted";
                            $msg['tokenhierarchy'] = $this->_request['tokenhierarchy'];
                            $this->response($this->json($msg), 200);
                        } else {
                            $msg = array("message" => "Something went wrong.");
                            $this->response($this->json($msg), 406);
                        }
                    } else {
                        $msg['message'] = "Invalid data.";
                        $this->response($this->json($msg), 400);
                    }
                    break;
                case 'MODIFY':
                    $db = new DbHandler();
                    $a_token = $db->isValidAccessToken($_GET['access_token']);
                    if (!$a_token) {
                        $msg['message'] = "Access denied. Invalid access token.";
                        $this->response($this->json($msg), 401);
                    }
                    if (isset($this->_request['token']) && isset($this->_request['acronym']) && isset($this->_request['fullname'])) {
                        //$this->_request['acronym'] = str_replace(" ", "_", $this->_request['acronym']);
                        $this->tokenFatherHExist($this->_request['token']);
                        $data = $db->modifyHierarchy($this->_request['token'], $this->_request['acronym'], $this->_request['fullname']);
                        if ($data) {
                            $msg['message'] = "Modified";
                            $msg['tokenhierarchy'] = $this->_request['token'];
                            $this->response($this->json($msg), 200);
                        } else {
                            $msg = array("message" => "Something went wrong.");
                            $this->response($this->json($msg), 406);
                        }
                    } else {
                        $msg['message'] = "Invalid data.";
                        $this->response($this->json($msg), 400);
                    }
                    break;
                case 'CHECK':
                    if (isset($this->_request['acronym']) && isset($this->_request['fullname']) && isset($this->_request['fathers_token'])) {
                        $res = $this->hierarchyExist($this->_request['acronym'], $this->_request['fullname']);
                        if (!$res) {
                            $msg['message'] = "Acronym and name available.";
                            $msg['code'] = 1;
                            $this->response($this->json($msg), 200);
                        }
                    }
                    break;
                case 'VIEW':
                    $db = new DbHandler();
                    $a_token = $db->isValidAccessToken($_GET['access_token']);
                    if (!$a_token) {
                        $msg['message'] = "Access denied. Invalid access token.";
                        $this->response($this->json($msg), 401);
                    }
                    if (isset($this->_request['tokenhierarchy']) && isset($this->_request['direction'])) {
                        switch ($this->_request['direction']) {
                            case 'UP':
                                $key = $this->tokenFatherHExist($this->_request['tokenhierarchy']);
                                $data = $this->get_pathH($key['keyhierarchy']);
                                if ($data) {
                                    $msg['message'] = "Ok";
                                    $msg['data'] = $data;
                                    $this->response($this->json($msg), 200);
                                } else {
                                    $msg['message'] = "No up data.";
                                    $msg['data'] = array();
                                    $this->response($this->json($msg), 406);
                                }
                                break;
                            case 'DOWN':
                                $key = $this->tokenFatherHExist($this->_request['tokenhierarchy']);
                                $data = $this->display_childrenH($key['keyhierarchy'], 0);
                                if ($data) {
                                    foreach ($data as &$key) {
                                        unset($key['keyhierarchy']);
                                    }
                                    $msg['message'] = "Ok";
                                    $msg['data'] = $data;
                                    $this->response($this->json($msg), 200);
                                } else {
                                    $msg['message'] = "No down data.";
                                    $msg['data'] = array();
                                    $this->response($this->json($msg), 406);
                                }
                                break;
                            default:
                                $msg['message'] = "Invalid data.";
                                $this->response($this->json($msg), 400);
                                break;
                        }
                        // for all
                        //$db = new DbHandler();
                        //$data = $db->deleteHierarchy($this->_request['tokenhierarchy']);
                    } else {
                        $msg['message'] = "Invalid data.";
                        $this->response($this->json($msg), 400);
                    }
                    break;
                case 'CHANGETOKEN':
                    $db = new DbHandler();
                    $a_token = $db->isValidAccessToken($_GET['access_token']);
                    if (!$a_token) {
                        $msg['message'] = "Access denied. Invalid access token.";
                        $this->response($this->json($msg), 401);
                    }
                    if (isset($this->_request['tokenhierarchy'])) {
                        //$this->changeHTokens();
                        $chn = $this->changeHTokenByOrg($this->_request['tokenhierarchy']);
                        if ($chn) {
                            $msg['message'] = "Token changed.";
                            $this->response($this->json($msg), 200);
                        } else {
                            $msg['message'] = "Token change fails.";
                            $this->response($this->json($msg), 400);
                            exit();
                        }
                    } else {
                        $msg['message'] = "Invalid data.";
                        $this->response($this->json($msg), 400);
                    }
                    break;
                default:
                    $msg['message'] = "Invalid action.";
                    $this->response($this->json($this->_request), 400);
                    break;
            }
        } else {
            $msg = array("message" => "Something went wrong.123");
            $this->response($this->json($msg), 406);
        }
    }

    private function display_childrenH($parent, $level)
    {
        $db = new DbHandler();
        $data = $db->selectChildrenH($parent);
        $path = array();
        if ($data) {
            foreach ($data as $key) {
                $path[] = $key;
                $path = array_merge($this->display_childrenH($key['keyhierarchy'], $level + 1), $path);
            }
        }
        return $path;
    }

    // el ultimo nivel no quita las key (no funciona)
    private function display_childrenHwithoutKeys($parent, $level)
    {
        $db = new DbHandler();
        $data = $db->selectChildrenH($parent);
        $path = array();
        if ($data) {
            foreach ($data as $key) {
                $key[] = $level;
                $temp = $key['keyhierarchy'];
                unset($key['keyhierarchy']);
                $path[] = $key;
                $path = array_merge($this->display_childrenH($temp, $level + 1), $path);
            }
        }
        return $path;
    }



    private function get_pathH($node)
    {
        $db = new DbHandler();
        $data = $db->selectNodeH($node);
        $path = array();
        $path[] = $data;
        if (isset($data['father']) && $data['father'] != '/') {
            //$path[] = $data['father'];
            $path = array_merge($this->get_pathH($data['father']), $path);
        }
        return $path;
    }

    public function hierarchyExist($acron, $name)
    {
        $db = new DbHandler();
        $data = $db->hierarchyExist($acron, $name);
        if ($data) {
            $msg['message'] = "Cant use this acronym or name.";
            $msg['code'] = 0;
            $this->response($this->json($msg), 400);
        }
        return false;
    }

    public function tokenFatherHExist($token)
    {
        $db = new DbHandler();
        $data = $db->tokenFatherHExist($token);
        if (!$data) {
            $msg['message'] = "Invalid hierarchy token.";
            $this->response($this->json($msg), 400);
        } else {
            return $data;
        }
    }

    public function fatherhExist($father)
    {
        $db = new DbHandler();
        $data = $db->fatherhExist($father);
        if (!$data) {
            $msg['message'] = "Invalid data.";
            $this->response($this->json($msg), 400);
        }
    }


    //--------------------------- change hierarchy tokens -------------------------------
    function changeHTokenByOrg($org)
    {
        $db = new DbHandler();
        $keys = $db->getKeyHierarchyByOrg($org);
        $newToken = $this->generateSHA256Token();
        //$res2=$db->changeTokenHierarchyOrg($newToken,$org);
        $res = $db->changeTokenHierarchy($newToken, $keys['keyhierarchy']);
        if ($res) {
            //return $newtoken;
            return true;
        } else {
            return false;
        }
    }

    function changeHTokens()
    {
        $db = new DbHandler();
        $keys = $db->getKeyHierarchy();
        //$failed = array();
        foreach ($keys as $key) {
            $newToken = $this->generateSHA256Token();
            $res = $db->changeTokenHierarchy($newToken, $key['keyhierarchy']);
            if (!$res) {
                //array_push($failed,$key['keyhierarchy']);
                $failed[] = $key['keyhierarchy'];
            }
        }
        if ($failed) {
            $msg['message'] = "Token change fails.";
            $msg['data'] = $failed;
            $this->response($this->json($msg), 400);
        } else {
            $msg['message'] = "Token changed.";
            $this->response($this->json($msg), 200);
            exit();
        }
    }




    //--------------------------------------------------------------------------
    //--------------------------- FUNCTIONS -------------------------------
    //--------------------------------------------------------------------------
    public function getGeolocationIP()
    {
        try {
            $url = 'http://ip-api.com/json';
            $ch  = curl_init($url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            $response = curl_exec($ch);
            curl_close($ch);
            if (!$response) {
                return false;
            } else {
                // parse the data and return the geo-ip
                $res = (array) json_decode($response, true);
                $sip = $res['query'];
                if (preg_match('/^(([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]).){3}([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/', $sip))
                    return $sip;
                else
                    return false;
            }
        } catch (Exception $e) {
            $this->log->lwrite($e->getMessage());
            return false;
        }
    }

    public function getRealIP()
    {
        try {
            if (!empty($_SERVER['HTTP_CLIENT_IP']))
                return $_SERVER['HTTP_CLIENT_IP'];
            if (!empty($_SERVER['HTTP_X_FORWARDED_FOR']))
                return $_SERVER['HTTP_X_FORWARDED_FOR'];
            return $_SERVER['REMOTE_ADDR'];
        } catch (Exception $e) {
            $this->log->lwrite($e->getMessage());
            return false;
        }
    }

    /** 256 - 076a89c23179cedfc61171fe400ecf01fb76b9a48a68fb82dd0cd688d684d900
     * Generating random Unique hash String for user Api key
     * @return String    User api key
     */
    private function generateToken()
    {
        return sha1(join('', array(time(), rand())));
    }

    private function generateSHA256Token()
    {
        return hash('sha256', join('', array(time(), rand())), false);
    }



    public function redirect($url, $statusCode = 303)
    {
        header('Location: ' . $url, true, $statusCode);
        die();
    }

    public function notFound()
    {
        $msg = array("Error" => "Not Found.");
        $this->response($this->json($msg), 404);
    }


    //--------------------------------------------------------------------------
    //--------------------------- dev only -------------------------------
    //--------------------------------------------------------------------------
    public function getAllHierarchy()
    {
        if ($this->getRequestMethod() != "GET") {
            $msg = array("message" => "Something went wrong.");
            $this->response($this->json($msg), 406);
        }
        $db = new DbHandler();

        $data = $db->getAllHierarchy();
        if ($data) {
            $msg['message'] = 'Ok';
            $msg['data'] = $data;
            $this->response($this->json($msg), 200);
        } else {
            $msg = array("message" => "No data.");
            $this->response($this->json($msg), 404);
        }
    }
}
