from diff_match_patch.diff_match_patch import diff_match_patch
from flask import request
from flask_jwt_extended import get_current_user

from server.common.database import db
from server.common.database.category import Category as CategoryModel
from server.common.database.change import Change as ChangeModel
from server.common.database.page import Page as PageModel
from server.common.rest import Resource
from server.common.schema import CategorySchema, PageSchema
from server.common.util import ServerError, RequestError, params, tag, marshal_with, use_kwargs, CacheDict, jwt_required


def cache_content(page: PageModel):
    content = ''
    for diffs in page.content:
        patches = diff_maker.patch_make(content, diffs.data)
        content, _ = diff_maker.patch_apply(patches, content)
    return content


def validate_cache(key, content, cache_version, page_version=None):
    if not page_version:
        return False
    return page_version <= cache_version


content_cache = CacheDict(cache_content, validate_cache)
diff_maker = diff_match_patch()


@tag('content')
class Categories(Resource):

    @tag('category')
    @marshal_with(CategorySchema(many=True), code=200)
    def get(self):
        """
        ## Get all categories
        """
        return CategoryModel.query.all()

    @tag('category')
    @jwt_required
    @use_kwargs(CategorySchema, required=True)
    @marshal_with(CategorySchema, code=201)
    def post(self, **kwargs):
        """
        ## Create a category

        ***Requires Authentication***
        """
        category = CategoryModel(**kwargs)
        try:
            db.session.add(category)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return category, 201


@tag('content')
@params(category_id='The id of the category')
class Category(Resource):

    @tag('category')
    @marshal_with(CategorySchema, code=200)
    def get(self, category_id):
        """
        ## Get the category (category_id)
        """
        return CategoryModel.query.get_or_404(category_id)

    @tag('category')
    @jwt_required
    @use_kwargs(CategorySchema(partial=True))
    @marshal_with(CategorySchema, code=200)
    @marshal_with(CategorySchema, code=201)
    def put(self, category_id, **kwargs):
        """
        ## Edit the category (category_id)
        ***Requires Authentication***
        """
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

    @tag('category')
    @jwt_required
    @marshal_with(None, code=204)
    def delete(self, category_id):
        """
        ## Delete the category (category_id)

        ***Requires Authentication***
        """
        category = CategoryModel.query.get_or_404(category_id)
        try:
            db.session.delete(category)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return {}, 204

    @tag('page')
    @jwt_required
    @use_kwargs(PageSchema, required=True)
    @marshal_with(PageSchema, code=201)
    def post(self, **kwargs):
        """
        ## Create a page in the category (category_id)

        ***Requires Authentication***
        """
        page = PageModel(**kwargs)
        try:
            db.session.add(page)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return page, 201


@tag('content')
@params(category_id='The id of the category')
class Pages(Resource):

    @tag('page')
    @marshal_with(PageSchema(many=True), code=200)
    def get(self, category_id):
        """
        ## Get all pages for the category (category_id)
        """
        return CategoryModel.query.get_or_404(category_id).pages


@tag('content')
@params(category_id='The id of the category', page_id='The id of the page')
class Page(Resource):

    @tag('page')
    @marshal_with(PageSchema, code=200)
    def get(self, category_id, page_id):
        """
        ## Get the page located at (category_id, page_id)
        """
        return PageModel.query.get_or_404((category_id, page_id))

    @tag('page')
    @jwt_required
    @use_kwargs(PageSchema(partial=True), required=True)
    @marshal_with(PageSchema, code=200)
    @marshal_with(PageSchema, code=201)
    def put(self, category_id, page_id, **kwargs):
        """
        ## Edit the page located at (category_id, page_id) or create it if it doesn't exist

        ***Requires Authentication***
        """
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

    @tag('page')
    @jwt_required
    @marshal_with(None, code=204)
    def delete(self, category_id, page_id):
        """
        ## Delete the page located at (category_id, page_id)

        ***Requires Authentication***
        """
        page = PageModel.query.get_or_404((category_id, page_id))
        try:
            db.session.delete(page)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return {}, 204


@tag('content')
@params(category_id='The id of the category', page_id='The id of the page')
class PageContent(Resource):

    @marshal_with({'type': 'string', 'format': 'markdown'}, code=200, content_type='text/markdown', apply=False)
    def get(self, category_id, page_id):
        """
        ## Get the cached content of the page located at (category_id, page_id)
        """
        key = (category_id, page_id)
        page: PageModel = PageModel.query.get_or_404(key)
        if content_cache.should_cache(key, page_version=page.last_update):
            content_cache.cache(key, page)
        return content_cache.get(key, '')

    @jwt_required
    @marshal_with({'type': 'string', 'format': 'markdown'}, code=201, content_type='text/markdown', apply=False)
    def post(self, category_id, page_id):
        """
        ## Set the new content of the page located at (category_id, page_id)

        ***Requires Authentication***
        """
        key = (category_id, page_id)
        page: PageModel = PageModel.query.get_or_404(key)
        if content_cache.should_cache(key, page_version=page.last_update):
            content_cache.cache(key, page)
        old_content = content_cache.get((category_id, page_id), '')
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
        content_cache.cache(key, page)
        return new_content, 201
