<?php

header('Content-Type: application/json');
 
include_once './dbconfig.php';
require_once './classes/user.php';

$firstname = @$_REQUEST['firstname'];
$lastname = @$_REQUEST['lastname'];
$username = @$_REQUEST['username'];
$password = @$_REQUEST['password'];
list($msec, $sec) = explode(' ', microtime());
$timestamp = (int) ($sec.substr($msec, 2, 3));

$responseArray = array();

if($firstname == NULL || $firstname == "") {
	$responseArray = array('status' => 'fail', 'message' => 'Please provide firstname');
	echo json_encode($responseArray);
}
else if($lastname == NULL || $lastname == "") {
	$responseArray = array('status' => 'fail', 'message' => 'Please provide lastname');
	echo json_encode($responseArray);
}
else if($username == NULL || $username == "") {
	$responseArray = array('status' => 'fail', 'message' => 'Please provide email');
	echo json_encode($responseArray);
}
else if($password == NULL || $password == "") {
	$responseArray = array('status' => 'fail', 'message' => 'Please provide password');
	echo json_encode($responseArray);
}
else if(strlen($password) < 6){
    $responseArray = array('status' => 'fail', 'message' => 'Your Password Must Contain At Least 6 Characters!');
    echo json_encode($responseArray);
}
else {
    $user = new User();
    $user->username = $username;
    $user->firstname = $firstname;
    $user->lastname = $lastname;
    $user->password = md5($password);
    $user->createdAt = $timestamp;
    $user->updatedAt = $timestamp;
    
    $existingUsername = $user->existingUser($username);
    if($existingUsername == NULL){
        $result = $user->save();
        $user->id = $result;
    
        if($result){
            $responseArray = array('status' => 'success', 'user' => $user, 'message' => "successfully signup");
        }
        else {
            $responseArray = array('status' => 'fail', 'message' => 'Username or password incorrect.');
        }
    }
    else{
         $responseArray = array('status' => 'fail', 'message' => 'Username already exists.');
    }
    
    
}
echo json_encode($responseArray);
?>
