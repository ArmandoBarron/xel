


/// SERVICOS DE PREPROCESAMIENTO
SECTION = "sec-datasource"
ServicesArr.push({
        id: "ds",
        type:"DATASOURCE",
        name: "Simple datasouce",
        section:SECTION,
        desc: `Upload your data to Xel`,
        columns:{
            default: null,
            parent: [] 
        },
        params: {
            actions:"",
            datasouce:"",
            user_workspace:"",
            SAVE_DATA:true
        },
        html: `

                <div class="form-group row">
                        <label for="txttype" class="col-12 col-form-label col-form-label-sm">Upload your dataset</label>
                </div>     
                <div class="form-group row ">
                        <div class="col-8">
                                <input type="file" id="files" class="form-control" />
                        </div>
                        <div class="col-4">
                                <button onclick="Upload_graph_data()" id="files_button"  class="btn btn-primary btn-block"><span class="glyphicon glyphicon-paperclip" aria-hidden="true"></span> upload data</button>
                        </div>
                </div>

                <div class="form-group row">
                        <div id="cleandata_button" style="display:none" >
                         <button  style="margin:1px;" onclick="Clean_graph_data()" class="btn btn-primary btn-block"><span class="glyphicon glyphicon-floppy-remove" aria-hidden="true"></span> remove data</button>
                        </div>
                </div>

                <div class="form-group row">
                        <label for="txttype" class="col-12 col-form-label col-form-label-sm">Select an existing dataset</label>
                </div>   

                <div class="form-group row">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Select a workspace: </label>
                        <div class="col-sm-8">
                                <select class="form-control" id="user_workspace" data-actions-box="true" onclick=fillworkspaces(this) >
                                <option value="Default" selected>Default</option>'
                                </select>
                        </div>
                </div>               

                <div class="form-group row container">
                        <button  style="margin:1px;" onclick="fillWorkspaceFilesliest()" class="btn btn-outline-primary btn-sm btn-block"> Load files list</button>
                </div>    


                <div class="form-group container col-12 table-responsive" id="datasource-table">
                </div>
                
`
    }
)