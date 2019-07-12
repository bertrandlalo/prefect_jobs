# Note: this module cannot go in iguazu.flows due to circular dependency,
#       we roll a lazy dictionary or something like that

import iguazu.flows.datasets


factory_methods = {
    'datasets:local': iguazu.flows.datasets.local_dataset_flow,
    'datasets:merged': iguazu.flows.datasets.merged_dataset_flow,
    'datasets:quetzal': iguazu.flows.datasets.quetzal_dataset_flow,
    'datasets:debug': iguazu.flows.datasets.print_dataset_flow,
}
