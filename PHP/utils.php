<?php

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 * Author Chris Fedun
 */
/**
 * @param $data
 * @return string
 */
function test_input($data) {
    return htmlspecialchars(stripslashes(trim($data)));
}

/**
 * @param $data
 * @return string
 */
function strict_input_Filter($data) {
    return test_input($data);
}

/**
 * @param $data
 * @return bool
 */
function filterMultipleEmailPattern($data) {
    return ( 1 == preg_match('/^([\w+-.%]+@[\w\-.]+\.[A-Za-z]{2,4},*[\W]*)+$/', $data));
}

/**
 * @param $data
 * @return bool
 */
function filterEmailPattern($data) {
    return ( 1 == preg_match('/^([\w+-.%]+@[\w\-.]+\.[A-Za-z]{2,4},*[\W]*)$/', $data));
}

/**
 * @param $email
 * @return string
 */
function filterEmail($email) {
    return mb_strtolower(strict_input_Filter($email));
}

/**
 * @param $data
 * @return bool
 */
function checkSpaces($data) {
    return ( 1 == preg_match('/\s/', $data));
}

/**
 * @param $data
 * @return bool
 */
function checkUserPattern($data) {
    return ( 1 == preg_match('/^([\w+-.%])/', $data));
}

/**
 * @param $data
 * @return bool
 */
function checkDomain($data) {
    return ( 1 == preg_match('/^([\w\-.]+\.[A-Za-z]{2,4})/', $data) );
}

/**
 *
 */
function echoPagePath() {
    echo currentPagePath();
}

/**
 * @return string
 */
function currentPagePath() {
    return htmlspecialchars($_SERVER["PHP_SELF"]);
}

/**
 * @return string
 */
function currentPageName(){
    return basename(htmlspecialchars($_SERVER['PHP_SELF']));
}

/**
 * @return string
 */
function currentPageDirectory(){
    return dirname(htmlspecialchars($_SERVER['PHP_SELF']));
}

/**
 *
 */
function isActiveCheck() {
    if ($_SESSION['last_activity'] < time() - $_SESSION['expire_time']) { //have we expired?
        // we don't want to destroy this session.... Yet...
        $_SESSION['destroy'] = FALSE;
        // Set to return to this page
        $_SESSION['prevPage'] = currentPagePath();
        //redirect to logout.php
        header('Location: logout.php');
    } else { //if we haven't expired:
        $_SESSION['destroy'] = TRUE; // Since we want to destroy the session if clicking logout
        $_SESSION['last_activity'] = time(); //this was the moment of last activity.
    }
}

/**
 *
 */
function isAuthenticated() {
    if (!$_SESSION['auth']) {
        //redirect back to login form if not authorized
        $_SESSION['prevPage'] = currentPagePath();
        header("Location: login.php");
        exit;
    }
}

/**
 * @return array|false|string
 */
function getBrowser() {
    return getenv("HTTP_USER_AGENT");
}

/**
 * @return array|false|string
 */
function getClientIP() {
    return getenv('REMOTE_ADDR');
}

/**
 * @return array|false|string
 */
function getUserAgent(){
    return getBrowser();
}

/**
 * @return EmailData
 */
function checkDB(): EmailData
{
    if ($_SESSION['emailDB']) {
        $mysqli = $_SESSION['emailDB'];
        $mysqli->connect();
    } else {
        $mysqli = new EmailData();
        $_SESSION['emailDB'] = $mysqli;
    }
    return $mysqli;
}

/**
 * @return array
 */
function pageStart(): array
{
    $displayBlock = '';
    isAuthenticated();
    isActiveCheck();
    $mysqli = checkDB();
    return array($displayBlock, $mysqli);
}
