<div class="row" style="margin-left: 0;margin-right: 0; height:calc(100% - 64px)">

<div id="mySidenav" class="sidenav">
  <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>
  <div id="sidebar-content" class='container'> </div>
</div>

    <div class="col-xl-3 col-md-5 d-none d-md-block container"  style="height:100%">

      <ul id="mytabs" class="nav nav-tabs nav-fill" role="tablist">
        <li class="nav-item" >
          <a class="nav-link active" data-toggle="tab" href="#xel-tab">
          Building blocks <i class="fas fa-boxes"></i>
          </a>
        </li>
        <li class="nav-item" data-step="6" data-intro='<?php echo $lngarr['Paso_6'] ?> '>
          <a class="nav-link" data-toggle="tab" href="#results-tab"><?php echo $lngarr['results'] ?> <i class="fas fa-poll"></i></a>
        </li>
      </ul>

      <div class="tab-content" style="height:calc(100% - 42px);overflow:auto">

        <!-- TAB 2.5 designer tools -->
        <div class="tab-pane active" id="xel-tab" style="height:100%">
          <div class="invisible" id="invisible_link" ></div> <!-- div invisible. unicamente para el link de descarga de datos -->
          <hr>
            
          <!-- Example split danger button -->
            <div class="btn-group btn-block">
              <button id="output" onClick="Xel_run()" class="btn btn-outline-success col-11">RUN</button>
              <button id="run_dropdown" type="button" class="btn btn-outline-success dropdown-toggle dropdown-toggle-split col-1" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <span class="sr-only">Toggle Dropdown</span>
              </button>
              <div class="dropdown-menu">
                <a class="dropdown-item" onClick="Xel_run(false,true)">Run everything (force)</a>
                <a class="dropdown-item" onClick="Xel_run(true,false)">Run as a Copy</a>

              </div>
            </div>
          
          <hr>
          <button onClick="Xel_clean()" class="btn btn-outline-secondary col-12">Clean</button>
          <hr>
          <div class ="col-sm-12" id="leftcard" style="height:100%" >

          <h5 class="font__family-montserrat font__weight-light text-uppercase font__size-18 text-blue brk-library-rendered" data-brk-library="component__title">Services</h5>




          <div id="sectionDIV" style=" overflow-y:auto; overflow-x:hidden" > <!--height:100%;-->
              <div id="blocklist">
                <div class="accordion" id="faq">
                  </div> <!-- end section of cards-->
                </div>
              </div>


          <hr>

          <div class="container-fluid" style="width: 100%; height: 40%; overflow-y: auto;overflow-x: hidden;" id="DAG_exe_opt"><!--display:None-->

          <h5>EXECUTION OPTIONS</h5>
            <div class="form-group row">
              <label for="ntype" class="col-5 col-form-label col-form-label-sm">API gateway host</label>
                <div class="col-5">
                        <input placeholder="default (e.g. 127.0.0.1:54350)" id="ip_gateway" value="" type="text" class="form-control form-control-sm">
                </div>
            </div>

            <div class="form-group row">
              <label for="ntype" class="col-5 col-form-label col-form-label-sm">Iterations (1 by default) </label>
                <div class="col-3">
                        <input value=1 id="dag_iterations" type="number" class="form-control form-control-sm"  min="1" max="1000">
                </div>
            </div>

            <div class="form-group row">
              <label for="ntype" class="col-3 col-form-label col-form-label-sm">Download log</label>
                <div class="col-1">
                        <input type="checkbox" class="form-check-input" id="dag_savelog">
                </div>
                <label for="ntype" class="col-5 col-form-label col-form-label-sm">Automatic download results</label>
                <div class="col-1">
                        <input type="checkbox" class="form-check-input" id="dag_saveresults">
                </div>
                <label for="ntype" class="col-5 col-form-label col-form-label-sm">Keep resources</label>
                <div class="col-1">
                        <input type="checkbox" class="form-check-input" id="if_keep_resources">
                </div>
            </div>
            



            
            </div>

            <div class="container row">
            <p class="text-left text-uppercase font-italic">Export/import Dags</p>

                <div class="btn-group btn-block">
                    <button id="btnImport" class="btn btn-outline-info ">IMPORT</button>
                    <button id="btnExport" class="btn btn-outline-dark ">EXPORT</button>
                </div>
                <div class="btn-group btn-block">
                    <button id="btnSave-solutions" onClick="$('#modal_save-solutions').modal('show');" class="btn btn-outline-info">SAVE</button>
                    <button id="btnList-solutions" onClick="BTN_list_solution()" class="btn btn-outline-dark ">LIST</button>
                </div>
                <input type="file" style="display: none" id="inputImport"/>

              </div>  
              <hr>

              <div class="container row">
             <p class="text-left text-uppercase font-italic">Download project</p>

                <div class="btn-group btn-block">
                    <button class="btn btn-outline-light" onclick="DownloadProject()">Download</button>
                </div>
              </div>  
          </div>
        </div>

        <!-- TAB 3 -->
        <div class="tab-pane options container-fluid" id="results-tab">
        <hr>
        <div class="container">
          <p class="text-left text-uppercase font-italic"><?php echo $lngarr['results'] ?></p>
          </div>

          <div id="results_panel" class="container-fluid">
            <div  id="results" class="col-12" ></div>
            <div  id="results2" class="col-12"> </div>
          </div>


        </div>

        
      </div>
    </div>


    <div class="col-xl-9 col-md-7 col-sm-12" style="height:100%">
      <ul id="tabs_show" class="nav nav-tabs">
        <li class="nav-item ml-auto"><a class="nav-link active" href="#designer" data-toggle="tab">Designer <i class="fas fa-pen-alt"></i></a></li>
        <li class="nav-item"><a aria-current="page" class="nav-link" href="#mapContainer" data-toggle="tab"> Map <i class="fas fa-map-marker-alt"></i></a></li>
        <li class="nav-item"><a aria-current="page" class="nav-link" href="#templates" data-toggle="tab">Templates <i class="fab fa-buromobelexperte"></i></a></li>
        <li class="nav-item"><a aria-current="page" class="nav-link" href="#logs" data-toggle="tab">Logs <i class="fas fa-scroll"></i></a></li>

        <!--<li class="nav-item">
          <a class="nav-link" href="#report" onClick="get_topoformas();" data-toggle="tab" id="btnReporte">Report 
            <span class="glyphicon glyphicon-list" aria-hidden="true">
            </span>
          </a>
        </li>-->
      </ul>

      <div class="tab-content" style="height:calc(100% - 42px)">

        <!-- TAB 1-->
        <div class="col-12 animate-smooth tab-pane options" style="height:100%" id="mapContainer"> 
          <div id="map" style="width:100%; height:100%"></div>
        </div>

        <!-- TAB 2-->
        <div class="col-12 animate-smooth tab-pane active" style="height:100%; padding-left: 1px;padding-right: 1px" id="designer">
            <div id="canvas"></div>
        </div>
        <!-- TAB 3 -->
        <div class="html-content col-8 animate-smooth tab-pane options" id="report" style="overflow:auto; height:100%">
        <br>
            <div style="float: right;" class="btn-group" role="group">
              <button onclick="get_topoformas()" class="btn btn-primary btn-sm"><span class="glyphicon glyphicon-refresh" aria-hidden="true"> Refrescar</span></button> &nbsp;
              <!-- <button id="mapa" class="btn btn-success btn-sm"><span class="glyphicon glyphicon-floppy-disk" aria-hidden="true"> Mapa </span></button>&nbsp; -->
              <button onclick="CreatePDF()" class="btn btn-danger btn-sm"><span class="glyphicon glyphicon-save" aria-hidden="true"> PDF</span></button>
              <br> Null = Ausencia de Valor
            </div><br>
            <div class="row"></div>
            <!--<div class="container col-sm-6" id="mapMERRA" style="height:300px"></div>
            <div class="container col-sm-6" id="mapEMAS" style="height:300px"></div>-->

            <div class="row col-sm-12" id="tableReport" style="height:100%; width:100%;">
            <div class="container col-sm-6" id="render_pdf" ></div>

            </div>
        </div>

        <!-- TAB 4-->
        <div class="col-12 animate-smooth tab-pane options" style="height:100%" id="templates"> 
          <hr>
          <div class="col-12">  <button onclick="create_table_templates('table_templates')" class="btn btn-outline-secondary col-12">List templates</button> </div>
          <hr>
          <div class="row"  style="max-height: 750px" id="table_templates"></div>
        </div>

        <!-- TAB logs-->
        <div class="col-12 animate-smooth tab-pane options " style="height:100%" id="logs"> 
          <div class="container" style="width:100%; height:100%;overflow:auto;padding-top: 10px " >

            <div class="panel__wrapper-icon mb-100 brk-library-rendered" data-brk-library="component__panel">
                <div class="panel__head all-light">
                  <h4 class="font__family-montserrat font__weight-medium font__size-21">LOGs</h4>
                  <p class="font__family-open-sans font__size-14"></p>
                </div>
              <ul class="panel__list" id="logs-panel">
              </ul>
            </div>

          </div>
        </div>


      </div>
    </div> <!--end left panel-->

</div>


