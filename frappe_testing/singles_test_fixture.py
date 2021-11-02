import frappe

from .test_fixture import TestFixture


class SinglesTestFixture(TestFixture):
    """
    Extends the Fixture Manager for Single doctypes
    Just as responsible; will backup the Single doc before testing, and restore afterwards

    :param `reset_before_test`: If set, all fields on the doc will be reset to default before tests.
    `True` by default.
    :param `singles_copy`: Contains the copy of the doc fields and values
    """

    def __init__(self):
        self.reset_before_test = True
        self.singles_copy = {}
        super().__init__()

    def setUp(self, skip_fixtures=False, skip_dependencies=False):
        """
        Overrides TestFixture setUp. Will backup the existing doc fields,
        and set them to their default values if `reset_before_test` is `True`.
        Then will setup the fixture fields.

        Args:
            `skip_fixtures` (bool): Skip the fixture creation
            `skip_dependencies` (bool): Skip the dependency creation

        Returns:
            `None`
        """

        if not self.DEFAULT_DOCTYPE:
            raise Exception("DEFAULT_DOCTYPE is not defined")

        if not frappe.get_meta(self.DEFAULT_DOCTYPE).get("issingle"):
            raise Exception("Doctype is not Single")

        if frappe.session.user != self.TESTER_USER:
            frappe.set_user(self.TESTER_USER)

        if self.isSetUp():
            self.duplicate = True
            og: TestFixture = self.get_locals_obj()[self.__class__.__name__]
            self.fixtures = getattr(og, "fixtures", frappe._dict())
            self._dependent_fixture_instances = getattr(
                og, "_dependent_fixture_instances", [])
            return

        # make a copy of ALL the fields
        self.singles_copy = frappe.get_doc(self.DEFAULT_DOCTYPE).as_dict()

        # reset the single doc to a 'default' state
        if self.reset_before_test:
            for field in self.singles_copy.keys():
                if not (field == "doctype" or field == "name"):

                    field_default = None
                    field_meta = frappe.get_meta(self.DEFAULT_DOCTYPE).get_field(field)
                    if field_meta:
                        field_default = field_meta.default

                    frappe.db.set_value(self.DEFAULT_DOCTYPE, self.DEFAULT_DOCTYPE,
                                        field, field_default)

        frappe.db.commit()

        if not skip_dependencies:
            self.make_dependencies()

        if not skip_fixtures:
            self.make_fixtures()
        self.get_locals_obj()[self.__class__.__name__] = self

    def make_fixtures(self):
        """
        Please override this function to change the value of any fields on the single doc.
        These changes will exist for the duration of the test, and will be reset after.
        """

    def tearDown(self):
        """
        Reset doc to it's pre-test state and destroy any dependencies
        """

        if frappe.session.user != self.TESTER_USER:
            frappe.set_user(self.TESTER_USER)

        if self.duplicate:
            self.fixtures = frappe._dict()
            self._dependent_fixture_instances = []
            self.duplicate = False
            return

        doctype = self.singles_copy["doctype"]
        del self.singles_copy["doctype"]

        name = self.singles_copy["name"]
        del self.singles_copy["name"]

        frappe.db.set_value(
            doctype,
            name,
            self.singles_copy,
            update_modified=False,
        )

        frappe.db.commit()

        self.destroy_dependencies()
        self.get_locals_obj()[self.__class__.__name__] = None
