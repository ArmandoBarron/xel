

Construir=true

#====================================#
# TAGS de las imagenes configurables #
#====================================#

#=====alias de modulos de xel=======#
tag_coordinator="xel_coordinator:v2.0"
tag_paxos="xel_paxos:v2.0"
tag_yaml_creator="xel_yaml_creator:v2.0"
tag_gui="xel_gui:v2.0"

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
    echo "construyendo imagenes"
    # construir imagenes de modulos de xelhua
    docker build -t ${tag_gui} ./Frontend
    docker build -t ${tag_coordinator} AG
    docker build -t ${tag_paxos} ./NonFunctional/Paxos
    docker build -t ${tag_yaml_creator} ./NonFunctional/Services_Creator

    #construir imagenes de servicios de xelhua (BB)
    docker build -t ${tag_filtercolumn} ./BuildingBlocks/FilterColumn #Filtrar columnas
    docker build -t ${tag_fusion} ./BuildingBlocks/Fusion #Fusion
    docker build -t ${tag_correlations} ./BuildingBlocks/Correlations
    docker build -t ${tag_data_split} ./BuildingBlocks/DataSplit
    docker build -t ${tag_data_clean} ./BuildingBlocks/DataClean
    docker build -t ${tag_imputation} ./BuildingBlocks/Imputation
    docker build -t ${tag_charts} ./BuildingBlocks/graphics
    docker build -t ${tag_maps} ./BuildingBlocks/maps
    docker build -t ${tag_catalog} ./BuildingBlocks/Catalogs
    docker build -t ${tag_regressions} ./BuildingBlocks/Regressions
    docker build -t ${tag_statistics} ./BuildingBlocks/statistics
    docker build -t ${tag_transform} ./BuildingBlocks/TransformStrData
    docker build -t ${tag_clustering} ./BuildingBlocks/ClusteringAlgh
    #docker build -t ${tag_deeplearning} ./BuildingBlocks/DeepLearning
    #docker build -t ${tag_text_preprocessing} ./BuildingBlocks/TextPreprocessing
    #docker build -t ${tag_text_processing} ./BuildingBlocks/TextProcessing
    #docker build -t ${tag_text_classification} ./BuildingBlocks/TextClassification
    #docker build -t ${tag_preprocessing} ./BuildingBlocks/Preprocessing
    #docker build -t ${tag_converters} ./BuildingBlocks/Converters
    docker build -t ${tag_acquisition} ./BuildingBlocks/Acq
    docker build -t ${tag_grobid} ./BuildingBlocks/Grobid
    docker build -t ${tag_glove} ./BuildingBlocks/Glove
    # nuevas
    docker build -t ${tag_classification_models} ./BuildingBlocks/Clasificate #modelos de clasificacion
    docker build -t ${tag_advanced_map} ./BuildingBlocks/AdvancedMaps
fi
