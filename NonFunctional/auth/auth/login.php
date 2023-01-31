<?php
        session_start();

        $_POST = json_decode(file_get_contents('php://input'), true);
        //$_POST = file_get_contents('php://input');
        $ip=$_POST['location']['host'];
        $data=json_encode(array('email' => $_POST['email'], 'password' => $_POST['password']));

        $url = 'auth/auth/v1/users/login';
        // http://127.0.0.1:47011/auth/v1/users/login
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_POST, true); 
        curl_setopt($ch, CURLOPT_HEADER, false); 
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); 
        curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data); 
        $response = curl_exec($ch);
        curl_close($ch);
        

        if (!$response) {
                return false;
        }else{
                $response= json_decode($response, true);
                $_SESSION['connected']=1;
                foreach ($response as $key => $value) {
                        $_SESSION[$key] = $value;
                }
                $_SESSION['ip']=$ip;
                echo 'ok';
        }
       

?>