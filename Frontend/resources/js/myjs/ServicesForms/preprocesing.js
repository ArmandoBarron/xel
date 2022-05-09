
/// SERVICOS DE PREPROCESAMIENTO
SECTION = "sec-preproc"
ServicesArr.push(
    {
        id: "s-preproc",
        section:SECTION,
        name: "preprocessing",
        desc: `Service to preprocess data`,
        columns:{
            default: [],
            parent: [] 
        },
        params: {
            columns: [],
            method: "",
            actions: [],
            SAVE_DATA:true
        },
        html: `
            <div class="form-check" style="text-align: right;">
                <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
                <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
            </div>
            <br>

                <div class="form-group row m-2">
                <label for="txttype" class="col-sm-2 col-form-label col-form-label-sm">Columns: </label>
                        <div class="col-sm-10">
                        <select class="form-control columns" id="columns" data-actions-box="true" onclick=fillselect(this) ></select>
                        </div>
                </div>
                <div class="form-group row m-2">
                <label for="txttype" class="col-sm-2 col-form-label col-form-label-sm">Imputation method: </label>
                        <div class="col-sm-10">
                        <select class="form-control" id="method">
                                <option value="mean"> mean </option>
                                <option value="median"> median </option>
                                <option value="mode"> mode </option>

                        </select>
                </div>
                </div>
                <h4>Applications list</h4>
                <ul id="list" class="list-group">
                        <li id="NORMALIZATION" class="list-group-item">Normalization</li>
                        <li id="OUTLIERS" class="list-group-item">Outliers</li>
                        <li id="SAMPLING" class="list-group-item">Sampling</li>
                        <li id="IMPUTATION" class="list-group-item">Imputation</li>
                </ul>

                <h4>Drag Actions</h4>
                <ul id="actions" class="list-group">
                        <li id="IMPUTATION" class="list-group-item">Imputation</li>
                </ul>
                <script type="text/javascript">
                        $('#list').sortable({
                                group: {
                                        name: 'shared',
                                        pull: 'clone',
                                        put: false // Do not allow items to be put into this list
                                },
                                animation: 150,
                                sort: false // To disable sorting: set sort to false
                        });
                        $('#actions').sortable({group: {name: 'shared'},animation: 350,});
                </script>`
    }
)


ServicesArr.push(
        {
            id: "s-clean",
            section:SECTION,
            name: "cleanning",
            desc: `Cleanning dataset: imputation for fill missing values\n and more`,
            columns:{
                default: [],
                parent: [] 
            },
            params: {
                columns: [],
                actions:[],
                imputation_type: "",
                strategy: [],
                groupby:"",
                n_neighbors:2,
                fill_value:"",
                SAVE_DATA:true
            },
            html: `
        <div class="form-check" style="text-align: right;">
        <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
        <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>
        
                <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Process:</label>
                        <div class="col-sm-8">
                                <select class="form-control" id="actions" onchange="ChangeVisibileOptionsOfService(this)">
                                        <option value="IMPUTATION"> Imputation </option>
                                </select>
                        </div>
                </div>

                <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Imputation type: </label>
                        <div class="col-sm-8">
                                <select class="form-control" id="imputation_type" onchange="ChangeVisibileOptionsOfService(this)">
                                        <option value="Single_N"> Single column </option>
                                        <option value="Single_G"> Single column by group </option>
                                        <option value="Iter_N"> Iterative </option>
                                        <option value="Iter_G"> "Iterative by group </option>
                                        <option value="Knn_N"> KNN </option>
                                        <option value="Knn_G"> KNN by group </option>
                                        <option value="Constant_N"> fill with a constant </option>
                                </select>
                        </div>
                </div>

                <div class="form-group row m-2">
                        <label class="col-sm-4 col-form-label col-form-label-sm">Variables:</label>
                        <div class="col-sm-8">
                                <select class="form-control" id="columns" data-actions-box="true" onclick=fillselect(this)></select>
                        </div>
                </div>

                <div class="form-group row m-2" servopt="Single_N Single_G">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Strategy: </label>
                        <div class="col-sm-8">
                                <select class="form-control" id="strategy">
                                        <option value="mean"> Mean </option>
                                        <option value="median"> Median </option>
                                        <option value="most_frequent"> Most frequent </option>
                                </select>
                        </div>
                </div>

                <div class="form-group row m-2" servopt="Knn_N Knn_G">
                        <label class="col-sm-4 col-form-label col-form-label-sm">neighbors:</label>
                        <div class="col-sm-4">
                                <input type="number" class="form-control solo-numero" min="2" id="n_neighbors">
                        </div>
                </div>

                <div class="form-group row m-2" servopt="Single_G Iter_G Knn_G">
                        <label class="col-sm-4 col-form-label col-form-label-sm">Group by:</label>
                        <div class="col-sm-8">
                                <select class="form-control" id="groupby" data-actions-box="true" onclick=fillselect(this)></select>
                        </div>
                </div>

                <div class="form-group row m-2" servopt="Constant_N">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Fill value:</label>
                        <div class="col-sm-8">
                                <input id="fill_value" type="text" class="form-control" placeholder="-99, missing value, wtc">
                        </div>
                </div>


`
        }
    )


ServicesArr.push({
        id: "DST",
        name: "transform_ds",
        section:SECTION,
        desc: `Map reduce: Group dataset to reduce data using a operator. \n Eval: create columns or traansfom your dataset.`,
        columns:{
            default: [],
            parent: [] 
        },
        params: {
            actions:[],
            group_columns:"",
            columns:"",
            group_by:"sum",
            query_str:"",
            query_list:"",
            query_flt:"",
            if_assign:"0",
            if_delete:"0",
            if_rename:"0",
            rename_dict:"{}",
            SAVE_DATA:true
        },
        html: `
        <div class="form-check" style="text-align: right;">
            <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
            <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>

                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm"> Process: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="actions" onchange="ChangeVisibileOptionsOfService(this)">
                                        <option value="MAPR" selected> Map reduce </option>
                                        <option value="EVAL"> Query </option>
                                        <option value="UPDATE"> delete or reneame columns </option>
                                </select>
                                </div>
                        </div>

                        
                        <div class="form-group row m-2" servopt="MAPR" >
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Column of groups</label>
                                <div class="col-sm-8">
                                <select class="form-control" id="group_columns" data-actions-box="true" onclick=fillselect(this) ></select>
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="UPDATE" >
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Delete columns?:</label>
                                <div class="col-sm-8">
                                <select class="form-control" id="if_delete">
                                        <option value="1"> yes </option>
                                        <option value="0"> no </option>
                                </select>
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="MAPR UPDATE" >
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Columns: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="columns" data-actions-box="true" onclick=fillselect(this) >
                                </select>
                                </div>
                        </div>

    
                        <div class="form-group row m-2" servopt="MAPR" >
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Operator:</label>
                                <div class="col-sm-8">
                                <select class="form-control" id="group_by">
                                        <option value="mean"> mean </option>
                                        <option value="median"> median </option>
                                        <option value="sum"> sum </option>
                                        <option value="count"> count </option>

                                </select>
                                </div>
                        </div>
                        <div class="form-group row m-2" servopt="MAPR" >
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Assign results to original dataset:</label>
                                <div class="col-sm-8">
                                <select class="form-control" id="if_assign">
                                        <option value="1"> yes </option>
                                        <option value="0"> no </option>
                                </select>
                                </div>
                        </div>

                        <hr>
                        <div class="form-group row m-2" servopt="MAPR" >
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Optional query:</label>
                                <div class="col-sm-8">
                                        <input id="query_str" type="text" class="form-control" placeholder="e.g. Fecha < 1990 && Fecha > 1980">
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="EVAL" >
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Create or alter columns:</label>
                                <div class="col-sm-8">
                                        <input id="query_list" type="text" class="form-control autocomplete-column" placeholder="e.g. create a column C as: C  = A + B ">
                                </div>
                                <div class="container">
                                        <span class="help-block">Multiple querys can be provided separated by ;</span>
                                        <span class="help-block">Express columns with white spaces enclosed wiith {}. Do note use " </span>
                                        <span class="help-block">Examples:</span>
                                        <span class="help-block">E = (A + B) / (C + D)</span>
                                        <span class="help-block">G = A + A.mean()</span>
                                        <span class="help-block">G = 'OK'</span>
                                        <span class="help-block">{Column A} = (A + A.mean()).round(1)</span>
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="EVAL" >
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Query for filter:</label>
                                <div class="col-sm-8">
                                        <input id="query_flt" type="text" class="form-control autocomplete-column" placeholder="e.g. fecha < 2000 ">
                                </div>
                                <div class="container">
                                        <span class="help-block">Multiple querys can be provided separated by ;</span>
                                        <span class="help-block">Express columns with white spaces enclosed wiith {}. Do note use " </span>
                                </div>

                        </div>

                        <div class="form-group row m-2" servopt="UPDATE" >
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Rename columns?</label>
                                <div class="col-sm-8">
                                <select class="form-control" id="if_rename">
                                        <option value="1"> yes </option>
                                        <option value="0"> no </option>
                                </select>
                                </div>
                        </div>
                        <div class="form-group row m-2" servopt="UPDATE" >
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">json string with column names:</label>
                        <div class="col-sm-8">
                                <input id="rename_dict" type="text" class="form-control autocomplete-column">
                        </div>
                        <div class="container">
                                <span class="help-block">{"name of column":"new name", "col2":"newcol2"}</span>
                                <span class="help-block">Use "" , '' or \`\` are not valid.</span>
                        </div>

                </div>

                </div>

                        `
    })