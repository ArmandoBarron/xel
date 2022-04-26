


/// SERVICOS DE PREPROCESAMIENTO
SECTION = "sec-proc"

ServicesArr.push({
        id: "s-neural-networks",
        name: "deeplearning",
        section:SECTION,
        columns:{
            default: ['class'],
            parent: [] 
        },
        desc: "Set of algorithms to preform predictions",
        params: { columns: [], trainSize: 80,epoch:10,classColumn:"",lossFunction:"CategoricalCrossentropy",metric:"",actions:"",SAVE_DATA:true},
        html: `
        <div class="form-check" style="text-align: right;">
            <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
            <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>
                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm"> Kind of neural network: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="actions" onchange="ChangeVisibileOptionsOfService(this)">
                                        <option value="CNN" selected> CNN </option>
                                        <option value="RNN"> RNN </option>
                                        <option value="LSTM"> LSTM </option>
                                </select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-2 col-form-label col-form-label-sm">Columns: </label>
                                <div class="col-sm-10">
                                <select class="form-control columns" id="columns" data-actions-box="true" onclick=fillselect(this) ></select>
                                </div>
                        </div>
                        <div class="form-group row m-2">
                                <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">training size(%): </label>
                                <div class="col-sm-8">
                                        <input id="trainSize" type="number" class="form-control form-control-sm" min="10" max="90" value=80>
                                </div>
                        </div>
                        <div class="form-group row m-2">
                                <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Epoch: </label>
                                <div class="col-sm-8">
                                        <input id="epoch" type="number" class="form-control form-control-sm"  min="1" max="100">
                                </div>
                        </div>
                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Class column (to predict): </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="classColumn" onclick=fillselect(this,mult=false) ></select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Batch size: </label>
                                <div class="col-sm-8">
                                        <input id="batch" type="number" class="form-control form-control-sm"  min="1" max="100">
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">units for input layer (filters for CNN): </label>
                                <div class="col-sm-8">
                                        <input id="layer_units" type="number" class="form-control form-control-sm"  min="1" max="999">
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">units for dense layer: </label>
                                <div class="col-sm-8">
                                        <input id="dense_units" type="number" class="form-control form-control-sm"  min="1" max="999">
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">units for gru layer: </label>
                                <div class="col-sm-8">
                                        <input id="gru_units" type="number" class="form-control form-control-sm"  min="1" max="999">
                                </div>
                        </div>
                        
                        <div class="form-group row m-2">
                                <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">kernel size: </label>
                                <div class="col-sm-8">
                                        <input id="kernel_size" type="number" class="form-control form-control-sm"  min="1" max="100">
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Loss function: </label>
                                <div class="col-sm-8">
                                        <select class="form-control" id="lossFunction">
                                        <optgroup label="Probabilistic losses">
                                                <option value="BinaryCrossentropy">BinaryCrossentropy </option>
                                                <option selected value="CategoricalCrossentropy"> CategoricalCrossentropy </option>
                                                <option value="SparseCategoricalCrossentropy"> SparseCategoricalCrossentropy</option>
                                                <option value="Poisson"> Poisson </option>
                                                <option value="binary_crossentropy"> binary_crossentropy</option>
                                                <option value="categorical_crossentropy"> categorical_crossentropy</option>
                                                <option value="sparse_categorical_crossentropy"> sparse_categorical_crossentropy</option>
                                                <option value="KLDivergence"> KLDivergence </option>
                                        </optgroup>

                                        <optgroup label="Regression losses">
                                                <option value="MeanSquaredError"> MeanSquaredError</option>
                                                <option value="MeanAbsoluteError">MeanAbsoluteError </option>
                                                <option value="MeanAbsolutePercentageError"> MeanAbsolutePercentageError </option>
                                                <option value="MeanSquaredLogarithmicError"> MeanSquaredLogarithmicError </option>
                                                <option value="CosineSimilarity"> CosineSimilarity </option>
                                                <option value="mean_squared_error"> mean_squared_error </option>
                                                <option value="mean_absolute_error"> mean_absolute_error </option>
                                                <option value="mean_absolute_percentage_error"> mean_absolute_percentage_error </option>
                                                <option value="mean_squared_logarithmic_error"> mean_squared_logarithmic_error </option>
                                                <option value="cosine_similarity"> cosine_similarity </option>
                                                <option value="Huber"> Huber </option>
                                                <option value="LogCosh"> LogCosh </option>
                                                <option value="log_cosh"> log_cosh </option>
                                        </optgroup>}

                                        <optgroup label="Hinge losses for 'maximum-margin'">
                                                <option value="Hinge"> Hinge </option>
                                                <option value="SquaredHinge"> SquaredHinge </option>
                                                <option value="CategoricalHinge"> CategoricalHinge </option>
                                                <option value="squared_hinge"> squared_hinge </option>
                                                <option value="categorical_hinge"> categorical_hinge </option>
                                        </optgroup>

                                        </select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Evaluation metric: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="metric">
                                        <option value="accuracy"> Accuracy </option>
                                </select>
                                </div>
                        </div>


                `

    }
)

ServicesArr.push(
        {
                id: "clustering-algh",
                name: "clustering_service",
                section:SECTION,
                desc: `Set of clustering algorithms. Group a dataset records in K groups`,
                columns:{
                    default: ['class'],
                    parent: [] 
                },
                params: {
                        algh: 'kmeans',
                        k:2,
                        columns: "",
                        clustering_params: '{"dbscan":{"eps":0.5,"min_samples":10},"agglomerative":{"linkage":"ward"}}',
                        SAVE_DATA:true
                },
                html: `
                <div class="form-check" style="text-align: right;">
                    <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
                    <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
                </div>
                <br>

                        <h4>Algorithm:</h4>
                        <div class="form-group">
                                <select id="algh" required data-actions-box='true' class="form-control">
                                        <option value="kmeans" selected>K-Means</option>
                                        <option value="gm">Gaussian Mixture</option>
                                        <option value="dbscan">DBscan</option>
                                        <option value="agglomerative">hierarchical</option>
                                </select>
                        </div>

                        <h4>No. of groups (k) </h4>
                        <div class="form-group">
                                <input type="number" class="form-control solo-numero" min="2" value="2" required id="k">
                        </div>

                        <h4>Variables: </h4>
                        <div class="form-group">
                                <select class="form-control" id="columns" data-actions-box="true" onclick=fillselect(this)></select>
                        </div>

                        <h4>Additional params </h4>
                        <div class="form-group">
                                <input type="text" class="form-control" id="clustering_params" value='{"dbscan":{"eps":0.5,"min_samples":10},"agglomerative":{"linkage":"ward"}}'>
                        </div>

                        <span class="help-block">linkage:average,complete,single, or ward.</span>
                        <span class="help-block">eps:0 to 1.</span>
                        <span class="help-block">min_samples:min 5</span>

                                `
            }
)


// REGRESSIONS 
//====================================================================================
ServicesArr.push(
        {
                id: "regression_serv",
                name: "regression",
                section:SECTION,
                desc: `service with linear and logarithmic regression models.`,
                columns:{
                    default: [],
                    parent: [] 
                },
                params: {
                        actions: '',
                        var_x:'',
                        list_var_x:[],
                        var_y: '',
                        filter_column: '',
                        filter_value: '',
                        alpha: .05,
                        SAVE_DATA:true
                },
                html: `
                <div class="form-check" style="text-align: right;">
                    <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
                    <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
                </div>
                <br>

                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm"> Kind of regression: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="actions" onchange="ChangeVisibileOptionsOfService(this)">
                                        <option value=""></option>
                                        <option value="LINEARS"> Linear - simple </option>
                                        <option value="LINEARM"> Linear - multivariable  </option>
                                        <option value="LOGS"> logarithmic - simple </option>
                                        <option value="LOGM"> logarithmic - multivariable  </option>
                                </select>
                                </div>
                        </div>

                        <h4>Input variable/s (x): </h4>
                        <div servopt="LINEARM LOGM" class="form-group">
                                <select class=" form-control" id="list_var_x" data-actions-box="true" onclick=fillselect(this)></select>
                        </div>
                        <div servopt="LINEARS LOGS" class="form-group">
                                <select class="form-control" id="var_x" data-actions-box="true" onclick=fillselect(this,mult=false)></select>
                        </div>

                        <h4>target variables (y): </h4>
                        <div class="form-group">
                                <select class="form-control" id="var_y" data-actions-box="true" onclick=fillselect(this,mult=false)></select>
                        </div>

                        <h4>Filter data by the column:</h4>
                        <div class="form-group">
                                <select class="form-control" id="filter_column" data-actions-box="true" onclick=fillselect(this,mult=false)>
                                <option value=""></option>
                                </select>
                        </div>
                        <h4>... with the value of: </h4>
                        <div class="form-group">
                                <input type="text" class="form-control" id="filter_value" value=''>
                        </div>

                
                        <h4>Alpha (Acceptable error rate)</h4>
                        <div class="form-group">
                                <input id="alpha" type="number" class="form-control form-control-sm"  min="0" max="1" value=".05">
                        </div>
                        <span class="help-block">For example, 0.05 acceptable error is equivalent to 95% reliability of the model.</span>


                `
            }
)