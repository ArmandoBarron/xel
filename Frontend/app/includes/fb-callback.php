<?php
include_once("../resources/conf.php");
include_once(SESIONES);
//INICIA LA SESIÓN
Sessions::startSession("buscador");
include_once(LIBRARY."/Facebook/autoload.php");

$fb = new Facebook\Facebook([
	'app_id'                => '315200965581285',
	'app_secret'            => '55d2259705fda5fe2e3a8778f2efdfe6',
	'default_graph_version' => 'v2.10',
  ]);
   
$helper = $fb->getRedirectLoginHelper();

try {
	if (isset($_SESSION['facebook_access_token'])) {
		$accessToken = $_SESSION['facebook_access_token'];
	} else {
  		$accessToken = $helper->getAccessToken();
	}
} catch(Facebook\Exceptions\FacebookResponseException $e) {
 	// When Graph returns an error
 	echo 'Graph returned an error: ' . $e->getMessage();
  	exit;
} catch(Facebook\Exceptions\FacebookSDKException $e) {
 	// When validation fails or other local issues
	echo 'Facebook SDK returned an error: ' . $e->getMessage();
  	exit;
}

if (isset($accessToken)) {
	if (isset($_SESSION['facebook_access_token'])) {
		$fb->setDefaultAccessToken($_SESSION['facebook_access_token']);
	} else {
		// getting short-lived access token
		$_SESSION['facebook_access_token'] = (string) $accessToken;
	  	// OAuth 2.0 client handler
		$oAuth2Client = $fb->getOAuth2Client();
		// Exchanges a short-lived access token for a long-lived one
		$longLivedAccessToken = $oAuth2Client->getLongLivedAccessToken($_SESSION['facebook_access_token']);
		$_SESSION['facebook_access_token'] = (string) $longLivedAccessToken;
		// setting default access token to be used in script
		$fb->setDefaultAccessToken($_SESSION['facebook_access_token']);
	}
	// redirect the user back to the same page if it has "code" GET variable
	if (isset($_GET['code'])) {
	   header("Location: ".$_SESSION['actual_url']);
	}
	// getting basic info about user
	try {
		$profile_request = $fb->get('/me?fields=name,first_name,last_name,email');
		$profile = $profile_request->getGraphNode()->asArray();
	} catch(Facebook\Exceptions\FacebookResponseException $e) {
		// When Graph returns an error
		echo 'Graph returned an error: ' . $e->getMessage();
		session_destroy();
		// redirecting user back to app login page
		header("Location: ".$_SESSION['actual_url']);
		exit;
	} catch(Facebook\Exceptions\FacebookSDKException $e) {
		// When validation fails or other local issues
		echo 'Facebook SDK returned an error: ' . $e->getMessage();
		exit;
	}

	// printing $profile array on the screen which holds the basic info about user
	include_once(CLASES . "/class.Sessions.php");
	include_once(CLASES . "/class.Logs.php");
	$_SESSION['user'] = $profile['first_name'];
	$_SESSION['email'] = $profile['email'];

	$session = new Sessions();
	$aux = $session->signup($profile['email'],$profile['first_name'],$profile['id']);
	$s = Logs::saveSession($aux['id'],null,null,null);
	$_SESSION['id'] = $aux['id'];
	$_SESSION['session_id'] = $s;
}
?>
