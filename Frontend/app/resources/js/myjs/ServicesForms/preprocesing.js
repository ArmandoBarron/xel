
/// SERVICOS DE PREPROCESAMIENTO
SECTION = "sec-preproc"
ServicesArr.push(
    {
        id: "s-preproc",
        section:SECTION,
        process_tag:"cleanning",
        valid_datatypes:{input:["CSV"],output:["CSV"]},
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
            id: "data_clean",
            section:SECTION,
            process_tag:"cleanning",
            valid_datatypes:{input:["CSV"],output:["CSV"]},
            name: "cleanning",
            desc: `Outliers detection, Normalization, Remove unwanted symbols, Transform categorical data to numeric values. `,
            columns:{
                default: [],
                parent: [] 
            },
            params: {
                actions:"",
                columns: [],
                outliers_detection: "",
                method:"",
                encoding_method:"",
                n_standard_desviations:2,
                min_range:1,
                max_range:1,
                norm_method:"",
                list_values:"",
                replace_with:"",
                label_column:"",
                list_labels:"",
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
                                <select class="form-control" id="actions" onchange="OptionsHandler(this)">
                                        <option value="OUTLIERS"> Outliers removal </option>
                                        <option value="NORMALIZATION"> Normalize and standarize </option>
                                        <option value="CLEAN">Remove unwanted values from dataset </option>
                                        <option value="TOKENIZATION">Categorical columns to numeric</option>
                                        <option value="RENAME">Rename numeric labels</option>
                                        <option value="CLEAN_INT">Clean numeric columns</option>
                                        <option value="COMPLETE">Complete dataset</option>

                                </select>
                        </div>
                </div>


                <div class="form-group row m-2" opth opt-actions="OUTLIERS">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Outliers detection method: </label>
                        <div class="col-sm-8">
                                <select class="form-control" id="outliers_detection" onchange="OptionsHandler(this)">
                                        <option value="ZS"> Z-score </option>
                                        <option value="IQR"> Interquartile range </option>
                                        <option value="M"> Custom range </option>
                                </select>
                        </div>
                </div>

               <div class="form-group row m-2" opth opt-actions="NORMALIZATION">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">normalization method: </label>
                        <div class="col-sm-8">
                                <select class="form-control" id="norm_method">
                                        <option value="ZS"> Z-score </option>
                                        <option value="MinMax"> Min-Max </option>
                                </select>
                        </div>
                </div>

               <div class="form-group row m-2" opth opt-actions="TOKENIZATION">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Encoding method: </label>
                        <div class="col-sm-8">
                                <select class="form-control" id="encoding_method">
                                        <option value="ENCODING"> Replace column by the encoded values </option>
                                        <option value="DUMMY"> Create a new column for every categorical value</option>
                                </select>
                        </div>
                </div>


                <div class="form-group row m-2" opth opt-actions="OUTLIERS NORMALIZATION CLEAN TOKENIZATION CLEAN_INT COMPLETE">
                        <label class="col-sm-4 col-form-label col-form-label-sm">Variables:</label>
                        <div class="col-sm-8">
                                <select class="form-control" id="columns" data-actions-box="true" onclick=fillselect(this)></select>
                        </div>
                </div>

                <div class="form-group row m-2" opth opt-actions="OUTLIERS">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">method: </label>
                        <div class="col-sm-8">
                                <select class="form-control" id="method">
                                        <option value="DEL"> Delete row </option>
                                        <option value="NAN"> Replace with NaN </option>
                                </select>
                        </div>
                </div>

                <div class="form-group row m-2" opth opt-actions="OUTLIERS" opt-outliers_detection="ZS">
                        <label class="col-sm-4 col-form-label col-form-label-sm">Number of standard desviations:</label>
                        <div class="col-sm-4">
                                <input type="number" class="form-control solo-numero" min="1" id="n_standard_desviations">
                        </div>
                </div>
                <div class="form-group row m-2" opth opt-actions="OUTLIERS" opt-outliers_detection="M">
                        <label class="col-sm-4 col-form-label col-form-label-sm">Range min value:</label>
                        <div class="col-sm-4">
                                <input type="number" class="form-control solo-numero" min="1" id="min_range">
                        </div>
                </div>
                <div class="form-group row m-2" opth opt-actions="OUTLIERS" opt-outliers_detection="M">
                        <label class="col-sm-4 col-form-label col-form-label-sm">Range max value :</label>
                        <div class="col-sm-4">
                                <input type="number" class="form-control solo-numero" min="1" id="max_range">
                        </div>
                </div>

                <div class="form-group row m-2" opth opt-actions="CLEAN">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">list of values to replace (separateed by ,)</label>
                        <div class="col-sm-8">
                                <input id="list_values" type="text" class="form-control">
                        </div>
                </div>
                
                <div class="form-group row m-2"  opth opt-actions="CLEAN">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">replace with:</label>
                        <div class="col-sm-8">
                                <input id="replace_with" type="text" class="form-control">
                        </div>
                </div>

                <div opth opt-actions="RENAME">
                        <div class="form-group row m-2">
                                <label class="col-sm-4 col-form-label col-form-label-sm">Label column:</label>
                                <div class="col-sm-8">
                                        <select class="form-control" id="label_column" data-actions-box="true" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">list of labels separated by ,</label>
                                <div class="col-sm-8">
                                        <input id="list_labels" type="text" class="form-control">
                                </div>
                        </div>

                </div>
`
        }
    )


ServicesArr.push(
        {
            id: "s-imputation",
            section:SECTION,
            process_tag:"imputation",
            valid_datatypes:{input:["CSV"],output:["CSV"]},
            name: "imputation",
            desc: `Fill missing values`,
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
                method:"any",
                n_na:0,
                to_drop:"",
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
                                <select class="form-control" id="actions" onchange="OptionsHandler(this)">
                                        <option value="IMPUTATION"> Imputation of Na values </option>
                                        <option value="DROP"> Drop Na values  </option>

                                </select>
                        </div>
                </div>



                <div class="form-group row m-2">
                        <label class="col-sm-4 col-form-label col-form-label-sm">Variables:</label>
                        <div class="col-sm-8">
                                <select class="form-control" id="columns" data-actions-box="true" onclick=fillselect(this)></select>
                        </div>
                </div>

                <div opth opt-actions="IMPUTATION">
                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Imputation type: </label>
                                <div class="col-sm-8">
                                        <select class="form-control" id="imputation_type" onchange="OptionsHandler(this)">
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


                        <div class="form-group row m-2" opth opt-imputation_type="Single_N Single_G">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Strategy: </label>
                                <div class="col-sm-8">
                                        <select class="form-control" id="strategy">
                                                <option value="mean"> Mean </option>
                                                <option value="median"> Median </option>
                                                <option value="most_frequent"> Most frequent </option>
                                        </select>
                                </div>
                        </div>

                        <div class="form-group row m-2" opth opt-imputation_type="Knn_N Knn_G">
                                <label class="col-sm-4 col-form-label col-form-label-sm">neighbors:</label>
                                <div class="col-sm-4">
                                        <input type="number" class="form-control solo-numero" min="2" id="n_neighbors">
                                </div>
                        </div>

                        <div class="form-group row m-2" opth opt-imputation_type="Single_G Iter_G Knn_G">
                                <label class="col-sm-4 col-form-label col-form-label-sm">Group by:</label>
                                <div class="col-sm-8">
                                        <select class="form-control" id="groupby" data-actions-box="true" onclick=fillselect(this)></select>
                                </div>
                        </div>

                        <div class="form-group row m-2" opth opt-imputation_type="Constant_N">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Fill value:</label>
                                <div class="col-sm-8">
                                        <input id="fill_value" type="text" class="form-control" placeholder="-99, missing value, wtc">
                                </div>
                        </div>
                </div>

                <div opth opt-actions="DROP">

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Drop if: </label>
                                <div class="col-sm-8">
                                        <select class="form-control" id="method">
                                                <option value="any"> Some columns </option>
                                                <option value="all"> All the columns </option>
                                        </select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label class="col-sm-6 col-form-label col-form-label-sm">If exist the following n columns with na, where n=</label>
                                <div class="col-sm-4">
                                        <input type="number" class="form-control solo-numero" min="0" id="n_na">
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Then drop: </label>
                                <div class="col-sm-8">
                                        <select class="form-control" id="to_drop" >
                                                <option value="1"> The columns </option>
                                                <option value="0"> The row </option>
                                        </select>
                                </div>
                        </div>


                </div>

               



`
        }
    )

    ServicesArr.push(
        {
            id: "s-split-and-join",
            section:SECTION,
            process_tag:"transform",

            valid_datatypes:{input:["CSV"],output:["CSV"]},
            name: "join_split",
            desc: `split and join column values.`,
            columns:{
                default: [],
                parent: [] 
            },
            params: {
                actions:[],
                column: "",
                method: "",
                date_format: "%Y-%m-%d",
                split_value:"/",
                columns:"",
                separator:"",
                column_name:"",
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
                                <select class="form-control" id="actions" onchange="OptionsHandler(this)">
                                        <option value="SCOLUMN"> split column </option>
                                        <option value="JCOLUMN"> join columns </option>

                                </select>
                        </div>
                </div>

                <div optg opt-actions="JCOLUMN">
                        <div class="form-group row m-2" >
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">list of columns to join:</label>
                                <div class="col-sm-8">
                                        <input id="columns" type="text" class="form-control autocomplete-column" placeholder="e.g.: date,year,ID">
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Separator: </label>
                                <div class="col-sm-8">
                                        <select class="form-control" id="separator">
                                                <option value="-"> - </option>
                                                <option value="_"> _ </option>
                                                <option value="/"> / </option>
                                                <option value="*"> * </option>
                                        </select>
                                </div>
                        </div>

                        <div class="form-group row m-2" >
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">New column name:</label>
                                <div class="col-sm-8">
                                        <input id="column_name" type="text" class="form-control">
                                </div>
                        </div>
                </div>

                <div optg opt-actions="SCOLUMN">
                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Column split type: </label>
                                <div class="col-sm-8">
                                        <select class="form-control" id="method" onchange="OptionsHandler(this)">
                                                <option value="DT"> Datetime </option>
                                                <option value="M"> Custom </option>
                                        </select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label class="col-sm-4 col-form-label col-form-label-sm">Column to split:</label>
                                <div class="col-sm-8">
                                        <select class="form-control" id="column" data-actions-box="true" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                        <div class="form-group row m-2" opth opt-method="DT">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Datetime format:</label>
                                <div class="col-sm-8">
                                        <input id="date_format" type="text" class="form-control" placeholder="%Y-%m-%d">
                                </div>
                        </div>

                        <div class="form-group row m-2" opt-method="M">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">split token:</label>
                                <div class="col-sm-8">
                                        <input id="split_value" type="text" class="form-control" placeholder="/">
                                </div>
                        </div>
                </div>
                
`
        }
    )


ServicesArr.push({
        id: "DST",
        name: "transform_ds",
        process_tag:"query or filter",
        valid_datatypes:{input:["CSV"],output:["CSV"]},
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
            column_name:"",
            rename_dict:"{}",
            exec_code:"",
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
                                        <option value="MELT"> Melt columns (columns to rows) </option>

                                </select>
                                </div>
                        </div>

                        
                        <div class="form-group row m-2" servopt="MAPR MELT" >
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Column of groups</label>
                                <div class="col-sm-8">
                                <select class="form-control" id="group_columns" data-actions-box="true" onclick=fillselect(this) ></select>
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="MELT" >
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">New column name:</label>
                                <div class="col-sm-8">
                                        <input id="column_name" type="text" class="form-control" placeholder="e.g. column_value">
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
                                <label for="txttype" class="col-sm-12 col-form-label col-form-label-sm">Optional query:</label>
                                <div class="col-sm-12">
                                        <textarea id="query_str" type="text" class="form-control codearea"></textarea>
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="EVAL" >
                                <label for="txttype" class="col-sm-12 col-form-label col-form-label-sm">Environment</label>
                                <div class="col-sm-12">
                                        <textarea id="exec_code" type="text" class="form-control codearea"></textarea>
                                </div>
                                <div class="container">
                                        <span class="help-block">Define Variables: x=19;y='great';</span>
                                </div>

                        </div>

                        <div class="form-group row m-2" servopt="EVAL" >
                                <label for="txttype" class="col-sm-12 col-form-label col-form-label-sm">Create or alter columns:</label>
                                <div class="col-sm-12">
                                        <textarea id="query_list" type="text" class="form-control codearea" placeholder="e.g. create a column C as: C  = A + B "></textarea>
                                </div>
                                <div class="container">
                                        <span class="help-block">Multiple querys can be provided separated by ;</span>
                                        <span class="help-block">Express columns with white spaces enclosed wiith {}. Do note use " </span>
                                        <span class="help-block">Use Ctrl+Space for hints</span>
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="EVAL" >
                                <label for="txttype" class="col-sm-12 col-form-label col-form-label-sm">Query for filter:</label>
                                <div class="col-sm-12">
                                        <textarea id="query_flt" type="text" class="form-control codearea" placeholder="e.g. fecha < 2000 "></textarea>
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

    ServicesArr.push(
        {
            id: "s-merge",
            section:SECTION,
            process_tag:"fusion",
            valid_datatypes:{input:["ZIP"],output:["CSV"]},
            name: "fusion",
            desc: `Service to fusion datasources in a zip.`,
            columns:{
                default: [],
                parent: [] 
            },
            params: {
                list_files: [],
                list_columns: "",
                method: [],
                SAVE_DATA:true
            },
            html: `
        <div class="form-check" style="text-align: right;">
                <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
                <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>

                <div class="form-group row m-2">
                        <div class="col-sm-12 namefiles-tree" id="list_files" type="namefiles-tree">
                        </div>
                </div>
                <div class="form-group row m-2">
                        <button id="btn_files" type="button" onclick="Handler_selectedFileNames('#list_files','list_columns')" class="btn btn-block btn-outline-primary">Confirm selections</button>
                </div>

                <hr>

                <div id="list_columns" type="namefiles-list">

                </div>

                <div class="form-group row m-2">
                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Method:</label>
                        <div class="col-sm-8">
                        <select class="form-control selectpicker" id="method">
                                <option value="inner"> inner </option>
                                <option value="outer"> outer </option>
                        </select>
                        </div>
                </div>


                    `
        }
    )
    


    ServicesArr.push(
        {
            id: "s-FilterColumn",
            section:SECTION,
            process_tag:"filter by rule",
            valid_datatypes:{input:["CSV"],output:["CSV"]},
            name: "filter_column",
            desc: `drop and keep columns given a rule.`,
            columns:{
                default: [],
                parent: [] 
            },
            params: {
                columns: [],
                rules: [],
                logical_operator: "",
                operation:"",
                SAVE_DATA:true
            },
            html: `
        <div class="form-check" style="text-align: right;">
        <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
        <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>
        
                <div class="form-group row m-2">
                        <label class="col-sm-4 col-form-label col-form-label-sm">Columns to apply:</label>
                        <div class="col-sm-8">
                                <select class="form-control" id="columns" data-actions-box="true" onclick=fillselect(this)></select>
                        </div>
                </div>

                <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">If column satisfy: </label>
                        <div class="col-sm-8">
                                <select class="form-control" id="logical_operator">
                                        <option value="and"> All the rules </option>
                                        <option value="or"> At least one rule </option>
                                </select>
                        </div>
                </div>

                <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Then: </label>
                        <div class="col-sm-8">
                                <select class="form-control" id="operation">
                                        <option value="drop"> drop the column </option>
                                        <option value="keep"> keep the column </option>
                                </select>
                        </div>
                </div>

                <div class="form-group row m-2">
                        <button id="btn_AddRule" type="button" onclick="Handler_Rules('#rules')" class="btn btn-block btn-outline-primary">Add new rule</button>
                </div>

                <hr>
                <div class="container" id="rules" type="logical-rules" style="overflow: auto;max-height: 400px;">

                </div>

`
        }
    )
