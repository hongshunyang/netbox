from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from netaddr import IPNetwork

from dcim.models import DeviceRole
from extras.scripts import *


class ScriptVariablesTest(TestCase):

    def test_stringvar(self):

        class TestScript(Script):

            var1 = StringVar(
                min_length=3,
                max_length=3,
                regex=r'[a-z]+'
            )

        # Validate min_length enforcement
        data = {'var1': 'xx'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate max_length enforcement
        data = {'var1': 'xxxx'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate regex enforcement
        data = {'var1': 'ABC'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate valid data
        data = {'var1': 'abc'}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], data['var1'])

    def test_textvar(self):

        class TestScript(Script):

            var1 = TextVar()

        # Validate valid data
        data = {'var1': 'This is a test string'}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], data['var1'])

    def test_integervar(self):

        class TestScript(Script):

            var1 = IntegerVar(
                min_value=5,
                max_value=10
            )

        # Validate min_value enforcement
        data = {'var1': 4}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate max_value enforcement
        data = {'var1': 11}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate valid data
        data = {'var1': 7}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], data['var1'])

    def test_booleanvar(self):

        class TestScript(Script):

            var1 = BooleanVar()

        # Validate True
        data = {'var1': True}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], True)

        # Validate False
        data = {'var1': False}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], False)

    def test_choicevar(self):

        CHOICES = (
            ('ff0000', 'Red'),
            ('00ff00', 'Green'),
            ('0000ff', 'Blue')
        )

        class TestScript(Script):

            var1 = ChoiceVar(
                choices=CHOICES
            )

        # Validate valid choice
        data = {'var1': CHOICES[0][0]}
        form = TestScript().as_form(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], CHOICES[0][0])

        # Validate invalid choices
        data = {'var1': 'taupe'}
        form = TestScript().as_form(data)
        self.assertFalse(form.is_valid())

    def test_objectvar(self):

        class TestScript(Script):

            var1 = ObjectVar(
                queryset=DeviceRole.objects.all()
            )

        # Populate some objects
        for i in range(1, 6):
            DeviceRole(
                name='Device Role {}'.format(i),
                slug='device-role-{}'.format(i)
            ).save()

        # Validate valid data
        data = {'var1': DeviceRole.objects.first().pk}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'].pk, data['var1'])

    def test_multiobjectvar(self):

        class TestScript(Script):

            var1 = MultiObjectVar(
                queryset=DeviceRole.objects.all()
            )

        # Populate some objects
        for i in range(1, 6):
            DeviceRole(
                name='Device Role {}'.format(i),
                slug='device-role-{}'.format(i)
            ).save()

        # Validate valid data
        data = {'var1': [role.pk for role in DeviceRole.objects.all()[:3]]}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'][0].pk, data['var1'][0])
        self.assertEqual(form.cleaned_data['var1'][1].pk, data['var1'][1])
        self.assertEqual(form.cleaned_data['var1'][2].pk, data['var1'][2])

    def test_filevar(self):

        class TestScript(Script):

            var1 = FileVar()

        # Dummy file
        testfile = SimpleUploadedFile(
            name='test_file.txt',
            content=b'This is a dummy file for testing'
        )

        # Validate valid data
        file_data = {'var1': testfile}
        form = TestScript().as_form(None, file_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], testfile)

    def test_ipnetworkvar(self):

        class TestScript(Script):

            var1 = IPNetworkVar()

        # Validate IP network enforcement
        data = {'var1': '1.2.3'}
        form = TestScript().as_form(data, None)
        self.assertFalse(form.is_valid())
        self.assertIn('var1', form.errors)

        # Validate valid data
        data = {'var1': '192.0.2.0/24'}
        form = TestScript().as_form(data, None)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['var1'], IPNetwork(data['var1']))
