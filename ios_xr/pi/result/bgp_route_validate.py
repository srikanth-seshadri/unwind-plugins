# The result plugin allows you to uncommon checks/very use-case specific
# checks that aren't exposed through unWind!'s flow comparison constructs.

# There are two callback functions to choose; you can choose either depending
# on your needs. The simple version would work for most.

# Returns True/False for Success/Failure and a result string on a per
# instance basis.
# result string follows the same convention as done() in case of
# success, rc() in case of a particular root cause that is equivalent
# to done since we've concluded. Anything else if considered a failure
# and the result string can contain anomalies concerning that failure.

# 'inst_tuples': contains the set of tuples derived from running the necessary
# collectors to compute your results. These tuples are for all the instance
# indices returned by the collectors. Each instance contains the set of
# key/value pairs from the collector. If you ran multiple collectors in this flow,
# they individual instances from them are merged based on the common instance
# index (eg. prefix or port#, slot#, etc.)
# The Flow section describes various options available on this aspect.
#
# The below callback gets invoked for each tuple instance separately.
#
# You also have access to in_params to access any input parameters for your
# comparisons.
#
# unWind offers the ability to convey result on a per instance basis on
# a give test case (workflow) for every iteration of the test case for a
# given set of parameters. The anomalies are at a per instance level.

import common
import pdb
def get_result_simple(inst_tuples, in_params):
    aggr_result = {}
    as_path = common.get_value_from_in_params(in_params, "as_path")
    peer_name = common.get_value_from_in_params(in_params, "peer_name")
    for index, tuples in inst_tuples.iteritems():
        # convention to access other node's tuples
        if as_path in tuples[peer_name+":"+"bgp-ipv4-path"]:
            result = True
            result_str = "done(BGP route received ok)"
        else:
            result = False
            result_str = "done(BGP route doesn't have East's AS Path)"
        aggr_result[index] = result, result_str

    return aggr_result
