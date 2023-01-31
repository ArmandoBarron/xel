<?php
include_once("../resources/conf.php");
include_once(LIBRARY . "/phpmailer/PHPMailerAutoload.php");

$mail = new PHPMailer();
$mail->setLanguage('es');

$from = "ggeoportal@gmail.com";
$fromName = "Geoportal";

$host 		= "smtp.gmail.com";
$username 	= "ggeoportal@gmail.com";
$password 	= "auja7f8y";
$port 		= 465;
$secure 	= false;

echo $mensaje;

$mail->isSMTP();
$mail->Host = $host;
$mail->SMTPAuth = true;
$mail->Username = $username;
$mail->Password = $password;
$mail->Port = $port;
$mail->SMTPSecure = $secure;

$mail->From = $from;
$mail->FromName = $fromName;
$mail->addReplyTo($from,$fromName);

$mail->addAddress($destinatario,"user");
$mail->isHTML(true);
$mail->CharSet = 'utf-8';
$mail->WordWrap = 70;

$mail->Subject = $asunto;
$mail->Body = $mensaje;
//$mail->AltBody = "Carrito de compras<br>".$mensaje;

$send = $mail->Send();
if($send){
	echo "true";
}else{
	echo "true";
}

?> 
