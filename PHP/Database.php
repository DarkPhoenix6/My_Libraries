<?php

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 * Description of Database
 * @notes All your Database are belong to us.
 * @author cfedun
 */
class Database {

    //put your code here
    protected $_Port = "";
    protected $_Host = "";
    protected $_DataBase = "";
    protected $_User = "";
    protected $_Pass = "";
    protected $_OpenTransactionCount = 0;
    protected $_TransactionRollback = FAlSE;

    /**
     *
     * @var mysqli
     */
    protected $_mysqli;

    // Constructor
    function __construct($Host, $User, $Pass, $DataBase, $Port) {
        $this->_Host = $Host;
        $this->_Port = $Port;
        $this->_DataBase = $DataBase;
        $this->_User = $User;
        $this->_Pass = $Pass;
    }

    function __destruct() {
        $this->verifyTransactions();
    }

    //Public methods

    Public function connect() {
        return($this->_connect());
    }

    public function close() {
        $isError = FALSE;
        if (FALSE !== $this->_mysqli) {
            mysqli_close($this->_mysqli);
            $this->_mysqli = FALSE;
        } else {
            $isError = TRUE;
        }
        return $isError;
    }

    public function fetchArray(&$queryResult, &$queryArray, $resultType = MYSQLI_ASSOC) {
        $queryArray = mysqli_fetch_array($queryResult, $resultType);
        return FALSE;
    }

    public function fetchAll(&$queryResult, &$queryArray, $resultType = MYSQLI_ASSOC) {
        $queryArray = mysqli_fetch_all($queryResult, $resulttype);
        return FALSE;
    }

    public function getQuery(&$result, $query) {
        $isError = FALSE;
        if (FALSE === ($result = mysqli_query($this->_mysqli, $query))) {
            $isError = TRUE;
        }
        return $isError;
    }

    public function getCount(&$result, &$rowcount) {
        $rowcount = mysqli_num_rows($result);
        return FALSE;
    }

    public function freeResult(&$result) {
        mysqli_free_result($result);
    }

    public function getOneQueryRow(&$row, $query, $resultType = MYSQLI_ASSOC) {
        $result = FALSE;
        $isError = FALSE;
        $row = NULL;
        $numOfRows = 0;

        if (FALSE != ($isError = $this->getQuery($result, $query))) {
            return $isError;
        } elseif (FALSE != ($isError = $this->getCount($result, $numOfRows))) {
            return $isError;
        } elseif (0 == $numOfRows) {
            return TRUE;
        } else {
            $isError = $this->fetchArray($result, $row, $resultType);
        }
        if ($result) {
            $this->freeResult($result);
        }
        return $isError;
    }

    public function realEscapeString($str_in) {
        return mysqli_real_escape_string($this->_mysqli, $str_in);
    }

    public function state($state) {
        return $this->getQuery($ignoreMe, $state);
    }

    public function isNotEmpty($input) {
        return $this->_isNotEmpty($input);
    }

    public function startTransaction() {
        $isError = FALSE;
        // ONLY IF THIS IS THE VERY FIRST/OUTERMOST BEGIN, EXECUTE IT.
        if (0 == $this->_OpenTransactionCount) {
            if (FALSE === $this->_mysqli && FALSE != ($isError = $this->connect())) {
                ;
            } elseif (FALSE != ($isError = $this->state("BEGIN"))) {
                ;
            } else {
                $this->_OpenTransactionCount = 1;
            }
            $this->_TransactionRollback = FALSE;
        } else {
            // increase the nest count
            $this->_OpenTransactionCount += 1;
        }
        return $isError;
    }

    public function commitTransaction() {
        $isError = FALSE;
        if (0 == $this->_OpenTransactionCount) {
            $isError = TRUE;
            //Something went awry!
        } else {
            $this->_OpenTransactionCount -= 1;
            // If this is the OUTERMOST Tx COMMIT/ROLLBACK it
            if (0 == $this->_OpenTransactionCount) {
                // If something failed
                $this->_commitTxRollback($isError);
                // else do Commit
                $this->_doCommitTx($isError);
            }
        }
        return $isError;
    }

    public function cancelTransaction() {
        $isError = FALSE;
        if (0 == $this->_OpenTransactionCount) {
            $isError = TRUE;
            //Something went awry!
        } else {
            $this->_OpenTransactionCount -= 1;
            // If this is the OUTERMOST Tx COMMIT/ROLLBACK it
            if (0 == $this->_OpenTransactionCount) {
                // If something failed
                $this->_commitTxRollback($isError);
            } else {
                // set rollback flag
                $this->_TransactionRollback = TRUE;
            }
        }
        return $isError;
    }

    public function verifyTransactions() {
        $isError = FALSE;
        if (0 != $this->_OpenTransactionCount) {
            $isError = TRUE;
            //Something went awry!
            $this->_OpenTransactionCount = 1;
            $this->cancelTransaction();
        }
        return $isError;
    }

    public function getVersion() {
        return(mysqli_get_server_version($this->_mysqli));
    }

    public function generateSQLISNULL($field) {
        return("ISNULL(" . $field . ")");
    }

    //PROTECTED Methods
    /**
     * tests if string is not empty
     * @param string $input
     * @return boolean
     * 
     */
    protected function _isNotEmpty($input) {
        $strTemp = trim($input);

        if ($strTemp !== '') {
            return TRUE;
        }

        return FALSE;
    }

    /**
     * (Re-)connects to data source if necessary
     * @returns FALSE on success and TRUE on error
     * @return boolean
     */
    protected function _connect() {
        $isError = FALSE;
        if ($this->_isNotEmpty($this->_Port)) {
            if (FALSE === ($this->_mysqli = mysqli_connect($this->_Host, $this->_User, $this->_Pass, $this->_DataBase, $this->_Port))) {
                $isError = TRUE;
            }
        } else {
            if (FALSE === ($this->_mysqli = mysqli_connect($this->_Host, $this->_User, $this->_Pass, $this->_DataBase))) {
                $isError = TRUE;

                echo mysqli_connect_error();
            }
        }
        return $isError;
    }

    // PRIVATE METHODS
    /**
     * 
     * @param type $isError
     */
    private function _commitTxRollback(&$isError) {
        if ($this->_TransactionRollback) {
            if (FALSE != ($isError = $this->state("ROLLBACK"))) {
                ;
            }
        }
    }

    /**
     * 
     * @param boolean $isError
     */
    private function _doCommitTx(&$isError) {
        if (FALSE === $this->_mysqli && FALSE != ($isError = $this->connect())) {
            ;
        } else {
            $isError = $this->state("COMMIT");
        }
    }

}
