from openerp.tests.common import TransactionCase


class TestMarketingCampaign(TransactionCase):

    def setUp(self):
        super(TestMarketingCampaign, self).setUp()

        self.MarketingWorkitem = self.env['marketing.campaign.workitem']

        self.campaign = self.env.ref(
            'generic_condition_marketing.marketing_campaign_maao_partner_channel')  # noqa
        self.segment = self.env.ref(
            'generic_condition_marketing.marketing_campaign_segment0')
        self.activity_0 = self.env.ref(
            'generic_condition_marketing.marketing_campaign_activity_0')
        self.activity_1 = self.env.ref(
            'generic_condition_marketing.marketing_campaign_activity_1')

    def test_00_campaign(self):
        # In order to test process of compaign, I start compaign.
        self.campaign.state_running_set()

        # I check the campaign on Running mode after started.
        self.assertEqual(self.campaign.state, 'running')

        # I start this segment after assinged campaign.
        self.segment.state_running_set()

        # I check the segment on Running mode after started.
        self.assertEqual(self.segment.state, 'running')

        # I synchronized segment manually to see all step of activity and
        # process covered on this campaign.
        self.assertTrue(
            self.segment.date_next_sync,
            'Next Synchronization date is not calculated.')
        self.segment.process_segment()

        # I cancel Marketing Workitems.
        workitems = self.MarketingWorkitem.search(
            [('segment_id', '=', self.segment.id),
             ('campaign_id', '=', self.campaign.id)])
        workitems.button_cancel()
        self.assertIn(
            workitems[0].state,
            ('cancelled', 'done'),
            'Marketing Workitem shoud be in cancel state.',
        )

        # I set Marketing Workitems in draft state.
        workitems = self.MarketingWorkitem.search(
            [('segment_id', '=', self.segment.id),
             ('campaign_id', '=', self.campaign.id)])
        workitems.button_draft()
        self.assertIn(
            workitems[0].state,
            ('todo', 'done'),
            'Marketing Workitem shoud be in draft state.',
        )

        # I process follow-up of first activity.
        workitems = self.MarketingWorkitem.search(
            [('segment_id', '=', self.segment.id),
             ('campaign_id', '=', self.campaign.id),
             ('activity_id', '=', self.activity_0.id)])
        self.assertTrue(
            workitems, 'Follow-up item is not created for first activity.')
        workitem = workitems[0]
        self.assertTrue(workitem.res_name, 'Resource Name is not defined.')
        workitems.process()
        self.assertEqual(
            workitems[0].state,
            'done',
            "Follow-up item should be closed after process.")

        # I check follow-up detail of second activity after process of first
        # activity.
        workitems = self.MarketingWorkitem.search(
            [('segment_id', '=', self.segment.id),
             ('campaign_id', '=', self.campaign.id),
             ('activity_id', '=', self.activity_1.id)])
        self.assertTrue(
            workitems, 'Follow-up item is not created for first activity.')

        # Now I increase credit limit of customer
        self.env.ref("base.res_partner_2").write({'credit_limit': 61000})

        # I process follow-up of second activity after set draft.
        workitems = self.MarketingWorkitem.search(
            [('segment_id', '=', self.segment.id),
             ('campaign_id', '=', self.campaign.id),
             ('activity_id', '=', self.activity_1.id)])
        workitems.button_draft()
        workitems.process()
        self.assertEqual(
            workitems[0].state,
            'cancelled',
            "Follow-up item should be cancelled after process.")
