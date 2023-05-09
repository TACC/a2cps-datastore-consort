# Data Loading
import json
import pandas as pd
import os
import io
import numpy as np
import datetime

# Data reqeuests
import requests


# ----------------------------------------------------------------------------
# Format data for Sankey
# ----------------------------------------------------------------------------

def get_sankey_nodes(dataframe,source_col = 'source', target_col = 'target'):
    ''' Extract node infomration from sankey dataframe in case this is not provided '''
    nodes = pd.DataFrame(list(dataframe[source_col].unique()) + list(dataframe[target_col].unique())).drop_duplicates().reset_index(drop=True)
    nodes.reset_index(inplace=True)
    nodes.columns = ['NodeID','Node']
    return nodes

def get_sankey_dataframe (data_dataframe,
                          node_id_col = 'NodeID', node_name_col = 'Node',
                          source_col = 'source', target_col = 'target', value_col = 'value'):
    ''' Merge Node dataframes with data dataframe to create dataframe properly formatted for Sankey diagram.
        This means each source and target gets assigned the Index value from the nodes dataframe for the diagram.
    '''
    # get nodes from data
    nodes = get_sankey_nodes(data_dataframe)

    # Copy of Node data to merge on source
    sources = nodes.copy()
    sources.columns = ['sourceID','source']

    # Copy of Node data to merge on target
    targets = nodes.copy()
    targets.columns = ['targetID','target']

    # Merge the data dataframe with node information
    sankey_dataframe = data_dataframe.merge(sources, on='source')
    sankey_dataframe = sankey_dataframe.merge(targets, on='target')

    return nodes, sankey_dataframe
