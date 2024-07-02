#
# Copyright (C) 2012 Sreeram Reddy Vanga <reddyvanga@gmail.com>
#
# Author(s): Rohitash Kumar <rohitash@innopark.in>
#            Sunil Mohan <sunil@innopark.in>
#

"""
Bingo Reporting Tool
"""

import re
import time
import gevent
import traceback
from zeus import config as config_module
from zeus import database as database_module
from zeus.reports import amount_to_money
from bingo import wrapper as wpr
import bingo.whack_a_bingo as wab
from zeus import mysql_database
from bingo.config import VARIABLE_TYPE, FIXED_TYPE, _DEFAULT_FREESPINS
import json
from zeus import log
from zeus.logger_mixin import LoggerMixin
from collections import OrderedDict
from datetime import datetime
import zeus.mysql_database as database
import bingo.whack_a_bingo as wab
from zeus.json_custom import JSONEncoder
LOGGER = log.Log(__name__)

_STATUS = 1
BUY_TYPE_MAPPING = {'quick': 4,
                    'get_tickets': 5,
                    'select_and_buy': 6,
                    'pre': 7,
                    'prebuy': 7,
                    'free_game': 8,
                    'instant_prebuy': 9,
                    'package_tickets': 10,
                    'next_game': 11}


class MysqlLogsMonitorHandler(LoggerMixin):
    """Bingo reports"""

    _instance = None
    _divisor = 1000000
    # time from cassandra is divided by this _divisor because the _event time
    # generated while inserted is the multiple of time * _divisor
    # If 10 requests are written  in a second  multiplying by lakh
    # will consider the nano seconds too.

    def __init__(self, *args, **kwargs):
        """Initialize module"""
        super(MysqlLogsMonitorHandler, self).__init__()
        self.application = 'bingo'
        self.summary = {}
        self.player_info = {}
        self.feature_winnings = {}
        self.initial_summary = []
        self.summary_time = {}
        self.configuration = config_module.get(self.application)['reports']
        self.queue = []
        self.player_queue = []
        self.mysql_batch_sender_thread = gevent.spawn(
            self._send_batch_continuously)
        self.mysql_player_batch_sender_thread = gevent.spawn(
            self._send_player_batch_continuously)
        self.failed_query_queue = []
        self.player_failed_query_queue = []
        self.final_failed_queue = []
        self.final_player_failed_queue = []
        self.batch_sleep_interval = 5
        self.player_summary_query = None
        self.whack_a_bingo_details = None

    def handle(self, details, game_details):
        """Store event in database"""
        if "logging" in details.keys():
            if not details["logging"]:
                return

        stream_id = game_details.stream_id
        round_id = game_details.round_id
        game_id = game_details.game_id
        column = time.time() * 1000000
        Required_class = []
        Required_class = [
            'winners',
            'round_summary',
            'round_summary_player_info_chunk',
            'round_summary_feature_winnings_chunk',
            'call_sequence']
        if details['class'] == 'round_id':
            self.initial_summary = []
            self.summary_time = {}
            self.summary_time[details['class']
                              ] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.initial_summary.append(details)
        elif details['class'] == 'table_config':
            if 'table_config' not in self.summary_time.keys():
                self.summary_time[details['class']] = datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S')
                self.initial_summary.append(details)
        elif details['class'] == 'player_wager_info':
            context = details['data']['game_state']
            config = details['data']['config']
            account_id, ticket_info = \
                details['data']['player_id'], details['data']['ticket_data']
            self.export_player_wager_info(account_id, ticket_info, config)
        elif details['class'] == 'round_end':
            self.summary_time[details['class']
                              ] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.initial_summary.append(details)
            self.summary_gather(self.initial_summary, self.summary_time)
        elif details['class'] in Required_class:
            self.summary_time[details['class']
                              ] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.initial_summary.append(details)

        if details['class'] == 'shutdown':
            if not details['data'].get('config_event', False):
                self.send_batch()
                self.send_failed_batch()
                self.send_player_batch()
                self.send_player_failed_batch()

    def summary_gather(self, details, summary_time):
        LOGGER.info('Gathering summary from events')
        self.summary = {}
        events = []
        [events.append(x) for x in details if x not in events]
        self.summary = {'full_log': OrderedDict()}
        for event in events:
            try:
                summary_handler = getattr(self, event['class'], None)
                if event['class'] == 'round_id':
                    summary_handler(
                        event['data'], summary_time[event['class']])
                elif event['class'] == 'round_end':
                    summary_handler(
                        event['data'], summary_time[event['class']])
                    if 'winner_details' in self.summary.keys():
                        gevent.spawn(self.export_summary)
                else:
                    summary_handler(event, summary_time[event['class']])
            except Exception as exception:
                LOGGER.error(
                    'Error occurred handling message - %s, %s',
                    exception,
                    traceback.format_exc())
                raise

    def export_summary(self):
        LOGGER.info('Starting DB update')
        start_time = time.time()
        try:
            self.export_config()
            gevent.sleep(0.1)
            self.export_winners()
            gevent.sleep(0.1)
        except Exception as error:
            LOGGER.error("Error inserting game logs - %s \
                for round: %s", error, self.summary['round_id'])
        try:
            self.export_round_summary()
        except Exception as error:
            LOGGER.error("Error inserting consolidated details - %s \
                for round: %s", error, self.summary['round_id'])
        elapsed_time = time.time() - start_time
        self.info(
            'Total elapsed time in formulating DB queries to buffer is %s',
            elapsed_time)

##############
## Handlers ##
##############
    def round_id(self, event, _summary_time):
        """Set Round id"""
        self.summary['round_id'] = event['round_id']

    def round_end(self, event, _summary_time):
        self.summary['round_end_time'] = _summary_time

    def table_config(self, event, _summary_time):
        """Update configuration"""
        self.summary['config'] = event['data']
        self.summary['ticket_requests'] = []
        self.summary['debits'] = []
        self.summary['config']['start_time'] = _summary_time
        cash, bonus, _, _ = \
            amount_to_money(self.summary['config']['ticket_cost'])

        cash = max(cash, bonus)
        self.summary['config']['ticket_cost'] = cash

    def round_summary(self, event, _summary_time):
        """
        Log round summary:
            * game_config
            * winner details
            * player info
        """
        self.summary['round_log_time'] = _summary_time
        self.summary['game_config'] = event['data']['config']
        self.summary['winner_details'] = event['data']['winner_details']
        self.summary['players_info'] = json.loads(
            event['data']['players_info'])
        self.summary['feature_winnings'] = json.loads(
            event['data']['feature_winnings'])
        self.summary['slingo_winners'] = event['data']['slingo_winners']

    def round_summary_player_info_chunk(self, event, _summary_time):
        """
        Log round summary player_info, appending chunks:
            * player info
        """
        if 'players_info' not in self.summary:
            self.summary['players_info'] = {}
        self.summary['players_info'] = event['data']['players_info']

    def round_summary_feature_winnings_chunk(self, event, _summary_time):
        if 'feature_winnings' not in self.summary:
            self.summary['feature_winnings'] = {}
        self.summary['feature_winnings'] = event['data']['feature_winnings']

    def winners(self, event, _summary_time):
        """Store winners"""
        self.summary['round_end_time'] = _summary_time
        self.summary['winners'] = event['data']['winners']

    def call_sequence(self, event, _summary_time):
        """Store call sequence"""
        _call_sequence = ','.join(str(value)
                                  for value in event['data']['call_sequence'])
        _part_calls = ','.join(str(value)
                               for value in event['data']['part_calls'])
        self.summary['call_sequence'] = _call_sequence
        self.summary['part_calls'] = _part_calls


#############
## exports ##
#############

    def export_config(self):
        """Export configuration"""
        _config = self.summary['config']
        _game_config = json.loads(self.summary['game_config'])
        win_sequence = self.summary['call_sequence']
        if 'extra_balls_call_sequence' in _game_config:
            _extra_ball_win_sequence = ','.join(
                str(value) for value in _game_config['extra_balls_call_sequence'])
            win_sequence = ';'.join([win_sequence, _extra_ball_win_sequence])
        query_list = {}
        query_list['query'] = """
                INSERT INTO bingo_new_gamelog.result(
                    schedule_id,
                    game_id,
                    game_name,
                    win_sequence,
                    pattern_nums,
                    pattern_name,
                    pattern_id,
                    card_cost,
                    purchase_time,
                    call_delay,
                    max_cards,
                    end_time,
                    start_time,
                    game_type,
                    pjp,
                    stream_id)
                VALUES (%(schedule_id)s, %(game_id)s, %(game_name)s,
                        %(win_sequence)s, %(pattern_nums)s, %(pattern_name)s,
                        %(pattern_id)s, %(card_cost)s, %(purchase_time)s,
                        %(call_delay)s, %(max_cards)s, %(end_time)s, %(start_time)s,
                        %(game_type)s, %(pjp)s, %(stream_id)s)
                """
        query_list['arguments'] = {'schedule_id': self.summary['round_id'],
                                   'game_id': _config['game_id'],
                                   'game_name': _config['game_name'],
                                   'win_sequence': win_sequence,
                                   'pattern_nums': _config['pattern'],
                                   'pattern_name': _config['pattern_name'],
                                   'pattern_id': _game_config['pattern_id'],
                                   'card_cost': _config['ticket_cost'],
                                   'purchase_time': _config['ticket_buy_time'],
                                   'call_delay': _config['call_delay'],
                                   'max_cards': _config['maximum_tickets'],
                                   'end_time': self.summary['round_end_time'],
                                   'start_time': _config['start_time'],
                                   'game_type': _config['pot_type'],
                                   'pjp': _config['participates_in_pjp'],
                                   'stream_id': _config['stream_id']
                                   }
        self.queue.append(query_list)

    def export_round_summary(self):
        self.export_game_config()
        self.export_winner_details()
        self.export_players_info()

    def export_game_config(self):
        config = json.loads(self.summary['game_config'])
        call_sequence = ','.join(str(value)
                                 for value in config['call_sequence'])
        linked_with = ','.join(str(value)
                               for value in config['linked_with'])

        context = config['context'].copy()
        round_config = self.summary.get('config', {})
        bonus_details = round_config.get('bonus_details')
        bonus_parts = []
        if bonus_details:
            try:
                for part, value in bonus_details.items():
                    if value['coupon_type'] == 'Bingo bonus':
                        part_name = round_config["parts"][part]["part_name"]
                        bonus_parts.append(part_name)
                context['bonus_parts'] = bonus_parts
            except Exception as e:
                LOGGER.error('unable to log bonus patterns', e)
        context = json.dumps(context)

        query_list = {}
        query_list['query'] = """
                INSERT INTO bingo_new_gamelog.game_config(
                    round_id,
                    bingo_type,
                    stream_id,
                    stream_name,
                    game_id,
                    game_name,
                    game_type,
                    `current_time`,
                    end_time,
                    start_time,
                    game_status,
                    min_cards,
                    max_cards,
                    pattern_id,
                    pattern_name,
                    call_delay,
                    card_cost,
                    call_sequence,
                    free_game_cards,
                    free_ratio,
                    room_currency,
                    ticket_currency,
                    total_bonus_wagered,
                    total_cash_wagered,
                    wagered_amount,
                    win_amount,
                    linked_game,
                    linked_with,
                    client_invokes,
                    wagered_player_count,
                    context)
                VALUES (%(round_id)s, %(bingo_type)s, %(stream_id)s,
						%(stream_name)s, %(game_id)s, %(game_name)s,
						%(game_type)s, %(current_time)s, %(end_time)s,
						%(start_time)s, %(game_status)s, %(min_cards)s,
						%(max_cards)s, %(pattern_id)s, %(pattern_name)s,
						%(call_delay)s, %(card_cost)s, %(call_sequence)s,
						%(free_game_cards)s, %(free_ratio)s, %(room_currency)s,
						%(ticket_currency)s, %(total_bonus_wagered)s,
						%(total_cash_wagered)s, %(wagered_amount)s, %(win_amount)s,
						%(linked_game)s, %(linked_with)s, %(client_invokes)s,
						%(wagered_player_count)s, %(context)s)"""
        query_list['arguments'] = {
            'round_id': config['round_id'],
            'bingo_type': config['bingo_type'],
            'stream_id': config['stream_id'],
            'stream_name': config['stream_name'],
            'game_id': config['game_id'],
            'game_name': config['game_name'],
            'game_type': config['game_type'],
            'current_time': self.summary['round_log_time'],
            'end_time': config['end_time'],
            'start_time': config['start_time'],
            'game_status': config['game_status'],
            'min_cards': config['minimum_cards'],
            'max_cards': config['maximum_cards'],
            'pattern_id': config['pattern_id'],
            'pattern_name': config['pattern_name'],
            'call_delay': config['call_delay'],
            'card_cost': config['card_cost'],
            'call_sequence': call_sequence,
            'free_game_cards': config['free_game_cards'],
            'free_ratio': config['free_ratio'],
            'room_currency': config['room_currency'],
            'ticket_currency': config['ticket_currency'],
            'total_bonus_wagered': config['wagered_amount_bonus'],
            'total_cash_wagered': config['wagered_amount_cash'],
            'wagered_amount': json.dumps(
                config['wagered_amount']),
            'win_amount': json.dumps(
                config['win_amount']),
            'linked_game': config['linked_game'],
            'linked_with': str(
                config['linked_with']),
            'client_invokes': config['participants_count'],
            'wagered_player_count': config['wagered_player_count'],
            'context': context}
        self.queue.append(query_list)

    def export_bingo_royale_winner_details(self):
        for part_type, value in self.summary['winners'].iteritems():
            for data in value:
                winner_tickets = ','.join(str(value)
                                          for value in data['tickets'])
                part_name = data['position']
                pot_type = 'bingo_royale'
                win_call_index = data['call_index']
                win_ball_call = data['call_number']
                query_list = {}
                query_list['query'] = """
                    INSERT INTO bingo_new_gamelog.winnings_summary(
                        round_id,
                        game_type,
                        part_name,
                        pot_type,
                        pot_prize_type,
                        winning_type,
                        cash_seed,
                        cash_maxcap,
                        cash_rtp,
                        bonus_seed,
                        bonus_maxcap,
                        bonus_rtp,
                        seed_amount,
                        maxcap_amount,
                        amount_won,
                        extra_pot,
                        total_tickets_won,
                        total_players_won,
                        winner_tickets,
                        win_call_index,
                        win_ball_call,
                        context)
                        VALUES( %(round_id)s, %(game_type)s, %(part_name)s, %(pot_type)s,
                                %(pot_prize_type)s, %(winning_type)s, %(cash_seed)s,
                                %(cash_maxcap)s, %(cash_rtp)s, %(bonus_seed)s,
                                %(bonus_maxcap)s, %(bonus_rtp)s, %(seed_amount)s, %(maxcap_amount)s,
                                %(amount_won)s, %(extra_pot)s, %(total_tickets_won)s,
                                %(total_players_won)s, %(winner_tickets)s, %(win_call_index)s,
                                %(win_ball_call)s, %(context)s)
                    """

                query_list['arguments'] = {
                    'round_id': self.summary['round_id'],
                    'game_type': 'variable',
                    'part_name': part_name,
                    'pot_type': pot_type,
                    'pot_prize_type': 'variable-amount',
                    'winning_type': 'per_ticket',
                    'cash_seed': 0.00,
                    'cash_maxcap': 0.00,
                    'cash_rtp': 0.00,
                    'bonus_seed': 0.00,
                    'bonus_maxcap': 0.00,
                    'bonus_rtp': 0.00,
                    'seed_amount': 0.00,
                    'maxcap_amount': 0.00,
                    'amount_won': json.dumps(
                        data['amount_won'].denominations),
                    'extra_pot': json.dumps(
                        {},
                        ensure_ascii=False),
                    'total_tickets_won': len(
                        data['tickets']),
                    'total_players_won': 1,
                    'winner_tickets': winner_tickets,
                    'win_call_index': win_call_index,
                    'win_ball_call': win_ball_call,
                    'context': json.dumps(
                        {})}
                self.queue.append(query_list)

    def export_winner_details(self):
        if self.summary['config'].get('bingo_royale', False):
            self.export_bingo_royale_winner_details()
            return
        winner_details = json.loads(self.summary['winner_details'])
        for winner_type, winner in winner_details.iteritems():
            winner_tickets = ','.join(str(value)
                                      for value in winner['winner_tickets'])
            if self.summary['config'].get('slingo_bingo', False):
                winner['part_name'] = 'slingo_bingo'
            query_list = {}
            query_list['query'] = """
                    INSERT INTO bingo_new_gamelog.winnings_summary(
                        round_id,
                        game_type,
                        part_name,
                        pot_type,
                        pot_prize_type,
                        winning_type,
                        cash_seed,
                        cash_maxcap,
                        cash_rtp,
                        bonus_seed,
                        bonus_maxcap,
                        bonus_rtp,
                        seed_amount,
                        maxcap_amount,
                        amount_won,
                        extra_pot,
                        total_tickets_won,
                        total_players_won,
                        winner_tickets,
                        win_call_index,
                        win_ball_call,
                        context)
                    VALUES(%(round_id)s, %(game_type)s, %(part_name)s,
                            %(pot_type)s, %(pot_prize_type)s, %(winning_type)s,
                            %(cash_seed)s, %(cash_maxcap)s, %(cash_rtp)s,
                            %(bonus_seed)s, %(bonus_maxcap)s, %(bonus_rtp)s,
                            %(seed_amount)s, %(maxcap_amount)s, %(amount_won)s,
                            %(extra_pot)s, %(total_tickets_won)s,
                            %(total_players_won)s, %(winner_tickets)s, %(win_call_index)s,
                            %(win_ball_call)s, %(context)s)
                    """
            query_list['arguments'] = {
                'round_id': self.summary['round_id'],
                'game_type': winner['game_type'],
                'part_name': winner['part_name'],
                'pot_type': winner['pot_type'],
                'pot_prize_type': winner['pot_prize_type'],
                'winning_type': winner['winning_type'],
                'cash_seed': winner['cash_seed'],
                'cash_maxcap': winner['cash_maxcap'],
                'cash_rtp': winner['cash_rtp'],
                'bonus_seed': winner['bonus_seed'],
                'bonus_maxcap': winner['bonus_maxcap'],
                'bonus_rtp': winner['bonus_rtp'],
                'seed_amount': json.dumps(
                    winner['seed_amount']),
                'maxcap_amount': json.dumps(
                    winner['maxcap_amount']),
                'amount_won': json.dumps(
                    winner['amount_won']),
                'extra_pot': json.dumps(
                    winner['extra_pot'],
                    ensure_ascii=False),
                'total_tickets_won': winner['total_tickets_won'],
                'total_players_won': winner['total_players_won'],
                'winner_tickets': winner_tickets,
                'win_call_index': winner['win_call_index'],
                'win_ball_call': winner['win_ball_call'],
                'context': json.dumps(
                    winner['context'])}
            self.queue.append(query_list)

    def export_players_info(self):
        player_start_time = time.time()
        players_info = self.player_info
        self.feature_winnings.update(self.summary['feature_winnings'])
        self.players_feature_data = self.feature_winnings
        self.player_summary_query = """INSERT INTO bingo_new_gamelog.player_summary_new(
                                    round_id,
                                    account_id,
                                    transaction_id,
                                    transaction_time,
                                    transaction_date,
                                    card_id,
                                    card_state,
                                    type,
                                    part,
                                    cash_wagered,
                                    bonus_wagered,
                                    wagered_amount,
                                    win_cash,
                                    win_bonus,
                                    win_amount)
                                VALUES"""
        _player_summary_query = self.player_summary_query
        ticket_count = 0
        total_ticket_count = 0
        for account_id, account_data in players_info.iteritems():
            gamelogs_flag = self.summary['config'].get(
                'gamelogs_optimization', False)
            if not gamelogs_flag and 'wager' in account_data.keys():
                for ticket_id, ticket_data in account_data['wager'].iteritems(
                ):
                    ticket_count = ticket_count + 1
                    total_ticket_count = total_ticket_count + 1
                    _player_summary_query = _player_summary_query + \
                        self.export_players_info_data(account_id, 'wager', ticket_data)
                    if ticket_count >= 100:
                        self.player_queue.append(_player_summary_query[:-1])
                        _player_summary_query = self.player_summary_query
                        ticket_count = 0
            if 'win' in account_data.keys():
                ticket_count = ticket_count + 1
                total_ticket_count = total_ticket_count + 1
                for win_item in account_data['win']:
                    _player_summary_query = _player_summary_query + \
                        self.export_players_info_data(account_id, 'win', win_item)
                    if ticket_count >= 100:
                        self.player_queue.append(_player_summary_query[:-1])
                        _player_summary_query = self.player_summary_query
                        ticket_count = 0
            self.export_player_level_data(account_id, account_data)
            if total_ticket_count >= 100:
                gevent.sleep(0.001)
                total_ticket_count = 0
        if ticket_count:
            self.player_queue.append(_player_summary_query[:-1])
        player_elapsed_time = time.time() - player_start_time
        self.info(
            'Total elapsed time in formulating player summary queries to buffer is %s',
            player_elapsed_time)

    def export_player_wager_info(self, account_id, ticket_info, config):
        """
        Handles the player wager related queries on the player_summary_new table
        """
        try:
            player_start_time = time.time()
            ticket_count = 0
            total_ticket_count = 0
            player_summary_query = """INSERT INTO bingo_new_gamelog.player_summary_new(
                                        round_id,
                                        account_id,
                                        transaction_id,
                                        transaction_time,
                                        transaction_date,
                                        card_id,
                                        card_state,
                                        type,
                                        part,
                                        cash_wagered,
                                        bonus_wagered,
                                        wagered_amount,
                                        win_cash,
                                        win_bonus,
                                        win_amount)
                                    VALUES"""
            _player_summary_query = player_summary_query
            for ticket_id, ticket_data in ticket_info.iteritems():
                ticket_count = ticket_count + 1
                total_ticket_count = total_ticket_count + 1
                _player_summary_query = _player_summary_query + \
                    self.export_players_info_data(account_id, 'wager', ticket_data, config)
                if ticket_count >= 100:
                    self.player_queue.append(_player_summary_query[:-1])
                    _player_summary_query = player_summary_query
                    ticket_count = 0

            if ticket_count:
                self.player_queue.append(_player_summary_query[:-1])
            player_elapsed_time = time.time() - player_start_time
            self.info(
                'Total time in creating wagering player summary query of player %s \
                        is %s',
                account_id,
                player_elapsed_time)
        except Exception as error:
            LOGGER.error(
                'Error occurred while forming wager query of player - %s,\
                          error - %s, %s',
                account_id,
                error,
                traceback.format_exc())

    def export_players_info_data(
            self,
            account_id,
            type,
            ticket_data,
            config=None):
        _config = config if config else self.summary['config']
        part = ''
        win_cash = 0.0
        win_bonus = 0.0
        win_amount = {}
        cash_wagered = 0.0
        bonus_wagered = 0.0
        wagered_amount = {}

        if type == 'wager':
            part = ticket_data['type']
            cash_wagered = ticket_data['wager_amount_cash']
            bonus_wagered = ticket_data['wager_amount_bonus']
            wagered_amount = ticket_data['wager_amount']
            transaction_id = ticket_data['transaction_uuid']

        if type == 'win':
            part = ticket_data['part']
            win_cash = ticket_data['win_amount_cash']
            win_amount = ticket_data['win_amount']
            try:
                if win_amount.get('Bonus_' + _config['currency'], None):
                    win_bonus = win_amount['Bonus_' + _config['currency']]
                if win_amount.get('Freespins_' + _config['currency'], None):
                    win_bonus = win_amount['Freespins_' + _config['currency']]
                if win_amount.get('Freetickets_' + _config['currency'], None):
                    win_bonus = win_amount['Freetickets_' +
                                           _config['currency']]
            except Exception as e:
                LOGGER.error('unable add the bonus', e)
            transaction_id = ticket_data['win_transaction_uuid']
            if 'win_type' in ticket_data:
                win_type = ticket_data['win_type']
                if 'pjp' in win_type:
                    type = 'pjp_win'
        _transaction_time = datetime.strptime(
            ticket_data['transaction_time'], '%Y-%m-%d %H:%M:%S')
        transaction_date = _transaction_time.strftime('%Y-%m-%d')
        _round_id = _config['round_id']
        player_values = """(%s, %s, "%s", "%s", "%s", "%s", "%s", "%s", "%s", %s, %s, '%s', %s, %s, '%s')""" % (_round_id,
                                                                                                                account_id, transaction_id, ticket_data['transaction_time'],
                                                                                                                transaction_date, ticket_data['card_id'], ticket_data['card_state'], type, part,
                                                                                                                cash_wagered, bonus_wagered, json.dumps(wagered_amount), win_cash, win_bonus,
                                                                                                                json.dumps(win_amount)) + ','
        return player_values

    def export_player_level_data(self, account_id, account_data):
        """Export player level data for a round"""
        _config = self.summary['config']
        cash_win = 0.0
        bonus_win = 0.0
        freespins_win = 0.0
        freetickets_win = 0.0
        points_win = 0.0
        win_amount = {}
        cash_wagered = 0.0
        bonus_wagered = 0.0
        wagered_amount = {}
        cash_discount = 0.0
        bonus_discount = 0.0
        context = {}
        bought_tickets = 0
        free_tickets = 0
        purchased_ticket_ids = ''
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
        wins = account_data.setdefault('win')
        wagers = account_data.setdefault('wager')
        features_win = self.players_feature_data.get(account_id, {})
        slingo_win = {}
        if wins:
            for win in wins:
                cash_win += win['win_amount_cash']
                bonus_win += win['win_amount_bonus']
                try:
                    if 'win_amount_freespins' in win.keys():
                        freespins_win += win['win_amount_freespins']
                    if 'win_amount_freetickets' in win.keys():
                        freetickets_win += win['win_amount_freetickets']
                    if 'win_amount_points' in win.keys():
                        points_win += win['win_amount_points']
                    if self.summary['config'].get('slingo_bingo', False):
                        slingo_win = {'Cash_GBP': cash_win,
                                      'Bonus_GBP': bonus_win,
                                      'Freespins_GBP': freespins_win,
                                      'Freetickets_GBP': freetickets_win,
                                      'Points_GBP': points_win}
                except Exception as e:
                    LOGGER.error('unable add the bonus in win', e)

        if wagers:
            purchased_ticket_ids += ', '.join(str(ticket) for ticket in wagers)
            for ticket in wagers:
                if wagers[ticket]['card_state'] == 'bought':
                    bought_tickets += 1
                    cash_wagered += wagers[ticket]['wager_amount_cash']
                    bonus_wagered += wagers[ticket]['wager_amount_bonus']
                    if 'discount' in wagers[ticket]:
                        cash, bonus, _, _ = amount_to_money(
                            wagers[ticket]['discount'])
                        cash_discount += cash
                        bonus_discount += bonus
                else:
                    free_tickets += 1
        if features_win:
            for feature in features_win:
                if features_win[feature].get('amount_won'):
                    try:
                        cash_win += features_win[feature]['amount_won'].get(
                            'Cash_' + _config['currency'], 0)
                        bonus_win += features_win[feature]['amount_won'].get(
                            'Bonus_' + _config['currency'], 0)
                        freespins_win += features_win[feature]['amount_won'].get(
                            'Freespins_' + _config['currency'], 0)
                        freetickets_win += features_win[feature]['amount_won'].get(
                            'Freetickets_' + _config['currency'], 0)
                        points_win += features_win[feature]['amount_won'].get(
                            'Points_' + _config['currency'], 0)
                    except Exception as e:
                        LOGGER.error(
                            'Error in adding the bonus in features_win', e)
        win_amount['cash_win'] = cash_win
        win_amount['bonus_win'] = bonus_win
        win_amount['freespins_win'] = freespins_win
        win_amount['freetickets_win'] = freetickets_win
        win_amount['points_win'] = points_win
        wagered_amount['cash_wagered'] = cash_wagered
        wagered_amount['bonus_wagered'] = bonus_wagered
        no_of_lines = 0
        pot_percentage = 0
        if self.summary['config'].get('slingo_bingo', False):
            # winner_details = json.loads(self.summary['game_config'])
            # winner_data = winner_details['slingo_summary']
            winner_data = self.summary['slingo_winners']
            if account_id in winner_data:
                no_of_lines = winner_data[account_id]['no_of_lines']
                pot_percentage = winner_data[account_id]['pot_percentage']
            context.update({'no_of_lines': no_of_lines,
                            'pot_percentage': pot_percentage,
                            'win_amount': slingo_win})

        context['discount'] = {"cash": cash_discount, "bonus": bonus_discount}

        try:
            if 'whack_a_bingo' in _config['features']:
                LOGGER.info("WHACK A BINGO : mysql round level summary")
                context['player_game_details'] = json.loads(
                    self.whack_a_bingo_details['player_state_' + str(account_id)])
                context['player_game_details']['on_points'] = json.loads(
                    self.whack_a_bingo_details['config']).get('on_points', None)
                currency_details = json.loads(
                    self.whack_a_bingo_details['config']).get(
                    'currency', _config['currency'])
                context['player_game_details']['features_name'] = 'whack_a_bingo'
                features_win['whack_a_bingo'] = context['player_game_details']
                win_amount['cash_win'] += context['player_game_details']['win_amount']['prize'].get(
                    "Cash_" + currency_details, 0)
                win_amount['bonus_win'] += context['player_game_details']['win_amount']['prize'].get(
                    "Bonus_" + currency_details, 0)
                win_amount['freespins_win'] += context['player_game_details']['win_amount']['prize'].get(
                    "Freespins_" + currency_details, 0)
                win_amount['freetickets_win'] += context['player_game_details']['win_amount']['prize'].get(
                    "Freetickets_" + currency_details, 0)
                win_amount['points_win'] += context['player_game_details']['win_amount']['prize'].get(
                    "Points_" + currency_details, 0)
        except Exception as error:
            self.error(
                "Whack A Bingo or Lucky Number:error at insert into player round level summary- %s",
                error)

        query_list = {}
        query_list['query'] = """
            INSERT INTO bingo_new_gamelog.player_round_level_summary(
                round_id,
                account_id,
                cash_wagered,
                bonus_wagered,
                wagered_amount,
                cash_win,
                bonus_win,
                win_amount,
                purchased_ticket_ids,
                bought_tickets,
                free_tickets,
                features_data,
                context)
                VALUES(%(round_id)s, %(account_id)s, %(cash_wagered)s,
                       %(bonus_wagered)s, %(wagered_amount)s,
                       %(cash_win)s, %(bonus_win)s, %(win_amount)s,
                       %(purchased_ticket_ids)s, %(bought_tickets)s, %(free_tickets)s,
                       %(features_data)s, %(context)s)"""
        query_list['arguments'] = {
            'round_id': self.summary['round_id'],
            'account_id': account_id,
            'cash_wagered': cash_wagered,
            'bonus_wagered': bonus_wagered,
            'wagered_amount': json.dumps(wagered_amount),
            'cash_win': cash_win,
            'bonus_win': bonus_win,
            'win_amount': json.dumps(win_amount),
            'purchased_ticket_ids': purchased_ticket_ids,
            'bought_tickets': bought_tickets,
            'free_tickets': free_tickets,
            'features_data': json.dumps(features_win),
            'context': json.dumps(context)}
        self.queue.append(query_list)

    def _export_winners(self, account_id, data, part_type):
        _tickets = data['tickets']
        cash, bonus, freespins, freetickets, points = wpr.amount_to_money_bonus_ability(
            data['amount_won'])
        cash = cash / len(_tickets)
        bonus = bonus / len(_tickets)
        freespins = freespins / len(_tickets)
        if freespins < _DEFAULT_FREESPINS and freespins:
            freespins = _DEFAULT_FREESPINS
        for ticket in _tickets:
            query_list = {}
            query_list['query'] = " INSERT INTO bingo_new_gamelog.winner "
            if part_type.startswith('part'):
                match = re.search('[0-9]+$', part_type)
                part_id = int(match.group(0))
                win_call_index = 0
                win_call_number = 0
                try:
                    if self.summary['config'].get('bingo_royale', False):
                        win_call_index = data['call_index']
                        part_id = data['position']
                    else:
                        win_call_index = int(
                            self.summary['part_calls'].split(',')[
                                part_id - 1])
                    win_call_number = \
                        int(self.summary['call_sequence'].split(',')
                            [win_call_index - 1])
                except Exception as error:
                    LOGGER.error("error updating winner table: %s", error)
                query_list['query'] += """(schedule_id, game_type, player_id,
                                    won_real, won_bb, card_id, stream_id, part,
                                    call_index, call_number)
                                    VALUES (%(schedule_id)s, %(game_type)s,
                                            %(player_id)s, %(won_real)s,
                                            %(won_bb)s, %(card_id)s, %(stream_id)s,
                                            %(part)s, %(call_index)s, %(call_number)s)
                                 """
                query_list['arguments'] = {
                    'schedule_id': self.summary['round_id'],
                    'game_type': self.summary['config']['pot_type'],
                    'player_id': account_id,
                    'won_real': cash,
                    'won_bb': bonus,
                    'card_id': ticket,
                    'stream_id': self.summary['config']['stream_id'],
                    'part': part_id,
                    'call_index': win_call_index,
                    'call_number': win_call_number}

                if freespins:
                    query_list['arguments']['won_bb'] = freespins
                if freetickets:
                    query_list['arguments']['won_bb'] = freetickets
                if points:
                    query_list['arguments']['won_bb'] = points
            elif part_type.startswith('pjp'):
                match = re.search('[0-9]+$', part_type)
                pjp_id = int(match.group(0))
                query_list['query'] += """
                                 (schedule_id, game_type, player_id, card_id,
                                 pjp_id, pjp_amount_real, pjp_amount_bb,
                                 stream_id, part)
                                 VALUES (%(schedule_id)s, %(game_type)s,
                                         %(player_id)s, %(card_id)s, %(pjp_id)s,
                                         %(pjp_amount_real)s, %(pjp_amount_bb)s,
                                         %(stream_id)s, %(part)s)"""
                query_list['arguments'] = {
                    'schedule_id': self.summary['round_id'],
                    'game_type': self.summary['config']['pot_type'],
                    'player_id': account_id,
                    'card_id': ticket,
                    'pjp_id': pjp_id,
                    'pjp_amount_real': cash,
                    'pjp_amount_bb': bonus,
                    'stream_id': self.summary['config']['stream_id'],
                    'part': self.get_last_part()}

            elif part_type.startswith('onetogo'):
                query_list['query'] += """
                                (schedule_id, stream_id, game_type, player_id,
                                card_id, part, ntogo, won_real, won_bb)
                                VALUES(%(schedule_id)s, %(stream_id)s, %(game_type)s,
                                        %(player_id)s, %(card_id)s, %(part)s,
                                        %(ntogo)s, %(won_real)s, %(won_bb)s)
                                """
                query_list['arguments'] = {
                    'schedule_id': self.summary['round_id'],
                    'stream_id': self.summary['config']['stream_id'],
                    'game_type': self.summary['config']['pot_type'],
                    'player_id': account_id,
                    'card_id': ticket,
                    'part': self.summary['config']['number_parts'],
                    'ntogo': 1,
                    'won_real': cash,
                    'won_bb': bonus}

            else:
                raise Exception('Invalid winning type')
            self.queue.append(query_list)

    def export_winners(self,):
        """Export winners"""
        _winners = {}
        if self.summary['config'].get('slingo_bingo', False):
            self.export_slingo_bingo_winners()
            return
        for part_type, value in self.summary['winners'].iteritems():
            if 'pjps' in part_type:
                for name, pjp_value in value.items():
                    _winners[name] = pjp_value
                continue
            _winners[part_type] = value

        for part_type, value in _winners.iteritems():
            for data in value:
                if isinstance(data['player'], list):
                    for wnnr in data['player']:
                        self._export_winners(
                            wnnr.details['account_id'], data, part_type)
                else:
                    self._export_winners(
                        data['player'].details['account_id'], data, part_type)

    def export_slingo_bingo_winners(self):
        """
        Entries for slingo winners
        """
        winner_info = json.loads(self.summary['winner_details'])
        # winner_details = json.loads(self.summary['game_config'])
        # winner_data = winner_details['slingo_summary']
        winner_data = self.summary['slingo_winners']
        player_info = self.player_info
        part_id = 1
        win_call_index = winner_info['part1']['win_call_index']
        win_call_number = winner_info['part1']['win_ball_call']
        for player in winner_data:
            query_list = {}
            if winner_data[player]['no_of_lines'] >= 1:
                player_id = int(player)
                cash = player_info[player_id]['win'][0]['win_amount_cash']
                bonus = player_info[player_id]['win'][0]['win_amount_bonus']
                freespins = player_info[player_id]['win'][0]['win_amount_freespins']
                freetickets = player_info[player_id]['win'][0]['win_amount_freetickets']
                ticket = player_info[player_id]['win'][0]['card_id']
                if freespins < _DEFAULT_FREESPINS and freespins:
                    freespins = _DEFAULT_FREESPINS
                query_list['query'] = """
                        INSERT INTO bingo_new_gamelog.winner(
                            schedule_id,
                            game_type,
                            player_id,
                            won_real,
                            won_bb,
                            card_id,
                            stream_id,
                            part,
                            call_index,
                            call_number)
                VALUES (%(schedule_id)s,%(game_type)s,%(player_id)s,%(won_real)s,
                        %(won_bb)s,
                        %(card_id)s, %(stream_id)s, %(part)s, %(call_index)s,
                        %(call_number)s)
                """
                query_list['arguments'] = {
                    'schedule_id': self.summary['round_id'],
                    'game_type': self.summary['config']['pot_type'],
                    'player_id': player_id,
                    'won_real': cash,
                    'won_bb': bonus,
                    'card_id': ticket,
                    'stream_id': self.summary['config']['stream_id'],
                    'part': part_id,
                    'call_index': win_call_index,
                    'call_number': win_call_number}
                self.queue.append(query_list)
            else:
                continue

    def get_last_part(self):
        LOGGER.info('Returns the last part of the round')
        """
        Returns the last part of the round.
        If roll on Bingo is enabled for the round
        this function returns the last part that is not a roll on.
        """
        last_part = 0
        if 'roll_on_parts' in list(self.summary['config'].keys()):
            for part_id, details in list(
                    self.summary['config']['parts'].items()):
                if part_id not in list(
                        self.summary['config']['roll_on_parts'].keys()):
                    last_part = max(int(last_part), int(part_id))
            return str(last_part)
        else:
            return str(self.summary['config']['number_parts'])

    def _send_batch_continuously(self):
        """Continuously send batches after a time interval"""
        while True:
            self.send_batch()
            gevent.sleep(self.batch_sleep_interval)
            self.send_failed_batch()
            gevent.sleep(self.batch_sleep_interval)
        LOGGER.error("MySQL: Send Batch Exited")

    def send_batch(self):
        """Flush inserts into the database"""
        try:
            if len(self.queue):  # pylint: disable-msg=W0212
                self.info('Inserting into DB')
                self.info('Total count of DB Events %s', len(self.queue))
                connection = database.connect()
                cursor = connection.cursor()
                if config_module.get('reports.dry_run'):
                    connection.rollback()
                else:
                    query_count = 0
                    while len(self.queue) > 0:
                        query = self.queue.pop()
                        try:
                            cursor.execute(query['query'], query['arguments'])
                            query_count = query_count + 1
                            if query_count >= 50:
                                connection.commit()
                                self.info(
                                    'count of DB Events %s', len(
                                        self.queue))
                                query_count = 0
                            elif len(self.queue) == 0:
                                connection.commit()
                                query_count = 0
                        except Exception as error:
                            self.failed_query_queue.append(query)

        except Exception as exception:
            self.error(
                'Error in Mysql Batch execution- %s, %s',
                exception,
                traceback.format_exc())

    def send_failed_batch(self):
        """Flush inserts into the database"""
        try:
            if len(self.failed_query_queue):  # pylint: disable-msg=W0212
                self.info('Inserting into DB')
                self.info(
                    'Total count of failed DB Events %s', len(
                        self.failed_query_queue))
                connection = database.connect()
                cursor = connection.cursor()
                if config_module.get('reports.dry_run'):
                    connection.rollback()
                else:
                    query_count = 0
                    while len(self.failed_query_queue) > 0:
                        query = self.failed_query_queue.pop()
                        try:
                            cursor.execute(query['query'], query['arguments'])
                            query_count = query_count + 1
                            if query_count >= 50:
                                connection.commit()
                                self.info(
                                    'count of failed DB Events %s', len(
                                        self.failed_query_queue))
                                query_count = 0
                            elif len(self.failed_query_queue) == 0:
                                connection.commit()
                                query_count = 0
                        except Exception as error:
                            self.final_failed_queue.append(query)
                            self.error('Error in logging into Mysql Database \
                                        - %s - query - %s - Traceback - %s', error,
                                       query, traceback.format_exc())
                    connection.commit()

        except Exception as exception:
            self.error(
                'Error in Mysql Batch execution- %s, %s',
                exception,
                traceback.format_exc())

    def _send_player_batch_continuously(self):
        while True:
            self.send_player_batch()
            gevent.sleep(self.batch_sleep_interval)
            self.send_player_failed_batch()
            gevent.sleep(self.batch_sleep_interval)
        LOGGER.error("MySQL: Send Player Batch Exited")

    def send_player_batch(self):
        """Flush inserts into the database"""
        try:
            if len(self.player_queue):  # pylint: disable-msg=W0212
                self.info('Inserting player summary into DB')
                self.info(
                    'Total count of player summary DB Events %s', len(
                        self.player_queue))
                connection = database.connect()
                cursor = connection.cursor()
                if config_module.get('reports.dry_run'):
                    connection.rollback()
                else:
                    query_count = 0
                    while len(self.player_queue) > 0:
                        query = self.player_queue.pop()
                        try:
                            cursor.execute(query)
                            query_count = query_count + 1
                            if query_count >= 50:
                                connection.commit()
                                self.info(
                                    'count of player summary DB Events %s', len(
                                        self.player_queue))
                                query_count = 0
                            elif len(self.player_queue) == 0:
                                connection.commit()
                                query_count = 0
                        except Exception as error:
                            self.player_failed_query_queue.append(query)

        except Exception as exception:
            self.error(
                'Error in Mysql Batch execution- %s, %s',
                exception,
                traceback.format_exc())

    def send_player_failed_batch(self):
        """Flush inserts into the database"""
        try:
            if len(self.player_failed_query_queue):  # pylint: disable-msg=W0212
                self.info('Inserting player summary into DB')
                self.info(
                    'Total count of player summary failed DB Events %s', len(
                        self.player_failed_query_queue))
                connection = database.connect()
                cursor = connection.cursor()
                if config_module.get('reports.dry_run'):
                    connection.rollback()
                else:
                    query_count = 0
                    while len(self.player_failed_query_queue) > 0:
                        query = self.player_failed_query_queue.pop()
                        try:
                            cursor.execute(query)
                            query_count = query_count + 1
                            if query_count >= 50:
                                connection.commit()
                                self.info(
                                    'count of failed player summary DB Events %s', len(
                                        self.player_failed_query_queue))
                                query_count = 0
                            elif len(self.player_failed_query_queue) == 0:
                                connection.commit()
                                query_count = 0
                        except Exception as error:
                            self.final_player_failed_queue.append(query)
                            self.error('Error in logging into Mysql Database \
                                        - %s - query - %s - Traceback - %s', error,
                                       query, traceback.format_exc())
                    connection.commit()

        except Exception as exception:
            self.error(
                'Error in Mysql Batch execution- %s, %s',
                exception,
                traceback.format_exc())
