<?php 
include_once("../resources/conf.php");
include_once(SESIONES);

Sessions::startSession("buscador");
echo "<h2>Estadísticas</h2>";

if(!empty($_SESSION['user'])):?>
	<ul>
		<li>
			<h4>Búsquedas</h4>
			<div style="position:relative;float:left;height:400px; width:400px">
				<canvas id="divSearchesStats" ></canvas>
			</div>
			<div style="margin-bottom:40px;margin-left:20px;position:relative;float:left;height:400px; width:400px">
				<canvas id="divSearchesWay" ></canvas>
			</div>
			<br>
		</li>
		<li>
			<div>
				<h4>Recomendaciones</h4>
				<div style="position:relative;float:left; width:400px">
					<canvas id="divGivenRecommendations" ></canvas>
				</div>
				<div style="position:relative;float:left; width:400px">
					<canvas id="divGivenRecommendationsPolys" ></canvas>
				</div>
				<div style="position:relative;float:left; width:400px">
					<canvas id="divGivenRecommendationsOverlaps" ></canvas>
				</div>
			</div>
			
		</li>
	</ul>
<?php endif;?>