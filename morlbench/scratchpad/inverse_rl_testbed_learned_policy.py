#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mar 02, 2016

@author: Johannes Feldmaier <johannes.feldmaier@tum.de>

    Copyright (C) 2016  Johannes Feldmaier

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

import logging as log
import numpy as np
import sys

import cPickle as pickle

#log.basicConfig(level=log.DEBUG)
log.basicConfig(level=log.INFO)


from morlbench.morl_problems import Deepsea
from morlbench.morl_agents import QMorlAgent, PreScalarizedQMorlAgent, SARSALambdaMorlAgent, SARSAMorlAgent
from morlbench.morl_policies import PolicyDeepseaRandom, PolicyDeepseaDeterministic, PolicyFromAgent, PolicyDeepseaExpert
from morlbench.inverse_morl import InverseMORLIRL
from morlbench.plot_heatmap import policy_plot, transition_map, heatmap_matplot, policy_plot2, policy_heat_plot
from morlbench.dynamic_programming import MORLDynamicProgrammingPolicyEvaluation, MORLDynamicProgrammingInverse
from morlbench.experiment_helpers import morl_interact_multiple_episodic, morl_interact_multiple_average_episodic

import pickle
import time

import matplotlib.pyplot as plt


if __name__ == '__main__':
    problem = Deepsea()

    # scalarization_weights = np.array([0.153, 0.847])
    # scalarization_weights = np.array([0.4, 0.2])
    scalarization_weights = np.array([1.0, 0.0])
    # scalarization_weights = np.array([7.14710973e-11, 62.0])
    # scalarization_weights = np.array([0.0, 1.0])

    eps = 0.6
    alfa = 0.3
    runs = 1
    interactions = 50000

    agent = QMorlAgent(problem, scalarization_weights, alpha=alfa, epsilon=eps)
    # # agent = PreScalarizedQMorlAgent(problem, scalarization_weights, alpha=alfa, epsilon=eps)
    # # agent = SARSAMorlAgent(problem, scalarization_weights, alpha=alfa, epsilon=eps)
    # # agent = SARSALambdaMorlAgent(problem, scalarization_weights, alpha=alfa, epsilon=eps, lmbda=0.9)
    #
    # # payouts, moves, states = morl_interact_multiple_average_episodic(agent, problem, runs=runs, interactions=interactions, max_episode_length=150)
    payouts, moves, states = morl_interact_multiple_episodic(agent, problem, interactions=interactions, max_episode_length=150)

    learned_policy = PolicyFromAgent(problem, agent, mode='gibbs')
    # learned_policy = PolicyFromAgent(problem, agent, mode='greedy')

    # learned_policy = PolicyDeepseaDeterministic(problem, policy='P1')

    # filename = 'figure_' + time.strftime("%Y%m%d-%H%M%S")
    # pickle.dump((payouts, moves, states, problem, agent), open(filename, "wb"))

    # log.info('Average Payout: %s' % (str(payouts.mean(axis=0))))

    i_morl = InverseMORLIRL(problem, learned_policy)
    # scalarization_weights = i_morl.solvep()
    scalarization_weights_alge = i_morl.solvealge()

    # log.info("scalarization weights (with p): %s" % (str(scalarization_weights)))
    # log.info("scalarization weights (without p): %s" % (str(i_morl.solve())))
    # log.info("scalarization weights (without p, sum 1): %s" % (str(i_morl.solve_sum_1())))
    log.info("scalarization weights (alge): %s" % (str(scalarization_weights_alge)))

    problem2 = Deepsea()
    agent2 = QMorlAgent(problem, scalarization_weights_alge, alpha=alfa, epsilon=eps)
    payouts, moves, states = morl_interact_multiple_episodic(agent2, problem2, interactions=interactions, max_episode_length=150)
    log.info('Average Payout: %s' % (str(payouts.mean(axis=0))))
    # learned_policy2 = PolicyFromAgent(problem2, agent2, mode='gibbs')
    learned_policy2 = PolicyFromAgent(problem2, agent2, mode='greedy')


    plt.ion()
    policy_plot2(problem, learned_policy)
    plt.ioff()
    policy_plot2(problem2, learned_policy2)
