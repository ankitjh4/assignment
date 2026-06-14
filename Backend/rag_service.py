"""
RAG (Retrieval-Augmented Generation) service for DRINKOO chatbot.
Handles document retrieval and LLM interaction.
"""
import logging
import json
from typing import List, Dict, Any, Optional
import requests
from backend.config import Config
from backend.database import execute_query

logger = logging.getLogger(__name__)


class TextRetrievalService:
    """Retrieves relevant documents from the database."""
    
    @staticmethod
    def retrieve_support_articles(query: str, limit: int = Config.RAG_CONTEXT_LIMIT) -> List[Dict[str, Any]]:
        """Retrieve support articles relevant to user query."""
        try:
            # Simple keyword-based retrieval (can be enhanced with semantic search)
            results = execute_query("""
                SELECT id, title, content, topic FROM support_articles
                WHERE title LIKE ? OR content LIKE ? OR topic LIKE ?
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
            
            logger.info(f"Retrieved {len(results)} support articles for query: {query}")
            return results
        
        except Exception as e:
            logger.error(f"Error retrieving support articles: {e}")
            return []
    
    @staticmethod
    def retrieve_products_info(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve product information relevant to query."""
        try:
            # Search across products and ingredients
            products = execute_query("""
                SELECT DISTINCT p.id, p.sku, p.name, p.description, 
                       p.unit_volume_ml, p.category, p.price_cents
                FROM products p
                WHERE p.name LIKE ? OR p.description LIKE ? OR p.category LIKE ?
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
            
            # Enrich with ingredient information
            for product in products:
                ingredients = execute_query("""
                    SELECT i.name, pi.quantity_grams
                    FROM ingredients i
                    JOIN product_ingredients pi ON i.id = pi.ingredient_id
                    WHERE pi.product_id = ?
                """, (product['id'],))
                product['ingredients'] = ingredients
            
            logger.info(f"Retrieved {len(products)} products for query: {query}")
            return products
        
        except Exception as e:
            logger.error(f"Error retrieving products: {e}")
            return []
    
    @staticmethod
    def retrieve_allergen_info(query: str) -> List[Dict[str, Any]]:
        """Retrieve allergen information."""
        try:
            if "allergen" not in query.lower():
                return []
            
            allergens = execute_query("""
                SELECT DISTINCT p.name as product_name, i.name as allergen
                FROM products p
                JOIN product_ingredients pi ON p.id = pi.product_id
                JOIN ingredients i ON pi.ingredient_id = i.id
                WHERE i.allergen_flag = 1
            """)
            
            logger.info(f"Retrieved allergen info: {len(allergens)} items")
            return allergens
        
        except Exception as e:
            logger.error(f"Error retrieving allergen info: {e}")
            return []


class RAGContext:
    """Structures context for LLM generation."""
    
    def __init__(self, query: str):
        self.query = query
        self.support_articles: List[Dict] = []
        self.products: List[Dict] = []
        self.allergens: List[Dict] = []
    
    def retrieve(self):
        """Retrieve all relevant documents."""
        self.support_articles = TextRetrievalService.retrieve_support_articles(self.query)
        self.products = TextRetrievalService.retrieve_products_info(self.query)
        self.allergens = TextRetrievalService.retrieve_allergen_info(self.query)
    
    def format_context(self) -> str:
        """Format retrieved documents as context string."""
        context_parts = []
        
        if self.support_articles:
            context_parts.append("Support Articles:")
            for article in self.support_articles:
                context_parts.append(f"- {article['title']}: {article['content'][:200]}...")
        
        if self.products:
            context_parts.append("\nProducts:")
            for product in self.products:
                price_usd = product['price_cents'] / 100
                context_parts.append(
                    f"- {product['name']} ({product['sku']}): {product['description']} "
                    f"({product['unit_volume_ml']}mL, ${price_usd:.2f})"
                )
                if product.get('ingredients'):
                    ingredients_str = ", ".join([i['name'] for i in product['ingredients']])
                    context_parts.append(f"  Ingredients: {ingredients_str}")
        
        if self.allergens:
            context_parts.append("\nAllergen Information:")
            for allergen in self.allergens[:5]:
                context_parts.append(f"- {allergen['product_name']} contains {allergen['allergen']}")
        
        return "\n".join(context_parts) if context_parts else "No relevant information found."


class LLMService:
    """Handles communication with OpenRouter API."""
    
    @staticmethod
    def generate_response(user_query: str, context: str) -> Optional[str]:
        """Generate LLM response using OpenRouter."""
        if not Config.OPENROUTER_API_KEY:
            logger.error("OpenRouter API key not configured")
            return "API not configured. Please set OPENROUTER_API_KEY."
        
        # If using test/demo API key, provide mock response based on context
        if Config.OPENROUTER_API_KEY in ["test-key", "test", "demo"]:
            logger.info("Using demo mode with test API key")
            return LLMService._generate_mock_response(user_query, context)
        
        system_prompt = """You are a helpful customer service assistant for DRINKOO beverages.
Use the provided context about products, ingredients, and support articles to answer user questions.
Keep responses concise and grounded in the provided information.
If information is not available in the context, clearly state that."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_query}"}
        ]
        
        try:
            response = requests.post(
                f"{Config.OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": Config.OPENROUTER_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.9
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                assistant_message = result["choices"][0]["message"]["content"]
                logger.info(f"LLM response generated for query: {user_query}")
                return assistant_message
            else:
                logger.error(f"Unexpected API response: {result}")
                return "Unable to generate response from LLM."
        
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {e}")
            return f"Service error: {str(e)}"
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    @staticmethod
    def _generate_mock_response(user_query: str, context: str) -> str:
        """Generate a mock response based on context (for testing without API key)."""
        # Simple keyword matching for demo responses
        query_lower = user_query.lower()
        
        mock_responses = {
            "orange": "Orange Splash is our refreshing orange juice drink (330ml), priced at $3.50. It's made with fresh orange juice and carbonated water, perfect for a morning refreshment.",
            "berry": "Berry Fizz is our carbonated berry drink (500ml) for $4.50. It combines fresh strawberries with carbonated water for a refreshing, bubbly experience.",
            "product": "We have 6 main DRINKOO beverages: Orange Splash (330ml, $3.50), Berry Fizz (500ml, $4.50), Tropical Mix (250ml, $3.00), Lemon Zest (330ml, $4.00), Honey Vanilla (330ml, $5.00), and Coconut Dream (250ml, $4.50).",
            "allergen": "Our drinks may contain traces of nuts and dairy. Some of our special drinks include ingredients with allergen flags. Please check the specific product labels for detailed allergen information.",
            "price": "Our beverages range from $3.00 to $5.00 depending on the product and size.",
            "storage": "Keep all DRINKOO products refrigerated. Use within 7 days of opening for best quality.",
            "ingredient": "Our products feature natural ingredients like orange juice, strawberry, lemon, honey, coconut milk, and more. All DRINKOO beverages contain no artificial colors or preservatives.",
        }
        
        # Try to match keywords in the query
        for keyword, response in mock_responses.items():
            if keyword in query_lower:
                return response
        
        # Default response if no keywords match
        return f"Thanks for asking! Based on our DRINKOO collection, we offer a variety of refreshing beverages with natural ingredients. Feel free to ask about specific products, ingredients, allergen information, or pricing. What would you like to know more about?"


def process_chatbot_query(user_query: str) -> Dict[str, Any]:
    """Main function to process user query through RAG pipeline."""
    try:
        # Retrieve relevant context
        rag_context = RAGContext(user_query)
        rag_context.retrieve()
        formatted_context = rag_context.format_context()
        
        # Generate response
        response = LLMService.generate_response(user_query, formatted_context)
        
        return {
            "status": "success",
            "query": user_query,
            "response": response,
            "context": {
                "support_articles": len(rag_context.support_articles),
                "products": len(rag_context.products),
                "allergens": len(rag_context.allergens)
            }
        }
    
    except Exception as e:
        logger.error(f"Chatbot processing error: {e}")
        return {
            "status": "error",
            "query": user_query,
            "response": f"Error processing query: {str(e)}",
            "context": {}
        }
