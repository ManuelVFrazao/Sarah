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
	
	if ($_GET["SerialNum1"]) {
		$serial = $_GET["SerialNum1"].$_GET["SerialNum2"].$_GET["SerialNum3"];
		if ($_GET["SerialNum1"] == "LI") {
			$sql = "INSERT INTO tblLights (fkRooms, Name, Description, SerialNum) VALUES ('".$_GET["fkRooms"]."','".$_GET["Name"]."','".$_GET["Description"]."','".$serial."')";
			#echo $sql;
			$result = $conn->query($sql);
		}
		if ($_GET["SerialNum1"] == "HE") {
		$sql = "INSERT INTO tblHeaters (fkRooms, Name, Description, SerialNum) VALUES ('".$_GET["fkRooms"]."','".$_GET["Name"]."','".$_GET["Description"]."','".$serial."')";
			#echo $sql;
			$result = $conn->query($sql);
		}
		if ($_GET["SerialNum1"] == "OU") {
		$sql = "INSERT INTO tblOutlets (fkRooms, Name, Description, SerialNum) VALUES ('".$_GET["fkRooms"]."','".$_GET["Name"]."','".$_GET["Description"]."','".$serial."')";
			#echo $sql;
			$result = $conn->query($sql);
		}
	}
?>

<html>
	<head>
		<link href="style.css" rel="stylesheet">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
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
						Room: <select name='fkRooms' required>
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
						</select>
						<br />
						Name: <input name='Name' type='text' required>
						<br />
						Description: <input name='Description' type='text' >
						<br />
						Serial Number: <input name='SerialNum1' type='text' placeholder="XX"  pattern="[A-Z]{2}" size="2"  maxlength="2" required>&nbsp;- 
						<input name='SerialNum2' type='text' placeholder="XXXX"  pattern="[a-z,A-Z,0-9]{4}" size="4"  maxlength="4" required>&nbsp;- 
						<input name='SerialNum3' type='text' placeholder="XXXXXX"  pattern="[a-z,A-Z,0-9]{6}" size="6"  maxlength="6" required>
						<br />
						<input type='submit' value='Submit'>
					</form>
				</article>
			</section>
		</section>
	</body>
</html>
