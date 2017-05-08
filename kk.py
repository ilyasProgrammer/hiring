import odoo

ODOO_CONF = '/pd/hiring/odoo.conf'
UID = odoo.SUPERUSER_ID


def source(env,env2):
    mod = 'utm.source'
    recs = env[mod].search([])
    l = len(recs)
    i = 1
    for r in recs:
        f = env2[mod].search([('id', '=', r.id)])
        if not f:
            p = env2[mod].create({'name': r.name})
            print "# NEW", p.name, i, l
        else:
            print ' GOT', r.name, i, l
        i += 1

def appl(env,env2):
    mod = 'hr.applicant'
    recs = env[mod].search([])
    l = len(recs)
    i = 1
    for r in recs:
        f = env2[mod].search([('id', '=', r.id)])
        if not f:
            p = env2[mod].create({'name': r.name,
                                  'datas_fname': r.datas_fname,
                                  'datas': r.datas,
                                  'res_model': r.res_model,
                                  'type': r.type,
                                  'res_id': r.res_id})
            print "# NEW", p.name, i, l
        else:
            print ' GOT', r.name, i, l
        i += 1

def part(env,env2):
    recs = env['res.partner'].search([])
    l = len(recs)
    i = 1
    for r in recs:
        f = env2['res.partner'].search([('id', '=', r.id)])
        if not f:
            found_country = env2['res.country'].search([('name', '=', r.name)], limit=1)
            p = env2['res.partner'].create({'name': r.name,
                                            'country_id': found_country.id if found_country else None,
                                            'city': r.city,
                                            'email': r.email,
                                            'gender': r.gender,  # - Gender / field from OCA partner_contact_gender
                                            'street': r.street})
            print "# NEW", p.name, i, l
        else:
            print ' GOT', r.name, i, l
        i += 1


odoo.tools.config.parse_config(['--config=%s' % ODOO_CONF])
with odoo.api.Environment.manage():
    registry = odoo.modules.registry.RegistryManager.get('bb')
    registry2 = odoo.modules.registry.RegistryManager.get('vdold')
    with registry.cursor() as cr:
        ctx = odoo.api.Environment(cr, UID, {})['res.users'].context_get()
        env = odoo.api.Environment(cr, UID, ctx)
        with registry2.cursor() as cr:
            ctx2 = odoo.api.Environment(cr, UID, {})['res.users'].context_get()
            env2 = odoo.api.Environment(cr, UID, ctx)
            # part(env,env2)
            # source(env,env2)
            appl(env,env2)
