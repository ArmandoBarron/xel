<?php
include_once("../resources/conf.php");
include_once(SESIONES);

Sessions::startSession("buscador");

echo "<h2>Preferencias</h2>";

if(!empty($_SESSION['id'])):?>
	<ul>
		<li>
			<h4>Ubicación</h4>
			<p>Para mejorar su experiencia de usuario, el sistema generá una serie de recomendaciones en base a su actividad dentro del geoportal. Para ello, por medio de la siguiente ubicación donde podría haber productos de su interés, la cuál puede ser ajustada moviendo la circunferencia en el mapa. </p>
			<div style="height: 300px;background-color: #bbdefb" id="map"></div>
			<br>
			<div class="">
				<button type="button" onclick="saveLocation()"  id="btnSaveLocation" class="btn btn-primary">Guardar ubicación</button>
				<button type="button" onclick="resetLocation()" id="btnUndoChanges" class="btn btn-warning">Deshacer cambios</button>
				<button type="button" onclick="useCurrentLocation()" id="btnCurrentLocation" class="btn btn-default">Utilizar mi ubicación actual</button>
			</div>
		</li>
	</ul>
<?php endif;
