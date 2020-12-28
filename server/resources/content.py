from diff_match_patch.diff_match_patch import diff_match_patch
from flask import request, make_response
from flask_jwt_extended import jwt_required, get_current_user

from common.util import ServerError, RequestError
from resources.ref import api
from server.common.database import db
from server.common.database.category import Category as CategoryModel
from server.common.database.change import Change as ChangeModel
from server.common.database.page import Page as PageModel
from server.common.rest import Resource


class CacheDict(dict):
    def invalidate(self, key):
        self.pop(key)

    def cache(self, key, value):
        self[key] = value


content_cache = CacheDict()
diff_maker = diff_match_patch()

ns = api.get_ns('content')
category_model = ns.model('Category', CategoryModel.__marshmallow__())
category_partial_model = ns.model('Category(partial)', CategoryModel.__marshmallow__(partial=True))
page_model = ns.model('Page', PageModel.__marshmallow__())
page_partial_model = ns.model('Page(partial)', PageModel.__marshmallow__(partial=True))


class Categories(Resource):
    method_decorators = {'post': [jwt_required]}

    @ns.marshal_with(CategoryModel.__marshmallow__, code=200, as_list=True)
    def get(self):
        return CategoryModel.query.all()

    @ns.expect(CategoryModel.__marshmallow__)
    @ns.marshal_with(category_model, code=201)
    def post(self, **kwargs):
        category = CategoryModel(**kwargs)
        try:
            db.session.add(category)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return category, 201


class Category(Resource):
    method_decorators = {'delete': [jwt_required],
                         'put': [jwt_required],
                         'post': [jwt_required]}

    @ns.marshal_with(category_model, code=200)
    def get(self, category_id):
        return CategoryModel.query.get_or_404(category_id)

    @ns.expect(category_partial_model)
    @ns.marshal_with(category_model, code=200)
    @ns.marshal_with(category_model, code=201)
    def put(self, category_id, **kwargs):
        category = CategoryModel.query.get(category_id)
        if not category:
            category = CategoryModel(**kwargs)
            try:
                db.session.add(category)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise ServerError(e)
            return category, 201
        else:
            try:
                for key, value in kwargs.items():
                    setattr(category, key, value)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise ServerError(e)
        return category

    @ns.marshal_with(None, code=204)
    def delete(self, category_id):
        category = CategoryModel.query.get_or_404(category_id)
        try:
            db.session.delete(category)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return {}, 204

    @ns.expect(page_model)
    @ns.marshal_with(page_model, code=201)
    def post(self, **kwargs):
        page = PageModel(**kwargs)
        try:
            db.session.add(page)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return page, 201


class Pages(Resource):

    @ns.marshal_with(page_model, code=200, as_list=True)
    def get(self, category_id):
        return CategoryModel.query.get_or_404(category_id).pages


class Page(Resource):
    method_decorators = {'delete': [jwt_required],
                         'put': [jwt_required]}

    @ns.marshal_with(page_model, code=200)
    def get(self, category_id, page_id):
        return PageModel.query.get_or_404((category_id, page_id))

    @ns.expect(page_partial_model)
    @ns.marshal_with(page_model, code=200)
    @ns.marshal_with(page_model, code=201)
    def put(self, category_id, page_id, **kwargs):
        page = PageModel.query.get((category_id, page_id))
        if not page:
            page = PageModel(**kwargs)
            try:
                db.session.add(page)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise ServerError(e)
            return page, 201
        else:
            try:
                for key, value in kwargs.items():
                    if key == 'category':
                        category = CategoryModel.query.get_or_404(kwargs['category'])
                        page.category = category.id
                    else:
                        setattr(page, key, value)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise ServerError(e)
        return page

    @ns.marshal_with(None, code=204)
    def delete(self, category_id, page_id):
        page = PageModel.query.get_or_404((category_id, page_id))
        try:
            db.session.delete(page)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return {}, 204


class PageContent(Resource):
    method_decorators = {'post': [jwt_required]}

    @ns.produces('text/markdown')
    def get(self, category_id, page_id):
        page: PageModel = PageModel.query.get_or_404((category_id, page_id))
        if (category_id, page_id) not in content_cache:
            content = ''
            for diffs in page.content:
                patches = diff_maker.patch_make(content, diffs.data)
                content, _ = diff_maker.patch_apply(patches, content)
            content_cache.cache((category_id, page_id), content)
        resp = make_response(content_cache[(category_id, page_id)] or '')
        resp.headers['Content-Type'] = 'text/markdown'
        return resp

    @ns.marshal_with(None, code=201)
    def post(self, category_id, page_id):
        page: PageModel = PageModel.query.get_or_404((category_id, page_id))
        if (category_id, page_id) not in content_cache:
            content = ''
            for diffs in page.content:
                patches = diff_maker.patch_make(content, diffs.data)
                content, _ = diff_maker.patch_apply(patches, content)
            content_cache.cache((category_id, page_id), content)
        old_content = content_cache.get((category_id, page_id)) or ''
        new_content = request.data.decode('utf_8')
        if not new_content:
            raise RequestError('missing body')

        diffs = diff_maker.diff_main(old_content or '', new_content)
        diff_maker.diff_cleanupEfficiency(diffs)
        author = get_current_user()
        change = ChangeModel(
            category=page.category,
            page=page.id,
            data=diffs,
            author=author.id
        )
        try:
            db.session.add(change)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return {}, 201
