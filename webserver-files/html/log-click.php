<?php

// record search in log
$log_file = 'logs/click.log';
//session_id,search_id,datetime,click_type,data_source,doc_id
$log_line = $_GET['session_id'].','.$_GET['search_id'].','.date("Y-m-d H:i:s").','.$_GET['click_type'].','.$_GET['data_source'].','.str_replace(',',"",$_GET['doc_id'])."\n";
file_put_contents($log_file, $log_line, FILE_APPEND | LOCK_EX);

?>