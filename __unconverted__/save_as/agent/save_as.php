<?php
    // Parameters:
    $name = $_GET["name"];
    $filename= $_GET["filename"]; //htmlspecialchars()

    // Create extra parameters:    
    // $_SERVER["DOCUMENT_ROOT"]
    $attachment_location = $filename;
    $mime_type = mime_content_type($filename);
    
    //Return procedure:
    if (file_exists($attachment_location)) {
        header($_SERVER["SERVER_PROTOCOL"] . " 200 OK");
        header("Cache-Control: private"); // Needed for internet explorer
        header("Content-Type: $mime_type");
        header("Content-Transfer-Encoding: Binary");
        header("Content-Length:".filesize($attachment_location));
        header("Content-Disposition: attachment; filename=\"$name\"");
        readfile($attachment_location);
        die();        
    } else {
        die("Error: File not found.");
    }
?>        
