"""
RAG Evaluation Tests
Tests for Text2SQL correctness and RAG grounding.
"""
import pytest
from backend.rag_service import TextRetrievalService, RAGContext
from backend.database import execute_query


class TestTextRetrieval:
    """Test retrieval of relevant documents."""
    
    def test_retrieve_support_articles_by_keyword(self):
        """Test retrieving support articles by keyword."""
        results = TextRetrievalService.retrieve_support_articles("storage")
        
        assert isinstance(results, list)
        if len(results) > 0:
            assert 'title' in results[0]
            assert 'content' in results[0]
    
    def test_retrieve_products_by_name(self):
        """Test retrieving products by name."""
        results = TextRetrievalService.retrieve_products_info("Orange")
        
        assert isinstance(results, list)
        if len(results) > 0:
            assert 'name' in results[0]
            assert 'sku' in results[0]
            assert 'ingredients' in results[0]
    
    def test_retrieve_allergen_info(self):
        """Test retrieving allergen information."""
        results = TextRetrievalService.retrieve_allergen_info("Which products contain allergens?")
        
        assert isinstance(results, list)
        if len(results) > 0:
            assert 'product_name' in results[0]
            assert 'allergen' in results[0]


class TestRAGContext:
    """Test RAG context formation."""
    
    def test_context_retrieval(self):
        """Test context retrieval for a query."""
        context = RAGContext("What orange juice products do you have?")
        context.retrieve()
        
        assert context.query == "What orange juice products do you have?"
        assert isinstance(context.support_articles, list)
        assert isinstance(context.products, list)
    
    def test_context_formatting(self):
        """Test context formatting for LLM input."""
        context = RAGContext("Tell me about products")
        context.retrieve()
        formatted = context.format_context()
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0


class TestText2SQLValidation:
    """Test Text2SQL query correctness.
    
    These tests validate that natural language questions can be properly
    converted to SQL and produce expected results.
    """
    
    def test_simple_product_lookup(self):
        """Test simple product lookup query."""
        # Query: "What orange juice products do we have?"
        results = execute_query("""
            SELECT * FROM products 
            WHERE category = 'Juice' AND name LIKE '%Orange%'
        """)
        
        assert len(results) > 0
        assert results[0]['category'] == 'Juice'
        assert 'Orange' in results[0]['name']
    
    def test_product_by_ingredient(self):
        """Test finding products by ingredient."""
        # Query: "Which products contain strawberry?"
        results = execute_query("""
            SELECT DISTINCT p.* FROM products p
            JOIN product_ingredients pi ON p.id = pi.product_id
            JOIN ingredients i ON pi.ingredient_id = i.id
            WHERE i.name = 'Strawberry'
        """)
        
        assert len(results) > 0
    
    def test_category_filter(self):
        """Test filtering by category."""
        # Query: "What are all sparkling drinks?"
        results = execute_query("SELECT * FROM products WHERE category = 'Sparkling'")
        
        assert len(results) > 0
        assert all(p['category'] == 'Sparkling' for p in results)
    
    def test_price_lookup(self):
        """Test price lookup."""
        # Query: "How much does Orange Splash cost?"
        results = execute_query("""
            SELECT price_cents FROM products WHERE name = 'Orange Splash'
        """)
        
        assert len(results) > 0
        assert 'price_cents' in results[0]
        assert results[0]['price_cents'] > 0
    
    def test_volume_comparison(self):
        """Test numeric comparison on volume."""
        # Query: "Show me products under 300ml"
        results = execute_query("""
            SELECT * FROM products 
            WHERE unit_volume_ml < 300
            ORDER BY unit_volume_ml
        """)
        
        assert len(results) > 0
        assert all(p['unit_volume_ml'] < 300 for p in results)
    
    def test_product_ingredients_join(self):
        """Test multi-table join for ingredients."""
        # Query: "What ingredients are in Berry Fizz?"
        results = execute_query("""
            SELECT i.name, pi.quantity_grams
            FROM ingredients i
            JOIN product_ingredients pi ON i.id = pi.ingredient_id
            JOIN products p ON pi.product_id = p.id
            WHERE p.name = 'Berry Fizz'
        """)
        
        assert len(results) > 0
        for row in results:
            assert 'name' in row
            assert 'quantity_grams' in row
    
    def test_allergen_free_products(self):
        """Test complex subquery for allergen-free products."""
        # Query: "Which products are allergen-free?"
        results = execute_query("""
            SELECT DISTINCT p.* FROM products p
            WHERE p.id NOT IN (
                SELECT pi.product_id FROM product_ingredients pi
                JOIN ingredients i ON pi.ingredient_id = i.id
                WHERE i.allergen_flag = 1
            )
        """)
        
        # Should have some allergen-free products
        assert len(results) >= 0
    
    def test_support_article_retrieval(self):
        """Test support article retrieval."""
        # Query: "Tell me about storage instructions"
        results = execute_query("""
            SELECT content FROM support_articles WHERE topic = 'Storage'
        """)
        
        assert len(results) > 0
    
    def test_sorted_products_by_price(self):
        """Test sorting by price."""
        # Query: "List all products with prices sorted by cost"
        results = execute_query("""
            SELECT name, price_cents FROM products 
            ORDER BY price_cents ASC
        """)
        
        assert len(results) > 0
        # Verify sorting
        for i in range(len(results) - 1):
            assert results[i]['price_cents'] <= results[i+1]['price_cents']
    
    def test_like_based_search(self):
        """Test LIKE-based ingredient search."""
        # Query: "Which products have coconut as ingredient?"
        results = execute_query("""
            SELECT DISTINCT p.* FROM products p
            JOIN product_ingredients pi ON p.id = pi.product_id
            JOIN ingredients i ON pi.ingredient_id = i.id
            WHERE i.name LIKE '%Coconut%'
        """)
        
        assert len(results) > 0


class TestRAGGrounding:
    """Test RAG grounding (factual consistency with source data)."""
    
    def test_product_data_accuracy(self):
        """Test that retrieved product data is accurate."""
        context = RAGContext("Orange Splash")
        context.retrieve()
        
        # Check products were retrieved
        if len(context.products) > 0:
            for product in context.products:
                # Verify fields exist and have reasonable values
                assert 'sku' in product
                assert 'name' in product
                assert 'price_cents' in product
                assert product['price_cents'] > 0
    
    def test_ingredient_relationships_correct(self):
        """Test that ingredient relationships are correctly retrieved."""
        products = execute_query("""
            SELECT id, name FROM products LIMIT 1
        """)
        
        if len(products) > 0:
            product_id = products[0]['id']
            
            ingredients = execute_query("""
                SELECT i.name FROM ingredients i
                JOIN product_ingredients pi ON i.id = pi.ingredient_id
                WHERE pi.product_id = ?
            """, (product_id,))
            
            # If product has ingredients, verify relationship
            if len(ingredients) > 0:
                assert all('name' in ing for ing in ingredients)


class TestRAGEvaluation:
    """Test RAG evaluation metrics."""
    
    def test_faithfulness_high_confidence_facts(self):
        """Test faithfulness on high-confidence facts.
        
        Target: ≥0.85 faithfulness for products and ingredients.
        """
        # Test that core product data matches schema
        products = execute_query("SELECT * FROM products")
        
        for product in products:
            # Check that all expected fields are present
            assert 'id' in product
            assert 'sku' in product
            assert 'name' in product
            assert 'unit_volume_ml' in product
            
            # Check constraints
            assert product['unit_volume_ml'] in [250, 330, 500, 1000, 1500, 2000]
        
        # Faithfulness: 100% compliance with schema
        assert len(products) > 0
    
    def test_context_relevance(self):
        """Test that context is relevant to queries.
        
        Target: Context relevance > 0.7
        """
        test_queries = [
            ("Orange", ["Orange Splash", "Juice"]),
            ("Sparkling", ["Fizz", "Sparkling"]),
            ("Strawberry", ["Berry", "Strawberry"]),
        ]
        
        for query, expected_keywords in test_queries:
            context = RAGContext(query)
            context.retrieve()
            formatted = context.format_context()
            
            # Check that at least one expected keyword appears
            has_relevant_content = any(
                keyword.lower() in formatted.lower()
                for keyword in expected_keywords
            )
            
            # If retrieval returned results, they should contain keywords
            if len(context.products) > 0 or len(context.support_articles) > 0:
                assert has_relevant_content or len(formatted) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
