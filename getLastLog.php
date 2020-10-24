<?php
    header('Content-Type: application/json');
    
    include_once './dbconfig.php';
    require_once './classes/user.php';
    require_once './classes/datalog.php';

    $date = @$_REQUEST['date'];
    $username = @$_REQUEST['username'];
    $password = @$_REQUEST['password'];

    if($username == NULL || $username == "") {
        $responseArray = array('status' => 'fail', 'message' => 'Please provide username');
        echo json_encode($responseArray);
    }
    else if($password == NULL || $password == "") {
        $responseArray = array('status' => 'fail', 'message' => 'Please provide password');
        echo json_encode($responseArray);
    }
    else {
        $user = new User();
        $result = $user->login($username, $password);
        if($result) {
            $userId = $result->id;
            $list = array();
            $responseArray = array();
            $datalog = new Datalog();
            if($date == NULL) {
                $list = $datalog->getLast($userId);
            }
            else {
                $list = $datalog->getDatalogForDate($date, $userId);
            }
            $responseArray = array('status' => "success", "datalogs" => $list);
            echo json_encode($responseArray);
        }
        else {
            $responseArray = array('status' => 'fail', 'message' => 'Username or password incorrect.');
        }
    }
?>
