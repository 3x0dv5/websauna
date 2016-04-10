=================
Introducing admin
=================

Websauna provides automated :ref:`admin` interface allowing you easily edit your modelled data through automatically generated web interface.

Manually coding an admin site, also known as back office, for your team and clients can be tedious work that doesn’t require much creativity or contain anything novel or value adding. Websauna automates the creation of admin by automatically generating data browsers and editors your models.

Unlike other frameworks, Websauna sites can have multiple admin interfaces. For example, one could have super admin for the developers and limited admin interfaces for customers or whitelabel owners to manage their own respective users.

Admin architecture
==================

Websauna aims to be flexible; it does not enforce any particular URL pattern onen has to follow for admin. On the contrary, the admin is based on :term:`traversal`. Any admin endpoint can declare its own hierarchy of children and grandchildren paths.

* Each model needs a corresponding admin resource of class :py:class:`websauna.system.admin.ModelAdmin`. This resource is responsible for listing and adding new items. (Actions on all items)

* Each model instance (object, a row in SQL database) needs a corresponding admin resource of class :py:class:`websauna.system.admin.ModelAdmin.Resource`. This is a nested class inside the parent ModelAdmin. This resource is responsible for show, edit and delete actions. (Actions on one item)

Including models in the admin
=============================

Models must be explicitly registered in the admin interface. For each model appearing in the admin interface a corresponding :term:`resource` class must be created in ``admins.py`` file. Resource reflects the :term:`traversal` URL part and associated :term:`views <view>`.

Edit ``admins.py`` file of ``myapp.py`` and add the following code:

.. code-block:: python

    """Admin resource registrations for your app."""

    from websauna.system.admin.modeladmin import model_admin
    from websauna.system.admin.modeladmin import ModelAdmin

    # Import our models
    from . import models


    @model_admin(traverse_id="question")
    class QuestionAdmin(ModelAdmin):
        """Admin resource for question model.

        This class declares a resource for question model admin root folder with listing and add views.
        """

        #: Label as shown in admin
        title = "Questions"

        #: Used in admin listings etc. user visible messages
        #: TODO: This mechanism will be phased out in the future versions with gettext or similar replacement for languages that have plulars one, two, many
        singular_name = "question"
        plural_name = "questions"

        #: Which models this model admin controls
        model = models.Question

        class Resource(ModelAdmin.Resource):
            """Declare resource for each individual question.

            View, edit and delete views are registered against this resource.
            """

            def get_title(self):
                """What we show as the item title in question listing."""
                return self.get_object().question_text


    @model_admin(traverse_id="choice")
    class ChoiceAdmin(ModelAdmin):
        """Admin resource for choice model."""

        title = "Choices"

        singular_name = "choice"
        plural_name = "choices"
        model = models.Choice

        class Resource(ModelAdmin.Resource):

            def get_title(self):
                return self.get_object().choice_text


The process breakdown of adding model admins is

* Create ``admin.py`` file where you place your model admins

* Create a :py:class:`websauna.system.admin.modeladmin.ModelAdmin` subclass for each model you wish to show in admin interface

* Decorate this class with :py:class:`websauna.system.admin.modeladmin.model_admin` class decorator

* In the ``__init__.py`` of your application import your admin module and run ``config.scan(admin)`` for it. The app :ref:`scaffold` should include this behavior in the default generated ``__init__.py``

In the example, we declare two classes per each model. Here is a breakdown for *Question* model.

* ``@model_admin(traverse_id="question")`` tells that this model admin is registered under ``/admin/question`` URL.

* Class ``myapp.admins.QuestionAdmin`` is a :term:`resource` for question model admin root itself. This resource provides add question and list questions views for all questions in the database.

* Class ``myapp.admins.QuestionAdmin.Resource`` is a :term:`resource` for individual questions. It maps :term:`SQLAlchemy` model instance to ``/admin/question/xxxx`` URLs, so that each model instance gets its own user friendly URL path. This resource provides view question, edit question and delete question views for individual question instances.

Visiting admin
==============

Start the web server or let it reload itself. Now you should see *Question* and *Choice* appear in the admin interface.

.. image:: images/question_admin.png
    :width: 640px

For example, you can edit the questions.

.. image:: images/edit_question.png
    :width: 640px

You can add new choices. For the choice you can choose the appropriate question from dropdown.

.. image:: images/add_choice.png
    :width: 640px

.. note ::

    TODO: Currently there is not possibility to add and edit question choices inline from the question page. This will change in the future versions.

Further information
===================

Read :ref:`admin` documentation. Read :ref:`CRUD` documentation.

`More examples how to register models to your admin interface in websauna.wallet package <https://github.com/websauna/websauna.wallet/blob/master/websauna/wallet/admins.py>`_.

Some examples how to customize and override views in admin interfaces

* :py:mod:`websauna.system.user.admin` module

* :py:mod:`websauna.system.user.adminviews` module

* `websauna.wallet package <https://github.com/websauna/websauna.wallet/blob/master/websauna/wallet/adminviews.py>`_

