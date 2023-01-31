<?php

require_once "models/User.php";

$api = new User;

if (isset($_GET['type'])) {
	$type = $_GET['type'];
	switch ($type) {
		
		case 2:
			$api->getOne($api->_request['id']);
			break;
		case 3:
			$api->createUserAdmin();
			break;
		case 33:
			$api->createUser();
			break;
		case 4:
			$api->delete($api->_request['keyuser']);
			break;
		case 5:
			$api->activation($api->_request['code'], $api->_request['tokenuser']);
			break;
		case 6: //
			$api->login();
			break;
		case 7:
			$api->editUserName();
			break;
		case 8:
			$api->editUserEmail();
			break;
		case 9:
			$api->editUserPass();
			break;
		case 10:
			$api->activateUser();
			break;
		case 11:
			$api->deactivateUser();
			break;
		case 12:
			$api->getUserByEmail($api->_request['email']);
			break;
		
			break;
		case 14:
			$api->getUserByApiKey($api->_request['api_key']);
			break;
		case 15: //this
			$api->getUsersByOrgToken($api->_request['tokenorg']);
			break;
		case 16:
			$api->getFullData();
			break;


			

		case 50:
			$api->hierarchyFunction();
			break;
		case 51:
			$api->usersFunction();
			break;
		case 61:
			$api->createUser();
			break;
		case 62:
			$api->createUserFromGlobal();
			break;
		case 52:
			$api->getUserByTokenUser($api->_request['tokenuser']);
			break;
		case 53:
			$api->getUserByAccessToken($api->_request['access_token']);
		case 99:
			$api->getAllHierarchy();
			break;
		case 100:
			$api->getAll($_GET['access_token']);
			break;


		default:
			$api->notFound();
			break;
	}
}else{
	$api->notFound();	
}
