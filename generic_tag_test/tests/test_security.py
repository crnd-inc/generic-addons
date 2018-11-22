from odoo.tests.common import SavepointCase
from odoo.exceptions import AccessError
import logging
_logger = logging.getLogger(__name__)


class TestSecurity(SavepointCase):
    """ Check basic tag logic
    """

    @classmethod
    def setUpClass(cls):
        super(TestSecurity, cls).setUpClass()

        cls.test_model = cls.env.ref('generic_tag_test.test_tag_model')
        cls.test_record_1 = cls.env.ref('generic_tag_test.taggable_object_1')
        cls.test_record_2 = cls.env.ref('generic_tag_test.taggable_object_2')
        cls.test_tag_cat_1 = cls.env.ref(
            'generic_tag_test.test_tag_category_1')
        cls.test_tag_1 = cls.env.ref('generic_tag_test.test_tag_1')
        cls.test_tag_2 = cls.env.ref('generic_tag_test.test_tag_2')
        cls.test_tag_3 = cls.env.ref('generic_tag_test.test_tag_3')
        cls.test_tag_4 = cls.env.ref('generic_tag_test.test_tag_4')
        cls.test_tags = (cls.test_tag_1 |
                         cls.test_tag_2 |
                         cls.test_tag_3 |
                         cls.test_tag_4)

        cls.demo_user = cls.env.ref('base.user_demo')
        cls.demo_user.groups_id |= cls.env.ref('base.group_user')
        cls.uenv = cls.env(user=cls.demo_user)

    def test_simple_user_access_records(self):
        # Add to record 2 one tag without group and one tag with group
        self.test_record_2.tag_ids |= self.test_tag_1
        self.test_record_2.tag_ids |= self.test_tag_4

        self.assertEqual(len(self.test_record_2.tag_ids), 2)

        urec = self.uenv['generic.tag.test.model'].browse(
            self.test_record_2.id)
        urec.ensure_one()
        self.assertEqual(len(urec.tag_ids), 1)
        self.assertEqual(urec.tag_ids[0].id, self.test_tag_1.id)

        self.demo_user.groups_id |= self.env.ref(
            'generic_tag_test.group_tags_test_group')

        urec = self.uenv['generic.tag.test.model'].browse(
            self.test_record_2.id)
        urec.ensure_one()
        self.assertEqual(len(urec.tag_ids), 2)
        self.assertIn(self.test_tag_1.id, urec.tag_ids.ids)
        self.assertIn(self.test_tag_4.id, urec.tag_ids.ids)

        uGenericTag = self.uenv['generic.tag']
        # Test create
        with self.assertRaises(AccessError):
            uGenericTag.create({
                'name': 'D',
                'model_id': self.test_model.id
            })

        # Test write
        with self.assertRaises(AccessError):
            uGenericTag.browse(self.test_tag_1.id).write({'name': 'D'})

        with self.assertRaises(AccessError):
            uGenericTag.browse(self.test_tag_4.id).write({'name': 'D'})

        # Test unlink
        with self.assertRaises(AccessError):
            uGenericTag.browse(self.test_tag_1.id).unlink()

        with self.assertRaises(AccessError):
            uGenericTag.browse(self.test_tag_4.id).unlink()

    def test_tags_user_access_records(self):
        self.demo_user.groups_id |= self.env.ref(
            'generic_tag.group_tags_user')

        # Add to record 2 one tag without group and one tag with group
        self.test_record_2.tag_ids |= self.test_tag_1
        self.test_record_2.tag_ids |= self.test_tag_4

        self.assertEqual(len(self.test_record_2.tag_ids), 2)

        urec = self.uenv['generic.tag.test.model'].browse(
            self.test_record_2.id)
        urec.ensure_one()
        self.assertEqual(len(urec.tag_ids), 1)
        self.assertEqual(urec.tag_ids[0].id, self.test_tag_1.id)

        self.demo_user.groups_id |= self.env.ref(
            'generic_tag_test.group_tags_test_group')

        urec = self.uenv['generic.tag.test.model'].browse(
            self.test_record_2.id)
        urec.ensure_one()
        self.assertEqual(len(urec.tag_ids), 2)
        self.assertIn(self.test_tag_1.id, urec.tag_ids.ids)
        self.assertIn(self.test_tag_4.id, urec.tag_ids.ids)

        uGenericTag = self.uenv['generic.tag']
        # Test create
        with self.assertRaises(AccessError):
            uGenericTag.create({
                'name': 'D',
                'model_id': self.test_model.id
            })

        # Test write
        with self.assertRaises(AccessError):
            uGenericTag.browse(self.test_tag_1.id).write({'name': 'D'})

        with self.assertRaises(AccessError):
            uGenericTag.browse(self.test_tag_4.id).write({'name': 'C'})

        # Test unlink
        with self.assertRaises(AccessError):
            uGenericTag.browse(self.test_tag_1.id).unlink()

        with self.assertRaises(AccessError):
            uGenericTag.browse(self.test_tag_4.id).unlink()

    def test_tags_user_restricted_access_records(self):
        self.demo_user.groups_id |= self.env.ref(
            'generic_tag.group_tags_user_restricted')

        # Add to record 2 one tag without group and one tag with group
        self.test_record_2.tag_ids |= self.test_tag_1
        self.test_record_2.tag_ids |= self.test_tag_4

        self.assertEqual(len(self.test_record_2.tag_ids), 2)

        urec = self.uenv['generic.tag.test.model'].browse(
            self.test_record_2.id)
        urec.ensure_one()
        self.assertEqual(len(urec.tag_ids), 0)

        self.demo_user.groups_id |= self.env.ref(
            'generic_tag_test.group_tags_test_group')

        urec = self.uenv['generic.tag.test.model'].browse(
            self.test_record_2.id)
        urec.ensure_one()
        self.assertEqual(len(urec.tag_ids), 1)
        self.assertIn(self.test_tag_4.id, urec.tag_ids.ids)

    def test_tags_manager_access_records(self):
        self.demo_user.groups_id |= self.env.ref(
            'generic_tag.group_tags_manager')

        # Add to record 2 one tag without group and one tag with group
        self.test_record_2.tag_ids |= self.test_tag_1
        self.test_record_2.tag_ids |= self.test_tag_4

        self.assertEqual(len(self.test_record_2.tag_ids), 2)

        urec = self.uenv['generic.tag.test.model'].browse(
            self.test_record_2.id)
        urec.ensure_one()
        self.assertEqual(len(urec.tag_ids), 2)
        self.assertIn(self.test_tag_1.id, urec.tag_ids.ids)
        self.assertIn(self.test_tag_4.id, urec.tag_ids.ids)

        self.demo_user.groups_id |= self.env.ref(
            'generic_tag_test.group_tags_test_group')

        urec = self.uenv['generic.tag.test.model'].browse(
            self.test_record_2.id)
        urec.ensure_one()
        self.assertEqual(len(urec.tag_ids), 2)
        self.assertIn(self.test_tag_1.id, urec.tag_ids.ids)
        self.assertIn(self.test_tag_4.id, urec.tag_ids.ids)

        # Tag create/edit/unlink should not raise exception
        uGenericTag = self.uenv['generic.tag']
        # Test create
        uGenericTag.create({
            'name': 'A',
            'model_id': self.test_model.id
        })

        # Test write
        uGenericTag.browse(self.test_tag_1.id).write({'name': 'D'})
        uGenericTag.browse(self.test_tag_4.id).write({'name': 'C'})

        # Test unlink
        uGenericTag.browse(self.test_tag_1.id).unlink()
        uGenericTag.browse(self.test_tag_4.id).unlink()
