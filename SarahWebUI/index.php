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
				<h1>SARaH</h1>
				<a href="#">Test</a>
			</section>
		</section>
	</body>
</html>
