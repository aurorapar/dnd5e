<?php
    require 'servercreds.php';
    header("Content-Type: application/json"); 
    
    
    $data = json_decode(file_get_contents("php://input"), True);   
    
    if(is_null($data['action']) or is_null($data['value']))
    {
        echo "You did not enter anything";
        exit(0);
    }    
    
    $actions = array('getstats', 'updatestats');    
    
    $action = $data['action'];
    $value = $data['value'];
    
    if(!in_array($action, $actions))
    {
        echo "App failed.";
        exit(0);
    }
    
    // Create connection
    $conn = new mysqli($servername, $username, $password, $dbname);

    // Check connection
    if ($conn->connect_error) {
        echo "<p>Connection to databased failed. Please report to aurorapariseau@gmail.com</p>";
        die("Connection failed");      
        exit(0);
    }
    
    setupDatabase($conn);
    
    if(!is_array($value))
    {   
        echo call_user_func_array($action, array($conn, $value));
    }
    else
    {
        echo call_user_func_array($action, array($conn, $value));
    }    
    
    function updatestats($conn, $values)
    {
        $steamid = $values['steamid'];
        $name = $values['name'];
        $lastPlayed = $values['last_played'];
        $classname= $values['classname']; 
        $level = $values['level']; 
        $xp = $values['xp'];
        
        $regex = "/^STEAM_[0-5]:[01]:[0-9]{2,15}/";    
        if(!preg_match($regex, $steamid))
        {
            return "FAILED";
        }        
        
        if(!existsUser($conn, $steamid))
        {
            createUser($conn, $steamid, $name, $lastPlayed);
        }
        
        if(!existsXP($conn,$steamid,$classname))
        {
            createXP($conn, $steamid, $classname, $level, $xp);
        }
        else
        {
            updateXP($conn, $steamid, $classname, $level, $xp);
        }
        
        return "SUCCESS";
    }     
    
    function updateXP($conn, $steamid, $classname, $level, $xp)
    {
        $stmt = $conn->prepare("SELECT id FROM DNDCLASS where name=?;");
        $stmt->bind_param("s", $classname);
        $stmt->execute();
        $stmt->bind_result($classid);
        $result = $stmt->fetch();
        $stmt->free_result();
        
        $stmt = $conn->prepare("UPDATE DNDXP SET level=?, xp=? WHERE dnduserid=? and dndclassid=?;");            
        $stmt->bind_param('ssss', $level, $xp, existsUser($conn,$steamid), $classid);
        $stmt->execute();
    }
    
    function createXP($conn, $steamid, $classname, $level, $xp)
    {
        $stmt = $conn->prepare("SELECT id FROM DNDCLASS where name=?;");
        $stmt->bind_param("s", $classname);
        $stmt->execute();
        $stmt->bind_result($classid);
        $result = $stmt->fetch();
        $stmt->free_result();
        
        $stmt = $conn->prepare("INSERT INTO DNDXP (dnduserid,dndclassid,level,xp) VALUES (?, ?, ?, ?);");            
        $stmt->bind_param('ssss', existsUser($conn,$steamid), $classid, $level, $xp);
        $stmt->execute();
        $stmt->store_result();
    }

    function existsXP($conn, $steamid, $classname)
    {   
        $stmt = $conn->prepare("SELECT id FROM DNDCLASS where name=?;");
        $stmt->bind_param("s", $classname);
        $stmt->execute();
        $stmt->bind_result($classid);
        $stmt->fetch();
        $stmt->free_result();      
        
        $sql = "SELECT id FROM DNDXP where dnduserid = ? AND dndclassid = ?;";
        $stmt2 = $conn->prepare($sql);
        $stmt2->bind_param("ss", existsUser($conn,$steamid), $classid);
        $stmt2->execute();
        $stmt2->bind_result($id);
        $result = $stmt2->fetch();
        $stmt2->free_result();
        return $id;
    }
    
    function existsUser($conn, $steamid)
    {
        $stmt = $conn->prepare("SELECT id FROM DNDUSER where steamid=?;");
        $stmt->bind_param("s", $steamid);
        $stmt->execute();
        $stmt->bind_result($id);
        $stmt->fetch();
        $stmt->free_result();
        return $id;
    }
    
    function createUser($conn, $steamid, $name, $lastPlayed)
    {
        // User not found            
        // CAN RETURN FALSE IF YOU DONT HAVE PERMS. $stmt::error_list
        $stmt = $conn->prepare("INSERT INTO DNDUSER (steamid,name,last_played) VALUES (?, ?, ?);");            
        $stmt->bind_param('sss', $steamid, $name, $lastPlayed);
        $stmt->execute();
        $stmt->free_result();
    }
    
    function getstats($conn,$steamid)
    {   
        $regex = "/^STEAM_[0-5]:[01]:[0-9]{2,15}/";    
        if(!preg_match($regex, $steamid))
        {
            return "<p>You didn't enter a Steam ID</p>";
        }
    
    
        // prepare and bind
        $stmt = $conn->prepare("SELECT usr.name as player, cls.NAME as classname, xp.LEVEL, xp.XP FROM DNDXP as xp JOIN DNDUSER as usr JOIN DNDCLASS as cls ON (xp.dnduserid = usr.id AND xp.dndclassid = cls.id) WHERE usr.STEAMID =?;");
        $stmt->bind_param("s", $steamid);
        $stmt->execute();
        $result = $stmt->get_result();
        $data = array();
        while ($row = $result->fetch_assoc()) 
        {
            array_push($data, $row);
        }    
        $stmt->close();
        $conn->close();
        
        if(count($data) < 1)
        {
            return "<p>The person with that Steam ID hasn't played on the server</p>";        
        }
        
        $player = null;
        $response = array('steamid' => $steamid, 'name' => null);
        foreach($data as $vals)
        {
            if(is_null($response['name'])) 
            {
                $response['name'] = $vals['player'];
            }
            $classname = ucwords($vals['classname']);
            $response[$classname] = array(
                                            'Level' => $vals["LEVEL"], 
                                            'XP' => $vals["XP"]
                                    );
        }
        return json_encode($response);
    }
    
    function setupDatabase($conn)
    {
        $sql = "CREATE TABLE IF NOT EXISTS `DNDCLASS` (
          `ID` int(11) NOT NULL AUTO_INCREMENT,
          `NAME` varchar(25) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
          PRIMARY KEY (`ID`)
        ) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; ";
        if(!($conn->query($sql)))
        {
            exit();
        }
        
        $sql = "CREATE TABLE IF NOT EXISTS `DNDUSER` (
          `ID` int(11) NOT NULL AUTO_INCREMENT,
          `STEAMID` varchar(25) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
          `NAME` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
          `LAST_PLAYED` datetime DEFAULT NULL,
          PRIMARY KEY (`ID`)
        ) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;";
        if(!($conn->query($sql)))
        {
            exit();
        }
        
        $sql = "CREATE TABLE IF NOT EXISTS `DNDXP` (
          `ID` int(11) NOT NULL AUTO_INCREMENT,
          `DNDUSERID` int(11) DEFAULT NULL,
          `DNDCLASSID` int(11) DEFAULT NULL,
          `LEVEL` int(11) DEFAULT NULL,
          `XP` int(11) DEFAULT NULL,
          PRIMARY KEY (`ID`)
        ) ENGINE=InnoDB AUTO_INCREMENT=487 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;";
        
        if(!($conn->query($sql)))
        {
            exit();
        }
    }
    
    function startsWith ($string, $startString) 
    { 
        $len = strlen($startString); 
        return (substr($string, 0, $len) === $startString); 
    } 
    
?>
