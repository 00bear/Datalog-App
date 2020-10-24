<?php

header('Content-Type: application/json');
 
include_once './dbconfig.php';
require_once './classes/user.php';

$username = @$_REQUEST['username'];
$oldPassword = @$_REQUEST['oldPassword'];
$newPassword = @$_REQUEST['newPassword'];

list($msec, $sec) = explode(' ', microtime());
$timestamp = (int) ($sec.substr($msec, 2, 3));

$responseArray = array();

if($username == NULL || $username == "") {
	$responseArray = array('status' => 'fail', 'message' => 'Please provide username');
	echo json_encode($responseArray);
}
else if($oldPassword == NULL || $oldPassword == "") {
	$responseArray = array('status' => 'fail', 'message' => 'Please provide old password');
	echo json_encode($responseArray);
}
else if($newPassword == NULL || $newPassword == "") {
	$responseArray = array('status' => 'fail', 'message' => 'Please provide new password');
	echo json_encode($responseArray);
}
else {
    $user = new User();
    $result = $user->update($username, $oldPassword, $newPassword);
    if($result) {
        $responseArray = array('message' => $result,);
	}
	else {
		$responseArray = array('status' => 'fail', 'message' => 'Please try again after sometime or contact to the KMSOFT kmsoft2013@gmail.com');
    }
    echo json_encode($responseArray);
}
?>