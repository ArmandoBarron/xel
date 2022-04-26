
<div id ="content">
  <div class="row">
    <?php if($tipo == 4 || $tipo == 5): ?>
    <div class="col-sm-5" id="imgelement">
      <img height='500px' width='100%' src="resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/<?php echo $res[0]['nombre'] ?>.jpg" />
      <?php if(isset($_SESSION['id'])) include_once("comentarios.php");  ?>
    </div>
    <?php
    endif;?>
    <div class="col-sm-7" id="divdata">
      <h3><?php echo $res[0]['nombre']; ?></h3>
      <?php if(isset($res[0]['tipopadre'])): ?>
        <strong><?php echo ucfirst($res[0]['tipopadre']); ?>: </strong><a href="?element=<?php echo $res[0]['idpadre'];?>"><?php echo ucfirst($res[0]['nombrepadre']); ?></a><br>
      <?php endif; ?>
      <?php if($tipo == 4){ ?>
        <table  width="100%">
          <tr>
            <td>
              <strong>Path: </strong><?php echo ucfirst($res[0]['path']); ?><br>
              <strong>Row: </strong><?php echo ucfirst($res[0]['row']); ?><br>
              <strong>Fecha de adquisición: </strong><?php echo ucfirst($res[0]['date']); ?><br>
              <strong>Proyección: </strong><?php echo ucfirst($res[0]['projection']); ?><br>
              <strong>Ellipsoid: </strong><?php echo ucfirst($res[0]['ellipsoid']); ?><br>
            </td>
            <td>
              <strong>Descargas: </strong><?php echo $res[0]['descargas'];; ?><br>
              <strong>Mi calificación: </strong>
              <div class="likes">
                <?php for ($j=1; $j <= 5; $j++):
                  if($j <= intval($res[0]["rating"])): ?>
                    <button id="btnStar<?php echo $res[0]["idelemento"].$j ?>" onclick='rate(this,"<?php echo $res[0]['idelemento'] ?>",<?php echo $j ?>)' type="button" class="btn btn-default btn-xs">
                      <span class="glyphicon glyphicon-star" aria-hidden="true"></span>
                    </button>
                  <?php else: ?>
                    <button id="btnStar<?php echo $res[0]["idelemento"].$j ?>" onclick='rate(this,"<?php echo $res[0]['idelemento'] ?>",<?php echo $j ?>)' type="button" class="btn btn-default btn-xs">
                      <span class="glyphicon glyphicon-star-empty" aria-hidden="true"></span>
                    </button>
                <?php endif;
                  endfor; ?>
              </div>
              <br>
              <strong>Calificación media: </strong>
              <div class="likes">

                <?php for ($j=1; $j <= 5; $j++):
                  if($j <= intval($res[0]["average"])): ?>
                    <button type="button" class="btn btn-default btn-xs">
                      <span class="glyphicon glyphicon-star" aria-hidden="true"></span>
                    </button>
                  <?php else: ?>
                    <button type="button" class="btn btn-default btn-xs">
                      <span class="glyphicon glyphicon-star-empty" aria-hidden="true"></span>
                    </button>
                <?php endif;
                  endfor; ?>
              </div>
            </td>
          <tr>
        </table>

      <?php }else if($tipo == 5){ ?>
        <strong>Composición: </strong><?php echo $res[0]['composition']; ?><br>
        <strong>Descripción: </strong><p><?php echo $res[0]['description']; ?></p>

      <?php } ?>
      <br>
      <?php if($tipo == 4){ ?>

        <button type='button' title="Ver metadatos" onclick='verMeta("<?php echo $res[0]["nombre"] ?>")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-file' aria-hidden='true'></span>Ver metadatos</button>
        <span id="btn<?php echo $res[0]['nombre']; ?>">
          <button title="Agregar a descargas" type='button'  onclick='addToCar("<?php echo $res[0]["nombre"] ?>","add")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span>Agregar</button>
       </span>

      <?php } ?>
      <a type="button" href="index.php" class="btn btn-default btn-xs">
        <span class="glyphicon glyphicon-globe" aria-hidden="true">Ir al geoportal</span>
      </a>
      <div class="table-responsive"  id="tblHijos"></div>

      <?php if($tipo == 4){ ?>
        <center>
          <div id="map"  style="min-height:300px;width:300px;"></div>
        </center>
      <?php } ?>
    </div>
  </div>
</div>
