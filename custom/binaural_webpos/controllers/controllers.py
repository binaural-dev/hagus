# -*- coding: utf-8 -*-
# from odoo import http


# class BinauralWebpos(http.Controller):
#     @http.route('/binaural_webpos/binaural_webpos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/binaural_webpos/binaural_webpos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('binaural_webpos.listing', {
#             'root': '/binaural_webpos/binaural_webpos',
#             'objects': http.request.env['binaural_webpos.binaural_webpos'].search([]),
#         })

#     @http.route('/binaural_webpos/binaural_webpos/objects/<model("binaural_webpos.binaural_webpos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('binaural_webpos.object', {
#             'object': obj
#         })
