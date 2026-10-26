from odoo.tests.common import TransactionCase


class RefreshViewTest(TransactionCase):
    """ Test notifications sent to web client to refresh displayed views.

        Notifications are not stored in 'bus.bus' immediately: they are
        accumulated in the precommit queue of the cursor and created on
        commit. Thus tests have to inspect that queue. Since Odoo 20.0 it
        holds `(channel, notification_type, message)` tuples, with the
        message not serialized yet.
    """

    def setUp(self):
        super().setUp()
        self.Model = self.env['test.gm.refresh.view']

    def _bus_queue(self):
        return self.env.cr.precommit.data.get('bus.bus.values', [])

    def _bus_queue_len(self):
        return len(self._bus_queue())

    def _get_refresh_notifications(self, since=0):
        """ Return payloads of refresh notifications queued after 'since'

            :param int since: amount of queued messages to skip
            :return list: list of payloads of refresh notifications
        """
        res = []
        for _channel, notification_type, message in self._bus_queue()[since:]:
            if notification_type == 'generic_mixin_refresh_view':
                res.append(message)
        return res

    def test_refresh_notification_on_create(self):
        queued = self._bus_queue_len()
        record = self.Model.create({'name': 'Rec 1'})

        self.assertEqual(
            self._get_refresh_notifications(queued),
            [{'test.gm.refresh.view': {'create': [record.id]}}])

    def test_refresh_notification_on_write(self):
        record = self.Model.create({'name': 'Rec 1'})

        queued = self._bus_queue_len()
        record.write({'name': 'Rec 1 updated'})

        self.assertEqual(
            self._get_refresh_notifications(queued),
            [{'test.gm.refresh.view': {'write': [record.id]}}])

    def test_refresh_notification_on_unlink(self):
        record = self.Model.create({'name': 'Rec 1'})
        record_id = record.id

        queued = self._bus_queue_len()
        record.unlink()

        self.assertEqual(
            self._get_refresh_notifications(queued),
            [{'test.gm.refresh.view': {'unlink': [record_id]}}])

    def test_refresh_notification_delayed(self):
        """ Changes made inside 'with_delay_refresh' block have to be sent
            as a single notification with ids serialized as JSON lists
        """
        record_1 = self.Model.create({'name': 'Rec 1'})

        queued = self._bus_queue_len()
        with self.Model.with_delay_refresh():
            record_2 = self.Model.create({'name': 'Rec 2'})
            record_1.write({'name': 'Rec 1 updated'})

        notifications = self._get_refresh_notifications(queued)
        self.assertEqual(len(notifications), 1)

        model_data = notifications[0]['test.gm.refresh.view']
        self.assertEqual(sorted(model_data.keys()), ['create', 'write'])
        # Ids have to be lists. Before they were accumulated in python sets,
        # that are not JSON-serializable, thus were silently sent to the
        # browser as their string representation ('{1}') and web client was
        # not able to match them with displayed records.
        self.assertEqual(model_data['create'], [record_2.id])
        self.assertEqual(model_data['write'], [record_1.id])

    def test_refresh_notification_delayed_multiple_records(self):
        """ Ids of multiple records have to be sent as a list of ints
        """
        queued = self._bus_queue_len()
        with self.Model.with_delay_refresh():
            records = self.Model.create([
                {'name': 'Rec 1'},
                {'name': 'Rec 2'},
                {'name': 'Rec 3'},
            ])

        notifications = self._get_refresh_notifications(queued)
        self.assertEqual(len(notifications), 1)

        create_ids = notifications[0]['test.gm.refresh.view']['create']
        self.assertIsInstance(create_ids, list)
        for create_id in create_ids:
            self.assertIsInstance(create_id, int)
        self.assertEqual(sorted(create_ids), sorted(records.ids))
