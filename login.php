<?php

header('Content-Type: application/json');
 
include_once './dbconfig.php';
require_once './classes/user.php';

$username = @$_REQUEST['username'];
$password = @$_REQUEST['password'];

$responseArray = array();

if($username == NULL || $username == "") {
	$responseArray = array('status' => 'fail', 'message' => 'Please provide username');
	echo json_encode($responseArray);
}
else if($password == NULL || $password == "") {
	$responseArray = array('status' => 'fail', 'message' => 'Please provide password');
	echo json_encode($responseArray);
}
else if(strlen($password) < 6){
	$responseArray = array('status' => 'fail', 'message' => 'Your Password Must Contain At Least 6 Characters!');
}
else {
    $user = new User();
    $result = $user->login($username, $password);
    if($result) {
        $responseArray = array('status' => 'success', 'user' => $result);
	}
	else {
		$responseArray = array('status' => 'fail', 'message' => 'Username or password incorrect.');
    }
    echo json_encode($responseArray);
}
?>