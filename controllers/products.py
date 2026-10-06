from helpers.utils import safe_int
import math
from flask import Blueprint, render_template, request
from models.product import ProductModel

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
def home():
    brands = ProductModel.get_all_brands()
    latest_products = ProductModel.get_latest(8)
    return render_template('home/index.html', page_title='Trang chủ', brands=brands, latest_products=latest_products)

@products_bp.route('/products')
def index():
    filters = {
        'keyword': request.args.get('keyword', ''),
        'brand': request.args.get('brand', ''),
        'cpu': request.args.get('cpu', ''),
        'ram': request.args.get('ram', ''),
        'price_min': request.args.get('price_min', ''),
        'price_max': request.args.get('price_max', ''),
        'sort': request.args.get('sort', 'newest')
    }
    
    current_page = safe_int(request.args.get('page', 1))
    per_page = 9
    
    all_products = ProductModel.get_all(filters)
    total = len(all_products)
    total_pages = math.ceil(total / per_page)
    
    # Phân trang
    start = (current_page - 1) * per_page
    end = start + per_page
    products = all_products[start:end]
    
    brands = ProductModel.get_all_brands()
    
    return render_template(
        'products/index.html', 
        page_title='Sản phẩm',
        products=products,
        brands=brands,
        filters=filters,
        total=total,
        current_page=current_page,
        total_pages=total_pages
    )

@products_bp.route('/products/detail/<int:product_id>')
def detail(product_id):
    product = ProductModel.find_by_id(product_id)
    if not product or not product['is_active']:
        return "Sản phẩm không tồn tại", 404
        
    related_products = ProductModel.get_related(product['brand'], product['id'])
    
    return render_template(
        'products/detail.html', 
        page_title=product['name'],
        product=product,
        related_products=related_products
    )
