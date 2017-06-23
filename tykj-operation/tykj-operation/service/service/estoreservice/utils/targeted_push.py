# -*- coding: utf-8 -*-
import random
import re
import simplejson
from django.conf import settings
from estorecore.db import timestamp_utc_now
from itertools import groupby


MESSAGE_PUSH_INTERVAL = 24 * 60 * 60


# utils begin

def _get_message_target_value(message, key, defauld_value=None):
    targets = message.get('targets', None)
    if not targets:
        return defauld_value

    return targets.get(key, defauld_value)


def _get_message_group_name(message):
    name = _get_message_target_value(
        message,
        'tg_msg_group',
        defauld_value='')
    if name == 'empty':
        name = ''
    return name


def _equal_dict(first, second):
    if len(first) != len(second):
        return False
    for k, v in first.iteritems():
        if k not in second or second[k] != v:
            return False
    return True


def _update_user_tags(
        user_tags, user_apps, chn, device_model, os_v, screensize, sim_operator,
        user_phone, client_version, ip, user_pushed_messages, debug_user_tags, location_db, perf):
    if user_tags is None:
        user_tags = {}

    if chn:
        user_tags['chn:%s' % chn] = 1
    if device_model:
        user_tags['devicemodel:%s' % device_model] = 1
    if os_v:
        user_tags['osv'] = os_v
    if screensize:
        user_tags['screensize:%s' % screensize] = 1
    if sim_operator:
        user_tags['simoperator'] = sim_operator
    if user_phone:
        user_tags['userphone:%s' % user_phone] = 1
    if client_version:
        user_tags['clientversion'] = client_version

    user_app_keys = [k for k in user_tags.keys() if k.startswith('app:')]
    for k in user_app_keys:
        del user_tags[k]
    if user_apps and 'apps' in user_apps:
        user_apps = user_apps['apps']
        for app in user_apps:
            user_tags['app:%s' %
                      app['packageName'].replace(
                          '.', '_')] = app['packageVersion']

    # user city
    if 'city' not in user_tags and ip:
        user_city = location_db.ip_to_city(ip)
        if user_city is not None:
            user_tags['city'] = user_city
        if perf:
            perf.set('city')

    if user_pushed_messages:
        for k, v in user_pushed_messages.iteritems():
            user_tags['pushedmessage:%s' % k] = v

    if debug_user_tags:
        user_tags.update(simplejson.loads(debug_user_tags))

    return user_tags


def _date_key_from_time(time_now):
    return str(time_now / 86400)


def _update_pushed_messages(
        client_id, time_now, user_pushed_messages, messages, push_db):
    new_user_pushed_messages = {}
    for k, v in user_pushed_messages.iteritems():
        if time_now - v < 365 * 24 * 60 * 60:
            new_user_pushed_messages[k] = v

    for message in messages:
        new_user_pushed_messages[str(message['message_id'])] = time_now

    if not _equal_dict(user_pushed_messages, new_user_pushed_messages):
        push_db.set_pushed_messages(client_id, new_user_pushed_messages)

    push_db.inc_message_pushed_counts(_date_key_from_time(time_now), messages)


def _weighted_sample(values):
    value_upto = 0
    value_random = random.uniform(0, sum(values))
    i = 0
    for value in values:
        value_upto += value
        if value_upto >= value_random:
            return i
        i += 1

    # ASSERT FALSE
    return 0

# end utils


class MessageMatcher:

    def __init__(self, user_tags, time_now, debug=0):
        self.user_tags = user_tags
        self.time_now = time_now
        self.debug = debug
        self.debug_logs = None
        if self.debug:
            self.debug_logs = []
            self.debug_logs.append('__init__ with debug enabled')

    def do_match(self, messages):
        if self.debug:
            self.debug_logs.append(
                'do_match: %s' %
                str([m.get('message_id', 0) for m in messages]))

        if not self.user_tags:
            if self.debug:
                self.debug_logs.append('no user_tags, no message filter')
            return messages

        try:
            final_messages = [
                message for message in messages if self._match_message(
                    message)]
        except Exception as e:
            if self.debug:
                self.debug_logs.append('fatal exception: %s' % str(e))
            return []

        if self.debug:
            self.debug_logs.append(
                'do_match: final=%s' %
                str([m.get('message_id', 0) for m in final_messages]))

        return final_messages

    def _match_message(self, message):
        if self.debug:
            self.debug_logs.append(
                'match message: %d' %
                message.get('message_id', 0))
            self.debug_logs.append(message.get('targets', None))
        targets = message.get('targets', None)
        if not targets:
            if self.debug:
                self.debug_logs.append('no targets, return True')
            return True

        if not self._match_device_model(targets):
            if self.debug:
                self.debug_logs.append('_match_device_model, return False')
            return False

        if not self._match_device_os_version(targets):
            if self.debug:
                self.debug_logs.append(
                    '_match_device_os_version, return False')
            return False

        if not self._match_device_screensize(targets):
            if self.debug:
                self.debug_logs.append(
                    '_match_device_screensize, return False')
            return False

        if not self._match_network_operator(targets):
            if self.debug:
                self.debug_logs.append('_match_network_operator, return False')
            return False

        if not self._match_city(targets):
            if self.debug:
                self.debug_logs.append('_match_city, return False')
            return False

        if not self._match_app_installed(targets):
            if self.debug:
                self.debug_logs.append('_match_app_installed, return False')
            return False

        if not self._match_app_not_installed(targets):
            if self.debug:
                self.debug_logs.append(
                    '_match_app_not_installed, return False')
            return False

        if not self._match_user_phone(targets):
            if self.debug:
                self.debug_logs.append('_match_user_phone, return False')
            return False

        if not self._match_pushed_messages(targets):
            if self.debug:
                self.debug_logs.append('_match_pushed_messages, return False')
            return False

        if not self._match_chn(targets):
            if self.debug:
                self.debug_logs.append('_match_chn, return False')
            return False

        if not self._match_client_version(targets):
            if self.debug:
                self.debug_logs.append('_match_client_version, return False')
            return False

        return True

    def _match_device_model(self, targets):
        return self._match_by_array_key(targets, 'tg_device', 'devicemodel:%s')

    def _match_device_os_version(self, targets):
        return self._match_by_array_value(targets, 'tg_sys_version', 'osv')

    def _match_device_screensize(self, targets):
        return (
            self._match_by_array_key(
                targets,
                'tg_screen_size',
                'screensize:%s')
        )

    def _match_network_operator(self, targets):
        return (
            self._match_by_array_value(
                targets,
                'tg_operator',
                'simoperator',
                target_value_tranform=lambda x: [int(y) for y in x.split(',')])
        )

    def _match_city(self, targets):
        return self._match_by_array_value(targets, 'tg_city', 'city')

    def _match_app_installed(self, targets):
        target_values = self._read_array(targets, 'tg_installed_app_pn')
        if not target_values:
            if self.debug:
                self.debug_logs.append(
                    '_match_app_installed, no target required, return True')
            return True

        for target_value in target_values:
            package_name = target_value
            op = None
            version = None
            s = re.split(r'(=|<|>)', target_value)
            if len(s) == 3:
                package_name = s[0].strip()
                op = s[1].strip()
                version = int(s[2].strip())
            package_name = package_name.replace('.', '_')
            value = self.user_tags.get('app:%s' % package_name, None)
            if self.debug:
                self.debug_logs.append(
                    '_match_app_installed, package_name=%s, value=%s, op=%s, version=%s' %
                    (package_name, str(value), str(op), str(version)))
            if value is not None:
                if ((op is None) or
                        (op == '=' and value == version) or
                        (op == '>' and value > version) or
                            (op == '<' and value < version)
                        ):
                        return True

        return False

    def _match_app_not_installed(self, targets):
        target_values = self._read_array(targets, 'tg_uninstalled_app_pn')
        if not target_values:
            if self.debug:
                self.debug_logs.append(
                    '_match_app_not_installed, no target required, return True')
            return True

        for target_value in target_values:
            target_value = target_value.replace('.', '_')
            value = self.user_tags.get('app:%s' % target_value, None)
            if self.debug:
                self.debug_logs.append(
                    '_match_app_not_installed, target_value=%s, value=%s' %
                    (str(target_value), str(value)))
            if value is None:
                return True

        return False

    def _match_user_phone(self, targets):
        return self._match_by_array_key(targets, 'tg_phone', 'userphone:%s')

    def _match_pushed_messages(self, targets):
        target_values = self._read_array(targets, 'tg_pushed_messages')
        if not target_values:
            if self.debug:
                self.debug_logs.append(
                    '_match_pushed_messages, %s, no target required, return True' %
                    ('tg_pushed_messages'))
            return True

        for target_value in target_values:
            message_id = target_value
            op = None
            push_time = None
            s = re.split(r'(=|<|>)', target_value)
            if len(s) == 3:
                message_id = s[0].strip()
                op = s[1].strip()
                push_time = int(s[2].strip())

            value = self.user_tags.get('pushedmessage:%s' % message_id, None)
            value = self.time_now - value if value is not None else None
            if self.debug:
                self.debug_logs.append(
                    '_match_pushed_messages, message_id=%s, value=%s, op= %s, push_time=%s' %
                    (message_id, str(value), str(op), str(push_time)))

            if value is not None:
                if ((op is None) or
                        (op == '=' and value == push_time) or
                        (op == '>' and value > push_time) or
                            (op == '<' and value < push_time)
                        ):
                        return True

        return False

    def _match_chn(self, targets):
        return self._match_by_array_key(targets, 'tg_channel_name', 'chn:%s')

    def _match_client_version(self, targets):
        target_values = self._read_array(targets, 'tg_version_code')
        if not target_values:
            if self.debug:
                self.debug_logs.append(
                    '_match_client_version, no target required, return True')
            return True

        if len(target_values) < 2 or target_values[0] not in ('>', '<', '>=', '<=', '=='):
            return True

        client_version = self.user_tags.get('clientversion', 0)
        if eval('%s%s' % (client_version, ''.join(target_values))):
            return True

        return False

    # check if user_tag in target_values
    def _match_by_array_value(
            self, targets, target_name, user_tag_name, target_value_tranform=None):
        target_values = self._read_array(targets, target_name)
        if not target_values:
            if self.debug:
                self.debug_logs.append(
                    '_match_by_array_value, %s, no target required, return True' %
                    (target_name))
            return True

        try:
            transformed_target_values = []
            for v in target_values:
                if target_value_tranform:
                    transformed_target_values += target_value_tranform(v)
                else:
                    transformed_target_values += [int(v)]
            target_values = transformed_target_values
        except Exception as e:
            if self.debug:
                self.debug_logs.append(
                    '_match_by_array_value, %s, target values=%s, got exception: %s' %
                    (target_name, str(target_values), str(e)))
            return False

        value = self.user_tags.get(user_tag_name, 0) in target_values
        if self.debug:
            self.debug_logs.append(
                '_match_by_array_value, name=%s, value=%s' %
                (target_name, str(value)))
        return value

    # check if user_tag % target in user_tags
    def _match_by_array_key(self, targets, target_name, user_tag_name,
                            target_value_tranform=None, detect_reverse_selection=True):
        target_values = self._read_array(targets, target_name)
        if not target_values:
            if self.debug:
                self.debug_logs.append(
                    '_match_by_array_key, %s, no target required, return True' %
                    (target_name))
            return True

        reverse_selection = False
        if detect_reverse_selection and target_values[0].startswith('-'):
            reverse_selection = True
            target_values[0] = target_values[0][1:]
        for target_value in target_values:
            if target_value_tranform is not None:
                target_value = target_value_tranform(target_value)
            value = self.user_tags.get(user_tag_name % target_value, None)
            if self.debug:
                self.debug_logs.append(
                    '_match_by_array_key, name=%s, target_value=%s, value=%s' %
                    (target_name, str(target_value), str(value)))
            if value is not None and value > 0:
                return not reverse_selection

        return reverse_selection

    def _read_array(self, targets, name):
        value = targets.get(name, None)
        if value is None:
            return None

        if not isinstance(value, list):
            value = value.strip()
            if value:
                value = value.split(',')
                value = [item.strip() for item in value]
            else:
                value = None
        return value


class MessageRanker:

    def __init__(self, user_tags, debug=0):
        self.user_tags = user_tags
        self.debug = debug
        self.debug_logs = None
        if self.debug:
            self.debug_logs = []
            self.debug_logs.append('__init__ with debug enabled')

    def do_rank(self, messages, count):
        if self.debug:
            self.debug_logs.append(
                'do_rank: %s' %
                str([m.get('message_id', 0) for m in messages]))

        try:
            final_messages = self._process_messages(messages)
        except Exception as e:
            if self.debug:
                self.debug_logs.append('fatal exception: %s' % str(e))
            return []

        # sort message: first empty group; then by score, then by time
        final_messages = sorted(
            final_messages,
            key=lambda x: (x.get('rscore',
                                 1e10),
                           x['last_modified']),
            reverse=True)

        final_messages = final_messages[: count]

        if self.debug:
            self.debug_logs.append(
                'do_rank: final=%s' %
                str([m.get('message_id', 0) for m in messages]))

        return final_messages

    def _process_messages(self, messages):
        final_messages = []

        for group_name, group_messages in groupby(messages, lambda r: self._get_message_group_name(r)):
            group_messages = [message for message in group_messages]
            final_messages += self._process_message_group(group_name,
                                                          group_messages)
            if self.debug:
                self.debug_logs.append(
                    'process group: %s, message=%s' %
                    (group_name, [(m.get('message_id', 0), m.get('rscore', 1e10)) for m in group_messages]))

        return final_messages

    def _process_message_group(self, group_name, messages):
        # handle the special group: messages in this group should be sent to
        # all user
        if group_name == '':
            return messages

        # handle normal message group: select only 1 message at each push
        for message in messages:
            message['rscore'] = self._evaluate_relevance_score(
                self.user_tags,
                message)

        # from a group: pick only one message at a push, based on the push
        # quota and score
        weights = [message['rscore'] * message.get('push_today', 1000000)
                   for message in messages]
        i = _weighted_sample(weights)
        if self.debug:
            self.debug_logs.append(
                'weighted sample: %s, weights=%s, selected=%d' %
                (group_name, str(weights), i))

        return [messages[i]]

    def _get_message_group_name(self, message):
        targets = message.get('targets', None)
        if not targets:
            return ''

        name = targets.get('tg_msg_group', '')
        if name == 'empty':
            name = ''
        return name

    def _get_app_from_message(self, message):
        message_value = message.get('value', None)
        if message_value:
            if 'package_name' in message_value:
                return message_value['package_name']
            message_click_value = message_value.get('click_value', None)
            if message_click_value:
                if 'package_name' in message_click_value:
                    return message_click_value['package_name']
        return None

    def _evaluate_relevance_score(self, user_tags, message):
        return 1

        # TODO: evaluate relevance score
#        target_app = _get_app_from_message(message)
#        if not user_tags or not target_app:
#            return 0
#
#        target_app = target_app.replace('.', '_')
#        edges = []
# try app usage
#        for k, v in user_tags.iteritems():
#            if k.startswith('appusage:') and v > 0:
#                edges.append((k[len('appusage:'):] + ':' + target_app, v))
#        if not edges:
# try user installed apps if there's no usage data
#            for k, v in user_tags.iteritems():
#                if k.startswith('app:') and v > 0:
#                    edges.append((k[len('app:'):] + ':' + target_app, 1))
#        if not edges:
#            return 0
#
#        edge_scores = user_targeting_db.query_app_graph([e[0] for e in edges])
#        edge_scores = dict([(e['_id'], e['score']) for e in edge_scores])
#
#        final_score = 0
#        weight_sum = 0
#        for edge in edges:
#            weight_sum += edge[1]
#            score = edges.get(edge[0], 0)
#            final_score += weight_sum * score
#        if weight_sum > 0:
#            final_score /= float(weight_sum)
#
#        return final_score


def select_messages(
        messages, client_id, source, chn, is_test_device, count, device_model='', os_v=0, screensize='', sim_operator=0,
        user_phone='', client_version=0, ip=None, debug=0, debug_user_tags=None, perf=None, push_db=None, user_db=None, location_db=None):
    if not messages:
        if debug:
            messages.append({'debug_message': 'no message found'})
        return messages

    time_now = timestamp_utc_now()

    final_messages = messages
    if perf:
        perf.set('pre')

    # push time check
    user_pushed_messages = push_db.get_pushed_messages(client_id)
    if user_pushed_messages:
        print 'pushed'
        final_messages = [message for message in final_messages if str(
            message['message_id']) not in user_pushed_messages]
        last_message_push_time = max(message[1]
                                     for message in user_pushed_messages.iteritems())
        # no two messages within 12 hours
        if time_now - last_message_push_time < MESSAGE_PUSH_INTERVAL:
            # push only if there's direct message
            if all(_get_message_group_name(message) != '' for message in final_messages):
                final_messages = []
                if debug:
                    final_messages.append(
                        {'debug_message': 'no direct message',
                         'last_message_push_time': last_message_push_time,
                         'now': time_now,
                         'messages': messages,
                         'user_pushed_messages': user_pushed_messages})
                return final_messages
    if perf:
        perf.set('ptc')

    print 'end .....'
    # filter messages which run out of quota
    pushed_counts = push_db.get_message_pushed_counts(final_messages)
    pushed_counts = dict([(item['_id'], item)
                         for item in pushed_counts]) if pushed_counts else {}
    date_now = _date_key_from_time(time_now)
    final_messages_new = []
    for message in final_messages:
        push_total = _get_message_target_value(
            message,
            'push_total',
            defauld_value=0)
        push_daily = _get_message_target_value(
            message,
            'push_daily',
            defauld_value=0)

        pushed_total = 0
        pushed_today = 0
        pushed_count = pushed_counts.get(message['message_id'], None)
        if pushed_count:
            pushed_total = pushed_count.get('total', 0)
            pushed_today = pushed_count.get(date_now, 0)

        if push_total != 0 and push_total <= pushed_total:
            continue
        if push_daily != 0 and push_daily <= pushed_today:
            continue

        # 1000000, this will be used for message sampling
        message['push_today'] = (
            push_daily - pushed_today) if push_daily != 0 else 1000000
        final_messages_new.append(message)
    final_messages = final_messages_new
    if perf:
        perf.set('qt')
    if not final_messages:
        if debug:
            final_messages.append(
                {'debug_message': 'all messages run out of quota',
                 'messages': messages,
                 'pushed_counts': pushed_counts})
        return final_messages

    # step 0: get user data
    user_tags = user_db.query_user_tags(client_id)
    if perf:
        perf.set('qut')
    user_apps = user_db.query_apps_installed(client_id)
    if perf:
        perf.set('qua')
    user_tags = _update_user_tags(
        user_tags,
        user_apps,
        chn,
        device_model,
        os_v,
        screensize,
        sim_operator,
        user_phone,
        client_version,
        ip,
        user_pushed_messages,
        debug_user_tags,
        location_db,
        perf)
    if perf:
        perf.set('uut')

    # step 1: filter message
    print '11111'
    print final_messages
    message_matcher = MessageMatcher(user_tags, time_now, debug=debug)
    final_messages = message_matcher.do_match(final_messages)
    # no message filter for test device:
    if is_test_device:
        final_messages = messages
    if perf:
        perf.set('fltr')

    # step 2: rank and select message
    message_ranker = MessageRanker(user_tags, debug=debug)
    final_messages = message_ranker.do_rank(final_messages, count)
    if perf:
        perf.set('rnk')

    if client_id == 'apitest':
        # client: apitest is a very special test id, it could always get all
        # valid messages
        final_messages = messages
    else:
        for message in final_messages:
            if 'targets' in message:
                del message['targets']
            if 'push_today' in message:
                del message['push_today']
        if not debug:
            _update_pushed_messages(
                client_id,
                time_now,
                user_pushed_messages,
                final_messages,
                push_db)
    if perf:
        perf.set('ums')

    if debug:
        debug_data = {'debug': debug,
                      'user_tags': user_tags,
                      'message_matcher': message_matcher.debug_logs,
                      'message_ranker': message_ranker.debug_logs,
                      'user_pushed_messages': user_pushed_messages,
                      'pushed_counts': pushed_counts}
        final_messages.append(debug_data)

    return final_messages
