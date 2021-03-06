"""mathematical algorithms for the particle pusher, Leapfrog and Boris"""
# coding=utf-8
import numpy as np

# import numba

# @numba.njit() # OPTIMIZE: add numba to this algorithm
def rotation_matrix(t: np.ndarray, s: np.ndarray, n: int) -> np.ndarray:
    """
    Implements the heavy lifting rotation matrix calculation of the Boris pusher
    Parameters
    ----------
    t (np.ndarray): vector
    s (np.ndarray): vector
    n (int): number of particles

    Returns
    -------
    result (np.ndarray): rotation matrix
    """
    result = np.zeros((n, 3, 3))
    result[:] = np.eye(3)

    sz = s[:, 2]
    sy = s[:, 1]
    tz = t[:, 2]
    ty = t[:, 1]
    sztz = sz * tz
    syty = sy * ty
    result[:, 0, 0] -= sztz
    result[:, 0, 0] -= syty
    result[:, 0, 1] = sz
    result[:, 1, 0] = -sz
    result[:, 0, 2] = -sy
    result[:, 2, 0] = sy
    result[:, 1, 1] -= sztz
    result[:, 2, 2] -= syty
    result[:, 2, 1] = sy * tz
    result[:, 1, 2] = sz * ty
    return result


# @numba.njit()
def rela_boris_push(x: np.ndarray, v: np.ndarray, E: np.ndarray, B: np.ndarray, q: float, m: float, dt: float,
                    c: float = 1):
    """
    relativistic Boris pusher
    """
    vminus = v + q * E / m * dt * 0.5  # eq. 21 LPIC
    n = x.size
    gamma_n = np.sqrt(1 + ((vminus / c) ** 2).sum(axis=1, keepdims=True))  # below eq 22 LPIC

    # rotate to add magnetic field
    t = B * q * dt / (2 * m * gamma_n)  # above eq 23 LPIC
    s = 2 * t / (1 + t * t)

    rot = rotation_matrix(t, s, n)

    vplus = np.einsum('ijk,ik->ij', rot, vminus)
    # import ipdb; ipdb.set_trace()

    v_new = vplus + q * E / m * dt * 0.5

    # TODO: check correctness of relativistic kinetic energy calculation
    energy = 0.5 * m * (v * v_new).sum(axis=0)
    gamma_new = np.sqrt(1 + ((vminus / c) ** 2).sum(axis=1))
    # import ipdb; ipdb.set_trace()

    x_new = x + v_new[:, 0] / gamma_new * dt
    return x_new, v_new, energy