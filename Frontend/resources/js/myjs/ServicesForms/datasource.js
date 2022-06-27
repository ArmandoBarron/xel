


/// SERVICOS DE PREPROCESAMIENTO
SECTION = "sec-datasource"
ServicesArr.push({
        id: "ds",
        service_type:"DATASOURCE",
        name: "Simple datasouce",
        section:SECTION,
        desc: `Upload your data to Xel`,
        columns:{
            default: null,
            parent: [] 
        },
        params: {
            file_delimiter:",",
            user_workspace:"Default",
            force_describe:false
        },
        html: `

                <div class="form-group row">
                        <label for="txttype" class="col-sm-3 col-form-label font-weight-bold">1) Select a workspace: </label>
                        <div class="col-sm-6">
                                <select class="form-control selectpicker" id="user_workspace" data-actions-box="true" onclick=fillworkspaces(this) onChange=SelectWorkspace(this)>
                                </select>
                        </div>
                        <div class="col-sm-3">
                                <div class="btn-group btn-block">
                                        <button  onclick="ModalCreate('workspace')" class="btn btn-outline-warning"><i class="fas fa-folder-plus"></i></button>
                                        <button  onclick="TriggerDelete('workspace')" class="btn btn-outline-danger"><i class="fas fa-trash"></i></button>
                                </div>
                        </div>
                </div>        
                <hr>

                <div class="form-group row">
                        <label for="txttype" class="col-3 col-form-label font-weight-bold">2) Preferences:</label>

                        <label for="txttype" class="col-2 col-form-label col-form-label-sm">Delimiter:</label>
                        <div class="col-sm-3">
                                <select class="form-control selectpicker" id="file_delimiter" data-actions-box="true">
                                        <option value=",">comma (,)</option>
                                        <option value="\t">TAB (\t)</option>
                                        <option value=";">semicol (;)</option>
                                </select>
                        </div>
                </div>

                <hr>
                <div class="form-group row">
                        <label for="txttype" class="col-12 col-form-label font-weight-bold">A) Upload your dataset</label>
                </div>     
                <div class="form-group row " id="group-upload">
                        <div class="col-7">
                                <input type="file" id="files" class="form-control-file"/>
                        </div>
                        <div class="col-5">
                                <button onclick="Upload_graph_data()" id="files_button"  class="btn btn-primary btn-block">Upload <i class="fas fa-cloud-upload-alt"></i></button>
                        </div>
                </div>
                <div id="progress-div" class="progress" style="display: none;">
                        <div id="progress_upload_dataset" class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>
                </div>
                
                <div class="form-group row container" id="cleandata_button" style="display:none">
                        <button  style="margin:1px;" onclick="Clean_graph_data()" class="btn btn-outline-warning btn-block"> Remove data </button>
                </div>    



                <hr>
                <div class="form-group row">
                        <label for="txttype" class="col-6 col-form-label font-weight-bold ">B) Select an existing dataset</label>
                        <div class="col-sm-6"> 
                                <div class="form-check">
                                        <input class="form-check-input" type="checkbox" value="" id="force_describe">
                                        <label class="form-check-label col-form-label-sm" for="flexCheckIndeterminate">Force render when loading existing dataset</label>
                                </div>
                        </div>
                </div>   

     
        
                <div class="form-group row container">
                        <button  style="margin:1px;" onclick="fillWorkspaceFilesliest()" class="btn btn-outline-primary btn-sm btn-block"> List datasets</button>
                </div>    


                <div class="form-group container col-12 table-responsive" id="datasource-table">
                </div>
                
`
    }
)