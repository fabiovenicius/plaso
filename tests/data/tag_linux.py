#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the tag_linux.txt tagging file."""

from __future__ import unicode_literals

import unittest

from plaso.containers import events
from plaso.lib import definitions
from plaso.parsers import bash_history
from plaso.parsers import docker
from plaso.parsers import dpkg
from plaso.parsers import selinux
from plaso.parsers import syslog
from plaso.parsers import utmp
from plaso.parsers import zsh_extended_history
from plaso.parsers.syslog_plugins import cron

from tests.data import test_lib


class LinuxTaggingFileTest(test_lib.TaggingFileTestCase):
  """Tests the tag_linux.txt tagging file.

  In the tests below the EventData classes are used to catch failing tagging
  rules in case event data types are renamed.
  """

  _TAG_FILE = 'tag_linux.txt'

  def testRuleApplicationExecution(self):
    """Tests the application_execution tagging rule."""
    # Test: data_type is 'bash:history:command'
    attribute_values_per_name = {}
    self._CheckTaggingRule(
        bash_history.BashHistoryEventData, attribute_values_per_name,
        ['application_execution'])

    # Test: data_type is 'docker:json:layer'
    attribute_values_per_name = {}
    self._CheckTaggingRule(
        docker.DockerJSONLayerEventData, attribute_values_per_name,
        ['application_execution'])

    # Test: data_type is 'selinux:line' AND audit_type is 'EXECVE'
    attribute_values_per_name = {
        'audit_type': ['EXECVE']}
    self._CheckTaggingRule(
        selinux.SELinuxLogEventData, attribute_values_per_name,
        ['application_execution'])

    # Test: data_type is 'shell:zsh:history'
    attribute_values_per_name = {}
    self._CheckTaggingRule(
        zsh_extended_history.ZshHistoryEventData, attribute_values_per_name,
        ['application_execution'])

    # Test: data_type is 'syslog:cron:task_run'
    attribute_values_per_name = {}
    self._CheckTaggingRule(
        cron.CronTaskRunEventData, attribute_values_per_name,
        ['application_execution'])

    # Test: reporter is 'sudo' AND body contains 'COMMAND='
    attribute_values_per_name = {
        'body': ['test if my COMMAND=bogus'],
        'reporter': ['sudo']}
    self._CheckTaggingRule(
        syslog.SyslogLineEventData, attribute_values_per_name,
        ['application_execution'])

  def testRuleLogin(self):
    """Tests the login tagging rule."""
    # Test: data_type is 'linux:utmp:event' AND type == 7
    attribute_values_per_name = {
        'type': [7]}
    self._CheckTaggingRule(
        utmp.UtmpEventData, attribute_values_per_name,
        ['login'])

    # Test: data_type is 'selinux:line' AND audit_type is 'LOGIN'
    attribute_values_per_name = {
        'audit_type': ['LOGIN']}
    self._CheckTaggingRule(
        selinux.SELinuxLogEventData, attribute_values_per_name,
        ['login'])

    # Test: reporter is 'login' AND (body contains 'logged in' OR
    #       body contains 'ROOT LOGIN' OR body contains 'session opened')
    attribute_values_per_name = {
        'body': ['logged in', 'ROOT LOGIN', 'session opened'],
        'reporter': ['login']}
    self._CheckTaggingRule(
        syslog.SyslogLineEventData, attribute_values_per_name,
        ['login'])

    # Test: reporter is 'sshd' AND (body contains 'session opened' OR
    #       body contains 'Starting session')
    attribute_values_per_name = {
        'body': ['session opened', 'Starting session'],
        'reporter': ['sshd']}
    self._CheckTaggingRule(
        syslog.SyslogLineEventData, attribute_values_per_name,
        ['login'])

    # Test: reporter is 'dovecot' AND body contains 'imap-login: Login:'
    attribute_values_per_name = {
        'body': ['imap-login: Login:'],
        'reporter': ['dovecot']}
    self._CheckTaggingRule(
        syslog.SyslogLineEventData, attribute_values_per_name,
        ['login'])

    # Test: reporter is 'postfix/submission/smtpd' AND body contains 'sasl_'
    attribute_values_per_name = {
        'body': ['sasl_method=PLAIN, sasl_username='],
        'reporter': ['postfix/submission/smtpd']}
    self._CheckTaggingRule(
        syslog.SyslogLineEventData, attribute_values_per_name,
        ['login'])

  def testRuleLoginFailed(self):
    """Tests the login_failed tagging rule."""
    # Test: data_type is 'selinux:line' AND audit_type is 'ANOM_LOGIN_FAILURES'
    attribute_values_per_name = {
        'audit_type': ['ANOM_LOGIN_FAILURES']}
    self._CheckTaggingRule(
        selinux.SELinuxLogEventData, attribute_values_per_name,
        ['login_failed'])

    # Test: data_type is 'selinux:line' AND audit_type is 'USER_LOGIN' AND
    #       body contains 'res=failed'
    attribute_values_per_name = {
        'audit_type': ['USER_LOGIN'],
        'body': ['res=failed']}
    self._CheckTaggingRule(
        selinux.SELinuxLogEventData, attribute_values_per_name,
        ['login_failed'])

    # Test: data_type is 'syslog:line' AND body contains 'pam_tally2'
    attribute_values_per_name = {
        'body': ['pam_tally2']}
    self._CheckTaggingRule(
        syslog.SyslogLineEventData, attribute_values_per_name,
        ['login_failed'])

    # Test: (reporter is 'sshd' OR
    #        reporter is 'login' OR
    #        reporter is 'postfix/submission/smtpd' OR
    #        reporter is 'sudo') AND
    #        body contains 'uthentication fail'
    attribute_values_per_name = {
        'body': ['authentication failed', 'authentication failure',
                 'Authentication failure'],
        'reporter': ['login', 'postfix/submission/smtpd', 'sshd', 'sudo']}
    self._CheckTaggingRule(
        syslog.SyslogLineEventData, attribute_values_per_name,
        ['login_failed'])

    # Test: (reporter is 'xscreensaver' or
    #        reporter is 'login') AND
    #       body contains 'FAILED LOGIN'
    attribute_values_per_name = {
        'body': ['FAILED LOGIN'],
        'reporter': ['login', 'xscreensaver']}
    self._CheckTaggingRule(
        syslog.SyslogLineEventData, attribute_values_per_name,
        ['login_failed'])

    # Test: reporter is 'su' AND body contains 'DENIED'
    attribute_values_per_name = {
        'body': ['DENIED su from'],
        'reporter': ['su']}
    self._CheckTaggingRule(
        syslog.SyslogLineEventData, attribute_values_per_name,
        ['login_failed'])

    # Test: reporter is 'nologin'
    attribute_values_per_name = {
        'reporter': ['nologin']}
    self._CheckTaggingRule(
        syslog.SyslogLineEventData, attribute_values_per_name,
        ['login_failed'])

  def testRuleLogout(self):
    """Tests the logout tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: data_type is 'linux:utmp:event' AND type == 8 AND terminal != '' AND
    #       pid != 0
    event_data = utmp.UtmpEventData()
    event_data.type = 0
    event_data.terminal = 'tty1'
    event_data.pid = 1

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.type = 8
    event_data.terminal = ''

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.terminal = 'tty1'
    event_data.pid = 0

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.pid = 1

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['logout'])

    # Test: reporter is 'login' AND body contains 'session closed'
    event_data = syslog.SyslogLineEventData()
    event_data.reporter = 'login'
    event_data.body = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'bogus'
    event_data.body = 'session closed'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'login'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['logout'])

    # Test: reporter is 'sshd' AND (body contains 'session closed' OR
    #       body contains 'Close session')
    event_data = syslog.SyslogLineEventData()
    event_data.reporter = 'sshd'
    event_data.body = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'bogus'
    event_data.body = 'session closed'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'sshd'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['logout'])

    event_data.body = 'Close session'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['logout'])

    # Test: reporter is 'systemd-logind' AND body contains 'logged out'
    event_data = syslog.SyslogLineEventData()
    event_data.reporter = 'systemd-logind'
    event_data.body = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'bogus'
    event_data.body = 'logged out'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'systemd-logind'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['logout'])

    # Test: reporter is 'dovecot' AND body contains 'Logged out'
    event_data = syslog.SyslogLineEventData()
    event_data.reporter = 'dovecot'
    event_data.body = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'bogus'
    event_data.body = 'Logged out'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'dovecot'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['logout'])

  def testRuleSessionStart(self):
    """Tests the session_start tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: reporter is 'systemd-logind' and body contains 'New session'
    event_data = syslog.SyslogLineEventData()
    event_data.reporter = 'systemd-logind'
    event_data.body = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'bogus'
    event_data.body = 'New session'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'systemd-logind'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['session_start'])

  def testRuleSessionStop(self):
    """Tests the session_stop tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: reporter is 'systemd-logind' and body contains 'Removed session'
    event_data = syslog.SyslogLineEventData()
    event_data.reporter = 'systemd-logind'
    event_data.body = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'bogus'
    event_data.body = 'Removed session'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'systemd-logind'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['session_stop'])

  def testRuleBoot(self):
    """Tests the boot tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: data_type is 'linux:utmp:event' AND type == 2 AND
    #       terminal is 'system boot' AND username is 'reboot'
    event_data = utmp.UtmpEventData()
    event_data.type = 0
    event_data.terminal = 'system boot'
    event_data.username = 'reboot'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.type = 2
    event_data.terminal = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.terminal = 'system boot'
    event_data.username = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.username = 'reboot'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['boot'])

  def testRuleShutdown(self):
    """Tests the shutdonw tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: data_type is 'linux:utmp:event' AND type == 1 AND
    #       (terminal is '~~' OR terminal is 'system boot') AND
    #       username is 'shutdown'
    event_data = utmp.UtmpEventData()
    event_data.type = 0
    event_data.terminal = 'system boot'
    event_data.username = 'shutdown'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.type = 1
    event_data.terminal = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.terminal = 'system boot'
    event_data.username = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.username = 'shutdown'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['shutdown'])

    event_data.terminal = '~~'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['shutdown'])

  def testRuleRunlevel(self):
    """Tests the runlevel tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: data_type is 'linux:utmp:event' AND type == 1 AND
    #       username is 'runlevel'
    event_data = utmp.UtmpEventData()
    event_data.type = 0
    event_data.username = 'runlevel'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.type = 1
    event_data.username = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.username = 'runlevel'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['runlevel'])

  def testRuleDeviceConnection(self):
    """Tests the device_connection tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: reporter is 'kernel' AND body contains 'New USB device found'
    event_data = syslog.SyslogLineEventData()
    event_data.reporter = 'kernel'
    event_data.body = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'bogus'
    event_data.body = 'New USB device found'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'kernel'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['device_connection'])

  def testRuleDeviceDisconnection(self):
    """Tests the device_disconnection tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: reporter is 'kernel' AND body contains 'USB disconnect'
    event_data = syslog.SyslogLineEventData()
    event_data.reporter = 'kernel'
    event_data.body = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'bogus'
    event_data.body = 'USB disconnect'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'kernel'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['device_disconnection'])

  def testRuleApplicationInstall(self):
    """Tests the application_install tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: data_type is 'dpkg:line' AND body contains 'status installed'
    event_data = dpkg.DpkgEventData()
    event_data.body = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.body = 'status installed'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['application_install'])

  def testRuleServiceStart(self):
    """Tests the service_start tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: data_type is 'selinux:line' AND audit_type is 'SERVICE_START'
    event_data = selinux.SELinuxLogEventData()
    event_data.audit_type = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.audit_type = 'SERVICE_START'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['service_start'])

  def testRuleServiceStop(self):
    """Tests the service_stop tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: data_type is 'selinux:line' AND audit_type is 'SERVICE_STOP'
    event_data = selinux.SELinuxLogEventData()
    event_data.audit_type = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.audit_type = 'SERVICE_STOP'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['service_stop'])

  def testRulePromiscuous(self):
    """Tests the promiscuous tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: data_type is 'selinux:line' AND audit_type is 'ANOM_PROMISCUOUS'
    event_data = selinux.SELinuxLogEventData()
    event_data.audit_type = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.audit_type = 'ANOM_PROMISCUOUS'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['promiscuous'])

    # Test: reporter is 'kernel' AND body contains 'promiscuous mode'
    event_data = syslog.SyslogLineEventData()
    event_data.reporter = 'kernel'
    event_data.body = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'bogus'
    event_data.body = 'promiscuous mode'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'kernel'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['promiscuous'])

  def testRuleCrach(self):
    """Tests the crash tagging rule."""
    event = events.EventObject()
    event.timestamp = self._TEST_TIMESTAMP
    event.timestamp_desc = definitions.TIME_DESCRIPTION_UNKNOWN

    # Test: data_type is 'selinux:line' AND audit_type is 'ANOM_ABEND'
    event_data = selinux.SELinuxLogEventData()
    event_data.audit_type = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.audit_type = 'ANOM_ABEND'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['crash'])

    # Test: reporter is 'kernel' AND body contains 'segfault'
    event_data = syslog.SyslogLineEventData()
    event_data.reporter = 'kernel'
    event_data.body = 'bogus'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'bogus'
    event_data.body = 'segfault'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 0)
    self._CheckLabels(storage_writer, [])

    event_data.reporter = 'kernel'

    storage_writer = self._TagEvent(event, event_data)

    self.assertEqual(storage_writer.number_of_event_tags, 1)
    self._CheckLabels(storage_writer, ['crash'])


if __name__ == '__main__':
  unittest.main()
