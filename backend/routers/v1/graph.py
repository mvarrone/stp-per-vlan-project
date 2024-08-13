import time

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

from graph import code

router = APIRouter(tags=["Graph"])


@router.get(path="/stp-graph", deprecated=True)
async def graph_endpoint() -> Dict[str, Any]:
    """
    Endpoint previously used to compute only one tree for Spanning Tree Protocol (STP).
    This tree is normally known as Common Spanning Tree (CST).
    Data was taken from the native VLAN 1.
    Now, this endpoint has been replaced by new one: /stp-graph-per-vlan which allows to represent data
    for multiple VLANs, including VLAN 1.
    """

    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Deprecated endpoint. Please, refer to /stp-graph-per-vlan",
    )

    # start_total: float = time.time()
    # data = code.main()
    # end_total: float = time.time() - start_total
    # end_total, unit = code.print_execution_time(end_total)
    # elapsed_time = {"value": end_total, "unit": unit}

    # if data.get("error"):
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail=data.get("error_description"),
    #     )

    # return {
    #     "nodes": data.get("nodes"),
    #     "edges": data.get("edges"),
    #     "edges_with_blocked_links": data.get("edges_with_blocked_links"),
    #     "blocked_interfaces": data.get("blocked_interfaces"),
    #     "results": data.get("results"),
    #     "elapsed_time": elapsed_time,
    # }


@router.get(path="/stp-graph-per-vlan")
async def graph_per_vlan_endpoint() -> Dict[str, Any]:
    """
    Endpoint computes data taken from multiple devices allowing to represent multiple VLANs in a canvas.
    It is used to implement Per VLAN Spanning Tree Protocol (PVST)
    """

    start_time = time.time()
    data_per_vlan = code.main()
    end_time = time.time() - start_time
    amount, unit = code.print_execution_time(end_time)
    elapsed_time = {"amount": amount, "unit": unit}
    error_found = data_per_vlan.get("error")
    error_descr = data_per_vlan.get("error_description")

    if error_found:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_descr,
        )

    data = {
        "data_per_vlan": data_per_vlan,
        "elapsed_time": elapsed_time,
    }

    return data
