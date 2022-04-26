<?php
include_once(CLASES . "/class.Recomendations.php");
//print_r($lngarr);
try{
  $r = new Recomendations($_SESSION['id']);
  $title1 = $lngarr['titleimgs'];
  $title2 = $lngarr['titleovers'];
  $title3 = $lngarr['titlepolys'];
  $arr1 = array_slice($r->get_recommended_images(), 0, 5);
  $arr2 = array_slice($r->get_recommended_overlaps(), 0, 5);
  $arr3 = array_slice($r->get_recommenden_polys(), 0, 5);
  $id1 = Recomendations::save_recomendations($arr1,1,$_SESSION['session_id']);
  $id2 = Recomendations::save_recomendations_over($arr2,3,$_SESSION['session_id']);
  $id3 = Recomendations::save_recomendations_poly($arr3,2,$_SESSION['session_id']);
}catch(Exception $e){
  $title1 = $lngarr['mostdown'];
  $title2 = $lngarr['bestrank'];
  $arr1 = Recomendations::most_downloaded($_SESSION['id']);
  $arr2 = Recomendations::most_liked($_SESSION['id']);
  $id1 = Recomendations::save_recomendations($arr1,4,$_SESSION['session_id']);
  $id2 = Recomendations::save_recomendations($arr2,5,$_SESSION['session_id']);
}

if(count($arr1) == 0){
  $arr1 = Recomendations::most_liked($_SESSION['id']);
}
//print_r($arr1);
//$id1 = Recomendations::save_recomendations($arr1,$title1,$_SESSION['session_id']);
//$id2 = Recomendations::save_recomendations($arr2,$title2,$_SESSION['session_id']);
?>

<!--RIGHT PANEL -->
<div id="test" >
  <?php if(isset($arr3)): ?> 
    <div class="card otros_usuarios">
      <div class="title">
        <?php echo $title3; ?>
      </div>
      <div class="body">
        <?php
          PageManagment::rightPanelPolys($arr3,$id3);
        ?>
      </div>
    </div>
  <?php endif; ?> 

  <div class="card intereses">
    <div class="title">
      <?php echo $title1; ?>
    </div>
    <div class="body">
      <?php
        PageManagment::rightPanelImages($arr1,$id1);
      ?>
    </div>
  </div>
  
  <div class="card otros_usuarios">
    <div class="title">
      <?php echo $title2; ?>
    </div>
    <div class="body">
      <?php
        if($title2 == "Solapamientos recomendados" || $title2=="Recommended overlaps"){
          PageManagment::rightPanelOverlaps($arr2,$id2);
        }else{
          PageManagment::rightPanelImages($arr2,$id2);
        }
        
      ?>
    </div>
  </div>

  
</div>
<!-- RIGHT PANEL -->
