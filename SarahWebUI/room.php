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
		if (substr($_GET["SerialNum"], 0,2) == "LI") {
			$sql = "UPDATE tblLights SET Red='".$_GET["Red"]."', Green='".$_GET["Green"]."', Blue='".$_GET["Blue"]."' WHERE SerialNum='".$_GET["SerialNum"]."'";
			#echo $sql;
			$result = $conn->query($sql);
		}
		if (substr($_GET["SerialNum"], 0,2) == "HE") {
			$sql = "UPDATE tblHeaters SET SetTo='".$_GET["SetTo"]."' WHERE SerialNum='".$_GET["SerialNum"]."'";
			#echo $sql;
			$result = $conn->query($sql);
		}
		if (substr($_GET["SerialNum"], 0,2) == "OU") {
			$sql = "UPDATE tblOutlets SET IsOn='".$_GET["IsOn"]."' WHERE SerialNum='".$_GET["SerialNum"]."'";
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
				<?php
					$sql = "SELECT pkRooms, Name, Description FROM tblRooms WHERE pkRooms = ".$_GET["room"];
					$result = $conn->query($sql);

					if ($result->num_rows > 0) {
						// output data of each row
						while($row = $result->fetch_assoc()) {
							echo "<h1>".$row["Name"]."</h1>";
							echo "<h2>".$row["Description"]."</h2>";
							
							$sql = "SELECT pkLights, Name, Description, Red, Green, Blue, SerialNum FROM tblLights WHERE fkRooms = ".$_GET["room"];
							$result = $conn->query($sql);

							if ($result->num_rows > 0) {
								// output data of each row
								while($row = $result->fetch_assoc()) {
									echo "<article>
										<h2>".$row["Name"]."</h2>
										<h3>".$row["Description"]."</h3>
										<form>
											Red: <input name='Red' type='range' min=0 max=255 value=".$row["Red"]." for='RedNum' oninput='RedNum.value=Red.value' >
											<input name='RedNum' type='number' min=0 max=255 value=".$row["Red"]." for='Red' oninput='Red.value=RedNum.value' >
											<br />
											Green: <input name='Green' type='range' min=0 max=255 value=".$row["Green"]." for='GreenNum' oninput='GreenNum.value=Green.value' >
											<input name='GreenNum' type='number' min=0 max=255 value=".$row["Green"]." for='Green' oninput='Green.value=GreenNum.value' >
											<br />
											Blue: <input name='Blue' type='range' min=0 max=255 value=".$row["Blue"]." for='BlueNum' oninput='BlueNum.value=Blue.value' >
											<input name='BlueNum' type='number' min=0 max=255 value=".$row["Blue"]." for='Blue' oninput='Blue.value=BlueNum.value' >
											<br />
											<input name='room' type='hidden', value=".$_GET["room"].">
											<input name='SerialNum' type='hidden', value=".$row["SerialNum"].">
											<input type='submit' value='Submit'>
										</form>
									</article>";
								}
							}
							
							
							$sql = "SELECT Name, Description, SetTo, Current, Humidity, SerialNum FROM tblHeaters WHERE fkRooms = ".$_GET["room"];
							$result = $conn->query($sql);

							if ($result->num_rows > 0) {
								// output data of each row
								while($row = $result->fetch_assoc()) {
									echo "<article>
										<h2>".$row["Name"]."</h2>
										<h3>".$row["Description"]."</h3>
										<form>
											Set: <input name='SetTo' type='range' min=17 max=23 value=".$row["SetTo"]." for='SetToNum' oninput='SetToNum.value=SetTo.value' >
											<input name='SetToNum' type='number' min=17 max=23 value=".$row["SetTo"]." for='SetTo' oninput='SetTo.value=SetToNum.value' >
											<br />
											Current: <input type='text' value=".$row["Current"]." readonly>
											<br />
											Humidity: <input type='text' value=".$row["Humidity"]." readonly>
											<br />
											<input name='room' type='hidden', value=".$_GET["room"].">
											<input name='SerialNum' type='hidden', value=".$row["SerialNum"].">
											<input type='submit' value='Submit'>
										</form>
									</article>";
								}
							}
							
							
							$sql = "SELECT pkOutlets, Name, Description, IsOn, Consumption, SerialNum FROM tblOutlets WHERE fkRooms = ".$_GET["room"];
							$result = $conn->query($sql);

							if ($result->num_rows > 0) {
								// output data of each row
								while($row = $result->fetch_assoc()) {
									echo "<article>
										<h2>".$row["Name"]."</h2>
										<h3>".$row["Description"]."</h3>
										<form>
											On: <select name='IsOn'>
											<option value='0' ";
											if ($row["IsOn"] == 0) {
												echo "selected";
											}
											echo ">Off</option>
											<option value='1' ";
											if ($row["IsOn"] == 1) {
												echo "selected";
											}
											echo ">On</option>
											</select>
											<br />
											Consumption: <input type='text' value=".$row["Consumption"]." readonly>
											<br />
											<input name='room' type='hidden', value=".$_GET["room"].">
											<input name='SerialNum' type='hidden', value=".$row["SerialNum"].">
											<input type='submit' value='Submit'>
										</form>
									</article>";
								}
							}
						}
					} else {
						echo "No rooms with id ".$_GET["room"]."<br /><a href='index.php'>Home</a>";
					}
				?>
			</section>
		</section>
	</body>
</html>
