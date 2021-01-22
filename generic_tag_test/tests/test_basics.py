import logging
from psycopg2 import IntegrityError

from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError
from odoo.tools.misc import mute_logger

_logger = logging.getLogger(__name__)


class TestBasics(SavepointCase):
    """ Check basic tag logic
    """

    @classmethod
    def setUpClass(cls):
        super(TestBasics, cls).setUpClass()

        cls.test_model = cls.env.ref('generic_tag_test.test_tag_model')
        cls.test_record_1 = cls.env.ref('generic_tag_test.taggable_object_1')
        cls.test_record_2 = cls.env.ref('generic_tag_test.taggable_object_2')
        cls.test_tag_cat_1 = cls.env.ref(
            'generic_tag_test.test_tag_category_1')
        cls.test_tag_1 = cls.env.ref('generic_tag_test.test_tag_1')
        cls.test_tag_2 = cls.env.ref('generic_tag_test.test_tag_2')
        cls.test_tag_3 = cls.env.ref('generic_tag_test.test_tag_3')

    def test_05_tags_count(self):
        self.assertEqual(self.test_model.tags_count, 4,
                         "Wrong tags_count for model")
        self.assertEqual(self.test_tag_cat_1.tags_count, 2,
                         "Wrong tags_count for model")

    def test_10_add_tag(self):
        """ Test that .add_tag method works fine
        """
        # Test simple add
        self.test_record_1.add_tag(name='Tag 1', code='Tag_1')
        self.assertFalse(
            self.test_record_1.tag_ids,
            "There must be no tags added. (tag with such name does not exists)"
        )

        # Test simple add with create
        self.test_record_1.add_tag(name='Tag 1', code='Tag_1', create=True)
        self.assertTrue(
            self.test_record_1.tag_ids,
            "There must be no tags added. (tag with such name does not exists)"
        )
        self.assertEqual(len(self.test_record_1.tag_ids), 1,
                         "There are one tag must be present in object")
        self.assertEqual(self.test_record_1.tag_ids[0].name, 'Tag 1')
        self.assertEqual(self.test_record_1.tag_ids[0].code, 'Tag_1')

        # Try to add existing tag to existing object (use only code)
        self.test_record_2.add_tag(code='Tag_1', create=True)
        self.assertTrue(
            self.test_record_2.tag_ids,
            "There must be no tags added. (tag with such name does not exists)"
        )
        self.assertEqual(len(self.test_record_2.tag_ids), 1,
                         "There are one tag must be present in object")
        self.assertEqual(self.test_record_2.tag_ids[0].name, 'Tag 1')
        self.assertEqual(self.test_record_2.tag_ids[0].code, 'Tag_1')

        # Try to add tag to many objects at once
        recs = self.test_record_1 | self.test_record_2
        recs.add_tag(name='Tag 3', code='Tag_3', create=True)

        self.assertEqual(len(self.test_record_1.tag_ids), 2,
                         "There are two tags must be present in object")
        self.assertEqual(len(self.test_record_2.tag_ids), 2,
                         "There are two tags must be present in object")

    def test_20_check_tag(self):
        """ Test that .check_tag method works fine
        """
        # First add tag to only one record
        self.test_record_1.add_tag(name='Tag 1', code='Tag_1', create=True)

        # And check if it present there
        self.assertTrue(
            self.test_record_1.check_tag(name='Tag 1', code='Tag_1'))

        # Then check for a list of records where only one record have specified
        # tag
        res = self.env['generic.tag.test.model'].browse([
            self.test_record_1.id,
            self.test_record_2.id,
        ]).check_tag(name='Tag 1', code='Tag_1')
        self.assertFalse(res)

        # And check record without tags
        self.assertFalse(
            self.test_record_2.check_tag(name='Tag 1', code='Tag_1'))

        # Check only by code
        self.assertTrue(
            self.test_record_1.check_tag(code='Tag_1'))

        # Check only by name
        self.assertTrue(
            self.test_record_1.check_tag(name='Tag 1'))

    def test_30_remove_tag(self):
        """ Test that .remove_tag method works fine
        """
        # First add tag to only one record
        self.test_record_1.add_tag(name='Tag 1', code='Tag_1', create=True)
        self.test_record_2.add_tag(name='Tag 2', code='Tag_2', create=True)
        self.test_record_1.add_tag(name='Tag 3', code='Tag_3', create=True)
        self.test_record_2.add_tag(name='Tag 3', code='Tag_3', create=True)

        # check preconditions
        self.assertEqual(len(self.test_record_1.tag_ids), 2)
        self.assertEqual(len(self.test_record_2.tag_ids), 2)

        # test .remove_tag on record without this tag
        self.test_record_1.remove_tag(name='Tag 2', code='Tag_2')
        self.assertEqual(len(self.test_record_1.tag_ids), 2)

        # test .remove_tag on recordset where one record have requested tag
        recs = self.test_record_1 | self.test_record_2
        recs.remove_tag(name='Tag 1', code='Tag_1')
        self.assertEqual(len(self.test_record_1.tag_ids), 1)
        self.assertEqual(len(self.test_record_2.tag_ids), 2)

        # test .remove_tag with unexisting tag, but name starts same as
        # existing
        recs.remove_tag(name='Tag', code='Tag')
        self.assertEqual(len(self.test_record_1.tag_ids), 1)
        self.assertEqual(len(self.test_record_2.tag_ids), 2)

        # test .remove_tag method to remove tag present in all records in set
        recs.remove_tag(name='Tag 3')
        self.assertEqual(len(self.test_record_1.tag_ids), 0)
        self.assertEqual(len(self.test_record_2.tag_ids), 1)

    def test_40_check_tag_category(self):
        """ Test if check tag category method works fine
        """
        self.test_record_1.add_tag(name='TC1', code='tc1')
        self.test_record_2.add_tag(
            name='Test Tag1', code='Testtag1', create=True)

        self.assertTrue(
            self.test_record_1.check_tag_category(code='tag_cat_1'))

        self.assertFalse(
            self.test_record_2.check_tag_category(code='tag_cat_1'))

        self.assertFalse(
            self.test_record_2.check_tag_category(name='Test Category 1'))

        self.assertTrue(
            self.test_record_1.check_tag_category(name='Test Category 1'))

    def test_50_category_xor(self):
        """ Check that tag category xor logic works fine
        """
        recs = self.test_record_1 | self.test_record_2

        # Check that if category have no 'xor' check, then it is posible to add
        # more then one tag from this category to object
        recs.add_tag(code='tc1')
        recs.add_tag(code='tc2')
        self.assertEqual(len(self.test_record_1.tag_ids), 2)
        self.assertEqual(len(self.test_record_2.tag_ids), 2)

        # Remove tags from objects
        recs.remove_tag(code='tc1')
        recs.remove_tag(code='tc2')
        self.assertEqual(len(self.test_record_1.tag_ids), 0)
        self.assertEqual(len(self.test_record_2.tag_ids), 0)

        # Mark category as 'XOR'
        self.test_tag_cat_1.write({'check_xor': True})

        # And retry adding two tags from same category
        recs.add_tag(code='tc1')
        with self.assertRaises(ValidationError):
            recs.add_tag(code='tc2')

    def test_60_name_tag(self):
        """ Test that .name_category_tag method works fine
        """
        self.assertEqual(self.test_tag_1.complete_name,
                         'Test Category 1 / TC1')

    def test_70_object(self):
        """ Test that .name_category_tag method works fine
        """
        recs = self.test_record_1 | self.test_record_2

        self.assertEqual(self.test_tag_3.objects_count, 0)
        recs.add_tag(name='TC3', code='tc3')

        # Refresh test_tag_3 record, to recompute objects_count.
        # objects count compute method have no 'depends' spec,
        # So we need manualy refresh cache
        self.test_tag_3.refresh()  # This is required
        self.assertEqual(self.test_tag_3.objects_count, 2)

    def test_80_action_show_tags(self):
        """ Test that action_show_tags method works fine
        """
        res = self.test_model.action_show_tags()
        self.assertEqual(res['res_model'], 'generic.tag')
        self.assertEqual(res['domain'],
                         [('model_id.id', '=', self.test_model.id)])

    def test_90_action_show_tags_category(self):
        """ Test that action_show_tags_category method works fine
        """
        res = self.test_tag_cat_1.action_show_tags()
        self.assertEqual(res['res_model'], 'generic.tag')
        self.assertEqual(res['domain'], [(
            'category_id.id', '=', self.test_tag_cat_1.id)])

    def test_91_action_show_objects(self):
        """ Test that action_show_objects method works fine
        """
        res = self.test_tag_1.action_show_objects()
        self.assertEqual(res['res_model'], 'generic.tag.test.model')
        self.assertEqual(res['domain'], [(
            'tag_ids.id', '=', self.test_tag_1.id)])

    def test_93_read_no_tag_id(self):
        """ Test that no_tag_id field evaluates to False
        """
        self.assertFalse(self.test_record_1.search_no_tag_id)
        self.assertFalse(self.test_record_2.search_no_tag_id)
        self.assertFalse(self.test_record_1.search_tag_id)
        self.assertFalse(self.test_record_2.search_tag_id)

    def test_95_search_no_tag_id(self):
        """ Test that _search_no_tag_id method works fine
        """
        recs = self.test_record_1 | self.test_record_2

        self.test_record_1.add_tag(code='tc3')

        # normal search
        res = self.env['generic.tag.test.model'].search(
            [('id', 'in', recs.ids),
             ('search_no_tag_id.code', '=', 'tc3')])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], self.test_record_2)

        # search by string
        res = self.env['generic.tag.test.model'].search(
            [('id', 'in', recs.ids),
             ('search_no_tag_id', '=', 'tc3')])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], self.test_record_2)

        # search by int
        res = self.env['generic.tag.test.model'].search(
            [('id', 'in', recs.ids),
             ('search_no_tag_id', '=', self.test_tag_3.id)])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], self.test_record_2)

    def test_96_search_tag_id(self):
        """ Test that _search_no_tag_id method works fine
        """
        recs = self.test_record_1 | self.test_record_2

        self.test_record_1.add_tag(code='tc3')

        # normal search
        res = self.env['generic.tag.test.model'].search(
            [('id', 'in', recs.ids),
             ('search_tag_id.code', '=', 'tc3')])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], self.test_record_1)

        # search by string
        res = self.env['generic.tag.test.model'].search(
            [('id', 'in', recs.ids),
             ('search_tag_id', '=', 'tc3')])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], self.test_record_1)

        # search by int
        res = self.env['generic.tag.test.model'].search(
            [('id', 'in', recs.ids),
             ('search_tag_id', '=', self.test_tag_3.id)])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], self.test_record_1)

    def test_97_get_default_model(self):
        """ Test that _get_default_model_id method works fine
        """
        tag = self.env['generic.tag'].with_context(
            default_model='generic.tag.test.model'
        ).create({
            'name': 'Test',
            'code': 'test',
        })
        self.assertEqual(tag.model_id.model, 'generic.tag.test.model')
        self.assertEqual(tag.model_id.id, self.test_model.id)

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['generic.tag'].with_context(
                default_model=False
            ).create({
                'name': 'Test 2',
                'code': 'test_2',
            })

    def test_100_wizard(self):
        record = self.env['generic.tag.test.model'].create({
            'name': 'Test',
        })
        tag = self.env['generic.tag'].with_context(
            default_model='generic.tag.test.model'
        ).create({
            'name': 'Test',
            'code': 'test',
        })

        self.assertFalse(record.tag_ids)
        self.env['generic.tag.wizard.manage.tags'].with_context(
            manage_tags_model='generic.tag.test.model',
            manage_tags_object_ids=record.ids,
        ).create({
            'action': 'set',
            'tag_ids': [(6, 0, tag.ids)],
        }).do_apply()
        self.assertEqual(record.tag_ids, tag)

        self.env['generic.tag.wizard.manage.tags'].with_context(
            manage_tags_model='generic.tag.test.model',
            manage_tags_object_ids=record.ids,
        ).create({
            'action': 'remove',
            'tag_ids': [(6, 0, tag.ids)],
        }).do_apply()
        self.assertFalse(record.tag_ids)

        self.env['generic.tag.wizard.manage.tags'].with_context(
            manage_tags_model='generic.tag.test.model',
            manage_tags_object_ids=record.ids,
        ).create({
            'action': 'add',
            'tag_ids': [(6, 0, tag.ids)],
        }).do_apply()
        self.assertEqual(record.tag_ids, tag)

    def test_name_get(self):
        self.assertEqual(
            self.test_tag_1.read(['display_name'])[0]['display_name'],
            'Test Category 1 / TC1')

    def test_name_get_context_switch(self):
        self.assertEqual(
            self.test_tag_1.with_context(
                _use_standart_name_get_=True
            ).read(['display_name'])[0]['display_name'],
            'TC1')
