<!--- MODALES -->

<!-- MODAL GALLERY NEW -->
<div class="modal fade" id="modal-gallery" tabindex="-1" role="dialog" aria-labelledby="gallery" aria-hidden="true">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-body">
        <!--begin carousel-->
        <div id="modal-gallery-carrusel" class="carousel slide" data-ride="carousel">
          <div id="modal-gallery-carrusel-items" class="carousel-inner">


          </div>
          <a class="carousel-control-prev" href="#carouselExampleIndicators" role="button" data-slide="prev">
            <span><i class="fa fa-angle-left" aria-hidden="true"></i></span>

            <span class="sr-only">Previous</span>
          </a>
          <a class="carousel-control-next" href="#carouselExampleIndicators" role="button" data-slide="next">
            <span><i class="fa fa-angle-right" aria-hidden="true"></i></span>
            <span class="sr-only">Next</span>
          </a>
        </div>


      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>



<!-- Modal LIST SOLUTIONS-->

<div class="modal fade" id="modal_list-solutions" tabindex="-1" role="dialog" aria-labelledby="Save" aria-hidden="true">
		<div class="modal-dialog modal-lg" role="document">
			<div class="modal-content" >
				<div class="modal-header" id="modal_list-solutions-header">
					<h5 class="modal-title" id="modal_list-solutions-title">List of solutions</h5>
					<button type="button" class="close" data-dismiss="modal" aria-label="Close">
						<span aria-hidden="true">&times;</span>
					</button>
				</div>
        <div id="modal_list-solutions-body" class="modal-body" style="max-height: 750px;overflow: auto;">
        

				</div>
				<div id="modal_list-solutions-footer" class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
				</div>
			</div>
		</div>
	</div>


<!-- Modal SAVE SOLUTIONS-->

<div class="modal fade" id="modal_save-solutions" tabindex="-1" role="dialog" aria-labelledby="Save" aria-hidden="true">
		<div class="modal-dialog" role="document">
			<div class="modal-content" >
				<div class="modal-header" id="modal_save-solutions-header">
					<h5 class="modal-title" id="modal_save-solutions-title">Save solution</h5>
					<button type="button" class="close" data-dismiss="modal" aria-label="Close">
						<span aria-hidden="true">&times;</span>
					</button>
				</div>
        <div id="modal_save-solutions-body" class="modal-body" style="max-height: 750px;overflow: auto;">
        
                <div class="form-group">
                    <label>Token solution (id)</label>
                    <input class="form-control" disabled="disabled" type="text" id="modal_save-solutions-form-tokensolution"></input>
                </div>

                <div class="form-group">
                    <label>Name</label>
                    <input class="form-control" type="text" id="modal_save-solutions-form-name"></input>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea  cols="40" rows="5" class="form-control" type="text" id="modal_save-solutions-form-desc"></textarea>
                </div>
                <div class="form-group">
                    <label>Tags</label>
                    <input class="form-control" type="text" id="modal_save-solutions-form-tags" placeholder="list separated by comma. e.g. bigdata,enviriomental,machine learning" ></input>
                </div>

                <div class="container row" id="modal_save-solutions-icon-load" >

                </div>
				</div>
				<div id="modal_save-solutions-footer" class="modal-footer">
        <button onclick="BTN_save_solution()" type="button" class="btn btn-primary">Save</button>
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
				</div>
			</div>
		</div>
	</div>



<!-- Modal INSPECT DATA SET-->

<div class="modal fade" id="modal_inspect" tabindex="-1" role="dialog" aria-labelledby="InspectDataset" aria-hidden="true">
		<div class="modal-dialog modal-lg" role="document">
			<div class="modal-content" >
				<div class="modal-header" id="modal_inspect_header">
					<h5 class="modal-title" id="modal_inspect_title">Inspect data</h5>
					<button type="button" class="close" data-dismiss="modal" aria-label="Close">
						<span aria-hidden="true">&times;</span>
					</button>
				</div>
				<div id="modal_inspect_body" class="modal-body container" >

				</div>
				<div id="modal_inspect_footer" class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
				</div>
			</div>
		</div>
	</div>

<!-- Modal MAP AAS-->

<div class="modal fade" id="modal_mapAAS" tabindex="-1" role="dialog" aria-labelledby="MAP" aria-hidden="true">
		<div class="modal-dialog" role="document">
			<div class="modal-content" >
				<div class="modal-header" >
					<h5 class="modal-title">Show in map</h5>
					<button type="button" class="close" data-dismiss="modal" aria-label="Close">
						<span aria-hidden="true">&times;</span>
					</button>
				</div>
				<div id="modal_mapAAS_body" class="modal-body" style="max-height: 750px;overflow: auto;">

                <input style="display:none" type="text" id="SOM-id_service"></input>
                <input style="display:none" type="text" id="SOM-rn"></input>

                <div class="form-group">
                    <label>Spatial option</label>
                    <select id="SOM-opcion_espacial" name="SOM-opcion_espacial"  required data-actions-box='true' class="form-control selectpicker">
                        <option value="lat-lon" selected>latitude & longitude</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Column with latitude: </label>
                    <select id="SOM-lat" name="SOM-lat" required data-actions-box='true' class="form-control selectpicker"><option></option></select>
                    <label>Column with longitude: </label>
                    <select id="SOM-lon" name="SOM-lon" required data-actions-box='true' class="form-control selectpicker"><option></option></select>
                </div>

                <div class="form-group">
                    <label>Temporal column: </label>
                    <select id="SOM-temporal" name="SOM-temporal" required data-actions-box='true' class="form-control selectpicker">
                    <option></option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Values to show:</label>
                    <select id="SOM-values" name="SOM-values" required data-actions-box='true' class="form-control selectpicker" multiple>
                      <option></option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Identifier:</label>
                    <select id="SOM-id" name="SOM-id" required data-actions-box='true' class="form-control selectpicker"><option></option></select>
                </div>
                

                <div class="form-group">
                    <label>Spatial filters:</label>
                    <select id="SOM-spatial-filter" name="SOM-spatial-filter" required data-actions-box='true' class="form-control selectpicker" multiple><option></option></select>
                </div>

                <div class="form-group">
                    <label>Value filter:</label>
                    <select id="SOM-value-filter" name="SOM-value-filter" required data-actions-box='true' class="form-control selectpicker"><option></option></select>
                </div>


                <div class="form-group">
                    <label>Column with class</label>
                    <select id="SOM-columna_class" name="SOM-columna_class" required data-actions-box='true' class="form-control selectpicker"></select>
                </div>

                <div class="form-group" id=SOM-loading></div>


				</div>
				<div id="modal_mapAAS_footer" class="modal-footer">
        <button onclick="Handler_map()" type="button" class="btn btn-primary">Show in map</button>
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
				</div>
			</div>
		</div>
	</div>


<!-- Modal DESIGNER-->

<div class="modal fade" id="modal_edition" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
		<div class="modal-dialog" role="document">
			<div class="modal-content">
				<div class="modal-header">
					<h5 class="modal-title">Modal title</h5>
					<button type="button" class="close" data-dismiss="modal" aria-label="Close">
						<span aria-hidden="true">&times;</span>
					</button>
				</div>
				<div class="modal-body">

				</div>
				<div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
					<button id="btnSave" type="button" class="btn btn-primary">Save changes</button>
				</div>
			</div>
		</div>
	</div>

<!-- Modal Datasource-->

<div class="modal fade" id="modal_datasource" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
		<div class="modal-dialog modal-lg" role="document">
			<div class="modal-content">
				<div class="modal-header">
					<h5 class="modal-title">Modal title</h5>
					<button type="button" class="close" data-dismiss="modal" aria-label="Close">
						<span aria-hidden="true">&times;</span>
					</button>
				</div>
				<div class="modal-body">

				</div>
				<div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
				</div>
			</div>
		</div>
	</div>


<!-- Modal BUSCAR LUGAR-->
<div class="modal fade" id="modSearchPlace" role="dialog">
  <div class="modal-dialog ">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h4 class="modal-title"><?php echo $lngarr['place'] ?></h4>
      </div>
      <div class="modal-body">
        <?php echo $lngarr['txtplace'] ?>
        <form method="post">
          <div class="form-group">
            <label for="exampleInputEmail1"><?php echo $lngarr['placew'] ?></label>
            <input type="text"  class="form-control" id="txtSearchText" placeholder="<?php echo $lngarr['example'] ?>">

          </div>
          <div class="pull-right">
            <button type="submit" id="btnBuscarLugar" class="btn btn-primary btn-sm "><?php echo $lngarr['search'] ?></button>
            <button id="btnLimpiarCampo"  class="btn btn-secondary btn-sm "><?php echo $lngarr['clean'] ?></button>
          </div>
        </form>
        <br><br>
        <div class="" id="lugaresEncontrados"></div>
         <div id="error" style="text-color:red"></div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>

<!-- Modal PATH/ROW-->
<div class="modal fade" id="modPathRow" role="dialog">
  <div class="modal-dialog ">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h4 class="modal-title"><?php echo $lngarr['titlepr'] ?></h4>
      </div>


      <div class="modal-body">
        <?php echo $lngarr['description'] ?><br><br>
        <form method="post" id="frmPathRow" class="form-inline">
          <div class="form-group">
            <label ><?php echo $lngarr['path'] ?></label>
            <input type="text"  class="form-control solo-numero" name="path" id="txtPath" placeholder="<?php echo $lngarr['path'] ?>"  maxlength="3" required>

           </div>
          <div class="form-group">
            <label ><?php echo $lngarr['row'] ?></label>
            <input type="text"  class="form-control"  id="txtRow" placeholder="<?php echo $lngarr['row'] ?>" name="row"  maxlength="3" required>

          </div>
        </form>
      </div>
      <div class="modal-footer">
        <button type="submit" id="btnAddPolygon" class="btn btn-primary"><?php echo $lngarr['add'] ?></button>
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>


<!-- Modal CHOOSE IMAGE/META-->
<div class="modal fade" id="modChoose" role="dialog">
  <div class="modal-dialog modal-sm">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h4 class="modal-title"><?php echo $lngarr['select'] ?> - <span id="spanImagen"></span></h4>
      </div>
      <div class="modal-body">
        <?php echo $lngarr['descselect'] ?>
        <div class="checkbox">
          <label><input type="checkbox" name="choose" id="chooseJPG" class="choose" value="jpg"><?php echo $lngarr['img'] ?></label>
        </div>
        <div class="checkbox">
          <label><input type="checkbox" name="choose" id="chooseMeta" class="choose" value="meta"><?php echo $lngarr['metadata'] ?></label>
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" id="btnAddImageToDownload" class="btn btn-primary"><?php echo $lngarr['add'] ?></button>
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>

<!-- Modal SESION-->
<div class="modal fade " id="modExpirado" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true" data-backdrop="static" data-keyboard="false">
  <div class="modal-dialog modal-sm ">
    <div class="modal-content ">
      <div class="modal-header alert alert-danger">
        <h4 class="modal-title"><?php echo $lngarr['titlesesion'] ?></h4>
      </div>
      <div class="modal-body ">
        <?php echo $lngarr['descsesion'] ?>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" id="btnModalReloadPage"><?php echo $lngarr['reload'] ?></button>
      </div>
    </div>
  </div>
</div>

<!-- Modal DOWNLOAD-->
<div class="modal fade" id="modDownload" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-sm">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h4 class="modal-title"><?php echo $lngarr['download'] ?></h4>
      </div>
      <div class="modal-body">
        <span id="mensajedownload"></span>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>

<!-- Modal DECIMALES-->
<div class="modal fade" id="modNewDec" role="dialog">
  <div class="modal-dialog modal-sm">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h4 class="modal-title"><?php echo $lngarr['titlenc'] ?></h4>
      </div>
      <div class="modal-body">
        <form>
           <div class="form-group">
             <label for="recipient-name" class="form-control-label "><?php echo $lngarr['latitude'] ?>:</label>
             <input type="text" class="form-control solo-numero" required id="txtNewLat">
           </div>
           <div class="form-group">
             <label for="message-text" class="form-control-label"><?php echo $lngarr['longitude'] ?>:</label>
             <input type="text"  class="form-control solo-numero" required id="txtNewLon">
           </div>
         </form>
         <div id="error" style="text-color:red"></div>
      </div>

      <div class="modal-footer">
        <button type="button" id="btnAddNewDecimal" class="btn btn-primary"><?php echo $lngarr['add'] ?></button>
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>


<!-- Modal GRADOS-->
<div class="modal fade" id="modNewGrad" role="dialog">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h4 class="modal-title"><?php echo $lngarr['titlenc'] ?></h4>
      </div>
      <div class="modal-body">
        <form>
           <div class="form-group">
             <label for="recipient-name" class="form-control-label"><?php echo $lngarr['latitude'] ?>:</label>
             <div class="row">
               <div class="form-group col-xs-2">
                     <input id="txtNewGradsLat" class="form-control input-group-lg reg_name" type="text"
                            title="<?php echo $lngarr['grads'] ?>"
                            placeholder="<?php echo $lngarr['grads'] ?>"/>
                </div>
                <div class="form-group col-xs-1">°</div>
                <div class="form-group col-xs-2">
                      <input id="txtNewMinsLat" class="form-control input-group-lg reg_name" type="text"
                             title="<?php echo $lngarr['minutes'] ?>"
                             placeholder="<?php echo $lngarr['minutes'] ?>"/>
                 </div>
                 <div class="form-group col-xs-1">'</div>
                 <div class="form-group col-xs-2">
                       <input id="txtNewSegsLat" class="form-control input-group-lg reg_name" type="text"
                              title="<?php echo $lngarr['seconds'] ?>"
                              placeholder="<?php echo $lngarr['seconds'] ?>"/>
                  </div>
                  <div class="form-group col-xs-1">''</div>
                  <div class="form-group col-xs-3">
                    <select id="latOrien" class="form-control">
                      <option value="N"><?php echo $lngarr['north'] ?></option>
                      <option value="S"><?php echo $lngarr['south'] ?></option>
                    </select>
                  </div>
             </div>
           </div>
           <div class="form-group">
             <label for="message-text" class="form-control-label"><?php echo $lngarr['longitude'] ?>:</label>
             <div class="row">
               <div class="form-group col-xs-2">
                     <input id="txtNewGradsLon" class="form-control input-group-lg reg_name" type="text"
                            title="<?php echo $lngarr['grads'] ?>"
                            placeholder="<?php echo $lngarr['grads'] ?>"/>
                </div>
                <div class="form-group col-xs-1">°</div>
                <div class="form-group col-xs-2">
                      <input id="txtNewMinsLon" class="form-control input-group-lg reg_name" type="text"
                             title="<?php echo $lngarr['minutes'] ?>"
                             placeholder="<?php echo $lngarr['minutes'] ?>"/>
                 </div>
                 <div class="form-group col-xs-1">'</div>
                 <div class="form-group col-xs-2">
                       <input id="txtNewSegsLon" class="form-control input-group-lg reg_name" type="text"
                              title="<?php echo $lngarr['seconds'] ?>"
                              placeholder="<?php echo $lngarr['seconds'] ?>"/>
                  </div>
                  <div class="form-group col-xs-1">''</div>
                  <div class="form-group col-xs-3">
                    <select id="lonOrien" class="form-control">
                      <option value="E"><?php echo $lngarr['east'] ?></option>
                      <option value="W"><?php echo $lngarr['west'] ?></option>
                    </select>
                  </div>
             </div>
           </div>
         </form>
         <div id="error2" style="text-color:red"></div>
      </div>
      <div class="modal-footer">
        <button type="button"  id="btnAddNewGrad"  class="btn btn-primary" ><?php echo $lngarr['add'] ?></button>
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>


<!-- MODAL METADATA -->

<div class="modal fade" id="modDataImg" role="dialog">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h4 id="titleModData" class="modal-title"></h4>
      </div>
      <div id="bodymodalData" class="modal-body">

      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>


<!-- MODAL IMAGEN  -->
<div class="autoModal modal fade " id="imagemodal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-body imgmodal">
        <center>
          <img id="imagepreview" src="" data-big="" />
        </center>
      </div>
      <div class="modal-footer">
        <span id="txtWhereIs" class="form-control-static pull-left"></span>
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>

<!-- MODAL PRODUCTOS  -->
<div class="modal fade" id="productsmodal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-admin modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h4 id="titleModProducs" class="modal-title"></h4>
      </div>
      <div class="modal-body">
        <div class="row">
          <div class="col-md-5">
            <img src="" height="400px" id="imgproduct" >
            <p id="imgdescription"></p>
          </div>
          <div class="col-md-7">
            <div class="table-responsive"  id="tblHijos">
              <table class='table'>
                <thead>
                  <tr>
                    <th><?php echo $lngarr['name'] ?></th>
                    <th><?php echo $lngarr['descprod'] ?></th>
                    <th><?php echo $lngarr['download'] ?></th>
                    <th><?php echo $lngarr['rate'] ?></th>
                    <th><?php echo $lngarr['url'] ?></th>
                  </tr>
                </thead>
                <tbody id="tblchilds">
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>


<!-- MODAL GALLERY  -->
<div class="modal fade" id="gallerymodal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-body">
        <!--begin carousel-->
          <div id="myGallery" class="carousel slide" data-interval="false">
            <div class="carousel-inner" id="divgaleria">


            <!--end carousel-inner--></div>
            <!--Begin Previous and Next buttons-->

            <a class="left carousel-control" href="#myGallery" role="button" data-slide="prev"> <span class="glyphicon glyphicon-chevron-left"></span></a> <a class="right carousel-control" href="#myGallery" role="button" data-slide="next"> <span class="glyphicon glyphicon-chevron-right"></span></a>


          <!--end carousel--></div>
      </div>
      <div class="modal-footer">

        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>


<!-- LOG IN -->
<div class="modal fade " id="loginmodal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true" data-backdrop="static">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-body" style="background-color:#272424;">
        <div class="loginbody">
          <div class="logo" style="margin-bottom: 30px;padding-left: 30px">
            <center>
              <a href="index.php"><img width="350px" height="50px" src="./resources/imgs/METEOlogo.png" alt="Geoportal ECOSUR" /></a>
            </center>
          </div>
          <div id="logindiv">
            <center>
              <div class="btn-group" id="btnchangelogin" data-toggle="buttons">
                <label class="btn btn-primary active">
                  <input type="radio" value="login" name="options" id="option1" autocomplete="off" checked> <?php echo $lngarr['login']; ?>
                </label>
                <label class="btn btn-primary">
                  <input type="radio" name="options" value="signup" id="option2" autocomplete="off">  <?php echo $lngarr['signup']; ?>
                </label>
                <br><br>
              </div>
            </center>
            <form id="frmlogin" action="">
              <fieldset>
                <input type="text" name="username" placeholder="<?php echo $lngarr['loginfield1']; ?>" required>
                <input type="password" name="password" placeholder="<?php echo $lngarr['password']; ?>" required>
              </fieldset>
              <div id="mensaje_login" style="color:red";></div>
              <a href="#" id="btnResetPass"><?php echo $lngarr['resetpass']; ?></a>
              <h3></h3>
              <input type="submit" value="<?php echo $lngarr['login']; ?>">
              <a href="<?php echo  htmlspecialchars($loginUrl);?>" id="btnLogFacebook"><?php echo $lngarr['facebook']; ?></a>
              <a  id="btnLogGhest"><?php echo $lngarr['invitado']; ?></a>
            </form>
            <form id="frmsignup" class="invisible">
              <fieldset>
                <input type="text" name="username" placeholder="<?php echo $lngarr['username']; ?>" required>
                <input type="email" name="email" placeholder="<?php echo $lngarr['email']; ?>" required>
                <input type="password" name="password" min placeholder="<?php echo $lngarr['password']; ?>" pattern=".{8,}"   required title="8 characters minimum" required>
              </fieldset>
              <div id="mensaje_signup" style="color:red";> </div>
              <input type="submit" value="<?php echo $lngarr['signup']; ?>">
              <a href="<?php echo  htmlspecialchars($loginUrl);?>" id="btnRegFacebook"><?php echo $lngarr['signupfacebook']; ?></a>
            </form>
          </div>
          <br>
          <div>
            <a href="index.php?lang=es"><span class="flag-icon flag-icon-mx"></span> Español </a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="index.php?lang=en"><span class="flag-icon flag-icon-us"></span> English </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>


<!-- Modal DOWNLOAD OPTIONS-->
<div class="modal fade" id="modDownload2" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-sm">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h4 class="modal-title"><?php echo $lngarr['download'] ?></h4>
      </div>
      <div class="modal-body">
        Click in "Generate file" and the system will generate automatically a compressed file with the selected images. While the file is generated you can still using the geoportal. <strong>You'll be notify when the file will be ready to download.</strong><br><br>
        <!--<span id="mensajedownload"></span>-->
        <button type="button" id="btnDownloadImages" class="btn btn-primary">Generate file</button>
        <button type="button" id="btnCleanCar" class="btn btn-warning">Clean</button>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>


<!-- MODAL PRODUCTOS  -->
<div class="modal fade" id="notificacionesmod" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-sm">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h4 id="titleModProducs" class="modal-title"></h4>
      </div>
      <div class="modal-body">
        <div id="bodynots"></div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal"><?php echo $lngarr['close'] ?></button>
      </div>
    </div>
  </div>
</div>