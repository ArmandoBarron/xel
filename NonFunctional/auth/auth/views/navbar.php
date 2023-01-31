<div class="navbar navbar-inverse navbar-fixed-top" rol="navigation">
	<div class="navbar-collapse collapse">
		<div class="container">
			<ul class="nav navbar-nav">
				<li><a href="../index.php">Inicio</a></li>
				<?php if(isset($_SESSION["tokenuser"]) && isset($_SESSION['username'])) { ?>
					<?php //if(isset($_SESSION["isadmin"]) && $_SESSION["isadmin"]==1) { ?>
								<li><a href="listaUsuarios.php">Administrar Usuarios</a></li>
					<?php //} ?>
				</ul>
				<ul class="nav navbar-nav navbar-right">
					<li class="dropdown">
						<a href="#" class="data-toggle"><i class="glyphicon glyphicon-user"></i> <?php echo $_SESSION["username"]; ?></a>
					</li>
					<li><a href="views/logout.php">Salir</a></li>
				<?php } ?>	
			</ul>
		</div>
	</div>
</div>



