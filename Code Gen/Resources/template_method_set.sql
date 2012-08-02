create or replace function <schema>.method_<class>_set(
    * list ,
	-- ID
    * expand:focus_attr
	p_<focus_attr>|t|<class>.<focus_attr>%type,
    ** expand
	-- Args
    * expand:modify_attr
	p_new_<modify_attr>|t|<class>.<modify_attr>%type default NULL,
    ** expand
    ** list
) returns void as 
$$
--
-- Method: Sets <Class> attributes.
-- ++ -
-- ==
--
-- Copyright <year> Model Integration, LLC
-- Developer: Leon Starr / leon_starr@modelint.com
-- 
-- This file is part of the miUML metamodel library.
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU Lesser General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.  The license text should be viewable at
-- http://www.gnu.org/licenses/
--
declare
	self	        <class>%rowtype;

    -- Update strings
    * expand:modify_attr
	u_new_<modify_attr>|t|text := NULL;
    ** expand
    no_set_values boolean := true;

begin
    * expand:modify_attr, modify_ui_type
    if p_new_<modify_attr> is not NULL then
    * conditional:'<modify_ui_type>' == 'text'
        u_new_<modify_attr> := '<modify_attr> = ' || quote_nullable( p_new_<modify_attr> );
    ** conditional
    * conditional:'<modify_ui_type>' != 'text'
        u_new_<modify_attr> := '<modify_attr> = ' || p_new_<modify_attr>;
    ** conditional
        no_set_values = false;
    end if;

    ** expand
    if no_set_values then
        raise exception 'UI: No values to set.';
    end if;

    -- ++ Pre-update code inserted here
    -- ==

    begin
        -- Apply any settings in a single UPDATE
        execute 'update <class> set '
            -- Concats only those values that are non-NULL
            || concat_ws( ', ',
                * list ,
                * expand:modify_attr
                u_new_<modify_attr>,
                ** expand
                ** list
            ) || ' where ' || concat_ws( ' and ',
                * list ,
                * expand:focus_attr
                '<focus_attr> = ' || quote_nullable( p_<focus_attr> ),
                ** expand
                ** list
            ) || ' returning *' into strict self;
	exception
		when no_data_found then raise exception
            'UI: <Class> [%] does not exist.',
                concat_ws( ', ',
                * list ,
                * expand:focus_attr
                    '<focus_attr>:' || p_<focus_attr>,
                ** expand
                ** list
                );
    end;

    -- ++ Post-update code inserted here
    -- ==
end
$$
language plpgsql;
