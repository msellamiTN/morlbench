#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Feb, 16 2016

@author: Dominik Meyer <meyerd@mytum.de>
@author: Johannes Feldmaier <johannes.feldmaier@tum.de>
@author: Simon Woelzmueller   <ga35voz@mytum.de>

    Copyright (C) 2016  Dominik Meyer, Johannes Feldmaier, Simon Woelzmueller

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
This module contains various helper functions with regard
to probability matrices and sampling.
"""

import numpy as np


def assureProbabilityMatrix(P):
    """
    Checks if the matrix P is a valid probability transition matrix.
    This means it has to contain transitions from state i to state j
    taking action a in the (i, a, j)-th entry.

    :param P: Probability transition matrix
    """
    if P.shape[0] != P.shape[2]:
        raise RuntimeError("Probability matrix check failed: Matrix is not square.")
    psum = P.sum(axis=-1).sum(axis=-1)
    if np.abs(psum - 1.0).any() > np.finfo(P.dtype).eps:
        raise RuntimeError("Probability matrix check failed: Probabilities don't add up to one.")


def assurePolicyMatrix(pi):
    """
    Checks if the matrix P is a valid policy distribution matrix.
    This means it has to contain the probability to choose action a
    under the condition, that the system is in state i in the
    element (a, i) (a-th row, i-th column).

    :param pi: Policy matrix
    """
    psum = pi.sum(axis=1)
    if np.abs(psum - 1.0).any() > np.finfo(pi.dtype).eps:
        raise RuntimeError("Policy matrix check failed: Rows don't add up to one.")


def sampleFromDiscreteDistribution(n, pi):
    """
    Sample n integers according to a discrete probability
    distribution given in the array pi.

    :param n: Number of integers to draw
    :param pi: Discrete distribution 1D array.
    :return: Array of integers.
    """
    if len(pi.shape) < 2:
        pi.shape = (1, pi.shape[0])
    p_accum = np.add.accumulate(pi, axis=1)
    n_v, n_c = p_accum.shape
    rnd = np.random.rand(n, n_v, 1)
    m = rnd < p_accum.reshape(1, n_v, n_c)

    m2 = np.zeros(m.shape, dtype='bool')
    m2[:, :, 1:] = m[:, :, :-1]
    m = np.logical_xor(m, m2)
    ind_mat = np.arange(n_c, dtype='uint8').reshape(1, 1, n_c)
    mask = np.multiply(ind_mat, m)
    s = np.add.reduce(mask, 2, dtype='uint8').squeeze()

    return s
