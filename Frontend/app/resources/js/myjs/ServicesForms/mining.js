


/// SERVICOS DE PREPROCESAMIENTO
SECTION = "sec-mining"

ServicesArr.push(    {
    id: "s-txt-class",
    process_tag:"text-mining",
    name: "text_classification",
    valid_datatypes:{input:["CSV"],output:["ZIP"]},

    section:SECTION,
    desc: `Classification algorithms for plain text`,
    columns:{
        default: null,
        parent: [] 
    },
    params: {
        SAVE_DATA: false,
        actions: "PREPROCESSING",
        batch_size: 32,
        contentColumn: "OriginalTweet",
        epoch: 10,
        labelColumn: "Sentiment",
        objective: "",
        mlp_parameters:"",
        svc_parameters:""
    },
    html: `
    <div class="form-check" style="text-align: right;">
        <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
        <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
    </div>
    <br>
                    <div class="form-group row m-2">
                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">neural network: </label>
                            <div class="col-sm-8">
                            <select class="form-control" id="actions" name="TMC_actions">
                                    <option value="PREPROCESSING" selected> Preprocessing (create zip from plain text) </option>
                                    <option value="DL"> LSTM </option>
                                    <option value="NB"> Naive Bayes </option>
                                    <option value="MLP"> Multi layer perceptron </option>
                                    <option value="SVC"> Support vector classification </option>

                            </select>
                            </div>
                    </div>

                    <div id="option_1">
                    
                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-2 col-form-label col-form-label-sm">Label: </label>
                                <div class="col-sm-10">
                                    <select class="form-control columns" id="labelColumn" data-actions-box="true" onclick=fillselect(this,mult=false) >
                                        <option class="editable" value="Custom">Custom</option>
                                        <option value="">None</option>

                                    </select>
                                    <input class="form-control columns editOption" style="display:none;"></input>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-2 col-form-label col-form-label-sm">Column with the plain text: </label>
                                <div class="col-sm-10">
                                    <select class="form-control columns" id="contentColumn" data-actions-box="true" onclick=fillselect(this,mult=false) >
                                        <option class="editable1" value="Custom">Custom</option>
                                        <option value="">None</option>

                                    </select>
                                    <input class="form-control columns editOption1" style="display:none;"></input>

                                </div>
                        </div>

                        <div class="form-group row m-2">
                            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Query to filter data: </label>
                            <div class="col-sm-8">
                                    <input id="objective" type="text" class="form-control">
                            </div>
                        </div>
                    </div>

                    <div id="option_2">

                        <div class="form-group row m-2">
                                <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Batch size: </label>
                                <div class="col-sm-8">
                                        <input id="batch_size" type="text" class="form-control form-control-sm">
                                </div>
                        </div>
                        <div class="form-group row m-2">
                                <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Epoch: </label>
                                <div class="col-sm-8">
                                        <input id="epoch" class="form-control form-control-sm" >
                                </div>
                        </div>
                    </div>
                    <div id="option_svc">
                        <div class="form-group row m-2">
                                <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">svc parameters: </label>
                                <div class="col-sm-8">
                                        <input id="svc_parameters" placeholder="{'gamma':'auto','verbose'=True}" class="form-control form-control-sm" >
                                </div>
                        </div>
                    </div>
                    <div id="option_mlp">
                        <div class="form-group row m-2">
                                <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">mlp neural network parameters: </label>
                                <div class="col-sm-8">
                                        <input id="mlp_parameters" placeholder="{'units':250,'input_dim':250, 'activation'='relu'},{'units':250,'kernel_initializer':'uniform', 'activation'='relu'},{'units':1,'activation':'sigmoid'}" type="text" class="form-control form-control-sm">
                                </div>
                        </div>
                    </div>
                    
                    <script>
                    function init_modal(){show_options_TMC()}

                    function show_options_TMC(){
                        opt = $("[name=TMC_actions]").val();
                        opt1 = $("#actions").val();
                        console.log(opt)
                        console.log(opt1)
                        $('#option_1').hide();
                        $('#option_2').hide();
                        $('#option_svc').hide();
                        $('#option_mlp').hide();
                        if (opt=="PREPROCESSING"){
                            $('#option_1').show();
                    
                        } else if (opt=="DL") {
                            $('#option_2').show();
                        } else if (opt=="MLP") {
                            $('#option_mlp').show();
                            $('#option_2').show();
                        } else if (opt=="SVC") {
                            $('#option_svc').show();
                        } 
                        else{
                            $('#option_1').hide();
                            $('#option_2').hide();
                        }
                    }
                
                    var initialText = $('.editable1').val();
                    $('.editOption1').val(initialText);
                    
                    $('#contentColumn').change(function(){
                        var selected = $('option:selected', this).attr('class');
                        var optionText = $('.editable1').text();
                        
                        if(selected == "editable1"){
                        $('.editOption1').show();
                        
                        
                        $('.editOption1').keyup(function(){
                            var editText = $('.editOption1').val();
                            $('.editable1').val(editText);
                            $('.editable1').html(editText);
                        });
                        
                        }else{
                        $('.editOption1').hide();
                        }
                    });

                    /////
                    var initialText = $('.editable').val();
                    $('.editOption').val(initialText);
                    
                    $('#labelColumn').change(function(){
                    var selected = $('option:selected', this).attr('class');
                    var optionText = $('.editable').text();

                    if(selected == "editable"){
                    $('.editOption').show();


                    $('.editOption').keyup(function(){
                        var editText = $('.editOption').val();
                        $('.editable').val(editText);
                        $('.editable').html(editText);
                    });

                    }else{
                    $('.editOption').hide();
                    }
                    });
                    $(document).ready(function(){
                        $("#actions").on('change', function() {
                                show_options_TMC()
                            });
                    }); 

                    </script>
    `
})

ServicesArr.push(
    {
        id: "s-txtProc",
        name: "text_processing",
        process_tag:"text-mining",
        valid_datatypes:{input:["ZIP"],output:["ZIP"]},
        section:SECTION,
        desc: `Clustering algorithms for plain text.`,
        columns:{
            default: null,
            parent: [] 
        },
        params: {
            SAVE_DATA: true,
            actions: "LDA",
            cluster_column_name: "cluster",
            clustered_dataframe_filename: "frame.csv",
            column_to_process: "synopsis",
            identifier_column: "",
            input_distance_filename: "dist.pkl",
            input_frame_filename: "default.csv",
            lang: "english",
            num_clusters: 5,
            num_exp: 1,
            linkage: "ward",
            num_words:20,
            sil_score:false,cal_score:false,cv_score:false,umass_score:false,cuci_score:false,cnpmi_score:false,
            score_file:"",variability:0.20,alpha:0.05,
            representation_filename: "tfidf_matrix.pkl"
        },
        html: `
        <div class="form-check" style="text-align: right;">
            <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
            <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>

                    <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm"> Processing: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="actions" name="PT_actions">
                                        <option value="K-MEANS" selected> K-means </option>
                                        <option value="HIERARCHY"> HIERARCHY </option>
                                        <option value="LDA"> LDA </option>
                                        <option value="REPRESENTATION"> Representation for k-means </option>
                                        <option value="VALIDATION"> Validation </option>
                                </select>
                                </div>
                    </div>

                    <div id="opt_lkh">
                        <div class="form-group row m-2">
                            <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Number of experimetns (for validatation): </label>
                            <div class="col-sm-8">
                                    <input id="num_exp" type="number" class="form-control form-control-sm"  min="1" max="1000" value=1>
                            </div>
                        </div>
                        <div class="form-group row m-2">
                            <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">number of clusters (topics for lda): </label>
                            <div class="col-sm-8">
                                    <input id="num_clusters" type="number" class="form-control form-control-sm"  min="0" max="50" value=5>
                            </div>
                        </div>

                    </div>

                    <div id="opt_l">
                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Languague: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="lang">
                                        <option value="english" selected> english </option>
                                        <option value="spanish"> spanish </option>
                                </select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Column name to process: </label>
                            <div class="col-sm-8">
                                    <input id="column_to_process" type="text" class="form-control">
                            </div>
                        </div>

                        <div class="form-group row m-2">
                            <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">number of words per topic: </label>
                            <div class="col-sm-8">
                                    <input id="num_words" type="number" class="form-control form-control-sm" min="20" value=20>
                            </div>
                        </div>

                        <hr>
                        <div class="form-group row m-2">
                        <h6 class="col-sm-12">Cluster validation indices calculation</h6>
                            <div class="form-check col-sm-3" style="text-align: left;">
                                <input type="checkbox" class="form-check-input" id="cv_score">
                                <label class="form-check-label" for="cv_score">Coherence cv</label>
                            </div>
                            <div class="form-check col-sm-4" style="text-align: left;">
                                <input type="checkbox" class="form-check-input" id="umass_score">
                                <label class="form-check-label" for="umass_score">Coherence umass</label>
                            </div>
                            <div class="form-check col-sm-3" style="text-align: left;">
                                <input type="checkbox" class="form-check-input" id="cuci_score">
                                <label class="form-check-label" for="cuci_score">Coherence cuci</label>
                            </div>
                            <div class="form-check col-sm-4" style="text-align: left;">
                                <input type="checkbox" class="form-check-input" id="cnpmi_score">
                                <label class="form-check-label" for="cnpmi_score">Coherence cnpmi</label>
                            </div>
                        </div>
                        <hr>
                    </div>

                    <div id="opt_k">
                        <div class="form-group row m-2">
                            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Representation filename: </label>
                            <div class="col-sm-8">
                                    <input id="representation_filename" type="text" class="form-control" value="tfidf_matrix.pkl">
                            </div>
                        </div>
                        </div>
                    </div>

                    <div id="opt_h">
                        <div class="form-group row m-2">
                            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm"> Linkage: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="linkage">
                                            <option value="complete" > Complete </option>
                                            <option value="average"> Average </option>
                                            <option value="ward" selected> Ward </option>
                                    </select>
                                    </div>
                        </div>
                    </div>
                    
                    <div id="opt_hr">
                        <div class="form-group row m-2">
                            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Distance filename: </label>
                            <div class="col-sm-8">
                                    <input id="input_distance_filename" type="text" class="form-control" value="dist.pkl">
                            </div>
                        </div>   
                        <div class="form-group row m-2">
                            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Identifier column: </label>
                            <div class="col-sm-8">
                                    <input id="identifier_column" type="text" class="form-control">
                            </div>
                        </div>
                    </div>
                    <div id="opt_kh">
                        <div class="form-group row m-2">
                            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Input filename: </label>
                            <div class="col-sm-8">
                                    <input id="input_frame_filename" type="text" class="form-control" value="default.csv">
                            </div>
                        </div>
                        <hr>
                        <div class="form-group row m-2">
                        <h6 class="col-sm-12">Cluster validation indices calculation</h6>
                            <div class="form-check col-sm-3" style="text-align: left;">
                                <input type="checkbox" class="form-check-input" id="sil_score">
                                <label class="form-check-label" for="sil_score">Silhouette</label>
                            </div>
                            <div class="form-check col-sm-4" style="text-align: left;">
                                <input type="checkbox" class="form-check-input" id="cal_score">
                                <label class="form-check-label" for="cal_score">Calinski-harabasz</label>
                            </div>
                        </div>
                        <hr>
                    </div>


                    <div id="opt_r">
                        <div class="form-group row m-2">
                            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Frame filename: </label>
                            <div class="col-sm-8">
                                    <input id="clustered_dataframe_filename" type="text" class="form-control" value="frame.csv">
                            </div>
                        </div>   
                        <div class="form-group row m-2">
                            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Cluster column: </label>
                            <div class="col-sm-8">
                                    <input id="cluster_column_name" type="text" class="form-control" value="cluster">
                            </div>
                        </div>
                    </div>

                    <div id="opt_v">
                        <div class="form-group row m-2">
                            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Filename with scores: </label>
                            <div class="col-sm-8">
                                    <input id="score_file" type="text" class="form-control" placeholder="e.g. cv.pkl, umass.pkl, calinski.pkl">
                            </div>
                        </div>   

                        <div class="form-group row m-2">
                            <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Acceptable variability: </label>
                            <div class="col-sm-8">
                                    <input id="variability" type="number" class="form-control form-control-sm" min="0" max="0.99" value="0.20" step=".01">
                            </div>
                        </div>

                        <div class="form-group row m-2">
                            <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Alpha: </label>
                            <div class="col-sm-8">
                                    <input id="alpha" type="number" class="form-control form-control-sm" min="0" max="0.99" value="0.05" step=".01" >
                            </div>
                        </div>
                    </div>

                        <script>
                            function init_modal(){show_options_PT()}
                            function show_options_PT(){
                                $('#opt_lkh').hide();
                                $('#opt_l').hide();
                                $('#opt_k').hide();
                                $('#opt_h').hide();
                                $('#opt_kh').hide();
                                $('#opt_hr').hide();
                                $('#opt_r').hide();
                                $('#opt_v').hide();

                                opt = $("[name=PT_actions]").val();
                                if (opt=="K-MEANS"){
                                    $('#opt_lkh').show();
                                    $('#opt_k').show();
                                    $('#opt_kh').show();
                                }
                                if (opt=="LDA"){
                                    $('#opt_lkh').show();
                                    $('#opt_l').show();
                                } 
                                if (opt=="HIERARCHY"){
                                    $('#opt_h').show();
                                    $('#opt_lkh').show();
                                    $('#opt_kh').show();
                                    $('#opt_hr').show();
                                }
                                if (opt=="REPRESENTATION"){
                                    $('#opt_hr').show();
                                    $('#opt_r').show();
                                } 
                                if (opt=="VALIDATION"){
                                    $('#opt_v').show();
                                } 
                            }
                            $(document).ready(function(){
                                
                                $("#actions").on('change', function() {
                                    show_options_PT()
                                    });
                            }); 

                        </script>
        `
    })

ServicesArr.push(
    {
        id: "s-txtPreproc",
        name: "text_preprocessing",
        process_tag:"doc-mining",
        valid_datatypes:{input:["ZIP"],output:["ZIP"]},
        section:SECTION,
        desc: `Preprocessing tools for plain text.`,
        columns:{
            default: null,
            parent: [] 
        },
        params: {
            SAVE_DATA: false,
            actions: "TF-IDF",
            column_to_process: "synopsis",
            idf: true,
            lang: "english",
            max_df: 0.8,
            max_features: 200000,
            max_window_size: 3,
            min_df: 0.2,
            min_window_size: 1
        },
        html: `
        <div class="form-check" style="text-align: right;">
            <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
            <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>

        <div class="form-check" style="text-align: right;">
        <input style="visibility:hidden" type="checkbox" checked class="form-check-input" id="idf">
         </div>

                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm"> Type of preprocessing: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="actions" name="PDM_actions">
                                        <option value="TF-IDF" selected> TF-IDF </option>
                                        <option value="STEMMING"> Stemming </option>
                                </select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Languague: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="lang">
                                        <option value="english" selected> english </option>
                                        <option value="spanish"> spanish </option>
                                </select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">column to process: </label>
                                <div class="col-sm-8">
                                    <select class="form-control columns" id="column_to_process" data-actions-box="true" onclick=fillselect(this,mult=false) >
                                        <option class="editable" value="Custom">Custom</option>
                                        <option value="" selected >None</option>

                                    </select>
                                    <input class="form-control columns editOption" style="display:none;"></input>
                                </div>
                        </div>
                    <div id="option1">
                        <div class="form-group row m-2">
                        <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Max differential: </label>
                        <div class="col-sm-8">
                                <input id="max_df" type="number" class="form-control form-control-sm"  min="0" max="1" value=.8>
                        </div>
                        </div>

                        <div class="form-group row m-2">
                        <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Min differential: </label>
                        <div class="col-sm-8">
                                <input id="min_df" type="number" class="form-control form-control-sm"  min="0" max="1" value=.2>
                        </div>
                        </div>

                        <div class="form-group row m-2">
                        <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Max features: </label>
                        <div class="col-sm-8">
                                <input id="max_features" type="number" class="form-control form-control-sm"  min="10" value=200000>
                        </div>
                        </div>

                        <div class="form-group row m-2">
                        <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Max window size: </label>
                        <div class="col-sm-8">
                                <input id="max_window_size" type="number" class="form-control form-control-sm"  min="0" max="100" value=3>
                        </div>
                        </div>

                        <div class="form-group row m-2">
                        <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">Min window size: </label>
                        <div class="col-sm-8">
                                <input id="min_window_size" type="number" class="form-control form-control-sm"  min="0" max="100" value=1>
                        </div>
                        </div>



                    </div>
                    


                        <script>
                            var initialText = $('.editable').val();
                            $('.editOption').val(initialText);
                            
                            $('#column_to_process').change(function(){
                            var selected = $('option:selected', this).attr('class');
                            var optionText = $('.editable').text();

                            if(selected == "editable"){
                            $('.editOption').show();


                            $('.editOption').keyup(function(){
                                var editText = $('.editOption').val();
                                $('.editable').val(editText);
                                $('.editable').html(editText);
                            });

                            }else{
                            $('.editOption').hide();
                            }
                            });

                            function init_modal(){show_options_PDM()}
                            //////
                            function show_options_PDM(){
                                opt = $("[name=PDM_actions]").val();
                                if (opt=="TF-IDF"){
                                    $('#option1').show();
                                } else{
                                    $('#option1').hide();
                                }
                            }
                            $(document).ready(function(){
                                $("#actions").on('change', function() {
                                        show_options_PDM()
                                    });
                            }); 

                        </script>`})