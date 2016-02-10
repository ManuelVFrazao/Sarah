<!DOCTYPE html>
<?php
	include "phpMQTT.php";
	
	$servername = "localhost";
	$username = "Sarah";
	$password = "SarahAI2016";
	$dbname = "Sarah";
	
	// Create connection
	$conn = new mysqli($servername, $username, $password, $dbname);

	// Check connection
	if ($conn->connect_error) {
		die("Connection failed: " . $conn->connect_error);
	} 
	//echo "Connected successfully";
	
	if ($_GET["SerialNum"]) {
		$serial = substr($_GET["SerialNum"], 0,2).substr($_GET["SerialNum"], 3,4).substr($_GET["SerialNum"], 8,6);
		if (substr($_GET["SerialNum"], 0,2) == "LI") {
			$sql = "INSERT INTO tblLights (fkRooms, Name, Description, SerialNum) VALUES ('".$_GET["fkRooms"]."','".$_GET["Name"]."','".$_GET["Description"]."','".$serial."')";
			#echo $sql;
			$result = $conn->query($sql);
		}
		if (substr($_GET["SerialNum"], 0,2) == "HE") {
		$sql = "INSERT INTO tblHeaters (fkRooms, Name, Description, SerialNum) VALUES ('".$_GET["fkRooms"]."','".$_GET["Name"]."','".$_GET["Description"]."','".$serial."')";
			#echo $sql;
			$result = $conn->query($sql);
		}
		if (substr($_GET["SerialNum"], 0,2) == "OU") {
		$sql = "INSERT INTO tblOutlets (fkRooms, Name, Description, SerialNum) VALUES ('".$_GET["fkRooms"]."','".$_GET["Name"]."','".$_GET["Description"]."','".$serial."')";
			#echo $sql;
			$result = $conn->query($sql);
		}
	}
?>

<html>
	<head>
		<link href="style.css" rel="stylesheet">
	</head>
	<body>
		<section id="page">
			<nav>
				<ul>
					<?php
						$sql = "SELECT pkRooms, Name FROM tblRooms";
						$result = $conn->query($sql);

						if ($result->num_rows > 0) {
							// output data of each row
							while($row = $result->fetch_assoc()) {
								echo "<li><a href='room.php?room=".$row["pkRooms"]."'>".$row["Name"]."</a></li>";
							}
						} else {
							echo "0 results";
						}

					?>
					<li><a href="options.php">Options</a></li>
				</ul>
			</nav><section id="main">
				<h1>Options</h1>
				<article>
					<h2>Add device</h2>
					<form>
						Room: <input name='fkRooms' type='text' required list=RoomList>
						<datalist id="RoomList">
							<?php
								$sql = "SELECT pkRooms, Name FROM tblRooms";
								$result = $conn->query($sql);

								if ($result->num_rows > 0) {
									// output data of each row
									while($row = $result->fetch_assoc()) {
										echo "<option value='".$row["pkRooms"]."'>".$row["Name"]."</option>";
									}
								}
							?>
						</datalist>
						<br />
						Name: <input name='Name' type='text' required>
						<br />
						Description: <input name='Description' type='text' >
						<br />
						Serial Number: <input name='SerialNum' type='text' placeholder="XX-0000-000000"  pattern="[A-Z]{2}-[0-9]{4}-[0-9]{6}"  maxlength="14" required>
						<br />
						<input type='submit' value='Submit'>
					</form>
				</article>
			</section>
		</section>
	</body>
</html>
