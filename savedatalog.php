<?php

header('Content-Type: application/json');
 
include_once './dbconfig.php';
require_once './classes/datalog.php';

$temperature = @$_REQUEST['temperature'];
$datetime = @$_REQUEST['datetime'];
$latitude = @$_REQUEST['latitude'];
$longitude = @$_REQUEST['longitude'];
$motion = @$_REQUEST['motion'];
$userId = @$_REQUEST['userId'];

list($msec, $sec) = explode(' ', microtime());
$timestamp = (int) ($sec.substr($msec, 2, 3));

$responseArray = array();

if($temperature == NULL) {
	$responseArray = array('status' => 'fail', 'message' => 'Please provide temperature');
	echo json_encode($responseArray);
}
else if($datetime == NULL || $datetime == "") {
	$responseArray = array('status' => 'fail', 'message' => 'Please provide datetime');
	echo json_encode($responseArray);
}
else {
    $datalog = new Datalog();
    $datalog->temperature = $temperature;
    $datalog->datetime = $datetime;
    if ($latitude != NULL) {
        $datalog->latitude = $latitude;
    }
    if ($longitude != NULL) {
        $datalog->longitude = $longitude;
    }
    if ($motion != NULL) {
        $datalog->motion = $motion;
    }
    //echo json_encode($datalog);
    //exit(0);
    $datalog->createdAt = $timestamp;
    $datalog->updatedAt = $timestamp;
    $datalog->userId = $userId;
    $result = $datalog->save();
    if($result) {
        $datalog->id = $result;
        $responseArray = array('status' => 'success', 'message' => 'Survay saved successfully.', 'datalog' => $datalog);
	}
	else {
		$responseArray = array('status' => 'fail', 'message' => 'Please try again after sometime or contact to the', 'error' => $mysqli->error);
    }
    echo json_encode($responseArray);
}
?>