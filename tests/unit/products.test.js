const request = require('supertest');
const app = require('../../src/server');
const { User } = require('../../src/models/User');
const { Product } = require('../../src/models/Product');

describe('Product Endpoints', () => {
  let user;
  let adminUser;
  let userToken;
  let adminToken;

  beforeEach(async () => {
    // Create regular user
    user = new User({
      username: 'testuser',
      email: 'user@example.com',
      password: 'TestPass123!',
      firstName: 'Test',
      lastName: 'User'
    });
    await user.save();

    // Create admin user
    adminUser = new User({
      username: 'admin',
      email: 'admin@example.com',
      password: 'AdminPass123!',
      firstName: 'Admin',
      lastName: 'User',
      role: 'admin'
    });
    await adminUser.save();

    // Get auth tokens
    const userResponse = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'user@example.com',
        password: 'TestPass123!'
      });
    userToken = userResponse.body.data.accessToken;

    const adminResponse = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'admin@example.com',
        password: 'AdminPass123!'
      });
    adminToken = adminResponse.body.data.accessToken;
  });

  describe('POST /api/products', () => {
    it('should create a new product successfully', async () => {
      const productData = {
        name: 'Test Product',
        description: 'A test product',
        price: 99.99,
        category: 'Test Category',
        stock: 10,
        sku: 'TEST-001'
      };

      const response = await request(app)
        .post('/api/products')
        .set('Authorization', `Bearer ${userToken}`)
        .send(productData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('Product created successfully');
      expect(response.body.data.product).toBeDefined();
      expect(response.body.data.product.name).toBe(productData.name);
      expect(response.body.data.product.price).toBe(productData.price);

      // Verify product was created in database
      const product = await Product.findOne({ name: productData.name });
      expect(product).toBeTruthy();
      expect(product.createdBy.toString()).toBe(user._id.toString());
    });

    it('should return validation errors for invalid input', async () => {
      const invalidProduct = {
        name: '', // required field missing
        price: -10, // negative price
        stock: 'invalid' // not a number
      };

      const response = await request(app)
        .post('/api/products')
        .set('Authorization', `Bearer ${userToken}`)
        .send(invalidProduct)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toBe('Validation failed');
      expect(response.body.errors).toBeDefined();
    });

    it('should return error for duplicate SKU', async () => {
      const productData = {
        name: 'Test Product',
        description: 'A test product',
        price: 99.99,
        category: 'Test Category',
        stock: 10,
        sku: 'TEST-001'
      };

      // Create first product
      await request(app)
        .post('/api/products')
        .set('Authorization', `Bearer ${userToken}`)
        .send(productData)
        .expect(201);

      // Try to create second product with same SKU
      const response = await request(app)
        .post('/api/products')
        .set('Authorization', `Bearer ${userToken}`)
        .send({
          ...productData,
          name: 'Another Product'
        })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toBe('SKU already exists');
    });

    it('should return error for unauthenticated user', async () => {
      const productData = {
        name: 'Test Product',
        price: 99.99,
        category: 'Test Category'
      };

      const response = await request(app)
        .post('/api/products')
        .send(productData)
        .expect(401);

      expect(response.body.success).toBe(false);
    });
  });

  describe('GET /api/products', () => {
    beforeEach(async () => {
      // Create test products
      const products = [
        { name: 'Product 1', price: 10.99, category: 'Category A', stock: 5, sku: 'SKU001', createdBy: user._id, updatedBy: user._id },
        { name: 'Product 2', price: 20.99, category: 'Category B', stock: 10, sku: 'SKU002', createdBy: user._id, updatedBy: user._id },
        { name: 'Product 3', price: 30.99, category: 'Category A', stock: 15, sku: 'SKU003', createdBy: user._id, updatedBy: user._id }
      ];

      await Product.insertMany(products);
    });

    it('should get all products with pagination', async () => {
      const response = await request(app)
        .get('/api/products')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.products).toBeDefined();
      expect(response.body.data.pagination).toBeDefined();
      expect(response.body.data.products.length).toBe(3);
    });

    it('should filter products by category', async () => {
      const response = await request(app)
        .get('/api/products?category=Category A')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.products).toBeDefined();
      expect(response.body.data.products.length).toBe(2);
      expect(response.body.data.products.every(p => p.category === 'Category A')).toBe(true);
    });

    it('should search products by name', async () => {
      const response = await request(app)
        .get('/api/products?search=Product 1')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.products).toBeDefined();
      expect(response.body.data.products.length).toBe(1);
      expect(response.body.data.products[0].name).toBe('Product 1');
    });

    it('should sort products by price ascending', async () => {
      const response = await request(app)
        .get('/api/products?sortBy=price&sortOrder=asc')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.products).toBeDefined();
      expect(response.body.data.products[0].price).toBe(10.99);
      expect(response.body.data.products[2].price).toBe(30.99);
    });

    it('should paginate products correctly', async () => {
      const response = await request(app)
        .get('/api/products?page=1&limit=2')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.products).toBeDefined();
      expect(response.body.data.products.length).toBe(2);
      expect(response.body.data.pagination.page).toBe(1);
      expect(response.body.data.pagination.limit).toBe(2);
      expect(response.body.data.pagination.total).toBe(3);
      expect(response.body.data.pagination.pages).toBe(2);
    });
  });

  describe('GET /api/products/:id', () => {
    let product;

    beforeEach(async () => {
      product = new Product({
        name: 'Test Product',
        description: 'A test product',
        price: 99.99,
        category: 'Test Category',
        stock: 10,
        sku: 'TEST-001',
        createdBy: user._id,
        updatedBy: user._id
      });
      await product.save();
    });

    it('should get product by ID', async () => {
      const response = await request(app)
        .get(`/api/products/${product._id}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.product).toBeDefined();
      expect(response.body.data.product.name).toBe('Test Product');
    });

    it('should return error for non-existent product', async () => {
      const response = await request(app)
        .get('/api/products/507f1f77bcf86cd799439011') // Non-existent ID
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toBe('Product not found');
    });
  });

  describe('PUT /api/products/:id', () => {
    let product;

    beforeEach(async () => {
      product = new Product({
        name: 'Test Product',
        description: 'A test product',
        price: 99.99,
        category: 'Test Category',
        stock: 10,
        sku: 'TEST-001',
        createdBy: user._id,
        updatedBy: user._id
      });
      await product.save();
    });

    it('should update product successfully', async () => {
      const updateData = {
        name: 'Updated Product',
        price: 149.99,
        stock: 20
      };

      const response = await request(app)
        .put(`/api/products/${product._id}`)
        .set('Authorization', `Bearer ${userToken}`)
        .send(updateData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('Product updated successfully');
      expect(response.body.data.product.name).toBe('Updated Product');
      expect(response.body.data.product.price).toBe(149.99);
      expect(response.body.data.product.stock).toBe(20);

      // Verify update in database
      const updatedProduct = await Product.findById(product._id);
      expect(updatedProduct.name).toBe('Updated Product');
      expect(updatedProduct.price).toBe(149.99);
    });

    it('should return error for duplicate SKU', async () => {
      // Create another product
      const otherProduct = new Product({
        name: 'Other Product',
        price: 50.99,
        category: 'Other Category',
        stock: 5,
        sku: 'OTHER-SKU',
        createdBy: user._id,
        updatedBy: user._id
      });
      await otherProduct.save();

      const response = await request(app)
        .put(`/api/products/${product._id}`)
        .set('Authorization', `Bearer ${userToken}`)
        .send({ sku: 'OTHER-SKU' })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toBe('SKU already exists');
    });

    it('should return error for non-existent product', async () => {
      const response = await request(app)
        .put('/api/products/507f1f77bcf86cd799439011')
        .set('Authorization', `Bearer ${userToken}`)
        .send({ name: 'Updated' })
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toBe('Product not found');
    });
  });

  describe('DELETE /api/products/:id', () => {
    let product;

    beforeEach(async () => {
      product = new Product({
        name: 'Test Product',
        description: 'A test product',
        price: 99.99,
        category: 'Test Category',
        stock: 10,
        sku: 'TEST-001',
        createdBy: user._id,
        updatedBy: user._id
      });
      await product.save();
    });

    it('should delete product successfully (soft delete)', async () => {
      const response = await request(app)
        .delete(`/api/products/${product._id}`)
        .set('Authorization', `Bearer ${userToken}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('Product deleted successfully');

      // Verify soft delete in database
      const deletedProduct = await Product.findById(product._id);
      expect(deletedProduct.isActive).toBe(false);
    });

    it('should return error for non-existent product', async () => {
      const response = await request(app)
        .delete('/api/products/507f1f77bcf86cd799439011')
        .set('Authorization', `Bearer ${userToken}`)
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toBe('Product not found');
    });

    it('should return error for unauthenticated user', async () => {
      const response = await request(app)
        .delete(`/api/products/${product._id}`)
        .expect(401);

      expect(response.body.success).toBe(false);
    });
  });

  describe('PATCH /api/products/:id/stock', () => {
    let product;

    beforeEach(async () => {
      product = new Product({
        name: 'Test Product',
        description: 'A test product',
        price: 99.99,
        category: 'Test Category',
        stock: 10,
        sku: 'TEST-001',
        createdBy: user._id,
        updatedBy: user._id
      });
      await product.save();
    });

    it('should update stock successfully', async () => {
      const response = await request(app)
        .patch(`/api/products/${product._id}/stock`)
        .set('Authorization', `Bearer ${userToken}`)
        .send({ quantity: 5 })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('Stock updated successfully');
      expect(response.body.data.product.stock).toBe(15);

      // Verify update in database
      const updatedProduct = await Product.findById(product._id);
      expect(updatedProduct.stock).toBe(15);
    });

    it('should decrease stock successfully', async () => {
      const response = await request(app)
        .patch(`/api/products/${product._id}/stock`)
        .set('Authorization', `Bearer ${userToken}`)
        .send({ quantity: -3 })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.product.stock).toBe(7);
    });

    it('should return error for insufficient stock', async () => {
      const response = await request(app)
        .patch(`/api/products/${product._id}/stock`)
        .set('Authorization', `Bearer ${userToken}`)
        .send({ quantity: -15 }) // More than available
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toBe('Insufficient stock');
    });

    it('should return error for missing quantity', async () => {
      const response = await request(app)
        .patch(`/api/products/${product._id}/stock`)
        .set('Authorization', `Bearer ${userToken}`)
        .send({})
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toBe('Validation failed');
    });
  });
});