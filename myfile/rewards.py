#
# Copyright (C) 2017 Sreeram Reddy Vanga <reddyvanga@gmail.com>
#
# Author(s): Vikas Singh <vsingh2@ivycomptech.com>
#

import copy
import uuid
import datetime
import json
import time
import gevent
import math
from nucleus import database
from nucleus import validation
from nucleus.api_decorator import api
from nucleus import api_key as api_key_module
from nucleus.api_decorator import api
from nucleus.caller_errors import InvalidAttributeValue
from nucleus.log import Log
from nucleus.gvcbingo import backend
from nucleus import backend_utils
from nucleus.gvcbingo import config as gvcbingo_config

LOGGER = Log(__name__)


@api('api_key', 'session_id', [type(None), int],
     [type(None), list], [type(None), str])
def get_reward_list(
        api_key,
        session_id,
        player_id,
        date_range=None,
        status=None):
    """Method for fetching lists of reward eligible for player
       and fetching existing reward history of a player"""
    LOGGER.info(
        'Reward Get Request - %s, %s, %s',
        player_id,
        session_id,
        status)
    session = validate_session(session_id.session_id)
    api_key_string = get_api_key_string(api_key)

    if not database.table_exists('bingo_new_gamelog', 'rewards_config'):
        return {'reward_list': []}

    connection = database.connect()
    cursor = connection.cursor()

    if not status:
        reward_data = fetch_current_rewards(cursor, player_id, date_range)
        if not reward_data:
            return {'reward_list': [],
                    'total_assigned_ftp': 0,
                    'total_played_ftp': 0
                    }

        formatted_data, total_assigned_ftp, total_played_ftp = format_current_rewards(
            reward_data)
        return {'play_data': formatted_data,
                'total_assigned_ftp': total_assigned_ftp,
                'total_played_ftp': total_played_ftp
                }

    elif status == 'history':
        history_data = fetch_reward_history(cursor, player_id)
        if not history_data:
            return {'reward_list': [],
                    'total_assigned_ftp': 0,
                    'total_played_ftp': 0,
                    'completed_ftp': 0,
                    'expired_ftp': 0
                    }

        formatted_history, totals = format_reward_history(history_data)
        return {**formatted_history, **totals}

    return {}


def validate_session(session_id):
    if isinstance(session_id, str):
        return validation.validate_session_id(session_id)
    try:
        token_data = backend_utils.get_token('gvcbingo', session_id, 'slave')
        session_id = token_data.get('session_id')
        session_response = backend_utils.get_token(
            'gvcbingo', session_id, 'slave')
    except Exception as err:
        LOGGER.info("Unable to fetch token")
        raise err

    return session_id


def get_api_key_string(api_key):
    if isinstance(api_key, api_key_module.APIKey):
        return api_key.api_key_string
    return api_key


def fetch_current_rewards(cursor, player_id, date_range):
    if date_range:
        start_date, end_date = date_range
        cursor.execute("""SELECT rc.feature_id,
                                 rc.name,
                                 rc.refernce_id,
                                 rc.end_date as expiry_date,
                                 rb.status
                          FROM bingo_new_gamelog.rewards_config rc
                          JOIN bingo_new_gamelog.rewards_balance rb
                          ON rc.refernce_id = rb.reference_id
                          WHERE rb.player_id = %s
                          AND rc.start_date <= %s
                          AND rc.end_date >= %s;""",
                       (player_id, start_date, end_date))
    else:
        cursor.execute("""SELECT rc.feature_id,
                                 rc.name,
                                 rc.refernce_id,
                                 rc.end_date as expiry_date,
                                 rb.status
                          FROM bingo_new_gamelog.rewards_config rc
                          JOIN bingo_new_gamelog.rewards_balance rb
                          ON rc.refernce_id = rb.reference_id
                          WHERE rc.status = 1
                          AND rb.player_id = %s;""",
                       (player_id,))
    return cursor.fetchall()


def format_current_rewards(reward_data):
    formatted_data = [{
        'feature_id': row[0],
        'feature_name': row[1],
        'reference_id': row[2],
        'expiry_date': row[3].strftime('%Y-%m-%d %H:%M:%S'),
        'status': row[4]
    } for row in reward_data]

    total_assigned_ftp = len(formatted_data)
    total_played_ftp = sum(
        1 for reward in formatted_data if reward['status'] in [
            'completed', 'inprogress'])

    return formatted_data, total_assigned_ftp, total_played_ftp


def fetch_reward_history(cursor, player_id):
    cursor.execute("""SELECT rc.feature_id,
                             rc.name,
                             rc.refernce_id,
                             rc.end_date as expiry_date,
                             rb.status,
                             rt.amount_won
                      FROM bingo_new_gamelog.rewards_config rc
                      JOIN bingo_new_gamelog.rewards_balance rb
                      ON rc.reference_id = rb.reference_id
                      JOIN bingo_new_gamelog.reward_transactions rt
                      ON rb.rewards_issue_id = rt.rewards_issue_id
                      WHERE rb.player_id = %s
                      AND rb.status IN ('expired', 'completed');""",
                   (player_id))

    return cursor.fetchall()


def format_reward_history(history_data):
    formatted_history = [{
        'feature_id': row[0],
        'feature_name': row[1],
        'reference_id': row[2],
        'expiry_date': row[3].strftime('%Y-%m-%d %H:%M:%S'),
        'status': row[4],
        'amount_won': row[5]
    } for row in history_data]
    total_assigned_ftp = len(formatted_history)
    total_played_ftp = sum(
        1 for reward in formatted_history if reward['status'] == 'completed')
    completed_ftp = sum(
        1 for reward in formatted_history if reward['status'] == 'completed')
    expired_ftp = sum(
        1 for reward in formatted_history if reward['status'] == 'expired')

    return {'history_data': formatted_history,
            'total_assigned_ftp': total_assigned_ftp,
            'total_played_ftp': total_played_ftp,
            'completed_ftp': completed_ftp,
            'expired_ftp': expired_ftp
            }


@api('api_key', 'session_id', int, int, bool)
def feature_launch(api_key, session_id, player_id, feature_id, refernce_id):

    return config_of_feature

# rtms integration


@api('api_key', int, int)
def assign_rewards(api_key, account_id, reference_id):
    if not validate_api_key(api_key):
        raise Exception('Invalid API key')

    if not validate_account_id(account_id):
        raise Exception('Invalid account ID')

    if not validate_ftp(reference_id, account_id):
        raise Exception('FTP validation failed')

    return {'success': True}


def validate_api_key(api_key):
    if isinstance(api_key, api_key_module.APIKey):
        return api_key

    if not isinstance(api_key, str):
        raise InvalidAttributeValue('Invalid type for API key')

    return api_key_module.get(api_key)


def validate_account_id(account_id):
    # checking against a database or data type
    if isinstance(account_id, int) and account_id > 0:
        return True
    else:
        return False


def validate_ftp(reference_id, account_id):

    # querying the reward configuration database
    # if the reference id in reward_config table and status == 'ACTIVE'
    # update the rewards balance table
    connection = database.connect()
    cursor = connection.cursor()

    cursor.execute("""SELECT rc.id, rc.name, rc.refernce_id,
                             rc.end_date
                      FROM bingo_new_gamelog.rewards_config rc
                      WHERE rc.refernce_id = %s AND rc.status = 1;""",
                   (reference_id,))
    result = cursor.fetchone()

    if result:
        # check in the reward balance table for the particular account_id
        # for first time players only insertion in rb
        expiry_date = result[3]  # datetime.date(2024, 6, 30)
        expiry_date = expiry_date.strftime('%Y-%m-%d %H:%M:%S')

        try:
            # check if the player_id is present in the rb table
            total_rows = 0
            cursor.execute("""SELECT rb.rewards_earned, rb.rewards_spent,
                           rb.balance
                           FROM bingo_new_gamelog.rewards_balance rb
                           WHERE rb.player_id = %s; """, (account_id,))

            total_rows = cursor.fetchone()

            if total_rows:
                update_balance_query = cursor.execute("""
                               UPDATE bingo_new_gamelog.rewards_balance rb
                               SET rewards_earned = rb.rewards_earned + 1,
                                   balance = rb.balance + 1,
                                   updated_on = now(),
                                   expiry_date = %s
                               WHERE rb.player_id = %s;
                               """, (expiry_date, account_id))
                # send rtms whenever update happens
                if update_balance_query:
                    cursor.execute("""SELECT rb.rewards_earned, rb.rewards_spent,
                                             rb.balance
                                      FROM bingo_new_gamelog.rewards_balance rb
                                      WHERE rb.player_id = %s
                                      AND rb.reference_id = %s;""",
                                   (account_id, reference_id))
                    updated_result = cursor.fetchone()
                    if updated_result:
                        rewards_earned, rewards_spent, balance = updated_result[0],
                    updated_result[1], updated_result[2]

                    cursor.execute(
                        """INSERT INTO bingo_new_gamelog.rewards_balance
                                   (rewards_issue_id, reference_id, player_id,
                                   rewards_earned, rewards_spent, balance,
                                   status, expiry_date, updated_on)
                    VALUES (NULL, %s, %s, %s, %s, %s, 1, %s, NOW());""",
                        (reference_id,
                         account_id,
                         rewards_earned,
                         rewards_spent,
                         balance,
                         expiry_date))

            else:
                cursor.execute("""INSERT INTO bingo_new_gamelog.rewards_balance
                                   (rewards_issue_id, reference_id, player_id,
                                   rewards_earned, rewards_spent, balance,
                                   status, expiry_date, updated_on)
                VALUES (NULL, %s, %s, 1, 0, 1, 1, %s, NOW());""",
                               (reference_id, account_id, expiry_date))

            connection.commit()

        except Exception as exception:  # in case unable to update
            LOGGER.exception('Encountered error while updating or \
                             inserting in the table - %s', exception)
        return True
    else:  # if no results found, validation failed
        return False


@api('api_key', int, int, int, str, str, str, str, [type(None), str])
def game_end(api_key, player_id, reward_config_id, reference_id, amount_won,
             transaction_id, currency_part1, currency_part2, status=None):
    """
    Rewards game end api
    change status of game.
    """
    state = 2
    STATUS_MAP = {
        "active": 0,
        "inprogress": 1,
        "completed": 2
    }
    if status in STATUS_MAP:
        state = STATUS_MAP[status]

    connection = database.connect(server_class='slave')
    cursor = connection.cursor(dictionary=True, buffered=True)

    check_query = """
            SELECT rb.status, rb.expiry_date, rc.full_site_code
            FROM bingo_new_gamelog.rewards_balance as rb
            JOIN bingo_new_gamelog.rewards_config as rc
            ON rb.reference_id = rc.reference_id
            WHERE rb.player_id = {player_id}
            AND rb.reference_id = {reference_id}
            AND rb.rewards_issue_id = {reward_config_id}
            """.format(player_id=player_id, reference_id=reference_id,
                       reward_config_id=reward_config_id, state=state)
    cursor.execute(check_query)
    game_data = cursor.fetchone()

    expiryTime = game_data.get("expiry_date").strftime('%s')
    rtms_data = {"message": {"game_completed": "success"},
                 "player_id": [player_id],
                 "expiryTime": int(expiryTime),
                 "full_site_code": game_data.get("full_site_code")}

    if game_data.get("status") == 2:
        send_rtms_message(rtms_data)
        return {"Game Status Already Updated": "Success"}

    query = """
            UPDATE bingo_new_gamelog.rewards_balance
            SET status={state}
            WHERE player_id = {player_id}
            AND reference_id = {reference_id}
            AND rewards_issue_id = {reward_config_id}
            """.format(player_id=player_id, reference_id=reference_id,
                       reward_config_id=reward_config_id, state=state)
    cursor.execute(query)
    if amount_won:
        amount_query = """
               INSERT INTO bingo_new_gamelog.reward_transactions
               (player_id, rewards_issue_id, amount_won, transaction_id, \
               currency_part1, currency_part2)
               VALUES (%s, %s, %s, %s, %s, %s)
               """
        values = (player_id, reward_config_id, amount_won,
                  transaction_id, currency_part1, currency_part2)
        cursor.execute(amount_query, values)
    connection.commit()
    connection.close()

    send_rtms_message(rtms_data)
    return {"game_completed": "success"}


def send_rtms_message(rtms_message):

    for brand in gvcbingo_config.CONFIG["site_code_fe_mappings"]:
        if brand["full_site_code"] in rtms_message.get("full_site_code"):
            brand_info = brand
            break
    message = rtms_message.get("message")
    rtms_data = {
        "brandId": brand_info['brand'],
        "frontEndId": brand_info['fe'],
        "toaster": True,
        "eventType": "BINGO",
        "message": json.dumps(message),
        "label": rtms_message.get("full_site_code"),
        "players": rtms_message.get("player_id"),
        "notificationType": "CUSTOM",
        "roomId": ["90"],
        "allowedPlayers": "specific",
        "expiryTime": rtms_message.get("expiryTime")
    }
    LOGGER.info("Triggering RTMS for reward game end == %s", rtms_data)
    backend.request('triggerNotification', rtms_data)
