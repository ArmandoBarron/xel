

Construir=true
URL_REPOSITORIO="qwerty3435ab"

#====================================#
# TAGS de las imagenes configurables #
#====================================#

#=====alias de modulos de xel=======#
tag_coordinator="xel_coordinator:v2.0"
tag_paxos="xel_paxos:v2.0"
tag_yaml_creator="xel_yaml_creator:v2.0"

#=====alias de servicios de xel======#
tag_filtercolumn="xel_bb_filtercolumn:v2.0"
tag_fusion="xel_bb_fusion:v2.0"
tag_correlations="xel_bb_correlations:v2.0"
tag_data_split="xel_bb_data_split:v2.0" 
tag_data_clean="xel_bb_data_clean:v2.0"
tag_imputation="xel_bb_imputation:v2.0"
tag_charts="xel_bb_charts:v2.0"
tag_maps="xel_bb_maps:v2.0" 
tag_catalog="xel_bb_catalog:v2.0" 
tag_regressions="xel_bb_regressions:v2.0" 
tag_statistics="xel_bb_statistics:v2.0"
tag_transform="xel_bb_transform:v2.0" 
tag_clustering="xel_bb_clustering:v2.0" 
tag_deeplearning="xel_bb_deeplearning:v2.0" 
tag_text_preprocessing="xel_bb_text_preprocessing:v2.0" 
tag_text_processing="xel_bb_text_processing:v2.0"
tag_text_classification="xel_bb_text_classification:v2.0"
tag_preprocessing="xel_bb_preprocessing:v2.0"
tag_converters="xel_bb_converters:v2.0"
tag_acquisition="xel_bb_acquisition:v2.0"
tag_grobid="xel_bb_grobid:v2.0"
tag_glove="xel_bb_glove:v2.0"
tag_classification_models="xel_bb_classification_models:v2.0"
tag_advanced_map="xel_bb_advanced_map:v2.0"

#=================================================================#
# Se construyen las imagenes de contenedor de modulos y servicios #
#=================================================================#
if $Construir; then
    echo "dscargando imagenes"
    # construir imagenes de modulos de xelhua
    docker pull ${URL_REPOSITORIO}/${tag_coordinator}
    docker pull ${URL_REPOSITORIO}/${tag_paxos}
    docker pull ${URL_REPOSITORIO}/${tag_yaml_creator}

    #construir imagenes de servicios de xelhua (BB)
    docker pull ${URL_REPOSITORIO}/${tag_filtercolumn}
    docker pull ${URL_REPOSITORIO}/${tag_fusion}
    docker pull ${URL_REPOSITORIO}/${tag_correlations}
    docker pull ${URL_REPOSITORIO}/${tag_data_split}
    docker pull ${URL_REPOSITORIO}/${tag_data_clean}
    docker pull ${URL_REPOSITORIO}/${tag_imputation}
    docker pull ${URL_REPOSITORIO}/${tag_charts}
    docker pull ${URL_REPOSITORIO}/${tag_maps}
    docker pull ${URL_REPOSITORIO}/${tag_catalog}
    docker pull ${URL_REPOSITORIO}/${tag_regressions}
    docker pull ${URL_REPOSITORIO}/${tag_statistics}
    docker pull ${URL_REPOSITORIO}/${tag_transform}
    docker pull ${URL_REPOSITORIO}/${tag_clustering}
    docker pull ${URL_REPOSITORIO}/${tag_deeplearning}
    docker pull ${URL_REPOSITORIO}/${tag_text_preprocessing}
    docker pull ${URL_REPOSITORIO}/${tag_text_processing}
    docker pull ${URL_REPOSITORIO}/${tag_text_classification}
    docker pull ${URL_REPOSITORIO}/${tag_preprocessing}
    docker pull ${URL_REPOSITORIO}/${tag_converters}
    docker pull ${URL_REPOSITORIO}/${tag_acquisition}
    docker pull ${URL_REPOSITORIO}/${tag_grobid}
    docker pull ${URL_REPOSITORIO}/${tag_glove}
    docker pull ${URL_REPOSITORIO}/${tag_classification_models}
    docker pull ${URL_REPOSITORIO}/${tag_advanced_map}
fi
