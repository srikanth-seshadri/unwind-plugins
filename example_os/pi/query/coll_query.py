#import common

# There are two methods either of which needs to be provided through which
# you the dependencies to run the collector can be supplied. Note that
# for many common cases, query plugin isn't required.

# Returns a dictionary (dependent parameters) with a set of instances;
# each instance containing the keys and the corresponding values (tuples)
# needed to run the collector.  The number of instances indicates number of
# times the collector needs to be run with the corresponding parameters
# inside the instance tuples.
# Notes:
# - The returned keys need to be fully qualified: i.e. in compname-key format
# - The instance index of dependent parameters is based on the dependent
#   collectors. They could have a parent-child relationship or a sibling
#   relationship. Either way, the instance index has to match that of
#   one/more of the dependent collector(s) for unWind! Bot to associate and
#   merge the tuples correctly for result comparison.

# get_dep_params()
# This function gives the flexibility to go through multiple runs of dependent
# collectors and form the dependent parameters required to run this collector.
# This is only if you require the historical access to collector runs. In
# most cases, the 'simple' version of this function would suffice.
# Note: This also has flow_run_dict supplied with the simple version.
#
# format of aggr_tuples:
# tuples[node][flow_name][flow_run_str][comp_name][coll_name] is a dictionary
# containing instanced tuples.
# node: the node on which the flow is being run now
# flow_name: name of the flow
# flow_run_str: instance of this flow run
# in_params: input parameters provided for this flow
#
# flow_run_dict[comp_name][coll_name]: This is a dictionary organized by the
# component names and collector names under that component. This contains the
# tuples for all the dependent components as evaluated by unWind! Bot.
# This is provided as an additional reference.
def get_dep_params(node, flow_name, flow_run_str, aggr_tuples, flow_run_dict,
        in_params):
    dep_params = {} # contains the list of dependent parameters

    # In this example, there are two collectors supplying dependent parameters
    # for this collector to run. This collector and dep_coll2 has got a
    # sibling relationship. Therefore the instance key for dep_params is
    # the same as dep_coll2's.

    # This collector needs the ifh (comes from collector 2) and parent's port
    # speed (comes from collector 1) for those ports that match the status
    # specified in in_params.

    # In this example, the dependent collectors don't have a common instance
    # index key also. Coll1 uses port (eg 0/0/0), while Coll2 uses interface
    # (eg. Ge0/0/0.1). There is a partial match and we use the 'in' operator
    # to do a join.
    dep_comp = "query_comp"
    dep_coll1 = "ports"
    dep_coll2 = "interfaces"

    # This will contain the tuples we need.
    my_flow_run_dict = {}
    my_flow_run_dict[dep_comp] = {}
    my_flow_run_dict[dep_comp][dep_coll1] = {}
    my_flow_run_dict[dep_comp][dep_coll2] = {}

    # Check if the current flow already run the required collectors.
    # you could write a loop of the number of components/collectors are more.
    if aggr_tuples[node][flow_name][flow_run_str].get(dep_comp, None):
        if aggr_tuples[node][flow_name][flow_run_str][dep_comp].get(dep_coll1, None):
            # found collector1 in the current flow
            my_flow_run_dict[dep_comp][dep_coll1] = \
                aggr_tuples[node][flow_name][flow_run_str][dep_comp][dep_coll1]
            if aggr_tuples[node][flow_name][flow_run_str][dep_comp].get(dep_coll2, None):
                # found collector2 in the current flow
                my_flow_run_dict[dep_comp][dep_coll2] = \
                aggr_tuples[node][flow_name][flow_run_str][dep_comp][dep_coll2]

    # If the current flow doesn't contain the tuples for all the dependent
    # collectors, if the current flow is a flow list, check other entries.
    for flow_name, details in aggr_tuples[node].iteritems():
        # if we have the required collectors, then exit the loop
        if my_flow_run_dict[dep_comp][dep_coll1] and \
            my_flow_run_dict[dep_comp][dep_coll2]:
                break

        # get the tuples for the component/collector of interest
        if details[flow_run_str].get(dep_comp, None):
            if not my_flow_run_dict[dep_comp][dep_coll1]:
                # Check if this flow has run dep_coll1 if we haven't gleaned
                # it from the current flow.
                if details[flow_run_str][dep_comp].get(dep_coll1, None):
                    my_flow_run_dict[dep_comp][dep_coll1] = \
                        details[flow_run_str][dep_comp][dep_coll1]
                # Same check for dep_coll2
                if details[flow_run_str][dep_comp].get(dep_coll2, None):
                    my_flow_run_dict[dep_comp][dep_coll2] = \
                        details[flow_run_str][dep_comp][dep_coll2]

    # If we still havent found the collectors, there could be more advanced
    # searches you could do. As an example look at other flow_runs, typically
    # the first one that is useful in some use cases like white box testing.
    # In those cases, you can run the above loop with different values of
    # 'flow_run_str'
    #
    # You could do more complicated resolution using in_params as well.
    # We aren't illustrating that in the picture, but is is very easy as
    # you know the structure you supply to in_params.

    # API used to get the value from in_params.
    #port_status = common.get_value_from_in_params(in_params, "port_status")
    port_status = "up"

    # business logic. This implements the use case described above.
    # Every instance of 'dep_params' is a dictionary that contains the
    # dependent tuples required to run this collector.
    coll1_tuples = my_flow_run_dict[dep_comp][dep_coll1]
    coll2_tuples = my_flow_run_dict[dep_comp][dep_coll2]
    for port, port_details in coll1_tuples.iteritems():
        for intf, intf_details in coll2_tuples.iteritems():
            if port in intf and port_details["query_comp-status"] == port_status:
                # The instance index for dep_params is choosen from our
                # sibling collector dep_coll2.
                inst = intf
                if dep_params.get(inst, None) is None:
                    dep_params[inst] = {}
                    dep_params[inst]["query_comp-speed"] = \
                        port_details["query_comp-speed"]
                    dep_params[inst]["query_comp-ifh"] = \
                        intf_details["query_comp-ifh"]

    return dep_params

# get_dep_params_simple()
# flow_run_dict[comp_name][coll_name]: This is a dictionary organized by the
# component names and collector names under that component. This contains the
# tuples for all the dependent components as evaluated by unWind! Bot.
def get_dep_params_simple(flow_run_dict, in_params):
    dep_params = {} # contains the list of dependent parameters

    # Note: check the function get_dep_params() above for a description of
    # the business logic for querying and creating the dependent params
    # dictionary.
    dep_comp = "query_comp"
    dep_coll1 = "ports"
    dep_coll2 = "interfaces"

    # flow_run_dict contains the tuples we need to run the business logic.
    coll1_tuples = flow_run_dict[dep_comp][dep_coll1]
    coll2_tuples = flow_run_dict[dep_comp][dep_coll2]

    # API used to get the value from in_params.
    port_status = common.get_value_from_in_params(in_params, "port_status")

    # business logic. This implements the use case described above.
    # Every instance of 'dep_params' is a dictionary that contains the
    # dependent tuples required to run this collector.
    for port, port_details in coll1_tuples.iteritems():
        for intf, intf_details in coll2_tuples.iteritems():
            if port in intf and port_details["query_comp-status"] == port_status:
                # The instance index for dep_params is choosen from our
                # sibling collector dep_coll2.
                inst = intf
                if dep_params.get(inst, None) is None:
                    dep_params[inst] = {}
                    dep_params[inst]["query_comp-speed"] = \
                        port_details["query_comp-speed"]
                    dep_params[inst]["query_comp-ifh"] = \
                        intf_details["query_comp-ifh"]

    return dep_params

