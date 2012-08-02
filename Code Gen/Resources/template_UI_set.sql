create or replace function <schema>.UI_set_<class>(
    * list ,
	-- Focus
    * expand:focus_attr, focus_type, focus_default
	p_<focus_attr>|t|mi.<focus_type><focus_default>,
    ** expand
	-- Modify
    * expand:modify_attr, modify_type, modify_ui_type, modify_default
    p_new_<modify_attr>|t|<modify_ui_type>|t|default <modify_default>,    -- ::mi.<modify_type>
    ** expand
    ** list
) returns void as 
$$
--
-- UI Bridge: Sets <Class> attributes
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
    * expand:modify_attr
	v_new_<modify_attr>|t|<class>.<modify_attr>%type;
    ** expand
begin
	-- Validate attributes
    * expand:modify_attr, modify_type, modify_ui_type
	begin
    * conditional:'<modify_ui_type>'!='text'
		v_new_<modify_attr> := p_new_<modify_attr>;
    ** conditional
    * conditional:'<modify_ui_type>'=='text'
		v_new_<modify_attr> := trim( p_new_<modify_attr> );
    ** conditional
	exception
		when check_violation then
			raise exception 'UI: New <modify_attr> [%] violates type: <modify_type>.',
            p_new_<modify_attr>;
	end;
    ** expand

	-- Call app
	perform method_<class>_set(
        * list:,
        * expand:focus_attr
        p_<focus_attr> := p_<focus_attr>,
        ** expand
        * expand:modify_attr
        p_new_<modify_attr> := v_new_<modify_attr>,
        ** expand
        ** list
    );
end
$$
language plpgsql;
