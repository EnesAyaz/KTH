"""Common-mode inductance bookkeeping for symmetric parallel commutation loops."""
import math


def equivalent_loop_nh(shared_nh, branch_nh, coupling_k, count):
    if type(count) is not int or count < 1:
        raise ValueError('Count must be a positive integer')
    if not all(math.isfinite(v) for v in [shared_nh,branch_nh,coupling_k]):
        raise ValueError('Parameters must be finite')
    if shared_nh < 0 or branch_nh <= 0 or not 0 <= coupling_k <= 1:
        raise ValueError('Require shared>=0, branch>0 and 0<=k<=1')
    return shared_nh + branch_nh*(1+(count-1)*coupling_k)/count
