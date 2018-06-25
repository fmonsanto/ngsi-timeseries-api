from flask import request
from translators.crate import CrateTranslatorInstance, CrateTranslator
import logging 


def serialize(entities, aggr_method, entity_id, type_, attr_name, timeproperty):
    if aggr_method:
        index = []
    else:
        index = [str(e[CrateTranslator.TIME_INDEX_NAME]) for e in entities]
    res = {
        'id': entity_id,
        'type': type_,
        attr_name: [],
    }
    
    time_index_name = timeproperty if timeproperty else CrateTranslator.TIME_INDEX_NAME

    for e in entities:
        entry = {
            time_index_name: str(e[time_index_name]),
            'value': e[attr_name]['value'],
            'type': e[attr_name]['type']
        }
        res[attr_name].append(entry)
    return res


def query_1T1E1A(attr_name,   # In Path
                 entity_id,
                 type_=None,  # In Query
                 aggr_method=None,
                 aggr_period=None,
                 options=None,
                 from_date=None,
                 to_date=None,
                 timerel=None,
                 timeproperty=None,
                 lastn=None,
                 limit=10000,
                 offset=0):
    """
    See /entities/{entityId}/attrs/{attrName} in API Specification
    quantumleap.yml
    """
    if type_ is None:
        r = {
            "error": "Not Implemented",
            "description": "For now, you must always specify entity type."
        }
        return r, 400

    if options or aggr_period:
        import warnings
        warnings.warn("Unimplemented query parameters: options, aggrPeriod")

    fiware_s = request.headers.get('fiware-service', None)
    fiware_sp = request.headers.get('fiware-servicepath', None)

    entities = None
    with CrateTranslatorInstance() as trans:
        entities = trans.query(attr_names=[attr_name],
                           entity_type=type_,
                           entity_id=entity_id,
                           aggr_method=aggr_method,
                           from_date=from_date,
                           to_date=to_date,
                           lastn=lastn,
                           timerel=timerel,
                           timeproperty=timeproperty,
                           limit=limit,
                           offset=offset,
                           fiware_service=fiware_s,
                           fiware_servicepath=fiware_sp,)
    if entities:
        return serialize(entities, aggr_method, entity_id, type_, attr_name, timeproperty)

    r = {
        "error": "Not Found",
        "description": "No records were found for such query."
    }
    return r, 404


def query_1T1E1A_value(*args, **kwargs):
    res = query_1T1E1A(*args, **kwargs)
    if isinstance(res, dict) and 'data' in res:
        res['data'].pop('entityId')
        res['data'].pop('attrName')
    return res
