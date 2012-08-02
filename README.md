mi_postgresql_function_code_generator
=====================================

Generates pl/pgsql code from miUML metamodel data.  Used to generate some of the miUML editor code!

There are two subdirectories, each of which is a little sub-project.

Code Gen
--
Code Gen reads the model.mi metamodel snippet file in its Resources directory
and fills in the templates, also in the Resources directory.

For now, only the attribute setter functions are generated.  These are named:

    UI_set_<metaclass>.sql
    method_<metaclass>_set.sql

And at this point only those in the Domain subsystem and some in the
Class subsystem have been gen'd.

As you will see, the model.mi file currently contains a small portion of the
overall miUML metamodel.  (Just what is needed for attribute setter generation
and only with data for the Domain Subsystem and a tiny slice of the Class Subsystem).

Knit
--
The templates provide sections where hand written (non-gen'd) code may be inserted.
After the code gen pass, Knit graps the hand code and comment snippets and 'knits them in'
to the correct locations.  If you look in the miUML plpgsql directories you will find
a Hand and Comment subdirectory in the Domain and Class subsystems.  That's where the
hand coded snippets are placed.
