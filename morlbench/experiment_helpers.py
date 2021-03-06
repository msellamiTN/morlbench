#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Apr 23, 2015

@author: Dominik Meyer <meyerd@mytum.de>

    Copyright (C) 2016 Dominik Meyer

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

import numpy as np
import logging as log

import progressbar as pgbar

my_debug = log.getLogger().getEffectiveLevel() == log.DEBUG


def interact_multiple(agent, problem, interactions):
    """
    Interact multiple times with the problem and then
    return arrays of actions chosen and payouts received
    in each stage.
    """
    # storage
    log.info('This program comes with ABSOLUTELY NO WARRANTY This is free software, and you are welcome to '
             'redistribute it under certain conditions. See GPL')
    payouts = []
    actions = []
    log.info('Playing %i interactions ... ' % (interactions))
    # playing for %interaction times
    for t in xrange(interactions):
        # first decide witch action to take in current state
        action = agent.decide(t)
        # take that action
        payout = problem.play(action)
        # learn from taken action
        agent.learn(t, action, payout)
        if my_debug: log.debug(' step %05i: action: %i, payout: %f' %
                  (t, action, payout))
        # store the reward and action history
        payouts.append(payout)
        actions.append(action)
    # return numpy arrays
    payouts = np.array(payouts)
    actions = np.array(actions)
    return actions, payouts


def morl_interact_multiple_episodic(agent, problem, interactions, max_episode_length=150, discounted_eps=False):
    """
    Interact multiple times with the multi objective RL
    problem and then return arrays of actions chosen and
    payouts received in each stage.
    """
    log.info('This program comes with ABSOLUTELY NO WARRANTY This is free software, and you are welcome to '
             'redistribute it under certain conditions. See GPL')
    # storage for interactions
    final_rewards = []
    moves = []
    states = []

    log.info('Playing %i interactions ... ' % interactions)
    pbar = pgbar.ProgressBar(widgets=['Interactions ', pgbar.SimpleProgress('/'), ' (', pgbar.Percentage(), ') ',
                                      pgbar.Bar(), ' ', pgbar.ETA()], maxval=interactions)
    pbar.start()
    # play for %interactions times
    for i in xrange(interactions):
        # storage for episodes
        if discounted_eps:
            if agent._epsilon > 0.5:
                agent._epsilon *= 0.99
            else:
                agent._epsilon = 0.5
        rewards = []
        actions = []
        tmp_states = []
        problem.reset()
        # obtain current state
        state = problem.state
        # store current state as last state
        last_state = state
        # go as long as the problem isn't in a final state or the max number of episode steps is reached
        for t in xrange(max_episode_length):

            # decide which action to take next
            action = agent.decide(t, problem.state)
            # take that action and recieve reward
            reward = problem.play(action)

            if my_debug:
                log.debug('  step %04i: state before %i - action %i - payout %s - state %i' %
                          (t, problem.last_state, action, str(reward), problem.state))
            # learn from that action
            agent.learn(t, problem.last_state, action, reward, problem.state)

            # Preserve reward, action and state
            rewards.append(reward)
            actions.append(action)
            tmp_states.append(problem.last_state)

            # Decide if terminal state
            if problem.terminal_state or t == max_episode_length-1:
                problem.reset()
                moves.append(actions)
                states.append(tmp_states)
                final_rewards.append(np.mean(rewards, axis=0))
                break
        pbar.update(i)
    # newline to fix output of pgbar
    print ""
    return np.array(final_rewards), np.array(moves), np.array(states)


def morl_interact_multiple(agent, problem, interactions, max_steps):
    """
    Interact multiple times with the multi objective RL
    problem and then return arrays of actions chosen and
    payouts received in each stage.
    """
    log.info('This program comes with ABSOLUTELY NO WARRANTY This is free software, and you are welcome to '
             'redistribute it under certain conditions. See GPL')
    # storage for interactions
    average_rewards_per_run = []
    moves = []
    states = []

    log.info('Playing %i interactions ... ' % interactions)
    pbar = pgbar.ProgressBar(widgets=['Interactions ', pgbar.SimpleProgress('/'), ' (', pgbar.Percentage(), ') ',
                                      pgbar.Bar(), ' ', pgbar.ETA()], maxval=interactions)
    pbar.start()
    # play for %interactions times
    for i in xrange(interactions):
        # storage for interactions
        rewards = []
        actions = []
        tmp_states = []
        problem.reset()
        # obtain current state
        state = problem.state
        # store current state as last state
        last_state = state
        # go as long as the problem isn't in a final state or the max number of episode steps is reached
        for t in xrange(max_steps):
            # decide which action to take next
            action = agent.decide(t, problem.state)
            # take that action and recieve reward
            reward = problem.play(action)
            if my_debug:
                log.debug('  step %04i: state before %i - action %i - payout %s - state %i' %
                          (t, problem.last_state, action, str(reward), problem.state))
            # learn from that action
            agent.learn(t, problem.last_state, action, reward, problem.state)

            # Preserve reward, action and state
            rewards.append(reward)
            actions.append(action)
            tmp_states.append(problem.last_state)

        problem.reset()
        moves.append(actions)
        states.append(tmp_states)
        average_rewards_per_run.append(np.sum(rewards, axis=0))

        pbar.update(i)
    # newline to fix output of pgbar
    print ""
    return np.array(average_rewards_per_run), np.array(moves), np.array(states)


def morl_interact_multiple_average_episodic(agent, problem, runs=50, interactions=500, max_episode_length=150):
    """
    Perform multiple runs with of multiple interactions with the
    multi objective RL problem and then return arrays of actions chosen and
    payouts received in each stage.
    """
    log.info('This program comes with ABSOLUTELY NO WARRANTY This is free software, and you are welcome to '
             'redistribute it under certain conditions. See GPL')

    final_rewards = []
    moves = []
    states = []
    log.info('Playing %i runs with %i interactions each... ', runs, interactions)
    pbar = pgbar.ProgressBar(widgets=['Runs ', pgbar.SimpleProgress('/'), ' (', pgbar.Percentage(), ') ',
                                      pgbar.Bar(), ' ', pgbar.ETA()], maxval=runs)
    pbar.start()
    for r in xrange(runs):
        for i in xrange(interactions):
            rewards = []
            actions = []
            tmp_states = []
            problem.reset()
            state = problem.state
            last_state = state
            for t in xrange(max_episode_length):
                action = agent.decide(t, problem.state)
                reward = problem.play(action)
                state = problem.state
                if my_debug:
                    log.debug('  step %04i: state before %i - action %i - payout %s - state %i' %
                              (t, problem.last_state, action, str(reward), problem.state))
                agent.learn(t, problem.last_state, action, reward, problem.state)

                # Preserve reward, action and state
                rewards.append(reward)
                actions.append(action)
                tmp_states.append(problem.last_state)
                last_state = state
                # Decide if terminal state
                if problem.terminal_state:
                    problem.reset()
                    moves.append(actions)
                    states.append(tmp_states)
                    try:
                        final_rewards.append(rewards[-2])
                    except IndexError:
                        final_rewards.append(rewards[-1])

                    break

        agent.save()
        agent.reset()
        pbar.update(r)

    agent.restore()
    # newline to fix output of pgbar
    print ""
    return np.array(final_rewards), np.array(moves), np.array(states)


def interact_multiple_twoplayer(agent1, agent2, problem, interactions,
                                use_sum_of_payouts=False):
    """
    Interact multiple times with the problem and then
    return arrays of actions chosen and payouts received
    in each stage.
    """
    log.info('This program comes with ABSOLUTELY NO WARRANTY This is free software, and you are welcome to '
             'redistribute it under certain conditions. See GPL')
    # TODO: Make this more flexible instead of tedious code duplication.
    payouts1 = []
    actions1 = []
    payouts2 = []
    actions2 = []
    log.info('Playing %i interactions ... ' % (interactions))
    for t in xrange(interactions):
        action1 = agent1.decide(t)
        action2 = agent2.decide(t)
        payout1, payout2 = problem.play(action1, action2)
        if use_sum_of_payouts:
            payoutsum = payout1 + payout2
            agent1.learn(t, action1, payoutsum)
            agent2.learn(t, action2, payoutsum)
        else:
            agent1.learn(t, action1, payout1)
            agent2.learn(t, action2, payout2)
        if my_debug: log.debug(' step %05i: action1: %i, payout1: %i, action2: %i, payout2: \
%i' % (t, action1, payout1, action2, payout2))
        payouts1.append(payout1)
        actions1.append(action1)
        payouts2.append(payout2)
        actions2.append(action2)
    payouts1 = np.array(payouts1)
    actions1 = np.array(actions1)
    payouts2 = np.array(payouts2)
    actions2 = np.array(actions2)
    return (actions1, payouts1), (actions2, payouts2)



