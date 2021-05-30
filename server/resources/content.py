from typing import Tuple, List

from diff_match_patch.diff_match_patch import diff_match_patch
from flask import request

from server.common.database import db
from server.common.database.category import Category as CategoryModel
from server.common.database.change import Change as ChangeModel
from server.common.database.page import Page as PageModel
from server.common.rest import Resource
from server.common.schema import CategorySchema, PageSchema
from server.common.schema import ChangeSchema
from server.common.util import RequestError, params, tag, marshal_with, use_kwargs, CacheDict, \
    jwt_required, transactional, Transaction


def cache_content(page: PageModel, **kwargs) -> str:
    content = ''
    for diffs in page.content:
        patches = diff_maker.patch_make(content, diffs.data)
        content, _ = diff_maker.patch_apply(patches, content)
    return content


def validate_cache(cache_version, page: PageModel = None, **kwargs) -> bool:
    if not page.last_update:
        return False
    return page.last_update <= cache_version


content_cache = CacheDict[Tuple[str, str], str](cache_content, validate_cache)
diff_maker = diff_match_patch()

DeleteReturn = Tuple[dict, int]


@tag('content')
@params(category_id='The id of the category', page_id='The id of the page')
class PageContent(Resource):

    @marshal_with({'type': 'string', 'format': 'markdown'}, code=200, content_type='text/markdown', apply=False)
    def get(self, category_id: str, page_id: str) -> str:
        """
        ## Get the cached content of the page located at (category_id, page_id)
        """
        key = (category_id, page_id)
        page: PageModel = PageModel.query.get_or_404(key)
        return content_cache.get(key, page=page)

    @jwt_required()
    @marshal_with({'type': 'string', 'format': 'markdown'}, code=201, content_type='text/markdown', apply=False)
    @transactional(db.session)
    def put(self, category_id: str, page_id: str, _transaction: Transaction) -> Tuple[str, int]:
        """
        ## Set the new content of the page located at (category_id, page_id)
        ***Requires Authentication***
        """
        key = (category_id, page_id)
        page: PageModel = PageModel.query.get_or_404(key)

        new_content = request.data.decode('utf_8')
        if not new_content:
            raise RequestError('missing body')

        old_content = content_cache.get(key, page=page)

        diffs = diff_maker.diff_main(old_content or '', new_content)
        diff_maker.diff_cleanupEfficiency(diffs)
        change = ChangeModel(
            category=page.category,
            page=page.id,
            data=diffs
        )
        _transaction.session.add(change)
        content_cache.invalidate(key)
        return new_content, 201


@tag('content')
@params(category_id='The id of the category', page_id='The id of the page')
class Changes(Resource):

    @marshal_with(ChangeSchema, code=200)
    def get(self, category_id: str, page_id: str) -> List[ChangeModel]:
        """
        ## Get the changes made to this pages content
        """
        return ChangeModel.query\
            .filter(ChangeModel.category == category_id, ChangeModel.page == page_id)\
            .order_by(ChangeModel.created_at)\
            .all()

    @jwt_required()
    @marshal_with(None, code=204)
    @transactional(db.session)
    def delete(self, category_id: str, page_id: str, _transaction: Transaction) -> DeleteReturn:
        """
        ## Delete the last change made to this page
        """
        change = ChangeModel.query\
            .filter(ChangeModel.category == category_id, ChangeModel.page == page_id)\
            .order_by(ChangeModel.created_at)\
            .first_or_404()
        _transaction.session.delete(change)
        return {}, 204


@tag('content')
@params(category_id='The id of the category', page_id='The id of the page')
class Page(Resource):

    @marshal_with(PageSchema, code=200)
    def get(self, category_id: str, page_id: str) -> PageModel:
        """
        ## Get the page located at (category_id, page_id)
        """
        return PageModel.query.get_or_404((category_id, page_id))

    @jwt_required()
    @use_kwargs(PageSchema(partial=True), required=True)
    @marshal_with(PageSchema, code=200)
    @marshal_with(PageSchema, code=201)
    @transactional(db.session)
    def patch(self, category_id: str, page_id: str, _transaction: Transaction, **kwargs) -> PageModel:
        """
        ## Edit the page located at (category_id, page_id) or create it if it doesn't exist
        ***Requires Authentication***
        """
        page = PageModel.query.get_or_404((category_id, page_id))
        if 'category' in kwargs.keys():
            CategoryModel.query.get_or_404(kwargs['category'])
        for k, v in kwargs.items():
            setattr(page, k, v)
        return page

    @jwt_required()
    @use_kwargs(PageSchema, required=True)
    @marshal_with(PageSchema, code=200)
    @marshal_with(PageSchema, code=201)
    @transactional(db.session)
    def put(self, category_id: str, page_id: str, _transaction: Transaction, **kwargs) -> Tuple[PageModel, int]:
        """
        ## Edit the page located at (category_id, page_id) or create it if it doesn't exist
        ***Requires Authentication***
        """
        page = PageModel.query.get((category_id, page_id))
        if page:
            if 'category' in kwargs.keys():
                CategoryModel.query.get_or_404(kwargs['category'])
            for k, v in kwargs.items():
                setattr(page, k, v)
            return page, 200
        else:
            if 'category' in kwargs.keys():
                CategoryModel.query.get_or_404(kwargs['category'])
            page = PageModel(**kwargs)
            _transaction.session.add(page)
            return page, 201

    @jwt_required()
    @marshal_with(None, code=204)
    @transactional(db.session)
    def delete(self, category_id: str, page_id: str, _transaction: Transaction) -> DeleteReturn:
        """
        ## Delete the page located at (category_id, page_id)
        ***Requires Authentication***
        """
        page = PageModel.query.get_or_404((category_id, page_id))
        _transaction.session.delete(page)
        return {}, 204


@tag('content')
@params(category_id='The id of the category')
class Pages(Resource):
    __child__ = Page

    @marshal_with(PageSchema(many=True), code=200)
    def get(self, category_id: str) -> List[PageModel]:
        """
        ## Get all pages for the category (category_id)
        """
        return CategoryModel.query.get_or_404(category_id).pages

    @jwt_required()
    @use_kwargs(PageSchema, required=True)
    @marshal_with(PageSchema, code=201)
    @transactional(db.session)
    def post(self, _transaction: Transaction, **kwargs) -> Tuple[PageModel, int]:
        """
        ## Create a page in the category (category_id)
        ***Requires Authentication***
        """
        kwargs.pop('category_id')
        page = PageModel(**kwargs)
        _transaction.session.add(page)
        return page, 201


@tag('content')
@params(category_id='The id of the category')
class Category(Resource):
    __child__ = Pages

    @marshal_with(CategorySchema, code=200)
    def get(self, category_id: str) -> CategoryModel:
        """
        ## Get the category (category_id)
        """
        return CategoryModel.query.get_or_404(category_id)

    @jwt_required()
    @use_kwargs(CategorySchema(partial=True))
    @marshal_with(CategorySchema, code=200)
    @transactional(db.session)
    def patch(self, category_id: str, _transaction: Transaction, **kwargs) -> CategoryModel:
        """
        ## Edit the category (category_id)
        ***Requires Authentication***
        """
        category = CategoryModel.query.get_or_404(category_id)
        for k, v in kwargs.items():
            setattr(category, k, v)
        return category

    @jwt_required()
    @use_kwargs(CategorySchema)
    @marshal_with(CategorySchema, code=200)
    @marshal_with(CategorySchema, code=201)
    @transactional(db.session)
    def put(self, category_id: str, _transaction: Transaction, **kwargs) -> Tuple[CategoryModel, int]:
        """
        ## Edit the category (category_id)
        ***Requires Authentication***
        """
        category = CategoryModel.query.get(category_id)
        if category:
            for k, v in kwargs.items():
                setattr(category, k, v)
            return category, 200
        else:
            category = CategoryModel(**kwargs)
            _transaction.session.add(category)
            return category, 201

    @jwt_required()
    @marshal_with(None, code=204)
    @transactional(db.session)
    def delete(self, category_id: str, _transaction: Transaction) -> DeleteReturn:
        """
        ## Delete the category (category_id)
        ***Requires Authentication***
        """
        category = CategoryModel.query.get_or_404(category_id)
        _transaction.session.delete(category)
        return {}, 204


@tag('content')
class Categories(Resource):
    __child__ = Category

    @marshal_with(CategorySchema(many=True), code=200)
    def get(self) -> List[CategoryModel]:
        """
        ## Get all categories
        """
        return CategoryModel.query.all()

    @jwt_required()
    @use_kwargs(CategorySchema, required=True)
    @marshal_with(CategorySchema, code=201)
    @transactional(db.session)
    def post(self, _transaction: Transaction, **kwargs) -> Tuple[CategoryModel, int]:
        """
        ## Create a category
        ***Requires Authentication***
        """
        category = CategoryModel(**kwargs)
        _transaction.session.add(category)
        return category, 201
